import os
import sys
import time

import django
from gps_collector import GPSCollector

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suivi_betail.settings")
django.setup()

print("=== COLLECTEUR GPS T-BEAM ===")
print(f"Port: COM6")
print(f"API Django: http://localhost:8000/api/gps-data/")
print("=" * 40)

try:
    collector = GPSCollector(
        django_url="http://localhost:8000/api/gps-data/",
        serial_port="COM6"
    )
    
    print("Démarrage dans 3 secondes...")
    time.sleep(3)
    
    collector.start_listening()
    
except KeyboardInterrupt:
    print("\nArrêt du programme")
except Exception as e:
    print(f"Erreur: {e}")
    input("Appuyez sur Entrée pour quitter...")
    from animaux.models import GPSData

from meshtastic.serial_interface import SerialInterface

interface = SerialInterface()
for node_id, node in interface.nodes.items():
    pos = node.get('position')
    if pos:
        GPSData.objects.create(
            node_id=node_id,
            latitude=pos['latitude'],
            longitude=pos['longitude'],
            altitude=pos.get('altitude')
        )