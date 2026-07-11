import json

import paho.mqtt.client as mqtt
from django.utils import timezone

from .models import Position  # Assurez-vous que ce modèle existe


class MeshtasticMQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        print("✅ Connecté au broker MQTT Meshtastic")
        # S'abonner aux topics Meshtastic
        client.subscribe("msh/+/json/position")
        client.subscribe("msh/+/json/telemetry")
        client.subscribe("msh/+/json/text")
        
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            print(f"📨 Message reçu sur {msg.topic}: {payload}")
            
            # Traiter les messages de position
            if "position" in payload:
                self.process_position_message(payload)
            elif "telemetry" in payload:
                self.process_telemetry_message(payload)
            elif "text" in payload:
                self.process_text_message(payload)
                
        except Exception as e:
            print(f"❌ Erreur traitement message: {e}")
    
    def process_position_message(self, data):
        """Traiter les données de position GPS"""
        position = data.get("position", {})
        latitude = position.get("latitude")
        longitude = position.get("longitude")
        altitude = position.get("altitude")
        
        print(f"📍 Position reçue: Lat={latitude}, Lon={longitude}, Alt={altitude}")
        
        # Sauvegarder en base de données
        self.save_position_to_db(latitude, longitude, altitude)
    
    def process_telemetry_message(self, data):
        """Traiter les données de télémétrie"""
        telemetry = data.get("telemetry", {})
        print(f"📊 Télémétrie: {telemetry}")
    
    def process_text_message(self, data):
        """Traiter les messages texte"""
        text = data.get("text", "")
        print(f"📝 Message texte: {text}")
    
    def save_position_to_db(self, lat, lon, alt):
        """Sauvegarder la position en base de données"""
        try:
            if lat and lon:
                Position.objects.create(
                    latitude=lat,
                    longitude=lon,
                    altitude=alt or 0,
                    timestamp=timezone.now()
                )
                print("💾 Position sauvegardée en base")
        except Exception as e:
            print(f"❌ Erreur sauvegarde BD: {e}")

# Fonction manquante qui cause l'erreur
def start_mqtt_client():
    """Démarrer le client MQTT - Cette fonction était manquante"""
    try:
        service = MeshtasticMQTTService()
        service.client.connect("localhost", 1883, 60)
        service.client.loop_start()  # Utiliser loop_start() au lieu de loop_forever()
        print("🚀 Client MQTT démarré avec succès")
        return service
    except Exception as e:
        print(f"❌ Erreur démarrage MQTT: {e}")
        return None