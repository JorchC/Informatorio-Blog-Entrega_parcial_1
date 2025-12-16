from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model

from .forms import RegistroUsuarioForm, LoginForm
Usuario = get_user_model() 


# MIXIN DE PERMISOS PARA ELIMINACIÓN (Mantener - Esta vista está bien)


class ColaboradorPuedeEliminarMiembroMixin(UserPassesTestMixin):
    """
    Permite el acceso a la vista de eliminación si:
    1. El usuario solicitante es un Superusuario.
    2. El usuario solicitante es un Colaborador y el objeto a eliminar NO es:
        a) Otro Colaborador
        b) Un Superusuario
        c) El mismo usuario solicitante (auto-eliminación)
    """
    def test_func(self):
        solicitante = self.request.user
        usuario_a_eliminar = self.get_object() 
        
        # 1. Si es Superusuario, siempre puede (excepto auto-eliminarse, manejado abajo)
        if solicitante.is_superuser:
            return True

        # 2. Si el solicitante NO es Superusuario, debe ser un Colaborador para operar
        if not solicitante.groups.filter(name='Colaborador').exists():
            return False

        # 3. Lógica de seguridad para Colaboradores
        
        # Un Colaborador NO puede eliminarse a sí mismo
        if solicitante == usuario_a_eliminar:
            return False
            
        # Un Colaborador NO puede eliminar a un Superusuario
        if usuario_a_eliminar.is_superuser:
            return False

        # Un Colaborador NO puede eliminar a otro Colaborador (solo a Miembros)
        if usuario_a_eliminar.groups.filter(name='Colaborador').exists():
            return False
            
        # Si pasó todas las comprobaciones, es un Colaborador eliminando un Miembro
        return True
    
    def handle_no_permission(self):
        messages.error(self.request, "No tenés permiso para realizar esta acción. Solo puedes eliminar Miembros.")
        return redirect(reverse_lazy("usuarios:lista_usuarios"))



# VISTAS DE AUTENTICACIÓN EXISTENTES


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
        return render(request, self.template_name)

    def post(self, request):
        logout(request)
        messages.info(request, "Sesión cerrada exitosamente.")
        return redirect("index")



# VISTAS DE ADMINISTRACIÓN


class UsuarioListView(LoginRequiredMixin, UserPassesTestMixin, ListView): 
    """
    Muestra la lista de usuarios con paginación y ordenamiento.
    Restringido a usuarios Colaboradores o Superusuarios.
    """
    model = Usuario
    template_name = 'usuarios/lista_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 10 

    def test_func(self):
        user = self.request.user
        # Permite acceso si es superusuario o pertenece al grupo 'Colaborador'
        return user.is_superuser or user.groups.filter(name='Colaborador').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, "No tenés permisos para administrar usuarios.")
        return redirect("index")

    def get_queryset(self):
        # Excluir al usuario actual de la lista para prevenir auto-eliminación accidental
        queryset = super().get_queryset().exclude(pk=self.request.user.pk) 
        
        orden = self.request.GET.get('orden', 'username') 
        
        campos_permitidos = [
            'username', '-username', 
            'nombre', '-nombre', 
            'apellido', '-apellido', 
            'last_login', '-last_login',
            'groups__name', '-groups__name' 
        ]

        if orden in campos_permitidos:
            queryset = queryset.order_by(orden)

        # Usar prefetch_related para grupos y optimizar la consulta
        usuarios_list = queryset.prefetch_related('groups')
        
        # OBTENER EL USUARIO SOLICITANTE PARA CHEQUEAR PERMISOS
        solicitante = self.request.user
        es_super_o_colaborador = solicitante.is_superuser or solicitante.groups.filter(name='Colaborador').exists()
        
        # Iterar para adjuntar la bandera de permiso
        for user in usuarios_list:
            # Bandera que usaremos en la plantilla
            user.puede_ser_eliminado = False 
            
            # Solo si el solicitante tiene permisos de Colaborador/Admin, chequeamos la eliminación
            if es_super_o_colaborador:
                es_colaborador_a_eliminar = user.groups.filter(name='Colaborador').exists()
                
                # Un Colaborador/Admin puede eliminar si el usuario no es Superusuario y no es otro Colaborador
                # Como ya excluimos al usuario actual en el queryset, solo chequeamos Superusuario/Colaborador
                if not user.is_superuser and not es_colaborador_a_eliminar:
                    user.puede_ser_eliminado = True
                    
        return usuarios_list # Retorna la lista con la nueva propiedad 'puede_ser_eliminado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orden_actual'] = self.request.GET.get('orden', 'username')
        return context


class UsuarioDeleteView(LoginRequiredMixin, ColaboradorPuedeEliminarMiembroMixin, DeleteView):
    # ... (Esta vista se mantiene intacta) ...
    model = Usuario
    template_name = 'usuarios/eliminar_usuario.html'
    success_url = reverse_lazy('usuarios:lista_usuarios')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Verificar permisos antes de eliminar
        if not self.test_func():
            return self.handle_no_permission()

        messages.success(self.request, f"Usuario '{self.object.username}' eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)