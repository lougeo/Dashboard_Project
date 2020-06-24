from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import *


class ModModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.company

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    account_type = forms.ModelChoiceField(queryset=Group.objects.all(), 
                                   required=True)

    class Meta:
        model = User
        fields = ['account_type',
                  'username', 
                  'email', 
                  'password1', 
                  'password2']

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
    company = ModModelChoiceField(queryset=Profile.objects.filter(user__groups__name='Client'))

    class Meta:
        model = Project
        fields = '__all__'