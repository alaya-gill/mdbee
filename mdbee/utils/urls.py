from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import include, path

from mdbee.utils.views.content_type import ContentTypeView
from .views import getCountries, getStatesofCountry, getCitiesofState

router = DefaultRouter()

app_name = "utils"

urlpatterns = [
    url('country', getCountries),
    url('state', getStatesofCountry),
    url('city', getCitiesofState),
    url('get-content-type', ContentTypeView.as_view(),name='get-content-type'),
    
]
urlpatterns = urlpatterns + router.urls
