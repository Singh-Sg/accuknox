from django.contrib import admin

from .models import CustomUser, FriendRequest, Friendship


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "is_staff", "is_superuser"]
    search_fields = ["email", "username", "first_name", "last_name"]


admin.site.register(CustomUser, CustomUserAdmin)

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["from_user__email", "to_user__email"]


admin.site.register(FriendRequest, FriendRequestAdmin)


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "friend", "created_at"]
    search_fields = ["user1__email", "user2__email"]


admin.site.register(Friendship, FriendshipAdmin)
