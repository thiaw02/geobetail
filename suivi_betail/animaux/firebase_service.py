import json
from datetime import datetime

from django.conf import settings


class FirebaseService:
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if not cls._initialized:
            try:
                import firebase_admin
                from firebase_admin import credentials
                
                service_account = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT', None)
                if not service_account:
                    return False
                
                cred = credentials.Certificate(service_account)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': getattr(settings, 'FIREBASE_DB_URL', '')
                })
                cls._initialized = True
                return True
            except Exception as e:
                print(f"Erreur initialisation Firebase: {e}")
                return False
        return True
    
    @classmethod
    def envoyer_notification(cls, titre, message, tokens=None, data=None):
        if not cls.initialize():
            return False
        
        try:
            from firebase_admin import messaging
            
            if not tokens:
                tokens = cls._get_all_tokens()
            
            if not tokens:
                return False
            
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
        if not cls.initialize():
            return None
        
        try:
            from firebase_admin import db
            
            ref = db.reference(f'positions/{position_data["animal_id"]}')
            nouvelle_ref = ref.push(position_data)
            return nouvelle_ref.key
        except Exception as e:
            print(f"Erreur sauvegarde Firebase: {e}")
            return None
    
    @classmethod
    def _get_all_tokens(cls):
        return []
