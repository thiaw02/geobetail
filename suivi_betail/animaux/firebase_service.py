import json
from datetime import datetime

import firebase_admin
from django.conf import settings
from firebase_admin import credentials, db, messaging


class FirebaseService:
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if not cls._initialized:
            try:
                # Configuration Firebase
                cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_CONFIG['databaseURL']
                })
                cls._initialized = True
            except Exception as e:
                print(f"Erreur initialisation Firebase: {e}")
    
    @classmethod
    def envoyer_notification(cls, titre, message, tokens=None, data=None):
        cls.initialize()
        
        if not tokens:
            # Récupérer tous les tokens des utilisateurs
            tokens = cls._get_all_tokens()
        
        if not tokens:
            return False
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=titre,
                    body=message
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            print(f"{response.success_count} messages envoyés avec succès")
            return response.success_count > 0
            
        except Exception as e:
            print(f"Erreur envoi notification: {e}")
            return False
    
    @classmethod
    def sauvegarder_position(cls, position_data):
        cls.initialize()
        
        try:
            ref = db.reference(f'positions/{position_data["animal_id"]}')
            nouvelle_ref = ref.push(position_data)
            return nouvelle_ref.key
        except Exception as e:
            print(f"Erreur sauvegarde Firebase: {e}")
            return None
    
    @classmethod
    def _get_all_tokens(cls):
        # Implémentez la récupération des tokens FCM des utilisateurs
        return []