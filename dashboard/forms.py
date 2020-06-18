from django import forms
from django.utils import timezone
from django.forms import ModelForm, inlineformset_factory
from .models import *
from users.models import *


########################### NEW REPORT FORM #####################################

class NewReportForm(ModelForm):
    test_type = forms.ChoiceField(choices=[(999, '--------'), (0, 'Compression'), (1, 'Sieve')])
    client = forms.ModelChoiceField(queryset=Profile.objects.filter(user__groups__name='Client'))

    class Meta:
        model = Report
        fields = ['test_type',
                  'report_type', 
                  'client',
                  'project_name', 
                  'date_received', 
                  'date_sampled', 
                  'technician']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['report_type'].queryset = ReportStandard.objects.none()
        self.fields['project_name'].queryset = Project.objects.none()

        # This is to limit the standard queryset to those of the selected test type.
        if 'form1-test_type' in self.data:
            try:
                test_type_id = int(self.data.get('form1-test_type'))
                self.fields['report_type'].queryset = ReportStandard.objects.filter(standard_type=test_type_id)
            except (ValueError, TypeError):
                pass # Invalid input, pass and fall back to empty queryset
        
        # This is to limit the project queryset to those of the selected client.
        if 'form1-client' in self.data:
            try:
                client_id = int(self.data.get('form1-client'))
                self.fields['project_name'].queryset = Project.objects.filter(company__id=client_id)
            except (ValueError, TypeError):
                pass # invalid input, pass and fall back to empty queryset

############################ NEW STANDARD FORMS ####################################

class ReportStandardForm(ModelForm):
    class Meta:
        model = ReportStandard
        fields = '__all__'

class CompressionParametersForm(ModelForm):
    class Meta:
        model = ReportStandardParametersCompression
        fields = ['cutoff']

class SieveParametersForm(ModelForm):
    class Meta:
        model = ReportStandardParametersSieve
        exclude = ['standard']


############################# REPORT UPDATE FORMS ##################################

class FullReportUpdateForm(ModelForm):
    class Meta:
        model = Report
        exclude = ['status', 'report_type']
    
    # This sets the project querset to only allow selection of that clients projects
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_name'].queryset = Project.objects.filter(company=self.instance.project_name.company)

class ProjectManagerForm(ModelForm):
    class Meta:
        model = Project
        fields = ['office', 'company']


############################# LAB FORMS ###########################################

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


############################ MANAGE FORMS #################################################


class ManageReportStandardForm(ModelForm):
    class Meta:
        model = ReportStandard
        fields = ['name']

#################### FORMSETS #############################

ConcreteSampleFormSet = inlineformset_factory(Report, 
                                              ConcreteSample, 
                                              fields=('cast_date', 'days_break', 'width', 'height', 'weight', 'strength', 'result'),
                                              extra=0)

SieveSampleFormSet = inlineformset_factory(Report, 
                                           SieveSample, 
                                           exclude=['report', 'status'],
                                           extra=0)

NewConcreteSampleFormSet = inlineformset_factory(Report, 
                                                 ConcreteSample, 
                                                 fields=['days_break'],
                                                 extra=3)

NewSieveSampleFormSet = inlineformset_factory(Report, 
                                              SieveSample, 
                                              exclude=['report', 'status', 'sample_day', 'process_day', 'moisture_content', 'result'],
                                              extra=1)