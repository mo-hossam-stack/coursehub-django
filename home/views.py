from django.shortcuts import render
from emails.forms import EmailForm
from django.conf import settings
from emails.models import Email
EMAIL_ADDRESS = settings.EMAIL_ADDRESS

def home_view(request, *args, **kwargs):
    template_name = "home.html"
    # request POST data
    print(request.POST)
    form = EmailForm(request.POST or None)
    context = {
        "form": form,
        "message": ""
    }
    if form.is_valid():
        email_val = form.cleaned_data.get("email")
        obj = form.save()
        email_obj, created = Email.objects.get_or_create(email=email_val)
        context['message'] = f"Succcess! Check your email for verification from {EMAIL_ADDRESS}"
        context['form'] = EmailForm()  # reset the form
    else:
        print(form.errors)
    return render(request, template_name, context)