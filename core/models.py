from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validar_arquivo_midia


class TrabalhoRealizado(models.Model):
    titulo = models.CharField(
        max_length=150,
        verbose_name='Título'
    )

    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )

    arquivo_antes = models.FileField(
        upload_to='trabalhos/antes/',
        validators=[validar_arquivo_midia],
        blank=True,
        null=True,
        verbose_name='Foto ou vídeo antes'
    )

    arquivo_depois = models.FileField(
        upload_to='trabalhos/depois/',
        validators=[validar_arquivo_midia],
        blank=True,
        null=True,
        verbose_name='Foto ou vídeo depois'
    )

    publicado = models.BooleanField(
        default=True,
        verbose_name='Publicado'
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Trabalho realizado'
        verbose_name_plural = 'Trabalhos realizados'
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo

    @property
    def antes_eh_video(self):
        if not self.arquivo_antes:
            return False

        return self.arquivo_antes.name.lower().endswith(
            ('.mp4', '.webm', '.mov')
        )

    @property
    def depois_eh_video(self):
        if not self.arquivo_depois:
            return False

        return self.arquivo_depois.name.lower().endswith(
            ('.mp4', '.webm', '.mov')
        )


class Avaliacao(models.Model):
    nome_cliente = models.CharField(
        max_length=120,
        verbose_name='Nome do cliente'
    )

    nota = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name='Nota'
    )

    comentario = models.TextField(
        verbose_name='Comentário'
    )

    publicado = models.BooleanField(
        default=False,
        verbose_name='Publicado'
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome_cliente} - {self.nota} estrelas'