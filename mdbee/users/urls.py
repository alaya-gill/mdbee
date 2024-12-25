from django.conf.urls import url
from django.urls import path
from rest_framework.routers import DefaultRouter

from mdbee.users.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# from mdbee.users.views import (
#     user_redirect_view,
#     user_update_view,
#     user_detail_view,
# )


app_name = "users"
urlpatterns = [
]
urlpatterns = urlpatterns + router.urls
# urlpatterns = [
#     path("~redirect/", view=user_redirect_view, name="redirect"),
#     path("~update/", view=user_update_view, name="update"),
#     path("<str:username>/", view=user_detail_view, name="detail"),
# ]
