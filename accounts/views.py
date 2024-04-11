import logging
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser, FriendRequest, Friendship
from .serializers import (
    FriendRequestSerializer,
    FriendshipSerializer,
    UserSignupSerializer,
)
from .service import create_friendship, get_pending_friend_requests
from .throttling import FriendRequestThrottle

logger = logging.getLogger(__name__)


class UserSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignupSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchAPIView(generics.ListAPIView):
    """
    API endpoint for searching users by email or username.
    """

    serializer_class = UserSignupSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination  # Add pagination class

    def get_queryset(self):
        """
        Get a queryset of users based on the search query.
        """
        query = self.request.query_params.get("search", "")
        return CustomUser.objects.filter(
            Q(email__icontains=query) | Q(username__icontains=query)
        )


class FriendRequestSendAPIView(generics.CreateAPIView):
    """
    API endpoint for sending friend requests.
    """

    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [FriendRequestThrottle]

    def create(self, request, *args, **kwargs):
        """
        Create a new friend request.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from_user = request.user
        to_user = serializer.validated_data["to_user"]
        if to_user == request.user:
            return Response(
                {"error": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response(
                {"error": "Friend request already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        return Response(
            {"message": "Friend request sent successfully."},
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        """
        Perform creation of a new friend request.
        """
        serializer.save()


class FriendRequestStatus(viewsets.ViewSet):
    """
    ViewSet for managing friend request status (accept, reject, list pending requests).
    """

    def accept(self, request, pk):
        """
        Accept a friend request.
        """
        try:
            friend_request = FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist:
            logger.error("Friend request not found")
            return Response(
                {"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if friend_request.to_user != request.user:
            raise PermissionDenied("You are not authorized to perform this action.")

        if friend_request.status == "accepted":
            logger.warning("Attempted to accept already accepted friend request")
            return Response(
                {"error": "This friend request has already been accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_request.status = "accepted"
        friend_request.save()
        # Create friendships for both users
        create_friendship(friend_request.from_user, friend_request.to_user)

        return Response({"detail": "Friend request accepted successfully."})

    def reject(self, request, pk):
        """
        Reject a friend request.
        """
        try:
            # get friend_request
            friend_request = FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist:
            logger.error("Friend request not found")
            return Response(
                {"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if friend_request.to_user != request.user:
            raise PermissionDenied("You are not authorized to perform this action.")

        if friend_request.status == "accepted":
            logger.warning("Attempted to reject already accepted friend request")
            return Response(
                {"error": "This friend request has already been accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_request.status = "rejected"
        friend_request.delete()  # delete Friends Request
        return Response({"detail": "Friend request rejected successfully."})


class FriendshipListAPIView(generics.ListAPIView):
    """
    API endpoint for listing a user's friends.
    """

    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination  # Add pagination class

    def get_queryset(self):
        """
        Get a queryset of the user's friends.
        """
        user = self.request.user
        queryset = Friendship.objects.filter(Q(user=user) | Q(friend=user)).order_by(
            "id"
        )
        return queryset


class PendingFriendRequestListAPIView(generics.ListAPIView):
    """
    API endpoint for listing pending friend requests.
    """

    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination  # Add pagination class

    def get_queryset(self):
        # Get a queryset of pending friend requests for the user.
        return get_pending_friend_requests(self.request.user).order_by("id")
