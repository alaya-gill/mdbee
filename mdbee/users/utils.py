from django.contrib.auth import login, logout, user_logged_in, user_logged_out
from django.contrib.auth.hashers import (
    check_password, )
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from mdbee.users.conf import settings

headers = {'name': 'Name', 'account__account_id': 'Account #', 'account__account_name': 'Account', 'address1': "Address", 'city': 'City', 'state': 'State', 'zipcode': 'Postal Code',
           'country': 'Country', 'user_type': 'User Type',  'is_active': "Active", 'email': 'Email', 'phone': 'Phone', }

def encode_uid(pk):
    return force_text(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(pk):
    return force_text(urlsafe_base64_decode(pk))


def login_user(request, user):
    token, _ = settings.TOKEN_MODEL.objects.get_or_create(user=user)
    if settings.CREATE_SESSION_ON_LOGIN:
        login(request, user)
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    return token


def logout_user(request):
    if settings.TOKEN_MODEL:
        settings.TOKEN_MODEL.objects.filter(user=request.user).delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )
    if settings.CREATE_SESSION_ON_LOGIN:
        logout(request)


def compare_password(new_password, old_password):
    """
    Return a boolean of whether the raw_password was correct. Handles
    hashing formats behind the scenes.
    """

    return check_password(new_password, old_password, None)


class ActionViewMixin(object):
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)
