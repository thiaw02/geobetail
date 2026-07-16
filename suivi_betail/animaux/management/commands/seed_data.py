# animaux/management/commands/seed_data.py
import os
import random
from datetime import datetime, timedelta

import django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from animaux.models import Animal, Position, Zone, Device


class Command(BaseCommand):
    help = 'Seed database with test data for GeoBétail'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Création des données de test...')
        
        # Créer un superutilisateur Django si inexistant
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@geobetail.com',
                password='admin123'
            )
            admin_user.profile.role = 'ADMIN'
            admin_user.profile.save()
            self.stdout.write('Superutilisateur Django créé: admin/admin123 (accès /admin/)')
        
        # Créer un compte superviseur admin_panel si inexistant
        if not User.objects.filter(username='superviseur').exists():
            superv = User.objects.create_user(
                username='superviseur',
                email='superviseur@geobetail.com',
                password='superviseur123',
                is_staff=True,
                is_superuser=False,
            )
            superv.profile.role = 'ADMIN'
            superv.profile.save()
            self.stdout.write('Superviseur admin_panel créé: superviseur/superviseur123 (accès /admin_panel/)')
        
        # Créer un utilisateur test
        user, created = User.objects.get_or_create(
            username='eleveur',
            defaults={
                'email': 'eleveur@example.com', 
                'password': 'eleveur123'
            }
        )
        
        if created:
            user.set_password('eleveur123')
            user.save()
        
        # Créer une zone
        zone, created = Zone.objects.get_or_create(
            nom='Pâturage Principal',
            defaults={
                'description': 'Zone principale de pâturage',
                'polygone': '[[14.6, -17.5], [14.7, -17.4], [14.75, -17.45], [14.65, -17.55]]',
                'type_zone': 'PATURAGE',
                'couleur': '#2E7D4F'
            }
        )
        
        # Données des animaux
        animaux_data = [
            {'nom': 'Bella', 'type_animal': 'VACHE', 'race': 'Gobra', 'emoji': 'fa-paw', 'couleur': '#2E7D4F'},
            {'nom': 'Luna', 'type_animal': 'VACHE', 'race': 'NDama', 'emoji': 'fa-paw', 'couleur': '#C9A227'},
            {'nom': 'Bouc', 'type_animal': 'BREBIS', 'race': 'Peul', 'emoji': 'fa-paw', 'couleur': '#6B8E7B'},
            {'nom': 'Biquette', 'type_animal': 'CHEVRE', 'race': 'Métisse', 'emoji': 'fa-paw', 'couleur': '#B83B2B'},
            {'nom': 'Spirit', 'type_animal': 'CHEVAL', 'race': 'Barbe', 'emoji': 'fa-horse', 'couleur': '#1B3B2F'},
        ]
        
        for data in animaux_data:
            # Créer un device pour chaque animal
            device, device_created = Device.objects.get_or_create(
                device_id=f"TBEAM_{data['nom'].upper()}",
                defaults={
                    'nom': f"Device {data['nom']}",
                    'type_device': 'TBEAM',
                    'statut': 'ACTIF',
                    'batterie': random.uniform(40, 100),
                }
            )
            
            animal, created = Animal.objects.get_or_create(
                nom=data['nom'],
                defaults={
                    'type_animal': data['type_animal'],
                    'race': data['race'],
                    'device': device,
                    'statut': 'ACTIF',
                    'emoji': data['emoji'],
                    'couleur': data['couleur'],
                }
            )
            
            if created:
                self.stdout.write(f'Animal créé: {animal.nom}')
            
            # Créer 3-5 positions récentes pour chaque animal
            base_lat = 14.6937
            base_lon = -17.44406
            
            for i in range(random.randint(3, 5)):
                lat = base_lat + random.uniform(-0.1, 0.1)
                lon = base_lon + random.uniform(-0.1, 0.1)
                
                Position.objects.create(
                    animal=animal,
                    latitude=lat,
                    longitude=lon,
                    altitude=random.uniform(10, 50),
                    satellites=random.randint(5, 12),
                    batterie=random.uniform(30, 100),
                    accuracy=random.uniform(1, 10),
                    speed=random.uniform(0, 5),
                    timestamp=datetime.now() - timedelta(hours=random.randint(1, 24))
                )
        
        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès!'))
        self.stdout.write('Animaux créés: 5')
        self.stdout.write('Positions créées: ~20')
        self.stdout.write('\nAccès:')
        self.stdout.write('- Admin: http://127.0.0.1:8000/admin/ (admin/admin123)')
        self.stdout.write('- Carte Live: http://127.0.0.1:8000/carte/')
