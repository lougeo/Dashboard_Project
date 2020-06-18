from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Profile, Project
from .utils import is_manager


class ReportStandard(models.Model):
    name = models.CharField(max_length=30)
    standard_type = models.PositiveSmallIntegerField(choices=[(0, 'Compression'),
                                                              (1, 'Sieve')])

    def __str__(self):
        return self.name

class ReportStandardParametersCompression(models.Model):
    standard = models.ForeignKey(ReportStandard, on_delete=models.CASCADE, related_name='compression')
    cutoff = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.id}'
        
class ReportStandardParametersSieve(models.Model):
    standard = models.ForeignKey(ReportStandard, on_delete=models.CASCADE, related_name='sieve')

    min_120 = models.DecimalField("Min Passing 120 mm", max_digits=10, decimal_places=2)
    min_80 = models.DecimalField("Min Passing 80 mm", max_digits=10, decimal_places=2)
    min_40 = models.DecimalField("Min Passing 40 mm", max_digits=10, decimal_places=2)
    min_20 = models.DecimalField("Min Passing 20 mm", max_digits=10, decimal_places=2)
    min_10 = models.DecimalField("Min Passing 10 mm", max_digits=10, decimal_places=2)
    min_5 = models.DecimalField("Min Passing 5 mm", max_digits=10, decimal_places=2)
    min_1 = models.DecimalField("Min Passing 1 mm", max_digits=10, decimal_places=2)
    min_05 = models.DecimalField("Min Passing 0.5 mm", max_digits=10, decimal_places=2)
    min_025 = models.DecimalField("Min Passing 0.25 mm", max_digits=10, decimal_places=2)

    max_120 = models.DecimalField("Max Passing 120 mm", max_digits=10, decimal_places=2)
    max_80 = models.DecimalField("Max Passing 80 mm", max_digits=10, decimal_places=2)
    max_40 = models.DecimalField("Max Passing 40 mm", max_digits=10, decimal_places=2)
    max_20 = models.DecimalField("Max Passing 20 mm", max_digits=10, decimal_places=2)
    max_10 = models.DecimalField("Max Passing 10 mm", max_digits=10, decimal_places=2)
    max_5 = models.DecimalField("Max Passing 5 mm", max_digits=10, decimal_places=2)
    max_1 = models.DecimalField("Max Passing 1 mm", max_digits=10, decimal_places=2)
    max_05 = models.DecimalField("Max Passing 0.5 mm", max_digits=10, decimal_places=2)
    max_025 = models.DecimalField("Max Passing 0.25 mm", max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.id}'
    
class Report(models.Model):
    # 0:incomplete 1:complete
    status = models.PositiveSmallIntegerField(default=0)

    # Need an ID tag that counts starting at 1 for each project
    report_type = models.ForeignKey(ReportStandard, on_delete=models.CASCADE)
    project_name = models.ForeignKey(Project, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, 
                                   on_delete=models.CASCADE, 
                                   limit_choices_to=models.Q(groups__name='Manager') | models.Q(groups__name='Technician'))
    date_received = models.DateField(default=timezone.now)
    date_sampled = models.DateField(default=timezone.now) 

    def __str__(self):
        return f'Project: {self.project_name}, Report Type: {self.report_type}, ID: {self.id}'

    def mark_complete(self):
        if self.report_type.standard_type == 0:
            samples = self.concrete_samples.all()
        elif self.report_type.standard_type == 1:
            samples = self.sieve_samples.all()
        total = 0
        complete = 0
        for sample in samples:
            total += 1
            if sample.status == 2:
                complete += 1
        if total > 0 and total == complete:
            self.status = 1

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

    def set_break_date_new(self):
        self.cast_date = self.report.date_sampled
        self.break_date = self.cast_date + timedelta(days=self.days_break)
    
    def set_break_date_update(self):
        self.break_date = self.cast_date + timedelta(days=self.days_break)
    
    # This only changes the status if the sample is complete, as oppossed to if only some fields are modified.
    def mark_complete(self, user):
        if self.width != None and \
           self.height != None and \
           self.weight != None and \
           self.strength != None and \
           self.result != None:
            if is_manager(user):
                self.status = 2
            else:
                self.status = 1            

    
class SieveSample(models.Model):

    # Identifiers
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='sieve_samples')
    # 0:new, 1:modified, 2:approved
    status = models.PositiveSmallIntegerField(default=0)
    process_day = models.DateField(default=timezone.now)

    # Metrics
    wet_weight = models.DecimalField(max_digits=10, 
                                     decimal_places=2)
    dry_weight = models.DecimalField(max_digits=10, 
                                     decimal_places=2)
    moisture_content = models.DecimalField(max_digits=10, 
                                           decimal_places=2, 
                                           blank=True)


    mm_120 = models.DecimalField("120 mm", 
                                 max_digits=10, 
                                 decimal_places=2)
    mm_80 = models.DecimalField("80 mm", 
                                max_digits=10, 
                                decimal_places=2)
    mm_40 = models.DecimalField("40 mm", 
                                max_digits=10, 
                                decimal_places=2)
    mm_20 = models.DecimalField("20 mm", 
                                max_digits=10, 
                                decimal_places=2)
    mm_10 = models.DecimalField("10 mm", 
                                max_digits=10, 
                                decimal_places=2)
    mm_5 = models.DecimalField("5 mm", 
                               max_digits=10, 
                               decimal_places=2)
    mm_1 = models.DecimalField("1 mm", 
                               max_digits=10, 
                               decimal_places=2)
    mm_05 = models.DecimalField("0.5 mm", 
                                max_digits=10, 
                                decimal_places=2)
    mm_025 = models.DecimalField("0.25 mm", 
                                 max_digits=10, 
                                 decimal_places=2)
    # 0:pass 1:warning 2:fail
    result = models.PositiveSmallIntegerField(choices=[(0, 'Pass'), 
                                                       (1, 'Warning'), 
                                                       (2, 'Fail')], 
                                              blank=True)

    def __str__(self):
        return f'{self.id}, {self.status}'

    def set_moisture_content(self):
        self.moisture_content = self.wet_weight - self.dry_weight
    
    def set_result(self, report):
        standard = report.report_type.sieve.first()
        print(standard)
        if self.mm_120 < standard.min_120 or self.mm_120 > standard.max_120 or \
           self.mm_80 < standard.min_80 or self.mm_80 > standard.max_80 or \
           self.mm_40 < standard.min_40 or self.mm_40 > standard.max_40 or \
           self.mm_20 < standard.min_20 or self.mm_20 > standard.max_20 or \
           self.mm_10 < standard.min_10 or self.mm_10 > standard.max_10 or \
           self.mm_5 < standard.min_5 or self.mm_5 > standard.max_5 or \
           self.mm_1 < standard.min_1 or self.mm_1 > standard.max_1 or \
           self.mm_05 < standard.min_05 or self.mm_05 > standard.max_05 or \
           self.mm_025 < standard.min_025 or self.mm_025 > standard.max_025:
            self.result = 2
        else:
            self.result = 0

    def set_status(self, user):
        if is_manager(user):
            self.status = 2
        else:
            self.status = 1
