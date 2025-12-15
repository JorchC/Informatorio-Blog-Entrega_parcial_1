from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Categoria
from .forms import PostForm, CategoriaForm



# POSTS - ADMINISTRAR (SOLO COLABORADOR)

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


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/detalle_post.html"
    context_object_name = "post"


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
    paginate_by = 3

    def get_queryset(self):
        return Post.objects.filter(
            categoria_id=self.kwargs["pk"],
            activo=True
        ).order_by("-publicado")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categoria"] = Categoria.objects.get(pk=self.kwargs["pk"])
        return context
