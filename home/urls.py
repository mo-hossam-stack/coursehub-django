from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from . import views
from emails.views import verify_email_token_view, email_token_login_view, logout_btn_hx_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path("courses/", include("courses.urls")),
    path("",views.home_view),
    path("verify-email/<uuid:token>/", verify_email_token_view, name="verify-email"),
    path("hx/login/", email_token_login_view,),
    path("hx/logout/", logout_btn_hx_view,),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )