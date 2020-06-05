import django_filters
from .models import Report
from users.models import Project, Profile

STATUS_CHOICES = ((0, 'Incomplete'), (1, 'Complete'))

def all_clients(request):
    # Condition if request is none
    if request is None:
        return Profile.objects.none()
    # Limits selection to Clients
    elif request.user.groups.first().name == 'Client':
        return Profile.objects.none()
    # Returns all for staff
    return Profile.objects.filter(user__groups__name='Client')

def is_client(request):
    # Condition if request is none
    if request is None:
        return Project.objects.none()
    # Limits selection to Clients
    elif request.user.groups.first().name == 'Client':
        return Project.objects.filter(company=request.user.profile.id)
    # Returns all for staff
    return Project.objects.all()
    

class ReportFilter(django_filters.FilterSet):
    client = django_filters.ModelChoiceFilter(field_name='project_name__company', 
                                              label='Client',
                                              queryset=all_clients)
    project = django_filters.ModelChoiceFilter(field_name='project_name',
                                               label='Project',
                                               queryset=is_client)
    status = django_filters.ChoiceFilter(field_name='status', choices=STATUS_CHOICES)
    class Meta:
        model = Report
        fields = ['client', 'project', 'report_type', 'status', 'date_sampled']
