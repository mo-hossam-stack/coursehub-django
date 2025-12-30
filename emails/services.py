import random
import string
from django.utils import timezone
from .models import Email, EmailVerificationEvent
from django.conf import settings
from django.core.mail import send_mail
EMAILL_HOST_USER = settings.EMAIL_HOST_USER
from django.template.loader import render_to_string
from datetime import timedelta

def check_rate_limit(email):
    # Limit: 5 attempts per hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    count = EmailVerificationEvent.objects.filter(
        email=email,
        timestamp__gte=one_hour_ago
    ).count()
    return count < 5
def verify_email(email):
    qs = Email.objects.filter(email=email, active=False)
    return qs.exists()

def get_verification_email_message(verification_instance, as_html=False):
    if not isinstance(verification_instance, EmailVerificationEvent):
        return None
    verify_link = verification_instance.get_link()
    context = {
        "verify_link": verify_link,
        "otp": verification_instance.otp,
        "expiration_minutes": 10
    }
    if as_html:
        return render_to_string("emails/verification_email.html", context)
    return f"Verify your email. Code: {verification_instance.otp}. Link: {verify_link}"
    
    
def start_verification_event(email):
    # Check rate limit
    if not check_rate_limit(email):
        return None, False

    email_obj , created = Email.objects.get_or_create(email=email)
    otp = "".join(random.choices(string.digits, k=6))
    obj = EmailVerificationEvent.objects.create(
        parent = email_obj,
        email=email,
        otp=otp
    )
    sent = send_verification_email(obj.id)
    return obj, sent

# cleary task -> background task 
def send_verification_email(verify_obj_id):
    verify_obj = EmailVerificationEvent.objects.get(id=verify_obj_id)
    email = verify_obj.email
    # next send verification email logic here
    test_message = get_verification_email_message(verify_obj, as_html=False)
    text_message_html = get_verification_email_message(verify_obj, as_html=True)
    return send_mail(
        subject = "Please verify your email",
        message = test_message,
        from_email = EMAILL_HOST_USER,
        recipient_list = [email],
        fail_silently = False,
        html_message = text_message_html)

def verify_token(token,max_attempts=5):
    qs  = EmailVerificationEvent.objects.filter(token=token)
    if not qs.exists() and not qs.count() == 1:
        return False, "Invalid token", None
    has_email_expired = qs.filter(expired=True)
    """ token expired"""
    if has_email_expired.exists():
        return False, "Token expired",None
    """Has token, not expired"""
    max_attempts_reached = qs.filter(attempts__gte=max_attempts)
    if max_attempts_reached.exists():
        """
        update max attempts ++ :)
        max_tempts_reached.update()
        """
        return False, "Max attempts reached",None
    """ valid token 
        update attempts, expire token if attemps  > max
    """     
    obj = qs.first()
    obj.attempts += 1
    obj.last_attempt_at = timezone.now()
    if obj.attempts > max_attempts:
        """invalidate process"""
        obj.expired = True
        obj.expired_at = timezone.now()
    obj.save()
    email_obj = obj.parent
    return True , "Welcome!" , email_obj

def verify_otp(email, otp, max_attempts=5):
    qs = EmailVerificationEvent.objects.filter(email=email).order_by('-timestamp')
    if not qs.exists():
         return False, "No verification found", None

    verification_event = qs.first() 
    
    if verification_event.expired:
        return False, "Code expired", None

    if verification_event.attempts >= max_attempts:
         # Ensure it is marked expired if not already
         if not verification_event.expired:
             verification_event.expired = True
             verification_event.save()
         return False, "Max attempts reached", None

    if verification_event.otp != otp:
        verification_event.attempts += 1
        verification_event.last_attempt_at = timezone.now()
        if verification_event.attempts >= max_attempts:
             verification_event.expired = True
             verification_event.expired_at = timezone.now()
        verification_event.save()
        return False, "Invalid code", None

    verification_event.attempts += 1
    verification_event.last_attempt_at = timezone.now()
    # Expire it so it can't be used again
    verification_event.expired = True
    verification_event.expired_at = timezone.now()
    verification_event.save()
    
    email_obj = verification_event.parent
    return True, "Welcome!", email_obj