from django.urls import path

from app import views


urlpatterns = [
    path("settings", views.SettingsView.as_view(), name="settings"),
    path("login", views.CustomLoginView.as_view(), name="login"),
    path("register", views.CustomRegisterView.as_view(), name="register"),
    path("logout", views.CustomLogoutView.as_view(), name="logout"),
    
    path("", views.HomeView.as_view(), name="home"),
    path("sites/", views.SiteAddView.as_view(), name='site_add'),
    path("sites/<uuid:id>/", views.SiteEditView.as_view(), name='site_edit'),
    path('sites/<uuid:id>/delete/', views.SiteDeleteView.as_view(), name='site_delete'),
    
    path('<str:name>/<str:url>/', views.ProxyView.as_view(), name='proxy'),
    path('static_proxy/<str:name>/<str:url>/', views.StaticProxyView.as_view(), name='static_proxy'),
]
