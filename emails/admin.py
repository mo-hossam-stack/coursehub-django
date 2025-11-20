from django.contrib import admin

from .models import Email, EmailVerificationEvent

admin.site.register(Email)
admin.site.register(EmailVerificationEvent)