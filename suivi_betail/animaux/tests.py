# test_fixed.py - Test GeoBétail CORRIGÉ
import json

import requests


def test_api():
    """Teste l'API GeoBétail"""
    
    # URLs COMPLÈTES avec http://
    base_urls = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
    
    # Données de test
    test_data = {
        "device_id": "TEST_001",
        "latitude": 46.603354,
        "longitude": 1.888334,
        "batterie": 85,
        "satellites": 12
    }
    
    for base_url in base_urls:
        # URL COMPLÈTE avec http://
        api_url = f"{base_url}/api/tbeam/receive/"
        
        try:
            print(f"🔍 Test de {api_url}...")
            
            response = requests.post(
                api_url,
                json=test_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ SUCCÈS! Données reçues par le serveur")
                print(f"📨 Réponse: {response.json()}")
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Impossible de se connecter - Serveur non démarré?")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return False

if __name__ == "__main__":
    print("🧪 Test API GeoBétail - VERSION CORRIGÉE")
    print("=" * 50)
    
    if test_api():
        print("\n🎉 Test réussi! Vérifiez le dashboard:")
        print("   http://127.0.0.1:8000/dashboard/")
    else:
        print("\n💡 Conseils de dépannage:")
        print("1. Le serveur Django est-il démarré?")
        print("2. Utilisez: python manage.py runserver 0.0.0.0:8000")
        print("3. Ouvrez une DEUXIÈME fenêtre cmd pour les tests")        print("2. Utilisez: python manage.py runserver 0.0.0.0:8000")
        