import json, csv, os
from datetime import datetime, timedelta
from uuid import uuid4

from django.conf import settings as s
from django.contrib.auth import get_user_model, user_logged_out
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from drf_jwt_2fa.authentication import Jwt2faAuthentication
from pytz import common_timezones
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from mdbee.users.compat import get_user_email
from mdbee.users.conf import settings

from mdbee.users.models import User
from mdbee.users.serializers import *


from mdbee.users.utils import headers
from mdbee.utils.filter_backend import CommonFilterBackend
from mdbee.utils.views.base import BaseViewset

User = get_user_model()

class UserViewSet(BaseViewset):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    action_serializers = {
        "default": UserSerializer,
        "create_system_user": SystemUserCreateSerializer,
        'reset_password_confirm': PasswordResetConfirmRetypeSerializer,
    }
    token_generator = default_token_generator
    
    permission_classes = [IsAuthenticated]
    
    def create_system_user_notification(self, request, user_to_create, *args, **kwargs):
        context = {"user": user_to_create}
        to = [get_user_email(user_to_create)]

        if settings.SEND_ACTIVATION_EMAIL:
            user_to_create.is_active = False
            user_to_create.save(update_fields=["is_active"])
            user_obj = User.objects.get(email=user_to_create.email)
            settings.EMAIL.activation_set_password(
                request, context).send(to)

            # signals.user_registered.send(sender=self.__class__, user_subj=request.user,
            #                              user_obj=user_obj)
            
    @action(["post"], detail=False, permission_classes=[], authentication_classes=[Jwt2faAuthentication])
    def create_system_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user_to_create = serializer.save()
        # user=request.user the user who is performing action.
        # Sending Email

        self.create_system_user_notification(request, user_to_create)
        # if settings.SEND_ACTIVATION_EMAIL:
        #     settings.EMAIL.activation(self.request, context).send(to)
        # elif settings.SEND_CONFIRMATION_EMAIL:
        #     settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_201_CREATED,
                        data={
                            "success": True,
                            "status_code": 201,
                            "message": _("User Created"),
                        }
                    )
        
    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        serializer.user.is_active = True
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request, context).send(to)
        return Response(status=status.HTTP_200_OK,
                        data={"success": True, "status_code": 200, "message": _("Password reset")})
