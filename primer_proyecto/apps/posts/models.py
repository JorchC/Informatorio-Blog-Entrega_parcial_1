from django.db import models
from django.utils import timezone
from django.conf import settings

########### MODELO CATEGORÍA (sirve para clasificación del Posts)
########### MODELO CATEGORÍA (sirve para clasificación del Posts)
########### MODELO CATEGORÍA (sirve para clasificación del Posts)

'''Creamos la clase “Categoria”, que representa una clasificación temática para 
los artículos del blog.'''

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True, null=False)
    
    ''' nombre: será el nombre identificatorio de una categoría.
    - max_length=50 → longitud máxima del texto
    - unique=True → evita categorías duplicadas
    - null=False → siempre debe existir un nombre'''

    def __str__(self):
        return self.nombre



# MODELO: POST (ARTÍCULO DEL BLOG)
# MODELO: POST (ARTÍCULO DEL BLOG)
# MODELO: POST (ARTÍCULO DEL BLOG)


''' La clase “Post” son los artículos/publicaciones que son creadas por 
los usuarios colaboradores.
Cada Post tiene que poseer un: título, subtítulo, una categoría, imagen, 
texto (que es el contenido),fecha de publicación, autor '''

class Post(models.Model):

    # título
    titulo = models.CharField(max_length=100, null=False)

    # Subtítulo (opcional)
    subtitulo = models.CharField(max_length=150, null=True, blank=True)

    # contenido / texto del post / artículo / etc...
    texto = models.TextField(null=False)

    # Imagen
    imagen = models.ImageField(null=True, blank=True, upload_to='posts', default='posts/post_default.png')
    
    '''- upload_to='posts' guarda las imágenes en /media/posts/
    - default: si no se carga ninguna imagen uso la de post_default.png'''

    # Fecha de creación del post
    creado = models.DateTimeField(auto_now_add=True)
    '''auto_now_add=True: Django coloca automáticamente la fecha/hora actual
      cuando se crea el post. (quiero que quede guardada pero no publicada)'''

    # Fecha de publicación
    publicado = models.DateTimeField(default=timezone.now)
    '''Esta fecha va a ser modificada y vamos a usar para ordenar/filtrar los artículos por fecha'''

    # Campo booleano para activar/desactivar un post
    activo = models.BooleanField(default=True)


    # RELACIONES: Relación POST con CATEGORÍA  # OJO / CUIDADO!!!
        
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    
    '''on_delete=models.SET_NULL:si elimino una categoría, no se tienen que eliminar }
      los posts, sino que quedan sin categoría (asignada digamos).'''


    # RELACIONES: Relación POST con AUTOR  # OJO / CUIDADO!!!

    autor = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    '''Un autor puede tener muchos posts, pero un post puede tener un solo autor,
    on_delete=models.CASCADE: Si un autor es eliminado, se eliminan todos los post que creó de manera automática'''

    # ORDEN DE POSTS:

    class Meta:
        ordering = ('-publicado',)

    def __str__(self):
        return self.titulo

    # Eliminación de la imagen asociada al posts
    def delete(self, using=None, keep_parents=False):
        if self.imagen:
            self.imagen.delete(save=False)
        super().delete(using=using, keep_parents=keep_parents)
'''verifica si el post tiene una imagen asociada y la elimina'''





# MODELO: COMENTARIO
# MODELO: COMENTARIO
# MODELO: COMENTARIO
'''Son los comentarios de los usuarios a los Post (1)'''


class Comentario(models.Model):

    post = models.ForeignKey( Post, related_name='comentarios', on_delete=models.CASCADE)
    
    ''' Un Post puede tener muchos comentarios, pero un comentario pertenece 
    solo a Un Post.
    on_delete=models.CASCADE, hace que si se borra un post, se eliminen todos los comentarios automaticamente    '''

    autor = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ''' El comentario pertenece a un usuario registrado. si se elimina el usuario, se eliminan sus comentarios'''

    contenido = models.TextField(null=False)
    ''' Texto del comentario.'''

    creado = models.DateTimeField(auto_now_add=True)
    '''Fecha de creación automática del comentario.'''

    class Meta:
        ordering = ('-creado',)
        '''Los comentarios se ordenan desde el mas reciente al mas antiguo'''

    def __str__(self):
        return f"Comentario de {self.autor} en {self.post.titulo}"
