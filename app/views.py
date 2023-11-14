import json
import re
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import (
    authenticate, 
    login as login_,
    logout as logout_,
)
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from urllib.parse import unquote_plus, urlparse

from app.forms import SiteForm, CustomUserChangeForm
from app.models import Site
from app.utils import urlencode


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
        chrome_options = Options()
        
        chrome_options.add_argument('--headless')  # run in background                                                                     
        chrome_options.add_argument('--ignore-certificate-errors')
        # for running in docker container
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.set_capability( 
            'goog:loggingPrefs',       # for getting performance and network  
            {'performance': 'ALL'}     # chrome devtools protocol logs
        ) 

        driver = webdriver.Chrome(options=chrome_options) 
        try: 
            site = Site.objects.get(name=unquoted_name)
            site_url = site.url.removesuffix('/')
            parsed_site_url = urlparse(site_url)
            host = parsed_site_url.netloc
            host_with_protocol = '{url.scheme}://{url.netloc}'.format(url=parsed_site_url)
            
            driver.execute_cdp_cmd('Network.enable', {}) # allow CDP network logs
            driver.get(unquoted_url)
            WebDriverWait(driver, 10) \
                .until(
                    EC.presence_of_element_located((By.TAG_NAME, 'link'))
                ) # wait for full load of page
               
            performance_logs = driver.get_log('performance')
            performance_list = [
                json.loads(log['message'].lower())['message']
                for log in performance_logs
            ]
            
            total_traffic = sum([
                int(log["params"]["response"]["headers"].get("content-length", 0))
                for log in performance_list
                if log["method"] == "network.responsereceived"
            ])
            
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for tag in soup.find_all(['a', 'script', 'link', 'meta', 'img',]):
                new_path_chunk = f'/{name}/'
                if tag.name != 'a':
                    new_path_chunk = '/static_proxy' + new_path_chunk
                for tag_attr in ['href', 'src', 'content', 'data-src',]:
                    if tag_attr in tag.attrs:
                        old_tag_attr_val = tag.get(tag_attr, '')
                        if old_tag_attr_val.startswith('/'):
                            tag[tag_attr] = new_path_chunk + urlencode(host_with_protocol + old_tag_attr_val)
                        elif host in old_tag_attr_val:
                            tag[tag_attr] = new_path_chunk + urlencode(old_tag_attr_val)

                if tag.get('srcset'):
                    tags_attr_chunks = []
                    new_path_chunk = f'/static_proxy/{name}/'
                    for tag_attr_chunk_val in tag['srcset'].split(' '):
                        if tag_attr_chunk_val.startswith('/'):
                            tag_attr_chunk_val = new_path_chunk + urlencode(f"{host_with_protocol}{tag_attr_chunk_val}")
                        elif host in tag_attr_chunk_val:
                            tag_attr_chunk_val = new_path_chunk + urlencode(tag_attr_chunk_val)
                        tags_attr_chunks.append(tag_attr_chunk_val)
                    tag['srcset'] = " ".join(tags_attr_chunks)
                    
            html_content = str(soup)
            
            if site_url == unquoted_url:
                site.visit_count += 1
                site.routed_data_amount += total_traffic
                site.save()
            
            return HttpResponse(html_content)
        except Exception as e:
            raise e
        finally:
            driver.quit()
    except Exception as e:
        message = f"Cant load '{unquoted_name}'  site " \
                            f"with '{unquoted_url}' url. "  \
                            "Make sure that url is correct."
        messages.error(request, message)
        return redirect('home')

@login_required
def static_proxy(request, name, url):
    unquoted_url = unquote_plus(url).removesuffix('/')
    
    try: 
        response = requests.get(unquoted_url)
        content_type = response.headers.get('content-type')
        
        if content_type.startswith('text/css'):
            content = response.text
            
            url_pattern = re.compile(r'url\((.*?)\)')
            matches = url_pattern.findall(content)
            for old_url in matches:
                old_relative_path = urlparse(old_url).path
                new_url = f'/static_proxy/{name}/{urlencode(old_relative_path)}'
                
                content = content.replace(f'url({old_url})', f'url({new_url})')
        else:
             content = response.content  
        return HttpResponse(content, content_type=content_type)
    except requests.exceptions.RequestException:
        raise Http404('Resource not found')
    
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
