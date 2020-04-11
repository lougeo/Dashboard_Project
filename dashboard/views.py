from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Report

@login_required
def home(request):
    return render(request, 'dashboard/home.html')


@login_required
def input(request):
    return render(request, 'dashboard/input.html')