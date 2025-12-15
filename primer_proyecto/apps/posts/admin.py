from django.contrib import admin
from .models import Categoria, Post, Comentario

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "autor", "publicado", "activo")
    list_filter = ("categoria", "activo", "publicado")
    search_fields = ("titulo", "subtitulo", "texto")


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("post", "autor", "creado")
    list_filter = ("creado", "autor")
