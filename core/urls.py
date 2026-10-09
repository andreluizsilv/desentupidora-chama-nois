from django.contrib.auth import views as auth_views
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
        auth_views.LoginView.as_view(
            template_name='core/dashboard/login.html',
            redirect_authenticated_user=True
        ),
        name='dashboard_login'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
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