from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Report(models.Model):
    cust_id = models.IntegerField()
    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    strength = models.IntegerField()
    technician = models.ForeignKey(User, on_delete=models.CASCADE) # Change this to PROTECT when ready

    def __str__(self):
        return self.name
