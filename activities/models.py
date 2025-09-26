from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
import os


def validate_avatar_extension(value):
    """Valide l'extension du fichier avatar"""
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'Type de fichier non autorisé: {ext}. Utilisez JPG, PNG, GIF ou WebP.')


def validate_avatar_size(value):
    """Valide la taille de l'avatar (2MB max)"""
    filesize = value.size
    if filesize > 2 * 1024 * 1024:  # 2MB
        raise ValidationError('L\'image est trop volumineuse (2MB maximum)')


def avatar_upload_path(instance, filename):
    """Génère un chemin de téléversement organisé par utilisateur"""
    # Garder l'extension originale
    ext = os.path.splitext(filename)[1]
    # Créer un nom de fichier basé sur l'ID utilisateur
    new_filename = f"avatar_{instance.username}{ext}"
    return f'avatars/{instance.id}/{new_filename}'


# ------------------------------
# Model User
#------------------------------
class User(AbstractUser):

    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        help_text="Téléchargez une image pour votre avatar (JPG, PNG, GIF ou WebP - 2MB max)",
        validators=[validate_avatar_extension, validate_avatar_size]
    )
    bio = models.TextField(
        verbose_name="Biographie",
        blank=True,
        null=True,
        help_text="Parlez-nous un peu de vous (optionnel).",
        max_length=500
    )

    class Meta:
        ordering = ['username']
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"



    def __str__(self):
        return f" {self.username} ({self.first_name} {self.last_name})"


# ------------------------------
# Model Category
#------------------------------
class Category(models.Model):
    """Modèle représentant une catégorie d'activité."""
    name = models.CharField(
        verbose_name="Nom de la catégorie",
        unique=True,
        max_length=100,
        blank=False,
        null=False,
        error_messages= {
            'unique': "Une catégorie avec ce nom existe déjà.",
            'blank': "Le nom de la catégorie ne peut pas être vide.",
            'max_length': "Le nom de la catégorie ne peut pas dépasser 100 caractères.",
        }
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return str(self.name)


# ------------------------------
# Model Activity
#------------------------------
class Activity(models.Model):
    title = models.CharField(
        verbose_name="Titre",
        blank=False,
        null=False,
       validators=[
              MinLengthValidator(5, "Le titre doit contenir au moins 5 caractères."),
              MaxLengthValidator(200, "Le titre doit contenir au plus 200 caractères.")

       ],
       error_messages={
           'blank': "Le titre ne peut pas être vide.",

       }

    )
    description = models.TextField(
            verbose_name="Description",
            blank=False,
            null=False,
            validators=[
                MinLengthValidator(10, "La description doit contenir au moins 10 caractères.")
            ],
            error_messages={
                'blank': "La description ne peut pas être vide.",
            }
        )
    location_city = models.CharField(
            verbose_name="Ville",
            max_length=100,
            validators=[
                MinLengthValidator(2, "La ville doit contenir au moins 2 caractères."),
            ],
            error_messages={
                'blank': "La ville ne peut pas être vide.",
                'max_length': "La ville ne peut pas dépasser 100 caractères.",
            }
        )
    start_time = models.DateTimeField(
            verbose_name="Date et heure de début",
            error_messages={
                'required': "La date et l'heure de début sont requises.",
            }
        )
    end_time = models.DateTimeField(
            verbose_name="Date et heure de fin",

            error_messages={
                'required': "La date et l'heure de fin sont requises.",
            }
        )
    proposer = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='proposed_activities',
            verbose_name="Organisateur",

        )
    attendees = models.ManyToManyField(
            User,
            related_name='attended_activities',
            blank=True,
            verbose_name="Participants",
        )
    category = models.ForeignKey(
            Category,
            related_name='activities',
            verbose_name="Catégorie",
            on_delete=models.SET_NULL,
            null=True,
        )

    class Meta:
        ordering = ['start_time']
        verbose_name = "Activité"
        verbose_name_plural = "Activités"

    # Validation personnalisée pour s'assurer que end_time est après start_time
    def clean(self):

        # Appeler la méthode clean du parent pour s'assurer que les validations par défaut sont effectuées
        super().clean()

        # Initialiser un dictionnaire pour collecter les erreurs
        errors = {}

        # Valider les dates
        if self.end_time <= self.start_time:
            errors['end_time'] = "L'heure de fin doit être après l'heure de début."

        if self.start_time < timezone.now():
            errors['start_time'] = "L'heure de début doit être dans le futur."

        # Si des erreurs ont été détectées, les lever
        if errors:
            raise ValidationError(errors)

    # Appeler la méthode clean pour valider avant de sauvegarder
    def save(self, *args, **kwargs):

        self.clean()
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('activity_detail', kwargs={'pk': self.pk})