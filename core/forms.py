from django import forms

from .models import TrabalhoRealizado


class TrabalhoRealizadoForm(forms.ModelForm):

    class Meta:
        model = TrabalhoRealizado

        fields = [
            'titulo',
            'descricao',
            'arquivo_antes',
            'arquivo_depois',
            'publicado',
        ]

        widgets = {
            'titulo': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ex.: Desentupimento de caixa de gordura',
                }
            ),

            'descricao': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Descreva o serviço realizado...',
                }
            ),

            'arquivo_antes': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*,video/*',
                }
            ),

            'arquivo_depois': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*,video/*',
                }
            ),

            'publicado': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }