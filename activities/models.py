from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError

class User(AbstractUser):

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        verbose_name="Biographie",
        blank=True,
        null=True,
        help_text="Une courte biographie de l'utilisateur.",
        validators=[MaxLengthValidator(500, "La biographie ne peut pas dépasser 500 caractères.")]
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f" {self.username} ({self.first_name} {self.last_name})"


class Category(models.Model):
    """Modèle représentant une catégorie d'activité."""
    name = models.CharField(
        verbose_name="Nom de la catégorie",
        unique=True,
        null=False,
        blank=False,
        help_text="Titre de la catégorie.",
        max_length=100,
        validators=[
            MinLengthValidator(3, "Le titre doit contenir au moins 3 caractères."),
            MaxLengthValidator(100, "Le titre doit contenir au plus 100 caractères.")
        ]
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return str(self.name)


class Activity(models.Model):
    title = models.CharField(
        verbose_name="Titre",
        max_length=200,
       validators=[
              MinLengthValidator(5, "Le titre doit contenir au moins 5 caractères."),
              MaxLengthValidator(100, "Le titre doit contenir au plus 100 caractères.")
       ]
    )
    description = models.TextField(
            verbose_name="Description",
            validators = [
                MinLengthValidator(10, "La description doit contenir au moins 10 caractères.")
            ]
        )
    location_city = models.CharField(
            verbose_name="Ville",
            max_length=100,
            validators=[
                MinLengthValidator(2, "La ville doit contenir au moins 2 caractères."),
                MaxLengthValidator(100, "La ville doit contenir au plus 100 caractères.")
            ]
        )
    start_time = models.DateTimeField(
            verbose_name="Heure de début",
            help_text="l'heure de début de l'activité.",
            default=timezone.now
        )
    end_time = models.DateTimeField(
            verbose_name="Heure de fin",
            help_text="l'heure de fin de l'activité.",
            default=timezone.now
        )
    proposer = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='proposed_activities',
            verbose_name="Organisateur",
            help_text="L'utilisateur qui propose cette activité.",
        )
    attendees = models.ManyToManyField(
            User,
            related_name='attended_activities',
            blank=True,
            verbose_name="Participants",
            help_text="Les utilisateurs participant à cette activité."
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

    def clean(self):
        # Validation personnalisée pour s'assurer que end_time est après start_time
        super().clean()

        errors = {}

        # Valider les dates
        if self.end_time <= self.start_time:
            errors['end_time'] = "L'heure de fin doit être après l'heure de début."

        if self.start_time < timezone.now():
            errors['start_time'] = "L'heure de début doit être dans le futur."

        # Valider le titre
        if len(self.title) < 5 or len(self.title) > 100:
            errors['title'] = "Le titre doit contenir entre 5 et 100 caractères."

        # Valider la description
        if len(self.description) < 10:
            errors['description'] = "La description doit contenir au moins 10 caractères."

        # Valider la location
        if len(self.location_city) < 2 or len(self.location_city) > 100:
            errors['location_city'] = "La ville doit contenir entre 2 et 100 caractères."

        # Si des erreurs ont été détectées, les lever
        if errors:
            raise ValidationError(errors)


    def save(self, *args, **kwargs):
        # Appeler la méthode clean pour valider avant de sauvegarder
        self.clean()
        super().save(*args, **kwargs)
