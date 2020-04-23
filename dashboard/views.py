from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import NewProjectForm, ReportForm, UpdateSampleForm, ReportTypeForm, ReportSelectorForm, NewSampleForm
from .models import ConcreteReport, ConcreteSample

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
def home(request):
    reports = ConcreteReport.objects.all()
    samples = ConcreteSample.objects.all()
    #in_lab = ConcreteReport.filter(status=0).count()


    return render(request, 'dashboard/home.html', {'reports':reports, 'samples':samples})

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
                                             break_day=new_report.date_cast + timedelta(days=days))
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
            instance.status = 1
            instance.save()
            messages.success(request, f'Report Updated for {instance}')
            return redirect('update_report')
    else:
        form = UpdateSampleForm(instance=instance)

    return render(request, 'dashboard/update_report_add.html', {'form': form, 'instance':instance})



# Need to figure out how I want this laid out
@login_required
@user_passes_test(is_manager)
def report_approval(request):
    # if request.method == 'POST':
    #     form = ReportSelectorForm(request.POST)
    #     if form.is_valid():
    #         report = form.cleaned_data.get('selected_report')
    #         return redirect('update_report_add', pk=report.pk)
    # else:
    #     form = ReportSelectorForm()
    #     reports = ConcreteSample.objects.filter(status=1)
    return render(request, 'dashboard/report_approval.html', {'form': form, 'reports':reports})



