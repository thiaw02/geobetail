# animaux/management/commands/seed_data.py
import os
import random
from datetime import datetime, timedelta

import django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from animaux.models import Animal, Position, Zone


class Command(BaseCommand):
    help = 'Seed database with test data for GeoBétail'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Création des données de test...')
        
        # Créer un superutilisateur si inexistant
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@geobetail.com',
                password='admin123'
            )
            self.stdout.write('Superutilisateur créé: admin/admin123')
        
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
                'polygon_coords': '[[46.5, 2.0], [46.6, 2.1], [46.7, 2.0], [46.6, 1.9]]'
            }
        )
        
        # Données des animaux
        animaux_data = [
            {'identifiant': 'VACHE001', 'nom': 'Bella', 'espece': 'VACHE', 'sexe': 'F'},
            {'identifiant': 'VACHE002', 'nom': 'Luna', 'espece': 'VACHE', 'sexe': 'F'},
            {'identifiant': 'MOUTON001', 'nom': 'Bouc', 'espece': 'MOUTON', 'sexe': 'M'},
            {'identifiant': 'CHEVRE001', 'nom': 'Biquette', 'espece': 'CHEVRE', 'sexe': 'F'},
            {'identifiant': 'CHEVAL001', 'nom': 'Spirit', 'espece': 'CHEVAL', 'sexe': 'M'},
        ]
        
        for data in animaux_data:
            animal, created = Animal.objects.get_or_create(
                identifiant=data['identifiant'],
                defaults={
                    'nom': data['nom'],
                    'espece': data['espece'],
                    'sexe': data['sexe'],
                    'proprietaire': user,
                    'zone_autorisee': zone,
                    'actif': True,
                    'date_naissance': datetime.now() - timedelta(days=random.randint(365, 2000))
                }
            )
            
            if created:
                self.stdout.write(f'Animal créé: {animal.identifiant}')
            
            # Créer 3-5 positions récentes pour chaque animal
            for i in range(random.randint(3, 5)):
                # Coordonnées autour du centre de la France avec variation
                lat = 46.5 + random.uniform(-0.2, 0.2)
                lon = 2.0 + random.uniform(-0.2, 0.2)
                
                Position.objects.create(
                    animal=animal,
                    latitude=lat,
                    longitude=lon,
                    altitude=random.uniform(200, 500),
                    satellites=random.randint(5, 12),
                    batterie=random.randint(30, 100),
                    vitesse=random.uniform(0, 5),
                    precision=random.uniform(1, 10),
                    force_signal=random.randint(-90, -60),
                    timestamp=datetime.now() - timedelta(hours=random.randint(1, 24))
                )
        
        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès!'))
        self.stdout.write('Animaux créés: 5')
        self.stdout.write('Positions créées: ~20')
        self.stdout.write('\nAccès:')
        self.stdout.write('- Admin: http://127.0.0.1:8000/admin/ (admin/admin123)')
        self.stdout.write('- Carte Live: http://127.0.0.1:8000/map/')