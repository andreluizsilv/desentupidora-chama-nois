from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Avaliacao, TrabalhoRealizado


class DashboardAuthenticationForm(AuthenticationForm):
    pending_access = False

    def clean(self):
        try:
            return super().clean()
        except forms.ValidationError:
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            if username and password:
                user_model = get_user_model()
                try:
                    usuario = (
                        user_model._default_manager.get_by_natural_key(
                            username
                        )
                    )
                except user_model.DoesNotExist:
                    raise

                if not usuario.is_active and usuario.check_password(password):
                    self.pending_access = True

            raise


class CadastroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'email',
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'username',
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        user_model = get_user_model()

        if user_model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Já existe uma conta cadastrada com este e-mail.'
            )

        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.is_active = False

        if commit:
            usuario.save()
            self.save_m2m()

        return usuario


class AvaliacaoForm(forms.ModelForm):
    comentario = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 5,
                'maxlength': 2000,
                'placeholder': 'Conte como foi sua experiência...',
            }
        ),
        label='Sua avaliação',
    )
    nota = forms.TypedChoiceField(
        choices=(
            (5, '5 estrelas - Excelente'),
            (4, '4 estrelas - Muito bom'),
            (3, '3 estrelas - Bom'),
            (2, '2 estrelas'),
            (1, '1 estrela'),
        ),
        coerce=int,
        widget=forms.RadioSelect(attrs={'class': 'star-rating-input'}),
        label='Sua nota',
    )

    class Meta:
        model = Avaliacao
        fields = ('nome_cliente', 'nota', 'comentario')
        widgets = {
            'nome_cliente': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'name',
                    'maxlength': 120,
                }
            ),
        }
        labels = {
            'nome_cliente': 'Seu nome',
            'comentario': 'Sua avaliação',
        }

    def clean_nome_cliente(self):
        return self.cleaned_data['nome_cliente'].strip()

    def clean_comentario(self):
        return self.cleaned_data['comentario'].strip()


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
        }


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