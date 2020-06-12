from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, 
                                on_delete=models.CASCADE,
                                related_name='profile')
    company = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    #signature = models.FileField(null=True, blank=True)


    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Project(models.Model):
    office = models.ForeignKey(Profile, 
                               on_delete=models.CASCADE, 
                               limit_choices_to=models.Q(user__groups__name='Manager'), 
                               related_name='office_contact')
    company = models.ForeignKey(Profile, 
                                on_delete=models.CASCADE, 
                                limit_choices_to=models.Q(user__groups__name='Client'), 
                                related_name='client_contact')
    name = models.CharField("Project Name", max_length=30, unique=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name



