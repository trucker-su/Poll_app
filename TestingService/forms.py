from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from TestingService.models import MyUser


class RegistrationForm(UserCreationForm):
    is_teacher = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('username', 'password1', 'password2', 'is_teacher')


class LoginForm(AuthenticationForm):
    is_teacher = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = '__all__'

