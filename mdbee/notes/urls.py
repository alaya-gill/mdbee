from rest_framework.routers import DefaultRouter

from .views import NoteViewSet

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')

app_name = "notes"
urlpatterns = [
]
urlpatterns = urlpatterns + router.urls