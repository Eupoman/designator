from persona.models import Benefactors
from django.http import HttpResponseRedirect
from django.contrib.auth.views import login

def get_profile_data(request, backend, user, response, details, *args, **kwargs):
    benifactors_email = details['email']
    if not Benefactors.objects.filter(benfactors__email__iexact=benifactors_email):
        return HttpResponseRedirect("/logout/")