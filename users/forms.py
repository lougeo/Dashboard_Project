from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm


# Here it will have to be modified to also include what kind of user permissions this user will have
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    group = forms.ModelChoiceField(queryset=Group.objects.all(), 
                                   required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'group']