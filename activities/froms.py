from django import forms
from .models import User


class CustomAuthenticationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        labels = {
            'username': 'Nom d\'utilisateur',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
        }
        help_texts = {
            'username': 'Entrez votre nom d\'utilisateur.',
        }
        error_messages = {
            'username': {
                'required': 'Le nom d\'utilisateur est requis.',
                'invalid': 'Entrez un nom d\'utilisateur valide.',
            },
        }