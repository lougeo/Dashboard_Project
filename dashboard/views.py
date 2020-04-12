from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Report

# Dasboard page. Need diff for client/staff?
@login_required
def home(request):
    return render(request, 'dashboard/home.html')

# Data Entry page
@login_required
def input(request):
    return render(request, 'dashboard/input.html')