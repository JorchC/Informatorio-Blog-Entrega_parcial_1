from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class Usuario(AbstractUser):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    fecha_nacimiento = models.DateField("Fecha nacimiento", default='2000-1-1')
    es_colaborador = models.BooleanField("Es colaborador", default=False)
    imagen = models.ImageField(null=True, blank=True, upload_to='usuarios', default='usuarios/user_default.png')

    class Meta:
        ordering = ('-nombre',)

    def get_absolute_url(self):
        return reverse("index")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"