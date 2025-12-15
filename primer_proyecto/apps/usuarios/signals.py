from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver

@receiver(post_migrate)
def crear_roles(sender, **kwargs):
    
    if sender.name != 'apps.usuarios':
        return

    
    miembro, created = Group.objects.get_or_create(name='Miembro')
    colaborador, created = Group.objects.get_or_create(name='Colaborador')

    
    permisos_colaborador = [
        'add_post', 'change_post', 'delete_post',
        'add_categoria', 'change_categoria', 'delete_categoria',
        'delete_comentario'
    ]

    for codename in permisos_colaborador:
        try:
            permiso = Permission.objects.get(codename=codename)
            colaborador.permissions.add(permiso)
        except Permission.DoesNotExist:
            pass  # se creará cuando migraciones estén completas
