from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from . import views
from emails.views import verify_email_token_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path("courses/", include("courses.urls")),
    path("",views.home_view),
    path("verify-email/<uuid:token>/", verify_email_token_view, name="verify-email"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )