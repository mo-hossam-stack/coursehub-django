from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from . import views
from emails.views import verify_email_token_view, email_token_login_view, logout_btn_hx_view, verify_otp_view, resend_otp_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path("courses/", include("courses.urls")),
    path("",views.home_view),
    path("verify-email/<uuid:token>/", verify_email_token_view, name="verify-email"),
    path("hx/login/", email_token_login_view,),
    path("hx/verify-otp/", verify_otp_view,),
    path("hx/resend-otp/", resend_otp_view, name="resend-otp"),
    path("hx/logout/", logout_btn_hx_view,),
    path("login/", views.login_logout_template_view,),
    path("logout/", views.login_logout_template_view,),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )
    """
    also for production comment out
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    """