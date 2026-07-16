# test_api.py - Test GeoBétail
import json

import requests


def test_api():
    """Teste l'API GeoBétail"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Données de test
    test_data = {
        "device_id": "TEST_001",
        "latitude": 14.6937,
        "longitude": -17.44406,
        "batterie": 85,
        "satellites": 12
    }
    
    endpoints = {
        'health': f"{base_url}/api/health/",
        'tbeam': f"{base_url}/api/tbeam/stream/",
        'dashboard': f"{base_url}/api/dashboard/stats/",
        'animaux': f"{base_url}/api/animaux/liste/",
    }
    
    print("🧪 Test API GeoBétail")
    print("=" * 50)
    
    # Test health
    try:
        response = requests.get(endpoints['health'], timeout=5)
        print(f"✅ Health: {response.status_code}")
    except Exception as e:
        print(f"❌ Health: {e}")
    
    # Test dashboard
    try:
        response = requests.get(endpoints['dashboard'], timeout=5)
        print(f"✅ Dashboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard: {e}")
    
    # Test T-Beam
    try:
        response = requests.post(endpoints['tbeam'], json=test_data, timeout=5)
        print(f"✅ T-Beam: {response.status_code}")
        if response.status_code in (200, 201):
            print(f"📨 Réponse: {response.json()}")
    except Exception as e:
        print(f"❌ T-Beam: {e}")
    
    # Test animaux list
    try:
        response = requests.get(endpoints['animaux'], timeout=5)
        print(f"✅ Animaux: {response.status_code}")
    except Exception as e:
        print(f"❌ Animaux: {e}")

if __name__ == "__main__":
    test_api()
