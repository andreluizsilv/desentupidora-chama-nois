from django.shortcuts import render

from .models import TrabalhoRealizado


def home(request):
    trabalhos = TrabalhoRealizado.objects.filter(
        publicado=True
    )[:3]

    context = {
        'trabalhos': trabalhos,
    }

    return render(
        request,
        'core/home.html',
        context
    )