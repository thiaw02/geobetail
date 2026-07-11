from django.db import models
from django.utils import timezone


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
    emoji = models.CharField(max_length=10, default='🐄')
    couleur = models.CharField(max_length=7, default='#4CAF50')
    
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
    polygone = models.TextField()
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