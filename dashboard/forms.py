from django import forms
from django.forms import ModelForm
from .models import ConcreteReport

# make a regular form for the report type which triggers a conditional to display the proper model form type
class ReportTypeForm(forms.Form):
    report_type = forms.ChoiceField(choices=[(1, 'Concrete'), (2, 'Shotcrete')])

class NewReportForm(ModelForm):
    class Meta:
        model = ConcreteReport
        fields = ['project_name', 
                  'date_received', 
                  'date_cast', 
                  'num_samples', 
                  'break_days', 
                  'technician']


# Need to set this to query only reports which are active (might be easier to do in the view)
class ReportSelectorForm(forms.Form):
    selected_report = forms.ModelChoiceField(queryset=ConcreteReport.objects.all())


class UpdateReportForm(ModelForm):
    class Meta:
        model = ConcreteReport
        fields = ['cust_id', 
                  'project_name', 
                  'date_cast', 
                  'strength', 
                  'technician']