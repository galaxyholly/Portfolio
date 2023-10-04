from django.urls import path
from . import views

app_name = "registration"   


urlpatterns = [
    path("", views.login_request, name="login"),
    path("register", views.register_request, name="register"),
    path("logout", views.logout_request, name= "logout"),
]