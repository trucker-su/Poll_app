from django import forms

from django.contrib.auth.forms import UserCreationForm

from TestingService.models import MyUser


class RegistrationForm(UserCreationForm):
    is_teacher = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('username', 'password1', 'password2', 'is_teacher', 'email')
