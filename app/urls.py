from django.urls import path
from django.contrib import admin

from app import views


urlpatterns = [
    path("", views.home, name="home"),
    path("settings", views.settings, name="settings"),

    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    
    path("sites/", views.site_add, name='site_add'),
    path("sites/<uuid:id>/", views.site_edit, name='site_edit'),
    path('sites/<uuid:id>/delete/', views.site_delete, name='site_delete'),
    
    path('<str:name>/<str:url>/', views.proxy, name='proxy'),
    path('static_proxy/<str:name>/<str:url>/', views.static_proxy, name='static_proxy'),
]
