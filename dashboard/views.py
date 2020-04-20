from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import NewProjectForm, NewReportForm, UpdateReportForm, ReportTypeForm, ReportSelectorForm, NewSampleForm
from .models import ConcreteReport, ConcreteSample

def is_staff(user):
    if user.groups.filter(name="Manager").exists() | user.groups.filter(name="Technician").exists():
        return True
    else:
        return False

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
        form = NewReportForm(request.POST)
        if form.is_valid():
            # Report
            new_report = form.save()
            name = form.cleaned_data.get('project_name')
            num_samples = form.cleaned_data.get('num_samples')
            break_days = form.cleaned_data.get('break_days')
            pk = new_report.id

            # Samples
            # Maybe include this part in the validation step
            
            break_days = break_days.split(', ')
            report_instance = ConcreteReport.objects.get(pk=pk)
            for i in break_days:
                days = int(i)
                # sample_form = NewSampleForm()
                sample_form = ConcreteSample(report=report_instance, 
                                            cast_day=report_instance.date_cast, 
                                            break_day=report_instance.date_cast + timedelta(days=days))
                # report=form.cleaned_data.get('pk')
                # cast_day=form.cleaned_data.get('date_cast')
                # break_day=form.cleaned_data.get('date_cast') + timedelta(days=days)

                sample_form.save()


            messages.success(request, f'Report Created for {name}')
            return redirect('new_report')
    else:
        form = NewReportForm()
    return render(request, 'dashboard/new_report.html', {'form': form})


# Need to query the db for all the reports which are "active"
# Then need to obtain the PK for selected report, and send user to update page with that info loaded

# Update Report Page
@login_required
@user_passes_test(is_staff)
def update_report(request):
    if request.method == 'POST':
        form = ReportSelectorForm(request.POST)
        if form.is_valid():
            report = form.cleaned_data.get('rtype')
            return redirect('#') # find out how to do the relative url path
    else:
        form = ReportSelectorForm()
    return render(request, 'dashboard/update_report.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def update_report_add(request):
    if request.method == 'POST':
        form = UpdateReportForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            messages.success(request, f'Report Updated for {name}')
            # return redirect('url name')
            # redirect to a page which says report successfully created and asks what user wants to do
    else:
        form = UpdateReportForm()
    return render(request, 'dashboard/update_report.html', {'form': form})





