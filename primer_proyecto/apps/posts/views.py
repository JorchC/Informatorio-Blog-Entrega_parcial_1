from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Importación necesaria

from .models import Post, Categoria, Comentario
from .forms import PostForm, CategoriaForm, ComentarioForm


# ==============================================================================
# MIXIN DE PERMISOS PARA COMENTARIOS (Autor O Colaborador)
# ==============================================================================

class Autor_o_ColaboradorMixin(UserPassesTestMixin):
    """
    Controla el acceso para la edición y eliminación de comentarios.
    Permite el acceso si:
    1. El usuario es el autor del comentario (Perfil Miembro o Colaborador)
    2. El usuario pertenece al grupo 'Colaborador' (puede editar comentarios de otros)
    """
    def test_func(self):
        user = self.request.user
        
        # El objeto (Comentario) se obtiene automáticamente.
        comentario = self.get_object() 

        es_autor = comentario.autor == user
        # La lógica de Colaborador es la pertenencia al grupo
        es_colaborador = user.groups.filter(name="Colaborador").exists() 
        
        # El usuario puede operar si es el autor O si es un Colaborador
        return es_autor or es_colaborador

    def handle_no_permission(self):
        # Manejo de error cuando no tiene permisos
        messages.error(self.request, "No tenés permisos para editar o eliminar este comentario.")
        
        # Redirige al detalle del post asociado
        try:
            comentario = self.get_object()
            return redirect('posts:detalle_post', pk=comentario.post.pk)
        except:
            return redirect('index') # Fallback


# ==============================================================================
# POSTS - ADMINISTRAR (SOLO COLABORADOR)
# ==============================================================================

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/lista_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para administrar posts.")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Post.objects.filter(autor=self.request.user).order_by("-publicado")


# ==============================================================================
# POSTS - DETALLE (PÚBLICO Y CARGA DE COMENTARIOS)
# ==============================================================================

class PostDetailView(DetailView):
    model = Post
    template_name = "posts/detalle_post.html"
    context_object_name = "post"

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasa una instancia nueva del formulario de comentario al contexto
        context['form_comentario'] = ComentarioForm()
        
        # FIX para TemplateSyntaxError: Pre-calcular la condición de Colaborador 
        # para que la plantilla pueda usarla con una simple variable.
        context['es_colaborador'] = False
        if self.request.user.is_authenticated:
            context['es_colaborador'] = self.request.user.groups.filter(name="Colaborador").exists()
            
        return context


    def post(self, request, *args, **kwargs):
        # Cargar: Sólo Usuarios Registrados (Miembros o Colaboradores)
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para publicar un comentario.")
            return redirect(reverse('posts:detalle_post', args=[self.get_object().pk])) 
            
        self.object = self.get_object() # Obtener el post
        form = ComentarioForm(request.POST)

        if form.is_valid():
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.post = self.object          # Asigna el post actual
            nuevo_comentario.autor = request.user        # Asigna el usuario autenticado
            nuevo_comentario.save()
            messages.success(request, "Comentario publicado correctamente.")
            
            # Redirige para evitar el doble envío (Patrón Post/Redirect/Get)
            return redirect(reverse('posts:detalle_post', args=[self.object.pk])) 

        # Si el formulario es inválido
        context = self.get_context_data()
        context['form_comentario'] = form # Pasar el formulario con errores
        messages.error(request, "El comentario no pudo ser publicado. Revisa los campos.")
        return self.render_to_response(context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/agregar_post.html"
    success_url = reverse_lazy("posts:lista_posts")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para crear artículos.")
            return redirect("posts:lista_posts")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        nuevo_post = form.save(commit=False)
        nuevo_post.autor = self.request.user
        nuevo_post.save()
        messages.success(self.request, "Artículo creado correctamente.")
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/editar_post.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para editar artículos.")
            return redirect("posts:lista_posts")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Artículo actualizado correctamente.")
        return reverse("posts:detalle_post", args=[self.object.pk])


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/eliminar_post.html"
    success_url = reverse_lazy("posts:lista_posts")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para eliminar artículos.")
            return redirect("posts:lista_posts")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Artículo eliminado correctamente.")
        return super().delete(request, *args, **kwargs)



# CATEGORÍAS - ADMINISTRAR (SOLO COLABORADOR)

class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "posts/categorias/lista_categorias.html"
    context_object_name = "categorias"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para administrar categorías.")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "posts/categorias/agregar_categoria.html"
    success_url = reverse_lazy("posts:lista_categorias")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para crear categorías.")
            return redirect("posts:lista_categorias")
        return super().dispatch(request, *args, **kwargs)


class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "posts/categorias/editar_categoria.html"
    success_url = reverse_lazy("posts:lista_categorias")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para editar categorías.")
            return redirect("posts:lista_categorias")
        return super().dispatch(request, *args, **kwargs)


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = "posts/categorias/eliminar_categoria.html"
    success_url = reverse_lazy("posts:lista_categorias")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para eliminar categorías.")
            return redirect("posts:lista_categorias")
        return super().dispatch(request, *args, **kwargs)



# POSTS POR CATEGORÍA (PÚBLICO)

class CategoriaPostsView(ListView):
    model = Post
    template_name = "posts/categorias/posts_por_categoria.html"
    context_object_name = "posts"
    paginate_by = 6 # es la cantidad de posts por página (lo haremos en 2 filas de 3 columnas)

    def get_queryset(self):
        return Post.objects.filter(
            categoria_id=self.kwargs["pk"],
            activo=True
        ).order_by("-publicado")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categoria"] = Categoria.objects.get(pk=self.kwargs["pk"])
        return context


# ==============================================================================
# COMENTARIOS - EDICIÓN Y ELIMINACIÓN (Autor O Colaborador)
# ==============================================================================

class ComentarioUpdateView(LoginRequiredMixin, Autor_o_ColaboradorMixin, UpdateView):
    model = Comentario
    fields = ['contenido'] # Solo permite editar el contenido
    template_name = 'posts/editar_comentario.html' 

    def get_success_url(self):
        # Redirige al detalle del post después de la edición
        return reverse_lazy('posts:detalle_post', kwargs={'pk': self.object.post.pk})

class ComentarioDeleteView(LoginRequiredMixin, Autor_o_ColaboradorMixin, DeleteView):
    model = Comentario
    template_name = 'posts/eliminar_comentario.html'

    def get_success_url(self):
        # Redirige al detalle del post después de la eliminación
        return reverse_lazy('posts:detalle_post', kwargs={'pk': self.object.post.pk})