from django import forms
from django.utils import timezone
from django.forms import ModelForm, inlineformset_factory
from .models import *
from users.models import *

# make a regular form for the report type which triggers a conditional to display the proper model form type
class ReportTypeForm(forms.Form):
    report_type = forms.ChoiceField(choices=[(1, 'Concrete'), (2, 'Sieve')])


# Only use this form for new reports, won't work with updating existing reports
class NewConcreteReportForm(ModelForm):
    client = forms.ModelChoiceField(queryset=Profile.objects.filter(user__groups__name='Client'))

    class Meta:
        model = ConcreteReport
        fields = ['client',
                  'project_name', 
                  'date_received', 
                  'date_cast', 
                  'technician']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_name'].queryset = Project.objects.none()

        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['project_name'].queryset = Project.objects.filter(company__id=client_id)
            except (ValueError, TypeError):
                pass # invalid input, pass and fall back to empty queryset

# Only use this form for new reports, won't work with updating existing reports
class NewSieveReportForm(ModelForm):
    client = forms.ModelChoiceField(queryset=Profile.objects.filter(user__groups__name='Client'))

    class Meta:
        model = SieveReport
        fields = ['client',
                  'project_name', 
                  'date_received', 
                  'date_sampled', 
                  'technician',
                  'agg_type']
    
    # This is to limit the project queryset to those of the selected client.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_name'].queryset = Project.objects.none()

        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['project_name'].queryset = Project.objects.filter(company__id=client_id)
            except (ValueError, TypeError):
                pass # invalid input, pass and fall back to empty queryset

class FullConcreteReportUpdateForm(ModelForm):
    class Meta:
        model = ConcreteReport
        exclude = ['num_samples', 'status', 'break_days']
    
    # This sets the project querset to only allow selection of that clients projects
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_name'].queryset = self.instance.project_name.company.project_set.order_by('name')

class NewSampleForm(ModelForm):
    class Meta:
        model = ConcreteSample
        fields = ['report', 'cast_date', 'days_break']

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


#################### FORMSETS #############################

ConcreteSampleFormSet = inlineformset_factory(ConcreteReport, 
                                              ConcreteSample, 
                                              fields=('days_break', 'width', 'height', 'weight', 'strength', 'result'),
                                              extra=0)

NewConcreteSampleFormSet = inlineformset_factory(ConcreteReport, 
                                                 ConcreteSample, 
                                                 fields=('days_break',),
                                                 widgets={'cast_date':forms.HiddenInput(), 'break_date':forms.HiddenInput()}, 
                                                 extra=3)