from django.contrib import admin
from django.urls import path, include
from inventory import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", views.signup, name="signup"),
    path("inventory/", include("inventory.urls")),
]
