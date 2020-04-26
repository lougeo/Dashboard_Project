from django import forms
from django.utils import timezone
from django.forms import ModelForm
from .models import ConcreteReport, ConcreteSample

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
    confirm = forms.BooleanField(initial=False, required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CONFIRM_MSG = {1:"Warning: Failure", 2:"Caution: Near Failure"}
        confirm_set = set(CONFIRM_MSG.values())
        if confirm_set.intersection(self.non_field_errors()):
            self.fields['confirm'].widget = forms.CheckboxInput()

    def clean(self):
        super().clean()
        CONFIRM_MSG = {1:"Warning: Failure", 2:"Caution: Near Failure"}
        if 'confirm' in self.cleaned_data and not self.cleaned_data['confirm']:
            if 'strength' in self.cleaned_data:

                value = self.cleaned_data['strength']
                # Change 50 to model value - create model for fail points
                if value < 50:
                    self.add_error(None, forms.ValidationError(CONFIRM_MSG[1]))
                elif value < 55:
                    self.add_error(None, forms.ValidationError(CONFIRM_MSG[2]))

    class Meta:
        model = ConcreteSample
        fields = ['width', 
                  'height',  
                  'weight',
                  'strength',
                  'confirm']

class SampleSelectorForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())