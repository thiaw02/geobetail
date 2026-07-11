from django.contrib import admin

from .models import Alerte, Animal, Device, Position, Zone


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'nom', 'type_device', 'statut', 'batterie', 'date_dernier_contact']

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_animal', 'device', 'statut', 'date_dernier_contact']
    # Supprimer les inlines problématiques
    inlines = []

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['animal', 'timestamp', 'latitude', 'longitude']
    readonly_fields = ['timestamp', 'latitude', 'longitude']

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_zone']

@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ['animal', 'type_alerte', 'resolue']