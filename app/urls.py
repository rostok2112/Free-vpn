from django.urls import path
from django.contrib import admin

from . import views, api


urlpatterns = [
    path("", views.home, name="home"),
    # path('admin/', admin.site.urls, name='admin'),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    path("settings", views.settings, name="settings"),
    path("sites/", views.site_add, name='site_add'),
    path("sites/<uuid:id>/", views.site_edit, name='site_edit'),
    path('sites/<uuid:id>/delete/', views.site_delete, name='site_delete'),
]
