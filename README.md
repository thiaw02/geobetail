# GeoBétail

Système de suivi et de surveillance de bétail via GPS/LoRa (T-BEAM/Meshtastic), avec tableau de bord web, API REST et streaming vidéo.

## Stack technique

- **Backend** : Django 5+, Django REST Framework
- **Temps réel** : Channels + Daphne (ASGI), InMemoryChannelLayer
- **API** : Django REST Framework, CORS (django-cors-headers)
- **Config** : python-decouple (fichier `.env`)
- **Communication** : MQTT (paho-mqtt), LoRa/Meshtastic, gateway série
- **Base de données** : SQLite (`db.sqlite3`)
- **Notifications** : Firebase (optionnel)
- **Frontend** : templates HTML (Django), streaming vidéo MJPEG

## Structure du projet

```
projetgeobetail/
├── README.md
├── .gitignore
└── suivi_betail/                # Projet Django
    ├── manage.py
    ├── db.sqlite3
    ├── lora_receiver.py         # Récepteur LoRa (série)
    ├── gateway/
    │   └── receiver.py          # Gateway de réception
    ├── gps_tracker/             # App GPS (placeholder)
    ├── animaux/                 # App principale
    │   ├── models.py            # Animal, Position, Zone, Alerte, Device...
    │   ├── views.py             # Pages HTML + API
    │   ├── urls.py
    │   ├── serializers.py
    │   ├── mqtt_service.py      # Client MQTT Meshtastic
    │   ├── gps_collector.py     # Collecteur GPS
    │   ├── firebase_service.py  # Notifications Firebase
    │   ├── management/commands/ # Commandes (seed_data...)
    │   └── templates/           # Templates HTML
    └── suivi_betail/
        ├── settings.py
        ├── urls.py
        ├── asgi.py
        ├── wsgi.py
        └── .env                 # Variables d'environnement
```

## Prérequis

- Python 3.11+ (testé avec Python 3.14)
- pip

## Installation

1. Cloner le dépôt puis se placer dans le dossier du projet Django :

   ```bash
   cd suivi_betail
   ```

2. (Recommandé) Créer et activer un environnement virtuel :

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # Linux / macOS
   ```

3. Installer les dépendances :

   ```bash
   pip install Django djangorestframework django-cors-headers \
               channels daphne python-decouple paho-mqtt
   ```

   Dépendances optionnelles (matériel / notifications) :

   ```bash
   pip install firebase-admin meshtastic pyserial requests
   ```

   > `firebase-admin`, `meshtastic` et `pyserial` ne sont nécessaires que pour
   > le suivi GPS/LoRa et les notifications push. Le serveur web démarre sans eux.

## Configuration

Le fichier `suivi_betail/suivi_betail/.env` contient les variables d'environnement.
Exemple :

```
SECRET_KEY=django-insecure-...
DEBUG=True

# Firebase (optionnel)
FIREBASE_API_KEY=...
FIREBASE_PROJECT_ID=suivi-betail-dagas
FIREBASE_SERVICE_ACCOUNT=firebase-service-account.json
```

Les réglages principaux (hôtes autorisés, MQTT, LoRa, CORS) se trouvent dans
`suivi_betail/suivi_betail/settings.py`.

## Commandes à lancer

Toutes les commandes sont à exécuter depuis le dossier `suivi_betail/`.

### 1. Vérifier la configuration

```bash
python manage.py check
```

### 2. Appliquer les migrations (base de données)

```bash
python manage.py migrate
```

### 3. (Optionnel) Peupler la base avec des données de démo

```bash
python manage.py seed_data
```

### 4. Créer un super-utilisateur (accès admin)

```bash
python manage.py createsuperuser
```

### 5. Lancer le serveur de développement

```bash
python manage.py runserver 0.0.0.0:8000
```

Le site est alors accessible sur :

- `http://127.0.0.1:8000/`
- `http://localhost:8000/`
- Interface d'administration : `http://127.0.0.1:8000/admin/`

### 6. Lancer avec ASGI (WebSockets / Channels)

Si vous utilisez les fonctionnalités temps réel (Channels) :

```bash
daphne -b 0.0.0.0 -p 8000 suivi_betail.asgi:application
```

## Services annexes (matériel)

Ces scripts tournent indépendamment et alimentent l'API en données GPS :

```bash
# Collecteur GPS via Meshtastic / T-BEAM
python animaux/run_gps_collector.py

# Récepteur LoRa série
python lora_receiver.py

# Gateway de réception
python gateway/receiver.py
```

## API REST principale

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health/` | GET | État de l'API |
| `/api/animaux/actifs/` | GET | Animaux actifs |
| `/api/animaux/liste/` | GET | Liste des animaux |
| `/api/positions/recentes/` | GET | Positions récentes |
| `/api/dashboard/stats/` | GET | Statistiques du tableau de bord |
| `/api/zones/` | GET | Zones de pâturage |
| `/api/alertes/` | GET | Alertes |
| `/api/devices/` | GET | Appareils connectés |
| `/api/tbeam/stream/` | POST | Réception de données T-BEAM |
| `/api/upload_image/` | POST | Upload d'image (caméra) |
| `/api/video_stream/` | POST | Flux vidéo |
| `/api/live_stream/` | GET | Flux live |

## Pages web

`/` (accueil), `/dashboard/`, `/animaux/`, `/carte/`, `/connexion/`,
`/inscription/`, `/surveillance/`, `/camera/`.

## Notes

- `db.sqlite3` et les fichiers `media/` sont générés localement.
- `firebase-service-account.json` est ignoré par git (voir `.gitignore`) :
  ne jamais le committer.
