from django.apps import AppConfig


class SuiviBetailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suivi_betail'
    
    def ready(self):
        # Démarrer le service MQTT au démarrage de Django
        import threading

        from .services.mqtt_service import MeshtasticMQTTService
        
        def start_mqtt():
            service = MeshtasticMQTTService()
            service.client.connect("localhost", 1883, 60)
            service.client.loop_forever()
        
        # Démarrer dans un thread séparé
        mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
        mqtt_thread.start()