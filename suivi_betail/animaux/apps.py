import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)

class AnimauxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'animaux'
    
    def ready(self):
        """Démarre le client MQTT après le chargement complet de Django"""
        # NE PAS démarrer MQTT pendant les migrations
        if os.environ.get('RUN_MAIN') and not os.environ.get('DJANGO_AUTORELOAD'):
            try:
                from .mqtt_service import start_mqtt_client
                start_mqtt_client()
                logger.info("🚀 Service MQTT Meshtastic démarré")
            except ImportError as e:
                logger.warning(f"Import MQTT ignoré pendant les migrations: {e}")
            except Exception as e:
                logger.error(f"Erreur démarrage MQTT: {e}")