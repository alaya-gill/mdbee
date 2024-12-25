from django.http import JsonResponse
from rest_framework.decorators import api_view, \
    authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from mdbee.utils.models.country import *


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def getCountries(request):

    countries = Country.objects.all().values('name')

    return JsonResponse({
        "success": True,
        "status_code": 200,
        "message": "List of Countries",
        "data": {
            "countries": list(countries)
        }
    })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def getStatesofCountry(request):
    country = request.query_params.get('country', None)
    state = State.objects.filter(country__name=country).values('name')

    return JsonResponse({
        "success": True,
        "status_code": 200,
        "message": "List of states",
        "data": list(state)
    })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def getCitiesofState(request):
    state = request.query_params.get('state', None)
    country = request.query_params.get('country', None)
    cities = City.objects.filter(
        state__name=state, state__country__name=country).values('name')

    return JsonResponse({
        "success": True,
        "status_code": 200,
        "message": "List of cities",
        "data": list(cities)
    })
