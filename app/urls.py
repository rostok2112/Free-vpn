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
    path("sites/", views.add_site, name='add_site'),
    path("sites/<str:id>/", views.edit_site, name='edit_site'),
]
