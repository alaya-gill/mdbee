from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if isinstance(exc, exceptions.AuthenticationFailed):
        response.status_code = status.HTTP_401_UNAUTHORIZED
    # Now add the HTTP status code to the response.

    if response is not None:
        if response.status_code == 500:
            response.data['message'] = "Error"
            response.data['detail'] = "Error"
        elif type(response.data) == dict and response.data.get('detail'):
            response.data['message'] = response.data['detail']
            del response.data['detail']
            response.data['status_code'] = response.status_code
            response.data['success'] = False
        elif type(response.data) == dict:
            message = {}
            for key, value in response.data.items():
                message[key] = str(value)
            response.data.clear()
            response.data['message'] = message
            response.data['status_code'] = response.status_code
            response.data['success'] = False
        else:
            pass

    return response


class TokenError(Exception):
    pass


class TokenBackendError(Exception):
    pass


class DetailDictMixin:
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {'detail': self.default_detail, 'code': self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict['detail'] = detail

        if code is not None:
            detail_dict['code'] = code

        super().__init__(detail_dict)


class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
    pass


class InvalidToken(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Token is invalid or expired')
    default_code = 'token_not_valid'
