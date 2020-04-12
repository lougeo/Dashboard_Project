from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegisterForm

def is_manager(user):
    return user.groups.filter(name="Manager").exists()

# This url will only be accessible my manager user
@login_required
@user_passes_test(is_manager)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            # This seems like a janky solution to update the group
            group = form.cleaned_data['group']
            group.user_set.add(form.save())
            messages.success(request, f'Account created for {username}')
            # return redirect('url name')
            # redirect to a page which says account successfully created and asks what user wants to do
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')
