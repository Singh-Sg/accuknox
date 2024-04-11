# service.py
import logging

from django.db.models import Q

from .models import FriendRequest, Friendship

logger = logging.getLogger(__name__)


def create_friendship(user1, user2):
    """
    Create a friendship between two users.
    """
    Friendship.objects.create(user=user1, friend=user2)
    Friendship.objects.create(user=user2, friend=user1)


def get_friends(user):
    """
    Get a list of friends for a given user.
    """
    return Friendship.objects.filter(Q(user=user) | Q(friend=user))


def get_pending_friend_requests(user):
    """
    Get a list of pending friend requests for a given user.
    """
    return FriendRequest.objects.filter(to_user=user, status="pending")
