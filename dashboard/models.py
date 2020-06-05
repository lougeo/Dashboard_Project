from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Profile, Project


class ReportStandard(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
class Report(models.Model):
    # 0:incomplete 1:complete
    status = models.PositiveSmallIntegerField(default=0)

    # Need an ID tag that counts starting at 1 for each project
    report_type = models.ForeignKey(ReportStandard, on_delete=models.CASCADE)
    project_name = models.ForeignKey(Project, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, on_delete=models.CASCADE, null=True, limit_choices_to={'groups__name':'Manager', 'groups__name':'Technician'}) # Figure out why it wont let me include both
    date_received = models.DateField(default=timezone.now)
    date_sampled = models.DateField(default=timezone.now) 

    def __str__(self):
        return f'Project: {self.project_name}, Report Type: {self.report_type}, ID: {self.id}'


class ConcreteSample(models.Model):

    # Identifiers
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='concrete_samples')
    # 0:new, 1:modified, 2:approved
    status = models.PositiveSmallIntegerField(default=0)
    cast_date = models.DateField()
    break_date = models.DateField()
    days_break = models.PositiveSmallIntegerField("Days Untill Break")

    # Metrics
    width = models.DecimalField(max_digits=10, 
                                decimal_places=2, 
                                null=True, 
                                blank=True)
    height = models.DecimalField(max_digits=10, 
                                 decimal_places=2, 
                                 null=True, 
                                 blank=True)
    weight = models.DecimalField(max_digits=10, 
                                 decimal_places=2, 
                                 null=True, 
                                 blank=True)
    strength = models.DecimalField(max_digits=10, 
                                   decimal_places=2, 
                                   null=True, 
                                   blank=True)
    # 0:pass 1:warning 2:fail
    result = models.PositiveSmallIntegerField(choices=[(0, 'Pass'), 
                                                       (1, 'Warning'), 
                                                       (2, 'Fail')], 
                                              null=True, 
                                              blank=True)

    def __str__(self):
        return f'{self.id}, {self.status}'

    
class SieveSample(models.Model):

    # Identifiers
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='sieve_samples')
    # 0:new, 1:modified, 2:approved
    status = models.PositiveSmallIntegerField(default=0)
    process_day = models.DateField(default=timezone.now)

    # Metrics
    wet_weight = models.DecimalField(max_digits=10, 
                                     decimal_places=2, 
                                     null=True, 
                                     blank=True)
    dry_weight = models.DecimalField(max_digits=10, 
                                     decimal_places=2, 
                                     null=True, 
                                     blank=True)
    moisture_content = models.DecimalField(max_digits=10, 
                                           decimal_places=2, 
                                           null=True, 
                                           blank=True)


    mm_120 = models.DecimalField("120 mm", 
                                 max_digits=10, 
                                 decimal_places=2, 
                                 null=True, 
                                 blank=True)
    mm_80 = models.DecimalField("80 mm", 
                                max_digits=10, 
                                decimal_places=2, 
                                null=True, 
                                blank=True)
    mm_40 = models.DecimalField("40 mm", 
                                max_digits=10, 
                                decimal_places=2, 
                                null=True, 
                                blank=True)
    mm_20 = models.DecimalField("20 mm", 
                                max_digits=10, 
                                decimal_places=2, 
                                null=True, 
                                blank=True)
    mm_10 = models.DecimalField("10 mm", 
                                max_digits=10, 
                                decimal_places=2, 
                                null=True, 
                                blank=True)
    mm_5 = models.DecimalField("5 mm", 
                               max_digits=10, 
                               decimal_places=2, 
                               null=True, 
                               blank=True)
    mm_1 = models.DecimalField("1 mm", 
                               max_digits=10, 
                               decimal_places=2, 
                               null=True, 
                               blank=True)
    mm_05 = models.DecimalField("0.5 mm", 
                                max_digits=10, 
                                decimal_places=2, 
                                null=True, 
                                blank=True)
    mm_025 = models.DecimalField("0.25 mm", 
                                 max_digits=10, 
                                 decimal_places=2, 
                                 null=True, 
                                 blank=True)
    # 0:pass 1:warning 2:fail
    result = models.PositiveSmallIntegerField(choices=[(0, 'Pass'), 
                                                       (1, 'Warning'), 
                                                       (2, 'Fail')], 
                                              null=True, 
                                              blank=True)

    def __str__(self):
        return f'{self.id}, {self.status}'



# class ConcreteReport(models.Model):
#     # 0:incomplete 1:complete
#     status = models.PositiveSmallIntegerField(default=0)

#     # Need an ID tag that counts starting at 1 for each project
#     project_name = models.ForeignKey(Project, on_delete=models.CASCADE) # Change to PROTECT
#     technician = models.ForeignKey(User, on_delete=models.CASCADE, null=True, limit_choices_to={'groups__name':'Manager', 'groups__name':'Technician'}) # Figure out why it wont let me include both, also change to PROTECT
#     date_received = models.DateField(default=timezone.now)
#     date_cast = models.DateField(default=timezone.now) 
    
#     def __str__(self):
#         return f'{self.project_name}, {self.id}'


# class SieveReport(models.Model):
#     # 0:incomplete 1:complete
#     status = models.PositiveSmallIntegerField(default=0)

#     # Need an ID tag that counts starting at 1 for each project
#     project_name = models.ForeignKey(Project, on_delete=models.CASCADE) # Change to PROTECT
#     technician = models.ForeignKey(User, on_delete=models.CASCADE, null=True, limit_choices_to={'groups__name':'Manager', 'groups__name':'Technician'}) # Figure out why it wont let me include both, also change to PROTECT
#     date_received = models.DateField(default=timezone.now)
#     date_sampled = models.DateField(default=timezone.now) 
#     agg_type = models.PositiveSmallIntegerField("Aggregate Type",
#                                                 choices=[(0, 'Coarse'),
#                                                          (1, 'Fine')])


#     def __str__(self):
#         return f'{self.project_name}, {self.id}'
