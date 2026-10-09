from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TrabalhoRealizado(models.Model):
    titulo = models.CharField(
        max_length=150,
        verbose_name='Título'
    )

    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )

    foto_antes = models.ImageField(
        upload_to='trabalhos/antes/',
        blank=True,
        null=True,
        verbose_name='Foto antes'
    )

    foto_depois = models.ImageField(
        upload_to='trabalhos/depois/',
        blank=True,
        null=True,
        verbose_name='Foto depois'
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
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome_cliente} - {self.nota} estrelas'