from django.urls import path

from . import views, api


urlpatterns = [
    path("", views.home, name="home"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
]
