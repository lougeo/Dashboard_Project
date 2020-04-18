from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Profile, Projects


class ConcreteReport(models.Model):
    # This gets set automatically at each stage
    status = models.SmallIntegerField(default=0)

    # These get set upon creation
    project_name = models.ForeignKey(Projects, on_delete=models.CASCADE) # Change to PROTECT
    date_received = models.DateField(default=timezone.now)
    date_cast = models.DateField(default=timezone.now)
    num_samples = models.SmallIntegerField()
    break_days = models.CharField(max_length=30)
    technician = models.ForeignKey(User, on_delete=models.CASCADE, null=True, limit_choices_to={'groups__name':'Manager', 'groups__name':'Technician'}) # Figure out why it wont let me include both, also change to PROTECT
    # cust_id = models.CharField(max_length=10, null=True) # change this to fk for user profile, need to import Profile. Might be redundant if we already have the project name. Is possible I suppose to have non unique project names though.

    # These get set upon update
    strength = models.IntegerField(null=True)
    

    def __str__(self):
        return f'{self.project_name}, {self.date_received}'
