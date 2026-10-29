from rest_framework.permissions import BasePermission
from .models import AuthorProfile


class IsApprovedAuthor(BasePermission):
    message = "An approved author account is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.author_profile.is_approved
        except AuthorProfile.DoesNotExist:
            return False

