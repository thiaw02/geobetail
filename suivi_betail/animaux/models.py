from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid


class Profile(models.Model):
    """Profil étendu portant le rôle métier et les préférences utilisateur."""

    ROLE_ELEVEUR = 'ELEVEUR'
    ROLE_ADMIN = 'ADMIN'
    ROLE_VETERINAIRE = 'VETERINAIRE'
    ROLE_CHOICES = [
        (ROLE_ELEVEUR, 'Éleveur'),
        (ROLE_ADMIN, 'Administrateur'),
        (ROLE_VETERINAIRE, 'Vétérinaire / Employé partagé'),
    ]

    CANAL_CHOICES = [
        ('app', 'Application'),
        ('email', 'E-mail'),
        ('sms', 'SMS'),
    ]

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ELEVEUR)
    telephone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to='profils/', null=True, blank=True)
    langue = models.CharField(max_length=5, default='fr')
    notif_canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='app')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return (
            self.role == self.ROLE_ADMIN
            or self.user.is_staff
            or self.user.is_superuser
        )

    @property
    def is_eleveur(self):
        return self.role == self.ROLE_ELEVEUR and not self.is_admin


@receiver(post_save, sender='auth.User')
def creer_ou_maj_profil(sender, instance, created, **kwargs):
    """Garantit qu'un profil existe pour chaque utilisateur."""
    if created:
        role = Profile.ROLE_ADMIN if (instance.is_staff or instance.is_superuser) else Profile.ROLE_ELEVEUR
        Profile.objects.get_or_create(user=instance, defaults={'role': role})
    else:
        Profile.objects.get_or_create(user=instance)


class CameraImage(models.Model):
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image du {self.date.strftime('%Y-%m-%d %H:%M:%S')}"


class Device(models.Model):
    TYPE_CHOICES = [
        ('TBEAM', 'T-Beam'),
        ('LORA', 'LoRa'),
        ('GPS', 'GPS Tracker'),
    ]
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('ERREUR', 'En erreur'),
    ]
    
    device_id = models.CharField(max_length=100, unique=True)
    nom = models.CharField(max_length=200)
    type_device = models.CharField(max_length=50, choices=TYPE_CHOICES, default='TBEAM')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    batterie = models.FloatField(null=True, blank=True)
    date_activation = models.DateTimeField(default=timezone.now)
    date_dernier_contact = models.DateTimeField(null=True, blank=True)
    
    proprietaire = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices'
    )
    code_appairage = models.CharField(max_length=20, unique=True, blank=True)
    date_appairage = models.DateTimeField(null=True, blank=True)
    est_appaire = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.code_appairage:
            self.code_appairage = self.generer_code_appairage()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generer_code_appairage():
        import random
        import string
        prefix = 'GB'
        segment1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        segment2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}-{segment1}-{segment2}"
    
    def __str__(self):
        return f"{self.device_id} - {self.nom}"


class Animal(models.Model):
    TYPE_ANIMAL_CHOICES = [
        ('VACHE', 'Vache'),
        ('TAUREAU', 'Taureau'),
        ('VEAU', 'Veau'),
        ('BREBIS', 'Brebis'),
        ('CHEVRE', 'Chèvre'),
    ]
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('PERDU', 'Perdu'),
        ('MORT', 'Mort'),
    ]
    
    nom = models.CharField(max_length=200)
    type_animal = models.CharField(max_length=50, choices=TYPE_ANIMAL_CHOICES, default='VACHE')
    race = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    device = models.OneToOneField(Device, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    date_dernier_contact = models.DateTimeField(null=True, blank=True)
    emoji = models.CharField(max_length=10, default='fa-paw')
    couleur = models.CharField(max_length=7, default='#4CAF50')
    zone = models.ForeignKey('Zone', on_delete=models.SET_NULL, null=True, blank=True, related_name='animaux_zone', related_query_name='animal_zone')

    # Correspondance type d'animal -> icône Font Awesome (animée via .icon-pulse)
    ANIMAL_ICONS = {
        'VACHE': 'fa-paw',
        'TAUREAU': 'fa-paw',
        'VEAU': 'fa-paw',
        'BREBIS': 'fa-paw',
        'CHEVRE': 'fa-paw',
        'CHEVAL': 'fa-horse',
    }

    @property
    def icon_class(self):
        if self.emoji and self.emoji.startswith('fa-'):
            return self.emoji
        return self.ANIMAL_ICONS.get(self.type_animal, 'fa-paw')
    
    def __str__(self):
        return self.nom


class Position(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField()
    batterie = models.FloatField(null=True, blank=True)
    satellites = models.IntegerField(default=0)
    accuracy = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)
    raw_data = models.TextField(blank=True)
    format_donnees = models.CharField(max_length=50, default='GPS')
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.animal.nom} - {self.timestamp}"


class Zone(models.Model):
    TYPE_ZONE_CHOICES = [
        ('PATURAGE', 'Pâturage'),
        ('STABULATION', 'Stabulation'),
        ('ZONE_RISQUE', 'Zone à risque'),
        ('ZONE_INTERDITE', 'Zone interdite'),
    ]
    
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type_zone = models.CharField(max_length=50, choices=TYPE_ZONE_CHOICES, default='PATURAGE')
    polygone = models.JSONField(default=list, blank=True)
    couleur = models.CharField(max_length=7, default='#FF0000')
    date_creation = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nom


class Alerte(models.Model):
    TYPE_ALERTE_CHOICES = [
        ('BATTERIE_FAIBLE', 'Batterie faible'),
        ('HORS_ZONE', 'Hors zone autorisée'),
        ('INACTIVITE', 'Inactivité prolongée'),
        ('MORT', 'Animal immobile'),
        ('ERREUR_GPS', 'Erreur GPS'),
    ]
    
    PRIORITE_CHOICES = [
        ('LOW', 'Basse'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Haute'),
        ('URGENT', 'Urgente'),
    ]
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    type_alerte = models.CharField(max_length=50, choices=TYPE_ALERTE_CHOICES)
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MEDIUM')
    message = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    resolue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    date_resolution = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Alerte {self.type_alerte} - {self.animal.nom}"


class SignalementVol(models.Model):
    STATUT_CHOICES = [
        ('NOUVEAU', 'Nouveau'),
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
        ('FAUX', 'Faux signalement'),
    ]

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    proprietaire = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_vol')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU')
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_resolution = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Signalement vol - {self.animal.nom} ({self.get_statut_display()})"


class JournalAudit(models.Model):
    ACTION_CHOICES = [
        ('CONNEXION_ADMIN', 'Connexion admin'),
        ('CONNEXION_ADMIN_ECHOUEE', 'Connexion admin échouée'),
        ('CREATION_UTILISATEUR', 'Création utilisateur'),
        ('MODIFICATION_UTILISATEUR', 'Modification utilisateur'),
        ('SUPPRESSION_UTILISATEUR', 'Suppression utilisateur'),
        ('CHANGEMENT_ROLE', 'Changement de rôle'),
        ('CREATION_COLLIER', 'Création collier'),
        ('MODIFICATION_COLLIER', 'Modification collier'),
        ('SUPPRESSION_COLLIER', 'Suppression collier'),
        ('CHANGEMENT_STATUT_SIGNALEMENT', 'Changement statut signalement vol'),
        ('AUTRE', 'Autre'),
    ]

    utilisateur_cible = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='journaux_cible')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    auteur = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='journaux_auteur')
    date = models.DateTimeField(default=timezone.now)
    detail = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_action_display()} - {self.utilisateur_cible} - {self.date}"
        