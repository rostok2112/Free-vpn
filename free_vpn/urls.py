from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('',  include("app.urls")),
    path('admin/', admin.site.urls),
    *static(settings.STATIC_URL, document_root=settings.BASE_DIR) # pathes for static files
] 
