from django import forms 
from .models import Email
from . import css

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
        qs = Email.objects.filter(email=email, active=False)
        if qs.exists():
            raise forms.ValidationError("inactive email. plz try again")
        return email 