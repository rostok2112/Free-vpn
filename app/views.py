import json
import re
import requests

from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import (
    login as login_,
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import View, ListView
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from urllib.parse import unquote_plus, urlparse

from app.forms import SiteForm, CustomUserChangeForm
from app.mixins import CustomLoginRequiredMixin
from app.models import Site
from app.utils import urlencode


class HomeView(CustomLoginRequiredMixin, ListView):
    model = Site
    template_name = 'home.html'
    context_object_name = 'sites'
    ordering = ['-visit_count']
    paginate_by = 20

    def get_queryset(self):
        return (
            self.model.objects
                .filter(user=self.request.user)
                .order_by(*self.get_ordering())
        )

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_message = 'Hello, %(username)s!'

    def form_valid(self, form):
        messages.success(self.request, self.success_message % form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid name or password')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('home')

class CustomRegisterView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login_(self.request, user)
        messages.success(self.request, f'Hello, {user.username}! You are now registered.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please check the form.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.info(request, 'You are successfully logged out!')
        return response

class SettingsView(CustomLoginRequiredMixin, FormView):
    template_name = 'settings.html'
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('settings')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "You have successfully edited your profile!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in editing your profile. Please check the form.")
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs
class SiteAddView(CustomLoginRequiredMixin, FormView):
    template_name = 'site_form.html'
    form_class = SiteForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "You are successfully added a new site!")
        return super().form_valid(form)

class SiteEditView(CustomLoginRequiredMixin, FormView):
    template_name = 'site_form.html'
    form_class = SiteForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(Site, pk=self.kwargs['id'])

        return kwargs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = self.get_form().instance
        context['editing'] = True
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"You are successfully edited site '{form.instance.name}'!")
        return super().form_valid(form)
    
class SiteDeleteView(CustomLoginRequiredMixin, View):
    def get(self, request, id):
        site = get_object_or_404(Site, pk=id)
        site.delete()
        messages.success(request, f"You have successfully deleted site '{site.name}' !")
        return redirect('home')
class ProxyView(CustomLoginRequiredMixin, View):
    def get(self, request, name, url):
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

class StaticProxyView(CustomLoginRequiredMixin, View):
    def get(self, request, name, url):
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
