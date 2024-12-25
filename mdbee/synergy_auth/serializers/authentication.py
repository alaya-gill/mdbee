from hashlib import sha1

import jwt
from django.contrib.auth import authenticate, get_user_model
from django.core import exceptions
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, APIException
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.compat import Serializer as JwtSerializer
from rest_framework_jwt.serializers import PasswordField
from rest_framework_jwt.serializers import RefreshJSONWebTokenSerializer, VerifyJSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings as jwt_settings

from mdbee.synergy_auth.token_manager import CodeTokenManager

User = get_user_model()
jwt_encode_handler = jwt_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = jwt_settings.JWT_PAYLOAD_HANDLER


class Jwt2faSerializer(JwtSerializer):
    token_manager_class = CodeTokenManager

    def __init__(self, *args, **kwargs):
        super(Jwt2faSerializer, self).__init__(*args, **kwargs)
        self.token_manager = self.token_manager_class(class_context=self.context.get('request', None))

    def validate(self, attrs):
        validated_attrs = super(Jwt2faSerializer, self).validate(attrs)
        user, is_authenticated, otp_sent_to = self._authenticate(validated_attrs)
        return {
            'token': self._create_token(user, send_to=otp_sent_to),
            'user': user if is_authenticated else None,
            'is_authenticated': is_authenticated,
            'otp_sent_to': otp_sent_to,
            '_user': user
        }


# class AdminCodeTokenSerializer(Jwt2faSerializer):
#     username_field = User.USERNAME_FIELD

#     default_error_messages = {
#         'no_active_account': _('No active account found with the given credentials'),
#         'no_admin_account': _('No active admin account found with the given credentials')
#     }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields[self.username_field] = serializers.CharField()
#         self.fields['password'] = PasswordField(required=False)

#     def _authenticate(self, attrs):
#         is_authenticated = False
#         authenticate_kwargs = {
#             self.username_field: attrs[self.username_field],
#             'password': attrs.get('password')
#         }
#         try:
#             authenticate_kwargs['request'] = self.context['request']
#         except KeyError:
#             pass
#         if authenticate_kwargs.get('password'):
#             user = authenticate(**authenticate_kwargs)
#             is_authenticated = True
#         else:
#             user = User.objects.get_by_natural_key(authenticate_kwargs.get(self.username_field))
#         if not user or not user.is_active:
#             raise AuthenticationFailed(self.error_messages['no_active_account'], 'no_active_account',)
#         elif not user.is_admin:
#             raise AuthenticationFailed(self.error_messages['no_admin_account'], 'no_admin_account',)
#         return (user,is_authenticated)

#     def _create_token(self, user):
#         return self.token_manager.create_code_token(user)


class AdminCodeTokenSerializer(Jwt2faSerializer):
    username_field = User.USERNAME_FIELD

    default_error_messages = {
        'no_active_account': _('Incorrect email address or password'),
        'no_admin_account': _('Incorrect email address or password')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(required=False)

    def _authenticate(self, attrs):
        is_authenticated = False
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs.get('password'),
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        if authenticate_kwargs.get('password'):
            user = authenticate(**authenticate_kwargs)
            # is_authenticated = True
            request = self.context.get('request')
        else:
            user = User.objects.get_by_natural_key(authenticate_kwargs.get(self.username_field))
        if not user or not user.is_active:
            raise AuthenticationFailed(self.error_messages['no_active_account'], 'no_active_account',)
        elif not user.is_superuser:
            raise AuthenticationFailed(self.error_messages['no_active_account'], 'no_active_account',)
        otp_sent_to = user.email
        return user, is_authenticated, otp_sent_to

    def _create_token(self, user, send_to=None):
        return self.token_manager.create_code_token(user, send_to)


class UserCodeTokenSerializer(Jwt2faSerializer):
    username_field = User.USERNAME_FIELD

    default_error_messages = {
        'no_active_account': _('Incorrect email address or password'),
        'no_admin_account': _('Incorrect email address or password')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(required=False)

    def _authenticate(self, attrs):
        is_authenticated = False
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs.get('password'),
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        if authenticate_kwargs.get('password'):
            user = authenticate(**authenticate_kwargs)
            request = self.context.get('request')
        else:
            user = User.objects.get_by_natural_key(authenticate_kwargs.get(self.username_field))
        if not user or not user.is_active:
            raise AuthenticationFailed(self.error_messages['no_active_account'], 'no_active_account',)
        elif user.is_superuser:
            raise AuthenticationFailed(self.error_messages['no_active_account'], 'no_active_account',)
        otp_sent_to = None
        otp_sent_to = user.email
        return user, is_authenticated, otp_sent_to

    def _create_token(self, user, send_to=None):
        return self.token_manager.create_code_token(user, send_to)


class ResendCodeTokenSerializer(Jwt2faSerializer):

    default_error_messages = {
        'no_active_account': _('Incorrect email address or password'),
        'no_admin_account': _('Incorrect email address or password')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['code_token'] = serializers.CharField()
        self.fields['send_to'] = serializers.CharField()

    def _authenticate(self, attrs):
        is_authenticated = False
        authenticate_kwargs = {
            'code_token': attrs.get('code_token'),
            'send_to': attrs.get('send_to'),
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        user_email = self._check_code_token(authenticate_kwargs['code_token'], None)
        user = User.objects.get(email=user_email)

        otp_sent_to = None
        if authenticate_kwargs['send_to'] == 'Email':
            otp_sent_to = user.email
        elif authenticate_kwargs['send_to'] == 'Primary':
            otp_sent_to = user.phone[0:3] + user.phone[-2:].rjust(len(user.phone)-2, '*')
        elif authenticate_kwargs['send_to'] == 'Secondary':
            if not user.phone2:
                raise APIException("Secondary phone number does not exist")
            otp_sent_to = user.phone2[0:3] + user.phone2[-2:].rjust(len(user.phone2) - 2, '*')

        return user, is_authenticated, otp_sent_to

    def _check_code_token(self, code_token, code):
        return self.token_manager.check_code_token_for_resend(code_token)

    def _create_token(self, user, send_to=None):
        return self.token_manager.create_code_token(user, send_to)



class AuthTokenSerializer(Jwt2faSerializer):
    code_token = serializers.CharField(required=True)
    code = PasswordField(write_only=True, required=True)
    remember_flag = serializers.BooleanField(required=False)

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        if(attrs.get('remember_flag')):
            validated_attrs['remember_token'] = self.\
                _create_remember_token(validated_attrs.get('user'))
        return validated_attrs

    def _authenticate(self, attrs):
        code_token = attrs.get('code_token')
        code = attrs.get('code')
        username = self._check_code_token_and_code(code_token, code)
        user = self._get_user(username)
        return user, True, None

    def _check_code_token_and_code(self, code_token, code):
        return self.token_manager.check_code_token_and_code(code_token, code)

    def _get_user(self, username):
        user_model = User
        try:
            user = user_model.objects.get_by_natural_key(username)
        except user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed()
        # check_user_validity(user)
        return user

    def _create_token(self, user, send_to=None):
        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)

    def _create_remember_token(self, user):
        return self.token_manager.create_remember_me_token(user)



class VerifyCodeTokenSerializer(Jwt2faSerializer):
    code_token = serializers.CharField(required=True)
    code = PasswordField(write_only=True, required=True)


    def validate(self, attrs):
        data = super().validate(attrs)
        return{
            'message': "OTP Code Verified",
            'status': 200,
            'success': True,
            'user': data.get('user')
        }

    def _authenticate(self, attrs):
        code_token = attrs.get('code_token')
        code = attrs.get('code')
        username = self._check_code_token_and_code(code_token, code)
        user = self._get_user(username)
        return user, False, None

    def _check_code_token_and_code(self, code_token, code):
        return self.token_manager.check_code_token_and_code(code_token, code)

    def _get_user(self, username):
        user_model = User
        try:
            user = user_model.objects.get_by_natural_key(username)
        except user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed()
        # check_user_validity(user)
        return user

    def _create_token(self, user, send_to=None):
        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)


class AdminAuthSerializer(Jwt2faSerializer):
    token_manager_class = CodeTokenManager
    username_field = User.USERNAME_FIELD

    default_error_messages = {
        'no_active_account': _('Incorrect email address or password'),
        'no_admin_account': _('Incorrect email address or password')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.token_manager = self.token_manager_class()
        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(required=True)

    def _authenticate(self, attrs):
        is_authenticated = False
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs.get('password')
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        user = authenticate(**authenticate_kwargs)
        request = self.context.get('request')
        cookie_name = sha1(request.data.get('email').encode('UTF-8')).hexdigest()[:10]
        remember_token = request.COOKIES.get(cookie_name)
        try:
            payload = self.token_manager.decode_token(remember_token)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise AuthenticationFailed()
        is_authenticated = True
        if not user or not user.is_active:
            raise AuthenticationFailed(self.error_messages['no_active_account'], 'no_active_account',)
        # elif not user.is_admin:
        #     raise AuthenticationFailed(self.error_messages['no_admin_account'], 'no_admin_account',)
        return (user,is_authenticated, None)

    # def _check_code_token_and_code(self, code_token, code):
    #     return self.token_manager.check_code_token_and_code(code_token, code)

    def _get_user(self, username):
        user_model = User
        try:
            user = user_model.objects.get_by_natural_key(username)
        except user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed()
        # check_user_validity(user)
        return user

    def _create_token(self, user, send_to=None):
        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)


class UserAuthSerializer(Jwt2faSerializer):
    token_manager_class = CodeTokenManager
    username_field = User.USERNAME_FIELD

    default_error_messages = {
        'no_active_account': _('Incorrect email address or password'),
        'no_admin_account': _('Incorrect email address or password')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.token_manager = self.token_manager_class()
        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(required=True)

    def _authenticate(self, attrs):
        is_authenticated = False
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs.get('password')
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        user = authenticate(**authenticate_kwargs)
        request = self.context.get('request')
        cookie_name = sha1(request.data.get('email').encode('UTF-8')).hexdigest()[:10]
        remember_token = request.COOKIES.get(cookie_name)
        try:
            payload = self.token_manager.decode_token(remember_token)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise AuthenticationFailed()
        is_authenticated = True
        if not user or not user.is_active:
            raise AuthenticationFailed(self.error_messages['no_active_account'], 'no_active_account',)
        elif user.is_superuser:
            raise AuthenticationFailed(self.error_messages['no_admin_account'], 'no_admin_account',)
        return (user,is_authenticated, None)

    # def _check_code_token_and_code(self, code_token, code):
    #     return self.token_manager.check_code_token_and_code(code_token, code)

    def _get_user(self, username):
        user_model = User
        try:
            user = user_model.objects.get_by_natural_key(username)
        except user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed()
        # check_user_validity(user)
        return user

    def _create_token(self, user, send_to=None):
        payload = jwt_payload_handler(user)
        return jwt_encode_handler(payload)


RefreshJSONWebTokenSerializer._declared_fields.pop('token')
VerifyJSONWebTokenSerializer._declared_fields.pop('token')


class RefreshJSONWebTokenSerializerCookieBased(RefreshJSONWebTokenSerializer):

    def validate(self, attrs):
        if 'token' not in attrs:
            if jwt_settings.JWT_AUTH_COOKIE:
                attrs['token'] = JSONWebTokenAuthentication().get_jwt_value(self.context['request'])
                if attrs['token'] is None:
                    raise AuthenticationFailed(detail='Authentication Token expired or missing', code='missing_or_expired_token')
        return super(RefreshJSONWebTokenSerializerCookieBased, self).validate(attrs)


class VerifyJSONWebTokenSerializerCookieBased(VerifyJSONWebTokenSerializer):

    def validate(self, attrs):
        if 'token' not in attrs:
            if jwt_settings.JWT_AUTH_COOKIE:
                user_id = self.context.get('request').session.get('user_id')
                cached_token = cache.get(user_id)
                if not cached_token:
                    raise AuthenticationFailed(detail="Authentication token is expired or missing")
                else:
                    attrs['token'] = JSONWebTokenAuthentication().get_jwt_value(self.context['request'])
                    if attrs['token'] is None:
                        raise AuthenticationFailed(detail='Authentication Token expired or missing', code='missing_or_expired_token')
                    else:
                        if cached_token != attrs['token']:
                            raise AuthenticationFailed(detail='Authentication Token expired or missing',
                                                       code='missing_or_expired_token')
        return super(VerifyJSONWebTokenSerializerCookieBased, self).validate(attrs)
