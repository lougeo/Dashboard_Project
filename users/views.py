from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *
from .models import Project
from dashboard.utils import is_manager

# This url will only be accessible my manager user
@login_required
@user_passes_test(is_manager)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, prefix='form1')
        profile_form = ProfileForm(request.POST, prefix='form2')

        if form.is_valid() and profile_form.is_valid():
            username = form.cleaned_data.get('username')
            new_user = form.save()

            profile_form = ProfileForm(request.POST, instance=new_user.profile, prefix='form2')

            profile_form.save()

            # This seems like a janky solution to update the group
            group = form.cleaned_data['account_type']
            group.user_set.add(new_user)

            messages.success(request, f'Account created for {username}')
            return redirect('register')
  
    form = UserRegisterForm(prefix='form1')
    profile_form = ProfileForm(prefix='form2')

    return render(request, 'users/register.html', {'form':form, 'profile_form':profile_form})

@login_required
def profile(request):
    instance = Profile.objects.get(pk=request.user.profile.id)

    return render(request, 'users/profile.html', {'profile':instance})

@login_required
def profile_update(request, pk):
    instance = Profile.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=instance, prefix='form1')
        email_form = UserEmailUpdateForm(request.POST, instance=request.user, prefix='form2')
        if form.is_valid():
            form.save()
        if email_form.is_valid():
            email_form.save()
        if form.is_valid() or email_form.is_valid():
            messages.success(request, f'Profile updated!')
            return redirect('profile')

    form = ProfileForm(instance=instance, prefix='form1')
    email_form = UserEmailUpdateForm(instance=request.user, prefix='form2')

    context = {'profile':instance,
               'form':form,
               'email_form':email_form}
               
    return render(request, 'users/profile_update.html', context)

# New Project page
@login_required
@user_passes_test(is_manager)
def new_project(request):
    if request.method == 'POST':
        form = NewProjectForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            company = form.cleaned_data.get('company')
            messages.success(request, f'Project: {name} Created for: {company}')
            return redirect('new_report')
    else:
        form = NewProjectForm()
    
    return render(request, 'users/new_project.html', {'form': form})
