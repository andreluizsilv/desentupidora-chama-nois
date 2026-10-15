from django.urls import path

from . import views


app_name = 'core'


urlpatterns = [
    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'dashboard/login/',
        views.DashboardLoginView.as_view(),
        name='dashboard_login'
    ),

    path(
        'dashboard/aguardando-liberacao/',
        views.aguardando_liberacao,
        name='aguardando_liberacao'
    ),

    path(
        'avaliar/',
        views.nova_avaliacao,
        name='nova_avaliacao'
    ),

    path(
        'avaliar/agradecimento/',
        views.agradecimento_avaliacao,
        name='agradecimento_avaliacao'
    ),

    path(
        'dashboard/cadastro/',
        views.cadastro_usuario,
        name='cadastro_usuario'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'dashboard/usuarios/',
        views.gerenciar_usuarios,
        name='gerenciar_usuarios'
    ),

    path(
        'dashboard/avaliacoes/',
        views.gerenciar_avaliacoes,
        name='gerenciar_avaliacoes'
    ),

    path(
        'dashboard/avaliacoes/<int:avaliacao_id>/publicacao/',
        views.alterar_publicacao_avaliacao,
        name='alterar_publicacao_avaliacao'
    ),

    path(
        'dashboard/avaliacoes/<int:avaliacao_id>/excluir/',
        views.excluir_avaliacao,
        name='excluir_avaliacao'
    ),

    path(
        'dashboard/usuarios/<int:user_id>/acesso/',
        views.alterar_acesso_usuario,
        name='alterar_acesso_usuario'
    ),

    path(
        'dashboard/usuarios/<int:user_id>/excluir/',
        views.excluir_usuario,
        name='excluir_usuario'
    ),

    path(
        'dashboard/usuarios/<int:user_id>/editar/',
        views.editar_usuario,
        name='editar_usuario'
    ),

    path(
        'dashboard/logout/',
        views.dashboard_logout,
        name='dashboard_logout'
    ),

    path(
        'dashboard/novo_trabalho/',
        views.trabalhos,
        name='trabalhos'
    ),

    path(
        'dashboard/novo_trabalho/novo/',
        views.novo_trabalho,
        name='novo_trabalho'
    ),
]