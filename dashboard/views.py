from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .forms import *
from .models import *
from .filters import *

def is_employee(user):
    if user.groups.filter(name="Manager").exists() | user.groups.filter(name="Technician").exists():
        return True
    else:
        return False

def is_manager(user):
    return user.groups.filter(name="Manager").exists()

# Dasboard page
@login_required
#@user_passes_test(is_employee, redirect_field_name='client_home')
def home(request):
    if is_employee(request.user):
        reports = ConcreteReport.objects.all()
        samples = ConcreteSample.objects.all()

        # Total in lab
        card_1 = reports.filter(status=0).count()
        # Breaks Today
        card_2 = samples.filter(break_day=timezone.now().date()).count()
        # Waiting approval
        card_3 = samples.filter(status=1).count()

        card_titles = ['Total Samples in Lab', 'Breaks Today', 'Waiting Approval']
    else:
        client = request.user.id
        reports = ConcreteReport.objects.filter(project_name__company__user__id=client)
        samples = ConcreteSample.objects.filter(report__project_name__company__user__id=client)

        # Total in lab
        card_1 = reports.filter(status=0).count()
        # Breaks Today
        card_2 = samples.filter(break_day=timezone.now().date()).count()
        # Waiting approval
        card_3 = samples.filter(status=1).count()

        card_titles = ['Total Samples in Lab', 'Breaks Today', 'Waiting Approval']


    myFilter = ReportFilter(request.GET, queryset=reports)
    reports = myFilter.qs

    context = {'reports':reports,
               'samples':samples,
               'card_1':card_1,
               'card_2':card_2,
               'card_3':card_3, 
               'card_titles':card_titles,
               'myFilter':myFilter}

    return render(request, 'dashboard/home.html', context)

# New Report page
@login_required
@user_passes_test(is_employee)
def new_report(request):
    if request.method == 'POST':
        form = ReportTypeForm(request.POST)
        if form.is_valid():
            rtype = form.cleaned_data.get('report_type')
            if rtype == '1':
                return redirect('new_report_add')
    else:
        form = ReportTypeForm()
    return render(request, 'dashboard/new_report.html', {'form': form})

@login_required
@user_passes_test(is_employee)
def new_report_add(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # Report
            new_report = form.save()
            name = form.cleaned_data.get('project_name')
            break_days = form.cleaned_data.get('break_days')

            # Samples            
            break_days = break_days.split(', ')
            for i in break_days:
                days = int(i)
                sample_form = ConcreteSample(report=new_report, 
                                             cast_day=new_report.date_cast, 
                                             break_day=new_report.date_cast + timedelta(days=days), 
                                             break_day_num=i)
                sample_form.save()


            messages.success(request, f'Report Created for {name}')
            return redirect('new_report')
    else:
        form = ReportForm()
    return render(request, 'dashboard/new_report.html', {'form': form})


# Update Report Page
@login_required
@user_passes_test(is_employee)
def update_report(request):
    if request.method == 'POST':
        form = ReportSelectorForm(request.POST)
        if form.is_valid():
            report = form.cleaned_data.get('selected_report')
            return redirect('update_report_add', pk=report.pk)
    else:
        form = ReportSelectorForm()
        reports = ConcreteSample.objects.filter(break_day=timezone.now().date()).filter(status=0)
    return render(request, 'dashboard/update_report.html', {'form': form, 'reports':reports})

@login_required
@user_passes_test(is_employee)
def update_report_add(request, pk):
    instance = ConcreteSample.objects.get(pk=pk)

    if request.method == 'POST':
        form = UpdateSampleForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            # This is to set the color on the approvals page, needs to be reimagined to be more dynamic, and also validate upon submission - triggering a popup confirm page if warning or fail
            if instance.strength > 55:
                instance.result = 0
            elif instance.strength < 50:
                instance.result = 2
            else:
                instance.result = 1
            
            instance.status = 1
            instance.save()
            messages.success(request, f'Report Updated for {instance}')
            return redirect('update_report')
    else:
        form = UpdateSampleForm(instance=instance)

    return render(request, 'dashboard/update_report_add.html', {'form': form, 'instance':instance})


@login_required
@user_passes_test(is_manager)
def report_approval(request):
    if request.method == 'POST':
        form = SampleSelectorForm(request.POST)
        if form.is_valid():
            pk = form.cleaned_data.get('id')
            instance = ConcreteSample.objects.get(pk=pk)
            instance.status = 2
            
            # Checks if there are any remaining samples and marks report complete if not
            if ConcreteSample.objects.filter(report=instance.report).filter(Q(status=0) | Q(status=1)).exists() == True:
                main_report = ConcreteReport.objects.get(id=instance.report.id)
                main_report.status = 1
                main_report.save()

            instance.save()
            # Updated list returned
            reports = ConcreteSample.objects.filter(status=1)
            return render(request, 'dashboard/report_approval.html', {'reports':reports})
    else:
        form = SampleSelectorForm()
        reports = ConcreteSample.objects.filter(status=1)
    return render(request, 'dashboard/report_approval.html', {'reports':reports, 'form':form})



