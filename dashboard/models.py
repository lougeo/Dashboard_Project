from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Profile, Project


class ConcreteReport(models.Model):
    # This gets set automatically at each stage
    status = models.SmallIntegerField(default=0)

    # Need an ID tag that counts starting at 1 for each project
    project_name = models.ForeignKey(Project, on_delete=models.CASCADE) # Change to PROTECT
    technician = models.ForeignKey(User, on_delete=models.CASCADE, null=True, limit_choices_to={'groups__name':'Manager', 'groups__name':'Technician'}) # Figure out why it wont let me include both, also change to PROTECT
    date_received = models.DateField(default=timezone.now)
    date_cast = models.DateField(default=timezone.now) # Change this to 
    # Make some validation which checks num samples against the break days
    num_samples = models.SmallIntegerField()
    break_days = models.CharField(max_length=30)
    


    def __str__(self):
        return f'{self.project_name}, {self.date_received}'

class ConcreteSample(models.Model):

    # Identifiers
    report = models.ForeignKey(ConcreteReport, on_delete=models.CASCADE)
    # 0:new, 1:modified, 2:approved
    status = models.PositiveSmallIntegerField(default=0)
    cast_day = models.DateField()
    break_day = models.DateField()
    break_day_num = models.PositiveSmallIntegerField()

    # Metrics
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    strength = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # 0:pass 1:warning 2:fail
    result = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return f'{self.id}, {self.status}'