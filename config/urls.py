from django.conf import settings
from django.urls import include, path
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views

from mdbee.synergy_auth.views import admin_obtain_code_token,\
    user_obtain_code_token, obtain_auth_token, verify_code_token, resend_code_token,\
    refresh_auth_token, verify_auth_token

# router = DefaultRouter()
handler500 = 'rest_framework.exceptions.server_error'
# handler400 = 'rest_framework.exceptions.bad_request'

urlpatterns = [

    # Django Admin, use {% url 'admin:index' %}
    path("admin/", admin.site.urls),
    # User management
    path("api/web/", include("mdbee.users.urls", namespace="users")),
    path("api/web/utils/", include("mdbee.utils.urls", namespace="utils")),
    path('api/token/refresh/', refresh_auth_token, name='token_refresh'),
    path("api/code-token", user_obtain_code_token, name="user-obtain-code-token"),
    path("api/token", obtain_auth_token, name="obtain-auth-token"),
    path("api/admin/code-token", admin_obtain_code_token, name="admin-obtain-code-token"),
    path("api/verify-code-token", verify_code_token, name="verify-code-token"),
    path("api/resend-code-token", resend_code_token, name="resend_code_token"),
    path("api/verify-auth-token", verify_auth_token, name="verify_auth_token")
    # Your stuff: custom urls includes go here
] 

# urlpatterns = urlpatterns + router.urls
urlpatterns = urlpatterns

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
