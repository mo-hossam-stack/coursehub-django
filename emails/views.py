from django.shortcuts import render,redirect
from django.http import HttpResponse
from . import services
from django.contrib import messages
# use messaging framework later
def verify_email_token_view(request, token, *args, **kwargs):
    did_verify, msg, email_obj = services.verify_token(token)
    if not did_verify:
        try:
            del request.session['email_id']
        except KeyError:
            pass
            
        messages.error(request, msg)
        return redirect("/login/")
    messages.success(request, msg)
    # django -> request.session.get('email_id)
    request.session['email_id'] = f"{email_obj.id}"
    return redirect("/")