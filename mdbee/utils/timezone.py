import datetime
import pytz
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # tzname = request.session.get('django_timezone')
        try:
            tzname = request.session['django_timezone']
        except KeyError:
            tzname = None

        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)

def datetime_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
