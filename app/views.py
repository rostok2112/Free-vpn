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
from django.contrib.auth.decorators import login_required

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from urllib.parse import unquote_plus, urlparse

from app.forms import SiteForm, CustomUserChangeForm
from app.models import Site
from app.utils import get_resource_size, urlencode


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {
            'sites':    request.user.site_set.all().order_by('-visit_count')
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

@login_required
def logout(request):
    logout_(request)
    messages.info(request, 'You are sucessfully logged out!')
    return redirect('home')

@csrf_protect
@login_required
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

@csrf_protect
@login_required
def site_edit(request, id):
    site = get_object_or_404(Site, pk=id)
    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, f"You are successfully edited site '{site.name}'!")
            
            return redirect('home')
    else:
        form = SiteForm(instance=site)

    return render(request, 'site_form.html', {
        'site': site, 'form': form, 'editing': True
    })
    
@csrf_protect
@login_required
def site_delete(request, id):
    site = get_object_or_404(Site, pk=id)
    site.delete()
    messages.success(request, f"You are successfully deleted site '{site.name}' !")
    
    return redirect('home')

@login_required
def proxy(request, name, url):
    unquoted_name = unquote_plus(name)
    unquoted_url = unquote_plus(url).removesuffix('/')
    
    try: 
        parsed_url = urlparse(unquoted_url)
        
        host_with_protocol = '{url.scheme}://{url.netloc}'.format(url=parsed_url)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')

        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(unquoted_url)
            WebDriverWait(driver, 1) \
                .until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                ) # wait for full load of page
            

            html_content = driver.page_source
            total_traffic = len(html_content.encode('utf-8'))
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for tag in soup.find_all(['link', 'script', 'meta', 'img']):
                for tag_attr in ['src', 'href', 'content', 'data-src',]:
                    if tag_attr in tag.attrs and  tag.get(tag_attr).startswith('/'):
                        tag[tag_attr] = f"{host_with_protocol}{tag.get(tag_attr)}"
                        total_traffic += get_resource_size(tag[tag_attr])
                if tag.get('srcset'):
                    tags_contents = []
                    for tag_content in tag['srcset'].split(' '):
                        if tag_content.startswith('/'):
                            tag_content = f"{host_with_protocol}{tag_content}"
                        tags_contents.append(tag_content)
                    tag['srcset'] = " ".join(tags_contents)
            
            for a in soup.find_all('a'):
                if a.get('href', '').startswith('/'):
                    a['href'] = f'/{name}/{urlencode(unquoted_url + a["href"])}'
                
        finally:
            driver.quit()
            
        html_content = str(soup)
        
        site = Site.objects.get(name=unquoted_name)
        site.visit_count += 1 
        site.routed_data_amount += total_traffic
        site.save()
        
        return HttpResponse(html_content)
    except Exception as e:
        message = f"Cant load '{unquoted_name}'  site " \
                        f"with '{unquoted_url}' url. "  \
                        "Make sure that url is correct."
        messages.error(request, message)
         
        return redirect('home')
        
@login_required
def settings(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "You are sucessfully edited your profile !")
            
            return redirect('settings')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'settings.html', {'form': form})
