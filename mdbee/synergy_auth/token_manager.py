import logging
import time
from datetime import timedelta

import jwt
from django.conf import settings as django_settings
from django.contrib.auth import hashers as django_hashers
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from drf_jwt_2fa.exceptions import VerificationCodeSendingFailed
from drf_jwt_2fa.sending import CodeSendingFailed
from drf_jwt_2fa.settings import api_settings
from rest_framework import exceptions

from mdbee.synergy_auth.sending import send_verification_code
from mdbee.utils.send_sms import send_otp

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CodeTokenManager(object):
    jwt_algorithm = 'HS256'

    def __init__(self, class_context):
        self.class_context = class_context

    @property
    def code_length(self):
        return api_settings.CODE_LENGTH

    @property
    def code_chars(self):
        return api_settings.CODE_CHARACTERS

    def create_code_token(self, user, send_to=None):
        """
        Create a code token and send a new verification code.
        Create a new code token for given user with a new randomly
        generated verification code.  The code token is returned and the
        verification code is sent via another channel (e.g. e-mail).
        :type user: django.contrib.auth.models.AbstractBaseUser
        :rtype: str
        """
        code = self.generate_verification_code()
        payload = self.get_token_payload(user, code)
        try:
            self.send_verification_code(user, code, send_to)
        except CodeSendingFailed as error:
            raise VerificationCodeSendingFailed(error)
        return self.encode_token(payload)

    def create_password_reset_token(self, user):
        payload = self.get_password_reset_token_payload(user)
        return self.encode_token(payload)

    def create_remember_me_token(self, user):
        payload = self.get_remember_me_token_payload(user)
        return self.encode_token(payload)

    def check_code_token_and_code(self, token, code):
        """
        Check code token and related verification code.
        Check integrity of the given code token and check that the
        verification code is correct for the given token.  Return
        username of the verified user, if both are OK, or raise a
        validation error otherwise.
        :type token: str
        :param token: Code token to check
        :type code: str
        :param code: Verification code to check against the token
        :rtype: str
        :return: Username of the verified user
        """
        payload = self.decode_token(token)
        hashed_code = payload.get('vch')
        nonce = payload.get('vcn')
        if not self.is_verification_code_ok(code, nonce, hashed_code):
            raise exceptions.AuthenticationFailed()
        return payload.get('usr')


    def check_code_token_for_resend(self, code_token):
        payload = self.decode_token_without_expiry(code_token)
        hashed_code = payload.get('vch')
        nonce = payload.get('vcn')
        usr = payload.get('usr')
        if not usr:
            raise exceptions.AuthenticationFailed()
        return usr



    def generate_verification_code(self):
        return get_random_string(self.code_length, self.code_chars)

    def get_token_payload(self, user, code):
        """
        Get code token for given user and verification code.
        :type user: django.contrib.auth.models.AbstractBaseUser
        :type code: str
        :rtype: dict[str, str|int]
        """
        now = int(time.time())
        expiration_time = api_settings.CODE_EXPIRATION_TIME
        expiration_seconds = int(expiration_time.total_seconds())
        (hashed_code, nonce) = self.hash_verification_code(code)
        return {
            'usr': user.get_username(),
            'vch': hashed_code,  # Verification Code Hash
            'vcn': nonce,  # Verification Code Nonce
            'iat': now,
            'exp': now + expiration_seconds,
        }

    # def get_password_reset_token_payload(self, user):
    #     """
    #     Get code token for given user and verification code.
    #     :type user: django.contrib.synergy_auth.models.AbstractBaseUser
    #     :type code: str
    #     :rtype: dict[str, str|int]
    #     """
    #     now = int(time.time())
    #     expiration_time = api_settings.CODE_EXPIRATION_TIME
    #     expiration_seconds = int(expiration_time.total_seconds())
    #     (hashed_code, nonce) = self.hash_verification_code(code)
    #     return {
    #         'usr': user.get_username(),
    #         'is_authenticated': False,
    #         'exp': now + expiration_seconds,
    #     }

    def get_remember_me_token_payload(self, user):
        """
        Get code token for given user and verification code.
        :type user: django.contrib.auth.models.AbstractBaseUser
        :type code: str
        :rtype: dict[str, str|int]
        """
        now = int(time.time())
        expiration_time = django_settings.SYNERGY_CLOUD.get('REMEMBER_THIS_DEVICE_EXPIRATION_TIME', timedelta(days=365))
        expiration_seconds = int(expiration_time.total_seconds())
        return {
            'user_id': user.pk,
            'username': user.get_username(),
            'exp': now + expiration_seconds,
        }

    def send_verification_code(self, user, code, send_to):
        try:
            send_verification_code( user, code, self.class_context)
        except:
            send_verification_code( user, code, self.class_context)

    def encode_token(self, payload):
        key = api_settings.CODE_TOKEN_SECRET_KEY
        jwt_data = jwt.encode(payload, key, self.jwt_algorithm)
        logger.info(jwt_data)
        return jwt_data.decode('utf-8')

    def decode_token(self, token):
        try:
            return jwt.decode(
                jwt=token,
                key=api_settings.CODE_TOKEN_SECRET_KEY,
                verify=True,
                algorithms=[self.jwt_algorithm])
        except jwt.ExpiredSignature:
            raise exceptions.PermissionDenied(_("Signature has expired."))
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed()

    def decode_token_without_expiry(self, token):
        try:
            return jwt.decode(
                jwt=token,
                key=api_settings.CODE_TOKEN_SECRET_KEY,
                verify=True,
                options={'verify_exp': False},
                algorithms=['HS256'])
        except jwt.ExpiredSignature:
            raise exceptions.PermissionDenied(_("Signature has expired."))
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed()

    def hash_verification_code(self, code):
        nonce = get_random_string(length=10)
        extended_code = self.extend_code(code, nonce)
        hashed_code = django_hashers.make_password(extended_code)
        return (hashed_code, nonce)

    def is_verification_code_ok(self, code, nonce, hashed_code):
        extended_code = self.extend_code(code, nonce)
        return django_hashers.check_password(extended_code, hashed_code)

    def extend_code(self, code, nonce):
        extension = api_settings.CODE_EXTENSION_SECRET
        return code + nonce + extension


