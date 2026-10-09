from django.core.exceptions import ValidationError
from pathlib import Path


EXTENSOES_PERMITIDAS = {
    '.jpg',
    '.jpeg',
    '.png',
    '.webp',
    '.mp4',
    '.webm',
    '.mov',
}

TAMANHO_MAXIMO_MB = 50


def validar_arquivo_midia(arquivo):
    extensao = Path(arquivo.name).suffix.lower()

    if extensao not in EXTENSOES_PERMITIDAS:
        raise ValidationError(
            'Formato não permitido. '
            'Envie uma imagem JPG, JPEG, PNG ou WEBP, '
            'ou um vídeo MP4, WEBM ou MOV.'
        )

    tamanho_maximo = TAMANHO_MAXIMO_MB * 1024 * 1024

    if arquivo.size > tamanho_maximo:
        raise ValidationError(
            f'O arquivo não pode ultrapassar '
            f'{TAMANHO_MAXIMO_MB} MB.'
        )