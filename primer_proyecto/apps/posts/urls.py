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
    ComentarioCreateView, 
    ComentarioUpdateView,
    ComentarioDeleteView,
)

app_name = "posts"

urlpatterns = [
    
    # POSTS (ADMIN COLABORADOR)
    
    path("", PostListView.as_view(), name="lista_posts"),
    path("agregar/", PostCreateView.as_view(), name="agregar_post"),
    path("editar/<int:pk>/", PostUpdateView.as_view(), name="editar_post"),
    path("eliminar/<int:pk>/", PostDeleteView.as_view(), name="eliminar_post"),

    # Detalle del Post (PÚBLICO)
    path("<int:pk>/", PostDetailView.as_view(), name="detalle_post"),


    # CATEGORÍAS (ADMIN COLABORADOR)
    
    path("categorias/", CategoriaListView.as_view(), name="lista_categorias"),
    path("categorias/agregar/", CategoriaCreateView.as_view(), name="agregar_categoria"),
    path("categorias/editar/<int:pk>/", CategoriaUpdateView.as_view(), name="editar_categoria"),
    path("categorias/eliminar/<int:pk>/", CategoriaDeleteView.as_view(), name="eliminar_categoria"),

    
    # POSTS POR CATEGORÍA (PÚBLICO)
    
    path("categoria/<int:pk>/", CategoriaPostsView.as_view(), name="posts_por_categoria"),
    
    
    # COMENTARIOS
    # Recibe el pk del post y llama a la vista de creación de comentarios
    path("post/<int:pk_post>/comentar/", ComentarioCreateView.as_view(), name="agregar_comentario"), 
    # Reciben el pk del comentario a editar/eliminar
    path("comentario/editar/<int:pk>/", ComentarioUpdateView.as_view(), name="editar_comentario"),
    path("comentario/eliminar/<int:pk>/", ComentarioDeleteView.as_view(), name="eliminar_comentario"),
]