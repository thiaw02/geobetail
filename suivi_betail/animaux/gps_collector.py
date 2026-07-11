import json
import logging
import time
from datetime import datetime

import meshtastic
import meshtastic.serial_interface
import requests

# Configuration
DJANGO_URL = "http://localhost:8000/api/gps-data/receive/"
SERIAL_PORT = "COM6"

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GPSCollector:
    def __init__(self, django_url, serial_port):
        self.django_url = django_url
        self.serial_port = serial_port
        self.interface = None

    def test_django_connection(self):
        """Teste la connexion à Django"""
        try:
            response = requests.get("http://localhost:8000/api/", timeout=5)
            logger.info("✅ Django API accessible")
            return True
        except Exception:
            logger.error("❌ Django inaccessible - Démarrez d'abord: python manage.py runserver")
            return False

    def connect_to_tbeam(self):
        """Connexion au T-Beam"""
        try:
            logger.info(f"🔌 Connexion au T-Beam sur {self.serial_port}...")
            self.interface = meshtastic.serial_interface.SerialInterface(self.serial_port)

            node_info = self.interface.getMyNodeInfo()
            node_id = node_info.get('num', 'inconnu')
            logger.info(f"✅ T-Beam connecté - Node ID: {node_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion T-Beam: {e}")
            return False

    def collect_and_send_position(self):
        """Collecte les positions GPS et les envoie à Django"""
        try:
            for node_id, node in self.interface.nodes.items():
                gps = node.get('position')
                if gps and gps.get('latitude') and gps.get('longitude'):
                    gps_data = {
                        "latitude": gps['latitude'],
                        "longitude": gps['longitude'],
                        "altitude": gps.get('altitude', 0),
                        "vitesse": 0,
                        "batterie": 100,
                        "satellites": 0,
                        "timestamp": datetime.utcnow().isoformat(),
                        "node_id": node_id
                    }
                    logger.info(f"📍 Position reçue: {gps_data['latitude']:.6f}, {gps_data['longitude']:.6f}")
                    self.send_to_django(gps_data)
        except Exception as e:
            logger.error(f"❌ Erreur traitement position: {e}")

    def send_to_django(self, gps_data):
        """Envoie les données à l'API Django"""
        try:
            response = requests.post(self.django_url, json=gps_data, timeout=10)
            if response.status_code == 201:
                logger.info("✅ Données envoyées à Django")
            else:
                logger.error(f"❌ Erreur API: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ Erreur envoi Django: {e}")

    def start(self):
        """Démarre le collecteur"""
        logger.info("🎯 Démarrage du collecteur GPS T-Beam")
        logger.info(f"📡 Port: {self.serial_port}")
        logger.info(f"🌐 API: {self.django_url}")
        logger.info("=" * 50)

        if not self.test_django_connection():
            return

        if not self.connect_to_tbeam():
            return

        logger.info("👂 En écoute des données GPS... (Ctrl+C pour arrêter)")
        try:
            while True:
                self.collect_and_send_position()
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt demandé")
        finally:
            if self.interface:
                self.interface.close()

if __name__ == "__main__":
    collector = GPSCollector(DJANGO_URL, SERIAL_PORT)
    collector.start()
