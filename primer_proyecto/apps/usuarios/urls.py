from django.urls import path
from .views import LoginUsuarioView, LogoutConfirmView, RegistroUsuarioView

app_name = "usuarios"

urlpatterns = [
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("logout/", LogoutConfirmView.as_view(), name="logout"),
    path("registrar/", RegistroUsuarioView.as_view(), name="registrar"),
]
