import jwt
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key

from mdbee.users.serializers import UserSerializer


def jwt_response_payload_handler(token, user=None, request=None, is_authenticated=False, otp_sent_to=None):
    return {
        'success': True,
        'status_code': 200,
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data if not user.is_anonymous else None,
        'message': 'success',
        'is_authenticated': is_authenticated,
        'otp_sent_to': otp_sent_to
    }


def jwt_decode_handler(token, verify_expiry=True):
    options = {
        'verify_exp': verify_expiry,
    }
    # get user from token, BEFORE verification, to get user secret key
    unverified_payload = jwt.decode(token, None, False)
    secret_key = jwt_get_secret_key(unverified_payload)
    return jwt.decode(
        token,
        api_settings.JWT_PUBLIC_KEY or secret_key,
        verify_expiry,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM]
    )
