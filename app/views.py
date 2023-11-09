from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate, 
    login as login_,
    logout as logout_,
)
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {
            'username': request.user.username,
        })
    else:
        messages.info(request, 'You are not logged in !')
        return redirect('login')
        

@csrf_protect
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login_(request, user)
                messages.success(request, f'Hello, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid name or passworld')
        else:
            messages.error(request, 'Invalid name or password')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login_(request, user)
            messages.success(request, f'Hello, {username}!')
            return redirect('home') 
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout(request):
    logout_(request)
    messages.info(request, 'You are sucessfully logged out!')
    return redirect('home')
