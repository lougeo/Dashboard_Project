from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import *


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    group = forms.ModelChoiceField(queryset=Group.objects.all(), 
                                   required=True)

    class Meta:
        model = User
        fields = ['username', 
                  'email', 
                  'password1', 
                  'password2', 
                  'group']

class UserEmailUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['email']

class ProfileForm(ModelForm):
    PROVINCE_CHOICES = [('BC', 'British Colombia'),
                        ('AB', 'Alberta'),
                        ('SK', 'Saskatchewan'),
                        ('MB', 'Manitoba'),
                        ('ON', 'Ontario'),
                        ('QC', 'Quebec'),
                        ('NB', 'New Brunswick'),
                        ('NS', 'Nova Scotia'),
                        ('PE', 'Prince Edward Island'),
                        ('NL', 'Newfoundlan and Labrador'),
                        ('YT', 'Yukon'),
                        ('NT', 'Northwest Territories'),
                        ('NU', 'Nunavut')]
    COUNTRY_CHOICES = [('CA', 'Canada'), 
                       ('USA', 'United States')]

    province = forms.ChoiceField(choices=PROVINCE_CHOICES)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)

    class Meta:
        model = Profile
        exclude = ['user']

class NewProjectForm(ModelForm):
    PROVINCE_CHOICES = [('BC', 'British Colombia'),
                        ('AB', 'Alberta'),
                        ('SK', 'Saskatchewan'),
                        ('MB', 'Manitoba'),
                        ('ON', 'Ontario'),
                        ('QC', 'Quebec'),
                        ('NB', 'New Brunswick'),
                        ('NS', 'Nova Scotia'),
                        ('PE', 'Prince Edward Island'),
                        ('NL', 'Newfoundlan and Labrador'),
                        ('YT', 'Yukon'),
                        ('NT', 'Northwest Territories'),
                        ('NU', 'Nunavut')]
    COUNTRY_CHOICES = [('CA', 'Canada'), 
                       ('USA', 'United States')]

    province = forms.ChoiceField(choices=PROVINCE_CHOICES)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)

    class Meta:
        model = Project
        fields = '__all__'