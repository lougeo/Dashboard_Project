from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from .models import *
from .filters import *
from .utils import *


# Dasboard page
@login_required
def home(request):
    if is_employee(request.user):
        # if conditional to check if paginated, and to modify reports if so
        reports = Report.objects.all().order_by('status', '-date_sampled', '-id')
        samples = ConcreteSample.objects.all()

        # Total samples in lab
        card_1 = reports.filter(status=0).count()
        # Breaks Today
        card_2 = samples.filter(break_date=timezone.now().date()).count()
        # Waiting approval
        card_3 = samples.filter(status=1).count()

        card_titles = ['Total Samples in Lab', 'Breaks Today', 'Waiting Approval']

    else:
        client = request.user.id
        reports = Report.objects.filter(project_name__company__user__id=client).order_by('status', '-date_sampled')
        samples = ConcreteSample.objects.filter(report__project_name__company__user__id=client)

        # Total completed reports
        card_1 = reports.filter(status=1).count()
        # Total samples in lab
        card_2 = reports.filter(status=0).count()
        # Breaks Today
        card_3 = samples.filter(break_date=timezone.now().date()).count()
        
        card_titles = ['Total Completed Reports', 'Total Samples in Lab', 'Breaks Today']

    

    # Instantiating the filter
    myFilter = ReportFilter(request.GET, request=request, queryset=reports)
    filtered = myFilter.qs
    
    # Pagination
    paginator = Paginator(filtered, 20)
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


############################# NEW REPORT VIEWS ################################
@login_required
@user_passes_test(is_employee)
def new_report(request):
    if request.method == 'POST':
        form = ReportTypeForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data.get('name')
            report_type_name = str(report_type).lower()
            return redirect(f'new_report_{report_type_name}', pk=report_type.id)
    
    form = ReportTypeForm()
    return render(request, 'dashboard/new_report.html', {'form': form})

@login_required
@user_passes_test(is_employee)
def new_report_concrete(request, pk):

    if request.method == 'POST':
        form = NewConcreteReportForm(request.POST)

        if form.is_valid():

            # Setting required variables 
            new_report = form.save(commit=False)
            new_report.report_type = ReportStandard.objects.get(pk=pk)
            cast_date = form.cleaned_data.get('date_sampled')
            sample_form = NewConcreteSampleFormSet(request.POST, instance=new_report, prefix='form2')

            if sample_form.is_valid():

                # Sets the cast, and break date for the sample if break day is entered
                for sample in sample_form:
                    if sample.cleaned_data.get('days_break') != None:
                        break_day = sample.cleaned_data.get('days_break')
                        sample_obj = sample.save(commit=False)
                        sample_obj.cast_date = cast_date
                        sample_obj.break_date = cast_date + timedelta(days=break_day)
                    else:
                        continue
                new_report.save()
                sample_form.save()

                messages.success(request, f'Report {new_report.id}, Created for {new_report.project_name}')
                return redirect('new_report')

    # Not prefixing the first form because that messes with the AJAX/form submission
    form = NewConcreteReportForm()
    sample_form = NewConcreteSampleFormSet(prefix='form2')

    context = {
        'form': form,
        'sample_form':sample_form
    }
    return render(request, 'dashboard/new_report_concrete.html', context)

@login_required
@user_passes_test(is_employee)
def new_report_sieve(request, pk):

    if request.method == 'POST':

        form = NewSieveReportForm(request.POST)

        if form.is_valid():

            new_report = form.save(commit=False)
            new_report.report_type = ReportStandard.objects.get(pk=pk)
            sample_form = NewSieveSampleFormSet(request.POST, instance=new_report, prefix='form2')

            if sample_form.is_valid():
                
                # THIS NEEDS TO BE UPGRADED
                for sample in sample_form:

                    wet_weight = sample.cleaned_data.get('wet_weight')
                    dry_weight = sample.cleaned_data.get('dry_weight')

                    if wet_weight != None and dry_weight != None:

                        sample_obj = sample.save(commit=False)
                        sample_obj.moisture_content = wet_weight - dry_weight
                        # Add conditional setting result
                        # Add conditional setting status based on Manager/Technician

                    else:
                        continue
                
                new_report.save()
                sample_form.save()

                messages.success(request, f'Report {new_report.id}, Created for {new_report.project_name}')
                return redirect('new_report')

    form = NewSieveReportForm()
    sample_form = NewSieveSampleFormSet(prefix='form2')

    context = {
        'form':form,
        'sample_form':sample_form
    }
    
    return render(request, 'dashboard/new_report_sieve.html', context)


###################### NEW STANDARD VIEWS ######################

@login_required
@user_passes_test(is_employee)
def new_standard(request):
    if request.method == 'POST':

        form = ReportStandardForm(request.POST, prefix='form1')
        print(f"THIS IS FROM POST DATA: {request.POST.get('form1-standard_type')}, {type(request.POST.get('form1-standard_type'))}")

        if form.is_valid():
            standard_type = form.cleaned_data.get('standard_type')
            report_standard = form.save(commit=False)     
        if standard_type == 0:
            parameter_form = CompressionParametersForm(request.POST, prefix='form2')
        elif standard_type == 1:
            parameter_form = SieveParametersForm(request.POST, prefix='form2')

        if form.is_valid() and parameter_form.is_valid():
            report_standard.save()
            standard_parameters = parameter_form.save(commit=False)
            standard_parameters.standard = report_standard
            standard_parameters.save()
        
            messages.success(request, f'Standard created for: {report_standard}, {standard_parameters}')
            return redirect('new_standard')
    
    form = ReportStandardForm(prefix='form1')

    return render(request, 'dashboard/new_standard.html', {'form': form})


# @login_required
# @user_passes_test(is_employee)
# def new_standard_compression(request, pk):
#     instance = ReportStandard.objects.get(pk=pk)

#     if request.method == 'POST':
#         form = CompressionParametersForm(request.POST)
#         if form.is_valid():
#             form_instance = form.save(commit=False)
#             form_instance.standard = instance
#             form_instance.save()
            
#             messages.success(request, f'Standard created for: {form_instance}')
#             return redirect('new_standard')
    
#     form = CompressionParametersForm()
#     return render(request, 'dashboard/new_standard_compression.html', {'form': form})

    
# @login_required
# @user_passes_test(is_employee)
# def new_standard_sieve(request, pk):
#     instance = ReportStandard.objects.get(pk=pk)

#     if request.method == 'POST':
#         form = SieveParametersForm(request.POST, instance=instance)
#         if form.is_valid():
#             instance = form.save()

#             messages.success(request, f'Standard created for: {instance.standard}')
#             return redirect('new_standard')
    
#     form = SieveParametersForm(instance=instance)
#     return render(request, 'dashboard/new_standard_sieve.html', {'form': form})

###################### LAB VIEWS ###############################

@login_required
@user_passes_test(is_employee)
def lab_update_sample_list(request):
    samples = ConcreteSample.objects.filter(break_date=timezone.now().date()).filter(status=0)
    return render(request, 'dashboard/lab_update_sample_list.html', {'samples':samples})

@login_required
@user_passes_test(is_employee)
def lab_update_sample(request, pk):
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
            return redirect('lab_update_sample_list')
    else:
        form = UpdateSampleForm(instance=instance)

    return render(request, 'dashboard/lab_update_sample.html', {'form': form, 'instance':instance})


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
                main_report = Report.objects.get(id=instance.report.id)
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


############################# MANAGE VIEWS ####################################
@login_required
def view_report_full(request, pk):
    instance = Report.objects.get(pk=pk)
    report_type_name = str(instance.report_type).lower()
    if report_type_name == 'concrete':
        samples = instance.concrete_samples.all()
        context = {'instance':instance, 'samples':samples}
    elif report_type_name == 'sieve':
        samples = instance.sieve_samples.all()
        sample = instance.sieve_samples.first()
        data = [
            sample.mm_120,
            sample.mm_80,
            sample.mm_40,
            sample.mm_20,
            sample.mm_10,
            sample.mm_5,
            sample.mm_1,
            sample.mm_05,
            sample.mm_025]
        plot_data = plot_sieve_report(data)
        context = {
            'instance':instance, 
            'samples':samples,
            'plot_data':plot_data}
    else:
        return HttpResponseNotFound('Report is incomplete')

    return render(request, f'dashboard/view_report_full_{report_type_name}.html', context)

# Update full concrete report
@login_required
@user_passes_test(is_employee)
def update_report_full(request, pk):
    instance = Report.objects.get(pk=pk)
    report_type_name = str(instance.report_type).lower()

    if request.method == 'POST':
        print(request.POST)

        # Checks which button is clicked
        # Updates report and samples
        if 'update' in request.POST:
            report_form = FullReportUpdateForm(request.POST, prefix='form1', instance=instance)
            sample_forms = ConcreteSampleFormSet(request.POST, prefix='form2', instance=instance)
            project_form = ProjectManagerForm(request.POST, prefix='form3', instance=instance.project_name)
            

            # If any of the 3 form save conditions execute, redirects to home page and flashes message
            if (report_form.is_valid() and report_form.has_changed()) or \
               (sample_forms.is_valid() and sample_forms.has_changed()) or \
               (project_form.is_valid() and project_form.has_changed()):

                # Saving the various forms
                if report_form.is_valid() and report_form.has_changed():
                    report_form.save()
                if sample_forms.is_valid() and sample_forms.has_changed():
                    sample_forms.save()
                if project_form.is_valid() and project_form.has_changed():
                    project_form.save()

                # Checking, and marking if report is now complete
                # This should be made slightly more comprehensive
                # Maybe a form checkbox "mark as complete"
                if sample_forms.is_valid():
                    num_samples = 0
                    num_complete = 0

                    for sample in sample_forms:
                        num_samples += 1

                        # Auto approving modified samples
                        if sample.has_changed() and sample.cleaned_data['result'] != None:
                            s_inst = sample.cleaned_data['id']
                            s_inst.status = 2
                            s_inst.save()

                        if s_inst.status == 2: #sample.cleaned_data['id'].status == 2
                            num_complete += 1
                    print(f'numsamples: {num_samples}')
                    print(f'numcomplete: {num_complete}')
                    if num_samples == num_complete:
                        instance.status = 1
                        instance.save()


                messages.success(request, f'Report Updated for: {instance}')
                return redirect('home')

            # Case where submit is pressed but nothing has changed
            else:
                messages.success(request, f'Nothing has changed')
                pass
        
        # Checks what submit button was clicked
        # Deletes report
        elif 'delete' in request.POST:
            instance.delete()
            return redirect('home')

    if report_type_name == 'concrete':
        samples = instance.concrete_samples.all()
        sample_forms = ConcreteSampleFormSet(instance=instance, prefix='form2')

    elif report_type_name == 'sieve':
        samples = instance.sieve_samples.all()
        sample_forms = SieveSampleFormSet(instance=instance, prefix='form2')

    report_form = FullReportUpdateForm(instance=instance, prefix='form1')
    project_form = ProjectManagerForm(instance=instance.project_name, prefix='form3')

    context = {
        'instance':instance, 
        'samples':samples, 
        'report_form':report_form, 
        'sample_forms':sample_forms,
        'project_form':project_form
        }
    
    return render(request, f'dashboard/update_report_full_{report_type_name}.html', context)


############################## HELPER VIEWS ######################################

# View Report PDF
@login_required 
def ViewPDF(request, pk):
    instance = Report.objects.get(pk=pk)
    report_type_name = str(instance.report_type).lower()

    if report_type_name == 'concrete':
        samples = instance.concrete_samples.all()
        context = {
            'instance':instance, 
            'samples':samples
        }

    elif report_type_name == 'sieve':
        samples = instance.sieve_samples.all()
        sample = instance.sieve_samples.first()
        data = [
            sample.mm_120,
            sample.mm_80,
            sample.mm_40,
            sample.mm_20,
            sample.mm_10,
            sample.mm_5,
            sample.mm_1,
            sample.mm_05,
            sample.mm_025]
        plot_data = plot_sieve_report(data)
        context = {
            'instance':instance,
            'samples':samples,
            'plot_data':plot_data
        }
    pdf = render_to_pdf(f'dashboard/pdf_{report_type_name}.html', context)
    return HttpResponse(pdf, content_type='application/pdf')

# Download Report PDF
@login_required
def DownloadPDF(request, pk):
    instance = Report.objects.get(pk=pk)
    samples = instance.concrete_samples.all()
    pdf = render_to_pdf('dashboard/view_cr.html', {'instance':instance, 'samples':samples})
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"Report_{instance.id}.pdf"
    content = f"attachment; filename={filename}"
    response['Content-Disposition'] = content
    return response

# Generate Sieve Plot
@login_required
def SievePlotGenerator(request):

    data = []
    for i in request.GET:
        data.append(float(request.GET.get(i)))

    plot_data = plot_sieve_report(data)

    return render(request, 'dashboard/sieve_plot_insert.html', {'plot_data':plot_data})


############################# AJAX VIEWS ####################################

@login_required
@user_passes_test(is_employee)
def load_projects(request):
    client_id = request.GET.get('client')
    if client_id != '':
        projects = Project.objects.filter(company__id=client_id)
    else:
        projects = Project.objects.none()
    return render(request, 'dashboard/project_dropdown_list.html', {'projects':projects})


@login_required
@user_passes_test(is_employee)
def load_parameter_form(request):
    standard_type = request.GET.get('standard_type')

    if standard_type == '0':
        parameter_form = CompressionParametersForm(prefix='form2')
        url = 'dashboard/new_standard_compression.html'
    elif standard_type == '1':
        parameter_form = SieveParametersForm(prefix='form2')
        url = 'dashboard/new_standard_sieve.html'
    else:
        print("UR A FOCKIN IDIOT")
        return HttpResponse('')

    return render(request, url, {'parameter_form':parameter_form})