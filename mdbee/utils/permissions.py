from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class IsSuperUser(IsAuthenticated):
    message = 'Super User Access permission required'

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAuthenticatedOrDebugging(IsAuthenticated):
    """
    Allows access only to authenticated users when not in debug mode.
    """

    def has_permission(self, request, view):
        if settings.DEBUG:
            return True
        return request.session and "user_id" in request.session


