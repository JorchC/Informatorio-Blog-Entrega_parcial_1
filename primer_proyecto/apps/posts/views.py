from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 

from .models import Post, Categoria, Comentario
from .forms import PostForm, CategoriaForm, ComentarioForm



# MIXIN DE PERMISOS PARA COMENTARIOS (Autor O Colaborador)


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
        messages.error(self.request, "No tenés permisos para editar o eliminar este comentario.")
        try:
            comentario = self.get_object()
            # Redirige al detalle del post asociado al comentario
            return redirect('posts:detalle_post', pk=comentario.post.pk)
        except:
            return redirect('index')



# POSTS - ADMINISTRAR (SOLO COLABORADOR) 


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/lista_posts.html"
    context_object_name = "posts"
    paginate_by = 10 # Cantidad de posts por página en el administrador

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para administrar posts.")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # 1. Base del Queryset: Mostrar solo los posts del usuario colaborador actual
        queryset = Post.objects.filter(autor=self.request.user)
        
        # 2. Obtener parámetros de filtrado y ordenamiento de la URL
        orden = self.request.GET.get('orden', '-publicado') # Por defecto: Reciente a Antiguo
        categoria_id = self.request.GET.get('categoria', None)

        # 3. Aplicar Filtro por Categoría
        if categoria_id and categoria_id != 'todas':
            try:
                # Filtrar por el ID de la categoría
                queryset = queryset.filter(categoria_id=int(categoria_id))
            except ValueError:
                pass # Ignorar si el ID no es un número válido
        
        # 4. Aplicar Ordenamiento
        # Las opciones en el template son: '-titulo', 'titulo', '-publicado', 'publicado'
        if orden in ['-titulo', 'titulo', '-publicado', 'publicado']:
            queryset = queryset.order_by(orden)
        else:
             # Si el parámetro es inválido, usar el orden por defecto
            queryset = queryset.order_by('-publicado')

        # Usar select_related para optimizar la consulta
        return queryset.select_related('categoria', 'autor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pasar todas las categorías al contexto para el menú desplegable de filtro
        context['categorias'] = Categoria.objects.all().order_by('nombre')
        
        # Pasar los valores de filtro y ordenamiento actuales al contexto
        context['orden_actual'] = self.request.GET.get('orden', '-publicado')
        context['categoria_actual_id'] = self.request.GET.get('categoria', 'todas')
        
        return context


# POSTS - VISTAS CRUD


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/detalle_post.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 1. Agrega el formulario de comentarios
        context["form"] = ComentarioForm()
        # 2. Pre-calcula si el usuario es colaborador (para la edición de comentarios)
        user = self.request.user
        context["es_colaborador"] = user.groups.filter(name="Colaborador").exists()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/agregar_post.html"
    success_url = reverse_lazy("posts:lista_posts")

    def form_valid(self, form):
        # Asigna el autor (usuario logueado) antes de guardar el post
        form.instance.autor = self.request.user
        messages.success(self.request, "Artículo publicado exitosamente.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Colaborador").exists():
            messages.error(request, "No tenés permisos para crear posts.")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/editar_post.html"
    
    def get_success_url(self):
        # Redirige al detalle del post después de la edición
        messages.success(self.request, "Artículo actualizado exitosamente.")
        return reverse_lazy("posts:detalle_post", kwargs={"pk": self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().autor != self.request.user:
            messages.error(request, "No tenés permisos para editar este post.")
            return redirect("posts:lista_posts")
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/eliminar_post.html"
    success_url = reverse_lazy("posts:lista_posts")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().autor != self.request.user:
            messages.error(request, "No tenés permisos para eliminar este post.")
            return redirect("posts:lista_posts")
        return super().dispatch(request, *args, **kwargs)



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
    # Se actualizó a 6 posts para mostrar 2 filas de 3
    paginate_by = 6 

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

class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm
    template_name = "posts/agregar_comentario.html" # No se usa realmente

    def form_valid(self, form):
        # 1. Asigna el autor (usuario logueado)
        form.instance.autor = self.request.user
        # 2. Asigna el post al que pertenece el comentario
        pk_post = self.kwargs.get('pk_post')
        post = get_object_or_404(Post, pk=pk_post)
        form.instance.post = post
        
        return super().form_valid(form)

    def get_success_url(self):
        # Redirige al detalle del post después de crear el comentario
        messages.success(self.request, "Comentario publicado exitosamente.")
        # La PK del post es la que se pasó en los kwargs
        return reverse_lazy('posts:detalle_post', kwargs={'pk': self.kwargs.get('pk_post')})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para comentar.")
            return redirect('usuarios:login')
        return super().dispatch(request, *args, **kwargs)


class ComentarioUpdateView(LoginRequiredMixin, Autor_o_ColaboradorMixin, UpdateView):
    model = Comentario
    fields = ['contenido'] # Solo permite editar el contenido
    template_name = 'posts/editar_comentario.html' 

    def get_success_url(self):
        # Redirige al detalle del post después de la edición
        messages.success(self.request, "Comentario actualizado exitosamente.")
        return reverse_lazy('posts:detalle_post', kwargs={'pk': self.object.post.pk})

class ComentarioDeleteView(LoginRequiredMixin, Autor_o_ColaboradorMixin, DeleteView):
    model = Comentario
    template_name = 'posts/eliminar_comentario.html'

    def get_success_url(self):
        # Redirige al detalle del post después de la eliminación
        messages.success(self.request, "Comentario eliminado exitosamente.")
        return reverse_lazy('posts:detalle_post', kwargs={'pk': self.object.post.pk})