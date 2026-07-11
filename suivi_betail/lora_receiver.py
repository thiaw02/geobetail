import json
import logging
import time
from datetime import datetime

import requests
import serial
from serial.tools import list_ports

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - URL LOCALE SEULEMENT
API_URL = "http://127.0.0.1:8000/api/recevoir-position-lora/"
BAUD_RATE = 115200

def find_available_ports():
    """Trouve les ports série disponibles"""
    try:
        ports = list_ports.comports()
        available_ports = []
        
        for port in ports:
            try:
                # Essaye d'ouvrir brièvement le port
                test_ser = serial.Serial(port.device, timeout=0.1)
                test_ser.close()
                available_ports.append(port.device)
                logger.info(f"✅ Port disponible: {port.device} - {port.description}")
            except:
                logger.info(f"❌ Port occupé: {port.device} - {port.description}")
        
        return available_ports
    except Exception as e:
        logger.error(f"Erreur recherche ports: {e}")
        return []

def init_serial_connection(port_name):
    """Initialise la connexion série"""
    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=BAUD_RATE,
            timeout=1,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        logger.info(f"✅ Connexion série établie sur {port_name}")
        return ser
    except serial.SerialException as e:
        logger.error(f"❌ Erreur connexion série {port_name}: {e}")
        return None

def send_to_django(data):
    """Envoie les données à l'API Django en local"""
    try:
        logger.info(f"📤 Envoi à l'API: {data}")
        
        response = requests.post(
            API_URL, 
            json=data, 
            timeout=5,  # Timeout court pour local
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Succès: {response.json()}")
        else:
            logger.warning(f"⚠️  Erreur {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Serveur Django non accessible - Lancez: python manage.py runserver")
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout connexion API")
    except Exception as e:
        logger.error(f"❌ Erreur envoi: {e}")

def parse_lora_data(raw_data):
    """Parse les données LoRa reçues"""
    try:
        data = raw_data.strip()
        logger.debug(f"Donnée brute: {data}")
        
        # Format JSON
        if data.startswith('{') and data.endswith('}'):
            json_data = json.loads(data)
            
            return {
                'animal_id': json_data.get('id', 1),
                'latitude': float(json_data.get('lat', 0)),
                'longitude': float(json_data.get('lon', 0)),
                'vitesse': float(json_data.get('spd', 0)),
                'altitude': float(json_data.get('alt', 0)),
                'satellites': int(json_data.get('sat', 0)),
                'batterie': float(json_data.get('bat', 0)),
                'timestamp': datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.warning(f"Erreur parsing: {e}")
    
    return None

def test_django_connection():
    """Teste la connexion à Django en local"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=3)
        if response.status_code == 200:
            logger.info("✅ Serveur Django détecté")
            return True
    except:
        logger.error("❌ Django non accessible - Lancez: python manage.py runserver")
        return False

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage récepteur LoRa (mode local)...")
    
    # Test connexion Django
    if not test_django_connection():
        return
    
    # Trouve les ports disponibles
    available_ports = find_available_ports()
    if not available_ports:
        logger.error("❌ Aucun port série disponible")
        logger.info("💡 Utilisez python test_sender.py pour tester sans hardware")
        return
    
    # Essaye de se connecter à chaque port disponible
    ser = None
    for port_name in available_ports:
        ser = init_serial_connection(port_name)
        if ser:
            break
    
    if not ser:
        logger.error("❌ Impossible de se connecter à aucun port")
        return
    
    logger.info("🎯 En attente de données LoRa... (Ctrl+C pour arrêter)")
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        logger.info(f"📨 Reçu: {line}")
                        parsed_data = parse_lora_data(line)
                        if parsed_data:
                            send_to_django(parsed_data)
                            
                except Exception as e:
                    logger.error(f"Erreur lecture: {e}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Arrêt demandé")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            logger.info("🔌 Port série fermé")

if __name__ == "__main__":
    main()