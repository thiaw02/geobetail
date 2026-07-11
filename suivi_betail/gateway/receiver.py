# gateway/receiver.py
import json
from datetime import datetime

import requests
import serial

LORA_SERIAL_PORT = "/dev/ttyUSB0"  # Port série du module LoRa
BAUD_RATE = 9600

def parse_lora_data(data):
    """Parse les données reçues du T-Beam"""
    parts = data.strip().split(',')
    if len(parts) >= 5:
        return {
            'device_id': parts[0],
            'latitude': float(parts[1]),
            'longitude': float(parts[2]),
            'altitude': float(parts[3]),
            'satellites': int(parts[4]),
            'timestamp': datetime.now().isoformat()
        }
    return None

def send_to_django(gps_data):
    """Envoie les données à l'API Django"""
    url = "http://127.0.0.1:8000/gpsdata/"
    
    payload = {
        'device_id': gps_data['device_id'],
        'latitude': gps_data['latitude'],
        'longitude': gps_data['longitude'],
        'altitude': gps_data['altitude'],
        'timestamp': gps_data['timestamp'],
        'battery_level': 85,  # À adapter
        'signal_strength': -65  # À adapter
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print("✅ Données envoyées avec succès")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")

def main():
    ser = serial.Serial(LORA_SERIAL_PORT, BAUD_RATE, timeout=1)
    print("🎯 Récepteur LoRa démarré - En attente de données...")
    
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print(f"📡 Données reçues: {data}")
            
            gps_data = parse_lora_data(data)
            if gps_data:
                send_to_django(gps_data)

if __name__ == "__main__":
    main()