# GeoBétail

Système de suivi et de surveillance de bétail via GPS/LoRa (T-BEAM/Meshtastic), avec tableau de bord web, API REST et streaming vidéo.

## Stack technique

- **Backend** : Django 5.2.6, Django REST Framework
- **Temps réel** : Channels + Daphne (ASGI), InMemoryChannelLayer
- **API** : DRF, CORS (django-cors-headers), JWT (simplejwt), OpenAPI (drf-spectacular)
- **Config** : python-decouple (fichier `.env`)
- **Communication** : MQTT (paho-mqtt), LoRa/Meshtastic, gateway série
- **Base de données** : SQLite (`db.sqlite3`) — migrer vers PostgreSQL en production
- **Notifications** : Firebase (optionnel)
- **Frontend** : Templates HTML Django, Bootstrap 5, Leaflet, design system GeoBétail
- **PWA** : Service Worker, manifest.json, notifications push

## Structure du projet

```
suivi_betail/
├── manage.py
├── db.sqlite3
├── lora_receiver.py         # Récepteur LoRa (série)
├── gateway/
│   └── receiver.py          # Gateway de réception
├── gps_tracker/             # App GPS (placeholder)
├── animaux/                 # App principale
│   ├── models.py            # Animal, Position, Zone, Alerte, Device
│   ├── views.py             # Pages HTML + API
│   ├── urls.py
│   ├── urls_api.py          # API v1 versionnée
│   ├── serializers.py       # DRF serializers
│   ├── forms.py             # Formulaires Django
│   ├── admin.py             # Admin Django
│   ├── mqtt_service.py      # Client MQTT Meshtastic
│   ├── firebase_service.py  # Notifications Firebase
│   ├── gps_collector.py     # Collecteur GPS
│   ├── apps.py              # Config app + auto-start MQTT
│   ├── management/commands/
│   │   └── seed_data.py     # Données de démo
│   └── templates/animaux/   # Templates HTML
│       ├── base.html
│       ├── accueil.html
│       ├── dashboard.html
│       ├── animaux_list.html
│       ├── map.html
│       ├── surveillance.html
│       ├── camera_stream.html
│       ├── connexion.html
│       ├── login.html
│       └── inscription.html
└── suivi_betail/             # Config projet Django
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

## Installation

1. Cloner le dépôt puis se placer dans le dossier du projet Django :

    ```bash
    cd suivi_betail
    ```

2. Créer et activer un environnement virtuel :

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. Installer les dépendances :

    ```bash
    pip install Django djangorestframework django-cors-headers \
                channels daphne python-decouple paho-mqtt \
                djangorestframework-simplejwt drf-spectacular \
                firebase-admin meshtastic pyserial requests
    ```

4. Configurer les variables d'environnement dans `suivi_betail/suivi_betail/.env`.

5. Appliquer les migrations :

    ```bash
    python manage.py migrate
    ```

6. Créer un super-utilisateur :

    ```bash
    python manage.py createsuperuser
    ```

7. Lancer le serveur :

    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

## URLs principales

- `http://127.0.0.1:8000/` — Accueil
- `http://127.0.0.1:8000/dashboard/` — Tableau de bord
- `http://127.0.0.1:8000/carte/` — Carte de suivi
- `http://127.0.0.1:8000/animaux/` — Liste des animaux
- `http://127.0.0.1:8000/surveillance/` — Surveillance visuelle
- `http://127.0.0.1:8000/admin/` — Administration
- `http://127.0.0.1:8000/api/docs/swagger/` — Documentation API

## API REST v1

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/token/` | POST | Obtenir token JWT |
| `/api/v1/token/refresh/` | POST | Rafraîchir token |
| `/api/v1/animaux/` | GET | Liste des animaux |
| `/api/v1/animaux/actifs/` | GET | Animaux actifs |
| `/api/v1/positions/` | GET | Positions récentes |
| `/api/v1/dashboard/stats/` | GET | Statistiques |
| `/api/v1/zones/` | GET | Zones |
| `/api/v1/alertes/` | GET | Alertes actives |
| `/api/v1/devices/` | GET | Devices |
| `/api/v1/tbeam/stream/` | POST | Ingestion données T-Beam |
| `/api/v1/health/` | GET | Santé API |

## Design System

- Palette : vert forêt `#1B3B2F`, or `#C9A227`, crème `#FAF8F3`
- Typographie : Inter (Google Fonts)
- Variables CSS dans `static/css/design-system.css`
- Tokens partagés dans `static/design-tokens.json` (web + mobile)

## PWA

- Manifest : `static/manifest.json`
- Service Worker : `static/sw.js`
- Icônes : `static/icons/`

## Sécurité

- Authentification API par JWT (simplejwt)
- CORS restreint en production
- HTTPS obligatoire en production
- Rate limiting sur endpoints d'ingestion
- Validation stricte des entrées
- Secrets dans `.env` (jamais commités)
