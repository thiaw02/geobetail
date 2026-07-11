import sys
import time

from gps_collector import GPSCollector

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