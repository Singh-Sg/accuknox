from django.urls import include, path
from .views import (
    FriendRequestSendAPIView,
    FriendRequestStatus,
    FriendshipListAPIView,
    PendingFriendRequestListAPIView,
    UserSearchAPIView,
    UserSignupView,
)

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path("signup/", UserSignupView.as_view(), name="user_signup"),
    path("search/", UserSearchAPIView.as_view(), name="user-search"),
    path(
        "friend-request/send/",
        FriendRequestSendAPIView.as_view(),
        name="friend-request-send",
    ),
    path(
        "friend-request/<int:pk>/accept/",
        FriendRequestStatus.as_view({"post": "accept"}),
        name="friend-request-accept",
    ),
    path(
        "friend-request/<int:pk>/reject/",
        FriendRequestStatus.as_view({"post": "reject"}),
        name="friend-request-reject",
    ),
    path("friends/", FriendshipListAPIView.as_view(), name="friend-list"),
    path(
        "friend-requests/pending/",
        PendingFriendRequestListAPIView.as_view(),
        name="pending-friend-requests",
    ),
]
