from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView


urlpatterns = [
    path('',  include("app.urls")),
    path('admin/', admin.site.urls),
    *static(settings.STATIC_URL, document_root=settings.BASE_DIR), # pathes for static files
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
] 
