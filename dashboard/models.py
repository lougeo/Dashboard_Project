from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class ConcreteReport(models.Model):
    cust_id = models.CharField(max_length=10)
    project_name = models.CharField(max_length=100)
    date_received = models.DateField(default=timezone.now)
    date_cast = models.DateField(default=timezone.now)
    num_samples = models.SmallIntegerField()
    break_days = models.CharField(max_length=30)
    strength = models.IntegerField()
    technician = models.ManyToManyField(User) # make this only show staff
    status = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name
