from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .forms import *
from .models import ConcreteReport, ConcreteSample
from .filters import *

def is_staff(user):
    if user.groups.filter(name="Manager").exists() | user.groups.filter(name="Technician").exists():
        return True
    else:
        return False

def is_manager(user):
    return user.groups.filter(name="Manager").exists()

# Dasboard page. Need diff for client/staff?
# Set conditional so that if user is client, can only view their own reports

@login_required
@user_passes_test(is_staff, redirect_field_name='#')
def home(request):
    reports = ConcreteReport.objects.all()
    samples = ConcreteSample.objects.all()
    in_lab = reports.filter(status=0).count()
    breaks_today = samples.filter(break_day=timezone.now().date()).count()
    waiting_approval = samples.filter(status=1).count()

    myFilter = ReportFilter(request.GET, queryset=reports)
    reports = myFilter.qs

    context = {'reports':reports,
               'samples':samples,
               'in_lab':in_lab,
               'breaks_today':breaks_today,
               'waiting_approval':waiting_approval,
               'myFilter':myFilter}

    return render(request, 'dashboard/home.html', context)

# New Project page
@login_required
@user_passes_test(is_staff)
def new_project(request):
    if request.method == 'POST':
        form = NewProjectForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            company = form.cleaned_data.get('company')
            messages.success(request, f'Project {name} Created for {company}')
            return redirect('new_report')
    else:
        form = NewProjectForm()
    return render(request, 'dashboard/new_project.html', {'form': form})


# New Report page
@login_required
@user_passes_test(is_staff)
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
@user_passes_test(is_staff)
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
@user_passes_test(is_staff)
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
@user_passes_test(is_staff)
def update_report_add(request, pk):
    instance = ConcreteSample.objects.get(pk=pk)

    if request.method == 'POST':
        form = UpdateSampleForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            # This is to set the color on the approvals page, needs to be reimagined to be more dynamic, and also validate upon submission - triggering a popup confirm page if warning or fail
            if instance.strength > 50:
                instance.result = 0
            elif instance.strength < 40:
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



