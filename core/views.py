from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    AvaliacaoForm,
    CadastroUsuarioForm,
    DashboardAuthenticationForm,
    EditarUsuarioForm,
    TrabalhoRealizadoForm,
)
from .models import Avaliacao, TrabalhoRealizado


WORK_MANAGER_GROUP = 'Gerenciador de trabalhos'


class DashboardLoginView(auth_views.LoginView):
    form_class = DashboardAuthenticationForm
    template_name = 'core/dashboard/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        if form.pending_access:
            return redirect('core:aguardando_liberacao')
        return super().form_invalid(form)

    def form_valid(self, form):
        usuario = form.get_user()
        if (
            not usuario.is_superuser
            and not usuario.has_perm('core.view_trabalhorealizado')
        ):
            return redirect('core:aguardando_liberacao')
        return super().form_valid(form)


def home(request):
    return render(
        request,
        'core/home.html',
        {
            'trabalhos': TrabalhoRealizado.objects.filter(publicado=True),
            'avaliacoes': Avaliacao.objects.filter(publicado=True)[:6],
        },
    )


def nova_avaliacao(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:agradecimento_avaliacao')
    else:
        form = AvaliacaoForm()

    return render(
        request,
        'core/avaliacao_form.html',
        {'form': form},
    )


def agradecimento_avaliacao(request):
    return render(
        request,
        'core/agradecimento_avaliacao.html',
    )


def cadastro_usuario(request):
    is_superadmin = (
        request.user.is_authenticated and request.user.is_superuser
    )
    if request.user.is_authenticated and not is_superadmin:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                (
                    f'A conta de {form.instance.username} foi criada e '
                    'está pendente de liberação.'
                    if is_superadmin else
                    'Sua conta foi criada. O acesso ao dashboard depende da '
                    'liberação do SuperAdmin.'
                ),
            )
            if is_superadmin:
                return redirect('core:gerenciar_usuarios')
            return redirect('core:aguardando_liberacao')
    else:
        form = CadastroUsuarioForm()

    return render(
        request,
        'core/dashboard/cadastro.html',
        {
            'form': form,
            'is_superadmin': is_superadmin,
        },
    )


def aguardando_liberacao(request):
    return render(
        request,
        'core/dashboard/aguardando_liberacao.html',
    )


@login_required(login_url='core:dashboard_login')
@permission_required(
    'core.view_trabalhorealizado',
    raise_exception=True
)
def dashboard(request):
    context = {
        'trabalhos_count': TrabalhoRealizado.objects.count(),
    }
    if request.user.is_superuser:
        grupo_admin = get_object_or_404(Group, name=WORK_MANAGER_GROUP)
        context['usuarios_count'] = grupo_admin.user_set.filter(
            is_active=True
        ).count()
    if request.user.has_perm('core.view_avaliacao'):
        context['avaliacoes_pendentes_count'] = Avaliacao.objects.filter(
            publicado=False
        ).count()

    return render(
        request,
        'core/dashboard/dashboard.html',
        context
    )


@login_required(login_url='core:dashboard_login')
@permission_required('core.view_avaliacao', raise_exception=True)
def gerenciar_avaliacoes(request):
    return render(
        request,
        'core/dashboard/avaliacoes.html',
        {
            'avaliacoes': Avaliacao.objects.all(),
            'avaliacoes_pendentes_count': Avaliacao.objects.filter(
                publicado=False
            ).count(),
        },
    )


@login_required(login_url='core:dashboard_login')
@permission_required('core.change_avaliacao', raise_exception=True)
@require_POST
def alterar_publicacao_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    action = request.POST.get('action')

    if action == 'publish':
        avaliacao.publicado = True
        message = f'A avaliação de {avaliacao.nome_cliente} foi publicada.'
    elif action == 'hide':
        avaliacao.publicado = False
        message = f'A avaliação de {avaliacao.nome_cliente} foi ocultada.'
    else:
        messages.error(request, 'Ação de publicação inválida.')
        return redirect('core:gerenciar_avaliacoes')

    avaliacao.save(update_fields=['publicado', 'atualizado_em'])
    messages.success(request, message)
    return redirect('core:gerenciar_avaliacoes')


@login_required(login_url='core:dashboard_login')
@permission_required('core.delete_avaliacao', raise_exception=True)
@require_POST
def excluir_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    nome_cliente = avaliacao.nome_cliente
    avaliacao.delete()
    messages.success(
        request,
        f'A avaliação de {nome_cliente} foi excluída permanentemente.',
    )
    return redirect('core:gerenciar_avaliacoes')


@require_POST
def dashboard_logout(request):
    logout(request)
    return redirect('core:dashboard_login')


@login_required(login_url='core:dashboard_login')
@permission_required(
    'core.view_trabalhorealizado',
    raise_exception=True
)
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
@permission_required(
    'core.add_trabalhorealizado',
    raise_exception=True
)
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


@login_required(login_url='core:dashboard_login')
def gerenciar_usuarios(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    grupo_admin = get_object_or_404(Group, name=WORK_MANAGER_GROUP)
    usuarios = get_user_model().objects.order_by('username')
    usuarios_com_acesso = set(
        grupo_admin.user_set.values_list('id', flat=True)
    )

    return render(
        request,
        'core/dashboard/usuarios.html',
        {
            'usuarios': usuarios,
            'usuarios_com_acesso': usuarios_com_acesso,
        },
    )


@login_required(login_url='core:dashboard_login')
@require_POST
def alterar_acesso_usuario(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    usuario = get_object_or_404(get_user_model(), pk=user_id)
    if usuario.is_superuser:
        raise PermissionDenied

    grupo_admin = get_object_or_404(Group, name=WORK_MANAGER_GROUP)
    action = request.POST.get('action')

    if action == 'grant':
        usuario.is_active = True
        usuario.save(update_fields=['is_active'])
        grupo_admin.user_set.add(usuario)
        messages.success(
            request,
            f'Acesso ao dashboard liberado para {usuario.username}.',
        )
    elif action == 'revoke':
        grupo_admin.user_set.remove(usuario)
        usuario.is_active = False
        usuario.save(update_fields=['is_active'])
        messages.success(
            request,
            f'Acesso de {usuario.username} removido e conta desativada.',
        )
    else:
        messages.error(request, 'Ação de acesso inválida.')

    return redirect('core:gerenciar_usuarios')


@login_required(login_url='core:dashboard_login')
@require_POST
def excluir_usuario(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    usuario = get_object_or_404(get_user_model(), pk=user_id)
    if usuario.is_superuser or usuario.pk == request.user.pk:
        raise PermissionDenied

    username = usuario.username
    usuario.delete()
    messages.success(
        request,
        f'A conta de {username} foi excluída permanentemente.',
    )
    return redirect('core:gerenciar_usuarios')


@login_required(login_url='core:dashboard_login')
def editar_usuario(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    usuario = get_object_or_404(get_user_model(), pk=user_id)
    if usuario.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Os dados de {usuario.username} foram atualizados.',
            )
            return redirect('core:gerenciar_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(
        request,
        'core/dashboard/editar_usuario.html',
        {
            'form': form,
            'usuario': usuario,
        },
    )