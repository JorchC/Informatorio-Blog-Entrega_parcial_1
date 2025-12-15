from django.views.generic import TemplateView
from apps.posts.models import Post


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Mostrar posts activos, más recientes primero
        context["posts"] = (
            Post.objects
            .filter(activo=True)
            .order_by("-publicado")
        )

        return context
