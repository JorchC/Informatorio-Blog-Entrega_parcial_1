from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.shortcuts import redirect, render

from .forms import RegistroUsuarioForm, LoginForm
from .models import Usuario


class RegistroUsuarioView(CreateView):
    model = Usuario
    template_name = "registration/registrar.html"
    form_class = RegistroUsuarioForm

    def form_valid(self, form):
        messages.success(self.request, "Registro exitoso. Por favor, inicia sesión.")
        form.save()
        return redirect("usuarios:login")


class LoginUsuarioView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm

    def form_valid(self, form):
        messages.success(self.request, "Login exitoso")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("index")


class LogoutConfirmView(View):
    template_name = "registration/logout.html"

    def get(self, request):
        # Muestra la pantalla de confirmación
        return render(request, self.template_name)

    def post(self, request):
        # Ejecuta el logout
        logout(request)
        return redirect("index")
