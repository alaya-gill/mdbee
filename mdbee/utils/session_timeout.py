import logging

from django.core.cache import cache

from mdbee.synergy_auth.models import ApplicationSettings

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_actual_value(request):
    if request.user is None:
        return None

    return request.user


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # tzname = request.session.get('django_timezone')
        try:
            session_timeout = ApplicationSettings.objects.get(setting_name="session_timeout").value
            user_id = request.session.get('user_id')

            if user_id:
                token = cache.get(user_id)
                is_updated = cache.touch(user_id, session_timeout * 60)
                # logger.info("token: " + str(token))
                # logger.info("is_updated: " + str(is_updated))
                # logger.info("Cache session timeout updated for user id " + str(user_id))
        except Exception as e:

            logger.error(e)
            # logger.error("*****************************************Failed to renew session_timeout in cache")

        return self.get_response(request)
