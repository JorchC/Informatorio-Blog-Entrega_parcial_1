from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from apps.posts.models import Post

# Definimos el formulario aquí mismo para no crear más archivos
class ContactoForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )
    correo = forms.EmailField(
        label="Correo Electrónico", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'})
    )
    asunto = forms.CharField(
        label="Asunto", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mensaje = forms.CharField(
        label="Mensaje", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mostrar posts activos, más recientes primero
        context["posts"] = (
            Post.objects
            .filter(activo=True)
            .order_by("-publicado")
        )
        return context

# Nueva vista para Acerca de
class AcercaDeView(TemplateView):
    template_name = "acercaDe.html"

# Nueva vista para el formulario de Contacto
def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Aquí podrías implementar el envío de mail real
            messages.success(request, "¡Gracias por contactarnos! Tu mensaje ha sido enviado con éxito.")
            return redirect('index')
    else:
        form = ContactoForm()
    
    return render(request, 'contacto.html', {'form': form})