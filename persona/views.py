from django.core.cache import cache
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from persona.models import Benefactors, BenefactorProfile
from .forms import SignupForm, LoginForm, OrderForm
from django.template.loader import render_to_string
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from persona.forms import SignupForm, LoginForm
from persona.models import Benefactors, TrainingData
from persona.tokens import account_activation_token


from django.conf import settings
from twilio import exceptions
from twilio.rest import TwilioRestClient
import random
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

class LoginView(View):

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if not user:
            try:
                a_user = User.objects.get(email__iexact = username)
                user = authenticate(username=a_user.username, password=password)
            except:
                pass
        if user is not None:
            if user.is_active:
                login(request, user)
                if Benefactors.objects.filter(benfactors__email__iexact=username):
                    return HttpResponseRedirect('/send_otp')
                    # return HttpResponseRedirect("/profile/")
                else:
                    return HttpResponseRedirect("/error/")
        return render(request, 'login.html', {'form': LoginForm(request.POST), 'Error': 'Invalid username or password'})

    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


class AuthenticationUserView(View):
    def post(self, request):
        updated_data = request.POST.copy()
        updated_data.update({'password2': updated_data['password1']})
        updated_data.update({'username': updated_data['email']})
        form = SignupForm(data=updated_data)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            BenefactorProfile.objects.create(user= user, phone_number= request.POST.get('phone_number'))
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            return render(request, 'sign-up.html', {'form': form})

    def get(self, request):
        form = SignupForm()

        return render(request, 'sign-up.html', {'form': form})


class ActivationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # return redirect('home')
            return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        else:
            return HttpResponse('Activation link is invalid!')

def _get_pin(length=5):
    """ Return a numeric PIN with length digits """
    return random.sample(range(10**(length-1), 10**length), 1)[0]


def _verify_pin(mobile_number, pin):
    """ Verify a PIN is correct """
    return pin == cache.get(mobile_number)


def ajax_send_pin(request):
    """ Sends SMS PIN to the specified number """
    mobile_number = request.POST.get('mobile_number', "")
    if not mobile_number:
        return HttpResponse("No mobile number", content_type='text/plain', status=403)

    pin = _get_pin()

    # store the PIN in the cache for later verification.
    # cache.set(mobile_number, pin, 24*3600) # valid for 24 hrs
    request.session['mobile_number'] = pin
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
                        body="Your one time password for account verification is %s" % pin,
                        to=mobile_number,
                        from_=settings.TWILIO_FROM_NUMBER,
                    )
    return HttpResponse("Message %s sent" % message.sid, content_type='text/plain', status=200)

def process_order(request):
    """ Process orders made via web form and verified by SMS PIN. """
    form = OrderForm(request.POST or None)

    if form.is_valid():
        pin = int(request.POST.get("pin", "0"))
        mobile_number = request.session.get("mobile_number", "")
        if mobile_number == pin:
            form.save()
            del request.session['mobile_number']
            return HttpResponseRedirect('/profile/')
        else:
            messages.error(request, "Invalid PIN!")
            return HttpResponseRedirect('/error/')
    else:
        return render(
                    request,
                    'page-otp.html',
                    {
                        'form': form
                    }
                )
@method_decorator(login_required, name='dispatch')
class TrainingDataView(TemplateView):
    template_name = "questions.html"


    def post(self, request, *args, **kwargs):
        try:
            reason = self.request.POST['reason']
        except:
            reason = ""
        training_obj = TrainingData.objects.filter(reason__iexact= reason)
        if training_obj and reason != "":
            return render(request, 'success.html')
            
        return render(request, self.template_name, {"message":"I hate cheese. Please retry."})

