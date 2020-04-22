from django import forms
from django.utils import timezone
from django.forms import ModelForm
from .models import ConcreteReport, ConcreteSample
from users.models import Project

class NewProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['company', 'name']

# make a regular form for the report type which triggers a conditional to display the proper model form type
class ReportTypeForm(forms.Form):
    report_type = forms.ChoiceField(choices=[(1, 'Concrete'), (2, 'Shotcrete')])

class ReportForm(ModelForm):
    class Meta:
        model = ConcreteReport
        fields = ['project_name', 
                  'date_received', 
                  'date_cast', 
                  'num_samples', 
                  'break_days', 
                  'technician']


class NewSampleForm(ModelForm):
    class Meta:
        model = ConcreteSample
        fields = ['report', 'cast_day', 'break_day']

# Need to set this to query only reports which are active (might be easier to do in the view)
class ReportSelectorForm(forms.Form):
    selected_report = forms.ModelChoiceField(queryset=ConcreteSample.objects.filter(break_day=timezone.now().date()))


class UpdateSampleForm(ModelForm):
    class Meta:
        model = ConcreteSample
        fields = ['width', 
                  'height',  
                  'weight',
                  'strength']