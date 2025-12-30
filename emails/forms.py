from django import forms 
from .models import Email
from . import css, services

class EmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs = {
                "id": "email-login-input",
                "class": css.EMAIL_FIELD_CSS,
                "placeholder": "your email login"
            }
        )
    )
    # class Meta:
    #     model = EmailVerificationEvent
    #     fields = ['email']
    def clean_email(self):
        email = self.cleaned_data.get("email")
        verified = services.verify_email(email)
        if verified:
            raise forms.ValidationError("inactive email. plz try again")
        return email 

class OTPForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": css.EMAIL_FIELD_CSS,
                "placeholder": "Enter 6-digit code",
                "maxlength": "6",
                "pattern": "\d{6}",
                "title": "Please enter the 6-digit code sent to your email"
            }
        )
    )