from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    CategoriaListView,
    CategoriaCreateView,
    CategoriaUpdateView,
    CategoriaDeleteView,
    CategoriaPostsView,
)

app_name = "posts"

urlpatterns = [
    
    # POSTS (ADMIN COLABORADOR)
    
    path("", PostListView.as_view(), name="lista_posts"),
    path("agregar/", PostCreateView.as_view(), name="agregar_post"),
    path("editar/<int:pk>/", PostUpdateView.as_view(), name="editar_post"),
    path("eliminar/<int:pk>/", PostDeleteView.as_view(), name="eliminar_post"),

    # Detalle (lo dejo disponible como lo tenías)
    path("<int:pk>/", PostDetailView.as_view(), name="detalle_post"),


    
    # CATEGORÍAS (ADMIN COLABORADOR)
    
    path("categorias/", CategoriaListView.as_view(), name="lista_categorias"),
    path("categorias/agregar/", CategoriaCreateView.as_view(), name="agregar_categoria"),
    path("categorias/editar/<int:pk>/", CategoriaUpdateView.as_view(), name="editar_categoria"),
    path("categorias/eliminar/<int:pk>/", CategoriaDeleteView.as_view(), name="eliminar_categoria"),

    
    # POSTS POR CATEGORÍA (PÚBLICO)
    
    path("categoria/<int:pk>/", CategoriaPostsView.as_view(), name="posts_por_categoria"),
]
