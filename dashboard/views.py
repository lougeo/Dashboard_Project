from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from .models import *
from .filters import *
from .utils import *

def is_employee(user):
    if user.groups.filter(name="Manager").exists() | user.groups.filter(name="Technician").exists():
        return True
    else:
        return False

def is_manager(user):
    return user.groups.filter(name="Manager").exists()

# Dasboard page
@login_required
def home(request):
    if is_employee(request.user):
        reports = ConcreteReport.objects.all().order_by('status', '-date_cast')
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
        reports = ConcreteReport.objects.filter(project_name__company__user__id=client).order_by('status', '-date_cast')
        samples = ConcreteSample.objects.filter(report__project_name__company__user__id=client)

        # Total in lab
        card_1 = reports.filter(status=0).count()
        # Breaks Today
        card_2 = samples.filter(break_day=timezone.now().date()).count()
        # Waiting approval
        card_3 = samples.filter(status=1).count()

        card_titles = ['Total Samples in Lab', 'Breaks Today', 'Waiting Approval']

    

    # Instantiating the filter
    myFilter = ReportFilter(request.GET, request=request, queryset=reports)
    filtered = myFilter.qs
    
    # Pagination
    paginator = Paginator(reports, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {'reports':reports,
               'card_1':card_1,
               'card_2':card_2,
               'card_3':card_3, 
               'card_titles':card_titles,
               'myFilter':myFilter,
               'page_obj':page_obj}

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
                return redirect('new_report_concrete')
            elif rtype == '2':
                return redirect('new_report_sieve')
    else:
        form = ReportTypeForm()
    return render(request, 'dashboard/new_report.html', {'form': form})

@login_required
@user_passes_test(is_employee)
def new_report_concrete(request):
    if request.method == 'POST':
        form = ConcreteReportForm(request.POST)
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
        form = ConcreteReportForm()
    return render(request, 'dashboard/new_report_concrete.html', {'form': form})

@login_required
@user_passes_test(is_employee)
def new_report_sieve(request):
    if request.method == 'POST':
        form = SieveReportForm(request.POST)
        if form.is_valid():

            messages.success(request, f'Report Created for')
            return redirect('new_report')
    else:
        form = SieveReportForm()
    return render(request, 'dashboard/new_report_sieve.html', {'form': form})


# Update Report Page
# Change the name of this view, and the following to something less ambiguous
@login_required
@user_passes_test(is_employee)
def update_report(request):
    samples = ConcreteSample.objects.filter(break_day=timezone.now().date()).filter(status=0)
    return render(request, 'dashboard/update_report.html', {'samples':samples})

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

# View full concrete Report
@login_required
def cr_view(request, pk):
    instance = ConcreteReport.objects.get(pk=pk)
    samples = instance.samples.all()
    return render(request, 'dashboard/view_cr.html', {'instance':instance, 'samples':samples})

# Update full concrete report
@login_required
@user_passes_test(is_employee)
def cr_update(request, pk):
    instance = ConcreteReport.objects.get(pk=pk)
    samples = instance.samples.all()

    if request.method == 'POST':

        # Checks which button is clicked
        # Updates report and samples
        if 'update' in request.POST:
            report_form = FullReportUpdateForm(request.POST, prefix='form1', instance=instance)
            sample_forms = SampleFormSet(request.POST, prefix='form2', instance=instance)
            
            # Saving the various forms
            if report_form.is_valid() and report_form.has_changed():
                report_form.save()
            if sample_forms.is_valid() and sample_forms.has_changed():
                sample_forms.save()

            # Checking, and marking if report is now complete
            # This should be made slightly more comprehensive
            if sample_forms.is_valid():
                num_samples = 0
                num_complete = 0
                for sample in sample_forms:
                    s_inst = sample.cleaned_data['id']
                    num_samples += 1
                    # Auto approving modified samples
                    if sample.has_changed() and sample.cleaned_data['strength'] != None:
                        s_inst.status = 2
                        s_inst.save()
                    if s_inst.status == 2: #sample.cleaned_data['id'].status == 2
                        num_complete += 1
                print(f'numsamples: {num_samples}')
                print(f'numcomplete: {num_complete}')
                if num_samples == num_complete:
                    instance.status = 1
                    instance.save()

            # If either of the two form save conditions execute, redirects to home page and flashes message
            if (report_form.is_valid() and report_form.has_changed()) or (sample_forms.is_valid() and sample_forms.has_changed()):
                messages.success(request, f'Report Updated for {instance}')
                return redirect('home')
            # Case where submit is pressed but nothing has changed
            else:
                messages.success(request, f'Fuck off')
                print(sample_forms.errors)
                print(report_form.errors)
                pass
        
        # Checks what submit button was clicked
        # Deletes report
        elif 'delete' in request.POST:
            instance.delete()
            return redirect('home')

    report_form = FullReportUpdateForm(instance=instance, prefix='form1')
    sample_forms = SampleFormSet(instance=instance, prefix='form2')

    return render(request, 
                 'dashboard/update_full_cr.html', 
                 {'instance':instance, 'samples':samples, 'report_form':report_form, 'sample_forms':sample_forms})


# View Report PDF
@login_required 
def ViewPDF(request, pk):
    instance = ConcreteReport.objects.get(pk=pk)
    samples = instance.samples.all()
    pdf = render_to_pdf('dashboard/dl_cr.html', {'instance':instance, 'samples':samples})
    return HttpResponse(pdf, content_type='application/pdf')

# Download Report PDF
@login_required
def DownloadPDF(request, pk):
    instance = ConcreteReport.objects.get(pk=pk)
    samples = instance.samples.all()
    pdf = render_to_pdf('dashboard/view_cr.html', {'instance':instance, 'samples':samples})
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"Report_{instance.id}.pdf"
    content = f"attachment; filename={filename}"
    response['Content-Disposition'] = content
    return response



############################# AJAX VIEWS ####################################

@login_required
def load_projects(request):
    client_id = request.GET.get('client')
    print(client_id)
    projects = Project.objects.filter(company__id=client_id)
    return render(request, 'dashboard/project_dropdown_list.html', {'projects':projects})