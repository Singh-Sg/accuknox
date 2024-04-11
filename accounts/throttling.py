from django.utils import timezone
from rest_framework.throttling import UserRateThrottle

from .models import FriendRequest


class FriendRequestThrottle(UserRateThrottle):
    scope = "friend_request"
