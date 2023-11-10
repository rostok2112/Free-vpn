from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth import (
    authenticate, 
    login as login_,
    logout as logout_,
)
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from app.forms import SiteForm

from app.models import Site


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {
            'sites':    request.user.site_set.all()
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

def settings(request):
    return HttpResponse("Settings !!!")

def site_add(request):
    if request.method == 'POST':
        form = SiteForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, "You are successfully added new site !")
            return redirect('home')
    else:
        form = SiteForm(request=request)

    return render(request, 'site_form.html', {'form': form})

def site_edit(request, id):
    site = get_object_or_404(Site, pk=id)
    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, "You are successfully edited site !")
            return redirect('home')
    else:
        form = SiteForm(instance=site)

    return render(request, 'site_form.html', {
        'site': site, 'form': form, 'editing': True
    })

def site_delete(request, id):
    site = get_object_or_404(Site, pk=id)
    # site_name = site.name
    site.delete()
    
    messages.success(request, f"You are successfully deleted site '{site.name}' !")
    
    return redirect('home')
