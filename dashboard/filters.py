import django_filters
from .models import *

class ReportFilter(django_filters.FilterSet):
    
    class Meta:
        model = ConcreteReport
        fields = '__all__'
        exclude = ['technician', 'break_days', 'num_samples']