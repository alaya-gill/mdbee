import logging
from datetime import timedelta, datetime, timezone
from hashlib import sha1

from django.contrib.auth import signals
from django.utils.translation import gettext as _
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.middleware.csrf import get_token
from django.conf import settings as django_settings

from drf_jwt_2fa.throttling import AuthTokenThrottler, CodeTokenThrottler
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_jwt import views as jwt_views
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import RefreshJSONWebToken, VerifyJSONWebToken

from mdbee.synergy_auth import serializers
from mdbee.synergy_auth.models import ApplicationSettings
from mdbee.users import signals as user_signals
from mdbee.utils.custom_payload import jwt_response_payload_handler

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AdminObtainCodeToken(jwt_views.ObtainJSONWebToken):
    # throttle_classes = [CodeTokenThrottler]
    throttle_classes = []

    def get_serializer_class(self):
        request = self.request
        try:
            cookie_name = sha1(request.data.get('email').encode('UTF-8')).hexdigest()[:10]
            if request.COOKIES.get(cookie_name) and request.data.get('password'):
                return serializers.AdminAuthSerializer
            else:
                return serializers.AdminCodeTokenSerializer
        except AttributeError as ex:
            logger.warning(ex)
            return serializers.AdminCodeTokenSerializer


    def post(self, request, *args, **kwargs):
        data = request.data
        # if data.get('email', None):
        #     data['email'] = data['email'].lower()
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            is_authenticated = serializer.validated_data.get('is_authenticated')
            user = serializer.validated_data.get('_user') or request.user
            token = serializer.validated_data.get('token')
            otp_sent_to = serializer.validated_data.get('otp_sent_to')

            # for logging purpose only
            _user = serializer.validated_data.get('_user')

            session_timeout = ApplicationSettings.objects.get(setting_name="session_timeout")

            
            request.session['django_timezone'] = django_settings.TIME_ZONE

            if is_authenticated:
                if api_settings.JWT_AUTH_COOKIE:
                    expiration = (datetime.now(timezone.utc) + timedelta(days=7))
                    response = Response(
                        jwt_response_payload_handler(token, user, request, is_authenticated, otp_sent_to), content_type="text/html")
                    cache.set(user.id, token, session_timeout.value * 60)
                    response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, httponly=True, samesite=None, secure=False)
                    signals.user_logged_in.send(
                sender=self.__class__, user=user, request=self.request
            )
                    return response

            response = jwt_response_payload_handler(token, user, request, is_authenticated, otp_sent_to)
            user_signals.otp_generated.send(
                sender=self.__class__, user=_user, request=self.request
            )
            return Response(response, content_type="text/html; charset=utf-8")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserObtainCodeToken(jwt_views.ObtainJSONWebToken):
    # throttle_classes = [CodeTokenThrottler]
    throttle_classes = []

    def get_serializer_class(self):
        request = self.request
        try:
            cookie_name = sha1(request.data.get('email').encode('UTF-8')).hexdigest()[:10]
            if request.COOKIES.get(cookie_name) and request.data.get('password'):
                return serializers.UserAuthSerializer
            else:
                return serializers.UserCodeTokenSerializer
        except:
            return serializers.UserCodeTokenSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        try:
            if serializer.is_valid():
                is_authenticated = serializer.validated_data.get('is_authenticated')
                user = serializer.validated_data.get('_user') or request.user
                token = serializer.validated_data.get('token')
                otp_sent_to = serializer.validated_data.get('otp_sent_to')

                # for logging purpose only
                _user = serializer.validated_data.get('_user')
                if otp_sent_to:
                    otp_sent_to =  _user.email
                request.session['django_timezone'] =  django_settings.TIME_ZONE

                session_timeout = ApplicationSettings.objects.get(setting_name="session_timeout")
                
                if is_authenticated:
                   if api_settings.JWT_AUTH_COOKIE:
                        expiration = (datetime.now(timezone.utc) + timedelta(days=7))

                        response = Response(
                            jwt_response_payload_handler(token, user, request, is_authenticated, otp_sent_to), content_type="text/html; charset=utf-8")
                        cache.set(user.id, token, session_timeout.value * 60)
                        response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                            token,
                                            httponly=True, samesite=None, secure=False)
                        signals.user_logged_in.send(
                            sender=self.__class__, user=_user, request=self.request
                        )
                        return response
                if _user.is_superuser:
                    raise AuthenticationFailed(_("Login Failed, user's email/password is incorrect or user's account is inactive"))
                response = jwt_response_payload_handler(token, user, request, is_authenticated, otp_sent_to)
                user_signals.otp_generated.send(
                    sender=self.__class__, user=_user, request=self.request
                )
                return Response(response, content_type="text/html; charset=utf-8")
        except AuthenticationFailed:
            signals.user_login_failed.send(sender=self.__class__,credentials=request.data,request=self.request)
            return Response({"message":_('Incorrect email address or password')},status=status.HTTP_401_UNAUTHORIZED)

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainAuthToken(jwt_views.ObtainJSONWebToken):
    serializer_class = serializers.AuthTokenSerializer
    # throttle_classes = [AuthTokenThrottler]
    throttle_classes = []

    def post(self, request, *args, **kwargs):
        data = request.data
        if data.get('email', None):
            data['email'] = data['email'].lower()
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            rm_token = serializer.object.get('remember_token')
            is_authenticated = serializer.object.get('is_authenticated')
            # response = super().post(request, args, kwargs)
            response_data = jwt_response_payload_handler(token, user, request, is_authenticated)
            response = Response(response_data, content_type="text/html; charset=utf-8")
            request.session['django_timezone'] =  django_settings.TIME_ZONE
            request.session['user_id'] = user.id
            if request.data.get("remember_flag"):
                site = Site.objects.get(id=1)
                cookie_name = sha1(user.email.encode('UTF-8')).hexdigest()[:10]
                response.set_cookie(cookie_name, rm_token, expires=datetime.now(timezone.utc) + timedelta(days=365),
                                    secure=False, httponly=True)

            session_timeout = ApplicationSettings.objects.get(setting_name="session_timeout")

            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.now(timezone.utc) + timedelta(days=7))
                cache.set(user.id, token, session_timeout.value * 60)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    httponly=True)
            # signals.user_logged_in.send(
            #     sender=self.__class__, user=user, request=self.request
            # )
            signals.user_logged_in.send(
                sender=self.__class__, user=user, request=self.request
            )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeToken(jwt_views.ObtainJSONWebToken):
    serializer_class = serializers.VerifyCodeTokenSerializer
    # throttle_classes = [AuthTokenThrottler]
    throttle_classes = []

    def post(self, request, *args, **kwargs):
        response = super().post(request, args, kwargs)
        response.delete_cookie(api_settings.JWT_AUTH_COOKIE)
        return response

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        response = Response(data={"success": True}, status=status.HTTP_200_OK, content_type="text/html; charset=utf-8")
        response.set_cookie(django_settings.CSRF_COOKIE_NAME,
                            csrf_token,
                            max_age=django_settings.CSRF_COOKIE_AGE,
                            domain=django_settings.CSRF_COOKIE_DOMAIN,
                            path=django_settings.CSRF_COOKIE_PATH,
                            secure=django_settings.CSRF_COOKIE_SECURE,
                            httponly=django_settings.CSRF_COOKIE_HTTPONLY,
                            samesite=django_settings.CSRF_COOKIE_SAMESITE,
                            )
        return response


# TODO add timezone set


class ResendCodeToken(jwt_views.ObtainJSONWebToken):
    # throttle_classes = [CodeTokenThrottler]
    throttle_classes = []
    serializer_class = serializers.ResendCodeTokenSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        if data.get('email', None):
            data['email'] = data['email'].lower()
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            is_authenticated = serializer.validated_data.get('is_authenticated')
            user = serializer.validated_data.get('user') or request.user
            print(user)
            token = serializer.validated_data.get('token')
            otp_sent_to = serializer.validated_data.get('otp_sent_to')
            # response_data = super().post(request, args, kwargs)

            # for logging purpose only
            _user = serializer.validated_data.get('_user')
            request.session['django_timezone'] =  django_settings.TIME_ZONE
            response = jwt_response_payload_handler(token, user, request, is_authenticated, otp_sent_to)
            user_signals.otp_resend_success.send(
                sender=self.__class__, user=_user, request=self.request
            )
            return Response(response, content_type="text/html; charset=utf-8")
        user_signals.otp_resend_failure.send(
            sender=self.__class__, user=_user, request=self.request
        )
        return Response("serializer.errors", status=status.HTTP_400_BAD_REQUEST, content_type="text/html; charset=utf-8")


# class VerifyAuthToken(jwt_views.VerifyJSONWebToken):
#     pass
RefreshJSONWebToken.serializer_class = serializers.RefreshJSONWebTokenSerializerCookieBased
VerifyJSONWebToken.serializer_class = serializers.VerifyJSONWebTokenSerializerCookieBased

admin_obtain_code_token = AdminObtainCodeToken.as_view()
user_obtain_code_token = UserObtainCodeToken.as_view()
obtain_auth_token = ObtainAuthToken.as_view()
verify_code_token = VerifyCodeToken.as_view()
resend_code_token = ResendCodeToken.as_view()
refresh_auth_token = RefreshJSONWebToken.as_view()
verify_auth_token = VerifyJSONWebToken.as_view()
