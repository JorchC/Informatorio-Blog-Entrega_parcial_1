from django.urls import path
from .views import LoginUsuarioView, LogoutConfirmView, RegistroUsuarioView, UsuarioListView, UsuarioDeleteView # <--- Agregada UsuarioDeleteView

app_name = "usuarios"

urlpatterns = [
    # Rutas de autenticación existentes
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("logout/", LogoutConfirmView.as_view(), name="logout"),
    path("registrar/", RegistroUsuarioView.as_view(), name="registrar"),
    
    # PANEL DE ADMINISTRACIÓN DE USUARIOS
    path("panel/", UsuarioListView.as_view(), name="lista_usuarios"),
    path("eliminar/<int:pk>/", UsuarioDeleteView.as_view(), name="eliminar_usuario"),
]