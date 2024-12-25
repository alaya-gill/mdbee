from rest_framework.routers import DefaultRouter

from .views import AppSettingsViewSet

router = DefaultRouter()
router.register(r'', AppSettingsViewSet, basename='synergy_app_settings')

app_name = "synergy_app_settings"

urlpatterns = [
]
urlpatterns = urlpatterns + router.urls
