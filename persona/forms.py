from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from persona.models import SaveOTP


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password1', 'password2', 'phone_number')


class LoginForm(AuthenticationForm):
    fields = '__all__'


class OrderForm(ModelForm):

    class Meta:
        model = SaveOTP
        fields = '__all__'

