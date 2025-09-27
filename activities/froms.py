from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import Activity, Category, User

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Votre nom d'utilisateur"
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Mot de passe"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')




        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Nom d'utilisateur ou mot de passe incorrect.")
        else:
            raise forms.ValidationError("Veuillez entrer à la fois le nom d'utilisateur et le mot de passe.")


    def save(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        return user



class RegisterForm(UserCreationForm):

    error_css_class = 'alert alert-danger'

    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        required=True,
        error_messages={
            'required': 'Veuillez entrer un nom d\'utilisateur.',
            'max_length': 'Le nom d\'utilisateur ne peut pas dépasser 150 caractères.'
        },
        widget=forms.TextInput(attrs={
            'placeholder': "ex: johndoe123"
        }),


    )


    email = forms.EmailField(
        label="Adresse courriel",
        required=True,
        error_messages={
            'required': 'Veuillez entrer votre adresse courriel.',
            'invalid': 'Veuillez entrer une adresse courriel valide.'
        },
        widget=forms.EmailInput(attrs={
            'placeholder': "ex: johndoe@example.com"
        })
    )


    first_name = forms.CharField(
        label="Prénom",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': "ex: John"
        })
    )

    last_name = forms.CharField(
        label="Nom de famille",
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': "ex: Doe"

        })
    )


    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')


        # Extra validation for username
        if username:  # Vérifier que username n'est pas None
            if len(username) < 3:
                self.add_error('username', 'Le nom d\'utilisateur doit contenir au moins 3 caractères.')
            if len(username) > 30:
                self.add_error('username', 'Le nom d\'utilisateur ne peut pas dépasser 30 caractères.')

        # Validation personnalisée pour l'adresse e-mail
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', 'Cette adresse e-mail est déjà utilisée.')


        # Validation personnalisée pour le prénom
        if first_name:
            if not first_name.isalpha():
                self.add_error('first_name', 'Le prénom ne peut contenir que des lettres.')

        # Validation personnalisée pour le nom de famille
        if last_name:
            if not last_name.isalpha():
                self.add_error('last_name', 'Le nom de famille ne peut contenir que des lettres.')

        return cleaned_data


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user



class ArticleSearchForm(forms.Form):
    # pylint: disable=no-member
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

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')

        # Validation de la catégorie : vérifier qu'elle existe dans les choix valides
        if category:
            valid_categories = [choice[0] for choice in self.fields['category'].choices]
            if category not in valid_categories:
                raise forms.ValidationError({
                    'category': f'La catégorie "{category}" n\'est pas valide. Veuillez choisir une catégorie dans la liste.'
                })

        return cleaned_data


class UserEditForm(forms.ModelForm):
    """
    Formulaire pour modifier le profil utilisateur.
    Permet de modifier : avatar, prénom, nom, email, biographie.
    Le username et mot de passe ne sont pas modifiables.
    """

    class Meta:
        model = User
        fields = ['avatar', 'first_name', 'last_name', 'email', 'bio']

        labels = {
            'avatar': 'Photo de profil',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse courriel',
            'bio': 'Biographie',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre prénom (optionnel)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom (optionnel)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre.email@exemple.com (optionnel)'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Parlez-nous un peu de vous, de vos intérêts et de vos activités préférées... (optionnel)'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'name': 'avatar',
                'id': 'avatar'
            })
        }

        error_messages = {
            'email': {
                'invalid': 'Veuillez entrer une adresse courriel valide.'
            },
            'first_name': {
                'max_length': 'Le prénom ne peut pas dépasser 30 caractères.'
            },
            'last_name': {
                'max_length': 'Le nom ne peut pas dépasser 150 caractères.'
            }
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Rendre tous les champs optionnels - seuls les champs modifiés seront validés
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['avatar'].required = False
        self.fields['bio'].required = False

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        bio = cleaned_data.get('bio')

        # Valider seulement les champs qui ont été remplis/modifiés
        if email and email.strip():
            # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
            if User.objects.filter(email=email).exclude(id=self.user.id).exists():
                self.add_error('email', 'Cette adresse courriel est déjà utilisée par un autre utilisateur.')

        if first_name and first_name.strip():
            if len(first_name.strip()) < 2:
                self.add_error('first_name', 'Le prénom doit contenir au moins 2 caractères.')
            # Validation : seulement des lettres et espaces
            if not first_name.strip().replace(' ', '').replace('-', '').isalpha():
                self.add_error('first_name', 'Le prénom ne peut contenir que des lettres, espaces et tirets.')

        if last_name and last_name.strip():
            if len(last_name.strip()) < 2:
                self.add_error('last_name', 'Le nom de famille doit contenir au moins 2 caractères.')
            # Validation : seulement des lettres et espaces
            if not last_name.strip().replace(' ', '').replace('-', '').isalpha():
                self.add_error('last_name', 'Le nom ne peut contenir que des lettres, espaces et tirets.')

        if bio and bio.strip() and len(bio.strip()) > 500:
            self.add_error('bio', 'La biographie ne peut pas dépasser 500 caractères.')

        return cleaned_data


    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Ne sauvegarder que les champs qui ont été modifiés (non vides)
        if commit:
            # Obtenir les données nettoyées
            cleaned_data = self.cleaned_data
            
            # Mise à jour sélective des champs
            if cleaned_data.get('first_name') and cleaned_data['first_name'].strip():
                user.first_name = cleaned_data['first_name'].strip()
            
            if cleaned_data.get('last_name') and cleaned_data['last_name'].strip():
                user.last_name = cleaned_data['last_name'].strip()
            
            if cleaned_data.get('email') and cleaned_data['email'].strip():
                user.email = cleaned_data['email'].strip()
            
            if cleaned_data.get('bio') is not None:  # Permettre de vider la bio
                user.bio = cleaned_data['bio'].strip() if cleaned_data['bio'] else ''
            
            # L'avatar est traité automatiquement par le ModelForm
            if 'avatar' in cleaned_data and cleaned_data['avatar']:
                user.avatar = cleaned_data['avatar']
            
            user.save()
        return user




class addNewActivity(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'description', 'location_city', 'start_time', 'end_time', 'category']
        labels = {
            'title': 'Titre de l\'activité',
            'description': 'Description',
            'location_city': 'Ville',
            'start_time': 'Date et heure de début',
            'end_time': 'Date et heure de fin',
            'category': 'Catégorie',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de l\'activité',
                'aria-describedby': 'id_title-help',
                'required': True,
                'minlength': '5',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de l\'activité',
                'aria-describedby': 'id_description-help',
                'required': True,
                'minlength': '10',
                'maxlength': '500'
            }),
            'location_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville où se déroule l\'activité',
                'required': True,
                'minlength': '2',
                'maxlength': '100'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'aria-describedby': 'id_start_time-help',
                'required': True
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'aria-describedby': 'id_end_time-help',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        description = cleaned_data.get('description')
        location_city = cleaned_data.get('location_city')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        category = cleaned_data.get('category')

        if title:
            if len(title) < 5:
                self.add_error('title', 'Le titre doit contenir au moins 5 caractères.')
            if len(title) > 200:
                self.add_error('title', 'Le titre ne peut pas dépasser 200 caractères.')

        if description:
            if len(description) < 10:
                self.add_error('description', 'La description doit contenir au moins 10 caractères.')
            if len(description) > 500:
                self.add_error('description', 'La description ne peut pas dépasser 500 caractères.')


        if location_city:
            if len(location_city) < 2:
                self.add_error('location_city', 'La ville doit contenir au moins 2 caractères.')
            if len(location_city) > 100:
                self.add_error('location_city', 'La ville ne peut pas dépasser 100 caractères.')

        if start_time and end_time:
            if start_time >= end_time:
                self.add_error('end_time', 'La date et l\'heure de fin doivent être après la date et l\'heure de début.')

        if not category:
            self.add_error('category', 'Veuillez sélectionner une catégorie.')

        return cleaned_data

    def save(self, commit=True):
        activity = super().save(commit=False)
        if commit:
            activity.save()
        return activity