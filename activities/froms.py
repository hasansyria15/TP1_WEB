from django import forms
from .models import User, Category


class CustomAuthenticationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            'username': 'Nom d\'utilisateur',
            'password': 'Mot de passe',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        }
        help_texts = {
            'username': 'Entrez votre nom d\'utilisateur.',
            'password': 'Entrez votre mot de passe.',
        }
        error_messages = {
            'username': {
                'required': 'Le nom d\'utilisateur est requis.',
                'invalid': 'Entrez un nom d\'utilisateur valide.',
            },
        }

class ArticleSearchForm(forms.Form):

    option = Category.objects.all().values_list('name', 'name')

    category = forms.ChoiceField(
        choices=[
            ('all', 'Toutes les activités'),
        ] + list(option),
        label="Catégorie",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()' 
        })
    )

        
