from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import TrabalhoRealizadoForm
from .models import TrabalhoRealizado

def home(request):

    trabalhos = TrabalhoRealizado.objects.filter(
        publicado=True
    )

    context = {
        'trabalhos': trabalhos,
    }

    return render(
        request,
        'core/home.html',
        context
    )


@login_required(login_url='core:dashboard_login')
def dashboard(request):
    return render(
        request,
        'core/dashboard/dashboard.html'
    )


def dashboard_logout(request):
    logout(request)
    return redirect('core:dashboard_login')


@login_required(login_url='core:dashboard_login')
def trabalhos(request):

    trabalhos_cadastrados = TrabalhoRealizado.objects.all()

    context = {
        'trabalhos': trabalhos_cadastrados,
    }

    return render(
        request,
        'core/dashboard/trabalhos.html',
        context
    )


@login_required(login_url='core:dashboard_login')
def novo_trabalho(request):

    if request.method == 'POST':
        form = TrabalhoRealizadoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()

            return redirect('core:trabalhos')

    else:
        form = TrabalhoRealizadoForm()

    context = {
        'form': form,
    }

    return render(
        request,
        'core/dashboard/novo_trabalho.html',
        context
    )