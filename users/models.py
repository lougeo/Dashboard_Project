from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    #is_client = models.BooleanField()

    def __str__(self):
        return f'{self.user.username} Profile'

class Projects(models.Model):
    company = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True) # limit_choices_to={'is_client':True}
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.company.company}, {self.name}'



