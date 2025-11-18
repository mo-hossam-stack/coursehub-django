from django.shortcuts import render
from emails.forms import EmailForm
from django.conf import settings

EMAIL_ADDRESS = settings.EMAIL_ADDRESS

def home_view(request, *args, **kwargs):
    template_name = "home.html"
    # request POST data
    form = EmailForm(request.POST or None)
    context = {
        "form": form,
        "message": ""
    }
    if form.is_valid():
        form.save()
        context['message'] = f"Succcess! Check your email for verification from {EMAIL_ADDRESS}"
        context['form'] = EmailForm()  # reset the form
    return render(request, template_name, context)