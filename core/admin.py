from django.contrib import admin

from .models import Avaliacao, TrabalhoRealizado


@admin.register(TrabalhoRealizado)
class TrabalhoRealizadoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'publicado',
        'criado_em',
        'atualizado_em',
    )

    list_filter = (
        'publicado',
        'criado_em',
    )

    search_fields = (
        'titulo',
        'descricao',
    )


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        'nome_cliente',
        'nota',
        'publicado',
        'criado_em',
    )

    list_filter = (
        'nota',
        'publicado',
        'criado_em',
    )

    search_fields = (
        'nome_cliente',
        'comentario',
    )