from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm

# This url will only be accessible my manager user
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            # return redirect('url name')
            # redirect to a page which says account successfully created and asks what user wants to do
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
