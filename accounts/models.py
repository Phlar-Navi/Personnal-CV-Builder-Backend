from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import re

def validate_cameroun_phone(value):
    """
    Validateur pour les numéros de téléphone camerounais
    Formats acceptés :
    - +237 6 XX XX XX XX
    - +237 2 XX XX XX XX
    - +237 3 XX XX XX XX
    - etc. (tous les indicatifs régionaux camerounais)
    """
    phone_regex = r'^\+237\s[23456789]\d{2}\s\d{2}\s\d{2}\s\d{2}$'
    
    if not re.match(phone_regex, value):
        raise ValidationError(
            'Format invalide. Utilisez le format : +237 X XX XX XX XX '
            '(où X est un chiffre entre 2-9)'
        )

# Create your models here.

class Socials(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    link = models.URLField()
    description = models.CharField(max_length=255, null=True, blank=True)
    # URL de l'icône (depuis un CDN comme FontAwesome ou Simple Icons)
    icon_url = models.URLField(
        help_text="URL de l'icône (ex: https://cdn.jsdelivr.net/npm/simple-icons@v10/icons/github.svg)"
    )
    
    class Meta:
        verbose_name = "Réseau social"
        verbose_name_plural = "Réseaux sociaux"
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    LICENSES_TYPES = (
        ('A', "permis A"),
        ('B', "permis B"),
        ('C', "permis C"),
        ('D', "permis D"),
    )

    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        unique=True,
        null=False,
        blank=True,
        validators=[validate_cameroun_phone]
    )
    abstract = models.TextField(null=False)
    image = models.ImageField(null=True)
    address = models.CharField(max_length=255, null=True)
    driving_license = models.CharField(max_length=1, null=True, choices=LICENSES_TYPES)
    socials = models.ManyToManyField(
        Socials,
        blank=True,
        related_name='users',
        help_text="Réseaux sociaux de l'utilisateur"
    )


class SessionLog(models.Model):
    """
    Modèle pour tracer les sessions utilisateur
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='session_logs'
    )
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Session utilisateur"
        verbose_name_plural = "Sessions utilisateur"
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.login_time}"
    
    @property
    def duration(self):
        """Calcule la durée de la session en minutes"""
        if self.logout_time:
            delta = self.logout_time - self.login_time
            return delta.total_seconds() / 60
        return None
    
    def end_session(self):
        """Termine la session"""
        from django.utils import timezone
        self.logout_time = timezone.now()
        self.is_active = False
        self.save()


