from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Report
from .forms import ReportForm


def is_staff(user):
    if user.groups.filter(name="Manager").exists() | user.groups.filter(name="Technician").exists():
        return True
    else:
        return False

# Dasboard page. Need diff for client/staff?
@login_required
def home(request):
    return render(request, 'dashboard/home.html')

# Data Entry page
@login_required
@user_passes_test(is_staff)
def input(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            messages.success(request, f'Report Submitted for {name}')
            # return redirect('url name')
            # redirect to a page which says report successfully created and asks what user wants to do
    else:
        form = ReportForm()
    return render(request, 'dashboard/input.html', {'form': form})