from .models import Email, EmailVerificationEvent
from django.conf import settings
from django.core.mail import send_mail
EMAILL_HOST_USER = settings.EMAIL_HOST_USER


def verify_email(email):
    qs = Email.objects.filter(email=email, active=False)
    return qs.exists()

def get_verification_email_message(verification_instance, as_html=False):
    if not isinstance(verification_instance, EmailVerificationEvent):
        return None
    verify_link = verification_instance.get_link()
    if as_html:
        return f"<a href='{verify_link}'>Click here to verify your email</a>"
    return f"Verify your email by clicking on the following link: {verify_link}"
    
    
def start_verification_event(email):
    email_obj , created = Email.objects.get_or_create(email=email)
        #obj = form.save()
    obj = EmailVerificationEvent.objects.create(
        parent = email_obj,
        email=email
        )
    sent = send_verification_email(obj.id)
    return obj, sent

# cleary task -> background task 
def send_verification_email(verify_obj_id):
    verify_obj = EmailVerificationEvent.objects.get(id=verify_obj_id)
    email = verify_obj.email
    # next send verification email logic here
    test_message = get_verification_email_message(obj, as_html=False)
    text_message_html = get_verification_email_message(obj, as_html=True)
    return send_mail(
        subject = "Please verify your email",
        message = test_message,
        from_email = EMAILL_HOST_USER,
        recipient_list = [email],
        fail_silently = False,
        html_message = text_message_html)
    