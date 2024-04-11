from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser, FriendRequest, Friendship

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
        ]

    def validate(self, data):
        if data["password"] != data.pop("confirm_password", None):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        user = User.objects.create_user(**validated_data)
        return user


class CustomLoginSerializer(LoginSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username")


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    to_user_email = serializers.EmailField(write_only=True)

    class Meta:
        model = FriendRequest
        fields = ["id", "from_user", "to_user_email", "status", "created_at"]

    def validate(self, attrs):
        to_user_email = attrs.get("to_user_email")

        try:
            user = CustomUser.objects.get(email=to_user_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with the provided email does not exist."
            )

        return {"from_user": attrs["from_user"], "to_user": user}


class FriendshipSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email")
    friend = serializers.EmailField(source="friend.email")

    class Meta:
        model = Friendship
        fields = ["id", "created_at", "user", "friend"]
