def categorias_nav(request):
    from .models import Categoria   # Import diferido
    return {
        "categorias_menu": Categoria.objects.all()
    }