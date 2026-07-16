# GeoBétail

Système de suivi et de surveillance de bétail via GPS/LoRa (T-BEAM/Meshtastic), avec tableau de bord web, API REST et streaming vidéo.

## Stack technique

- **Backend** : Django 5+, Django REST Framework
- **Temps réel** : Channels + Daphne (ASGI), InMemoryChannelLayer
- **API** : Django REST Framework, CORS (django-cors-headers), JWT (djangorestframework-simplejwt), drf-spectacular (OpenAPI)
- **Config** : python-decouple (fichier `.env`)
- **Communication** : MQTT (paho-mqtt), LoRa/Meshtastic, gateway série
- **Base de données** : SQLite (`db.sqlite3`)
- **Notifications** : Firebase (optionnel)
- **Colliers** : QR codes (`qrcode`), appairage multi-colliers
- **Zones de pâturage** : geofencing (polygones + cercles), dessin sur carte (Leaflet.draw)
- **Frontend** : templates HTML (Django), streaming vidéo MJPEG, PWA (service worker)

## Structure du projet

```
projetgeobetail/
├── README.md
├── .gitignore
└── suivi_betail/                # Projet Django
    ├── manage.py
    ├── db.sqlite3
    ├── animaux/                 # App principale
    │   ├── models.py            # Animal, Position, Zone, Alerte, Device...
    │   ├── views.py             # Pages HTML + API
    │   ├── views_colliers.py    # Appairage / QR codes des colliers
    │   ├── urls.py
    │   ├── urls_api.py          # API REST v1
    │   ├── urls_colliers.py     # Routes colliers
    │   ├── serializers.py
    │   ├── geofencing.py        # Logique de géofencing (point-in-polygone, haversine)
    │   ├── mqtt_service.py      # Client MQTT Meshtastic (ingestion GPS/LoRa)
    │   ├── firebase_service.py  # Notifications Firebase (optionnel)
    │   ├── qr_utils.py          # Génération de QR codes d'appairage
    │   ├── management/commands/ # Commandes (seed_data...)
    │   └── templates/           # Templates HTML (pages + espace de gestion)
    ├── admin_panel/             # Espace de gestion multi-rôles (/gestion/)
    │   ├── views.py, forms.py, mixins.py, urls.py
    │   └── templates/admin_panel/
    ├── static/                  # Fichiers statiques (CSS design-system, JS...)
    ├── media/                   # Uploads (images caméra, généré localement)
    ├── templates/               # robots.txt, sitemap.xml
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

## Démarrage rapide

Pour lancer le projet minimalement (sans venv) :

```bash
cd suivi_betail
pip install Django djangorestframework django-cors-headers channels daphne python-decouple paho-mqtt djangorestframework-simplejwt drf-spectacular qrcode pillow
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Le site sera accessible sur `http://127.0.0.1:8000/`.
Pour une installation propre et isolée (venv), voir la section **Installation** ci-dessous.

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

   > **Environnement virtuel : obligatoire ou non ?**
   > L'activation d'un venv **n'est pas obligatoire** pour lancer le projet.
   > Les dépendances peuvent être installées globalement et `python manage.py runserver`
   > fonctionnera directement. Un venv est **recommandé** pour isoler les
   > dépendances du projet des autres projets Python de la machine et éviter les
   > conflits de versions.

3. Installer les dépendances **(dans le venv activé, ou globalement)** :

   ```bash
    pip install Django djangorestframework django-cors-headers \
                channels daphne python-decouple paho-mqtt \
                djangorestframework-simplejwt drf-spectacular qrcode pillow
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

L'ingestion des données GPS/LoRa (T-BEAM / Meshtastic) est gérée par le
client MQTT démarré automatiquement avec Django (`animaux/mqtt_service.py`,
voir `animaux/apps.py`). Les positions sont reçues sur l'endpoint
`/api/tbeam/stream/` (`animaux/views.py::receive_tbeam_data`).

## API REST principale

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health/` | GET | État de l'API |
| `/api/animaux/actifs/` | GET | Animaux actifs |
| `/api/animaux/liste/` | GET | Liste des animaux |
| `/api/positions/recentes/` | GET | Positions récentes |
| `/api/dashboard/stats/` | GET | Statistiques du tableau de bord |
| `/api/zones/` | GET | Zones de pâturage |
| `/api/zones/creer/` | POST | Créer une zone de pâturage (auth) |
| `/api/zones/<id>/supprimer/` | DELETE | Supprimer une zone (auth) |
| `/api/alertes/` | GET | Alertes |
| `/api/devices/` | GET | Appareils connectés |
| `/api/v1/colliers/appairer/` | POST | Appairer un collier (code) |
| `/api/v1/colliers/appairer-qr/` | POST | Appairer un collier (QR) |
| `/api/v1/colliers/mes-colliers/` | GET | Mes colliers (auth) |
| `/api/v1/colliers/<id>/dissocier/` | DELETE | Dissocier un collier (auth) |
| `/api/v1/colliers/<id>/qr-code/` | GET | QR code du collier (auth) |
| `/api/tbeam/stream/` | POST | Réception de données T-BEAM |
| `/api/upload_image/` | POST | Upload d'image (caméra) |
| `/api/video_stream/` | POST | Flux vidéo |
| `/api/live_stream/` | GET | Flux live |

> Documentation interactive de l'API : `/api/docs/swagger/` et `/api/docs/redoc/`.

## Pages web

`/` (accueil), `/dashboard/`, `/animaux/`, `/carte/`, `/connexion/`,
`/inscription/`, `/surveillance/`, `/camera/`, `/colliers/` (mes colliers),
`/colliers/ajouter/` (appairage d'un collier).

## Colliers et zones de pâturage

- **Appairage multi-colliers** : chaque collier possède un code unique
  `GB-XXXX-XXXX` (généré automatiquement). L'éleveur peut l'appairer en
  scannant le QR code (`geobetail://pair/<code>`) ou en saisissant le code
  manuellement. Un collier est alors associé à son compte et à un animal.
- **Gestion** : page « Mes colliers » listant batterie, statut, dernier
  contact, animal associé, avec régénération du QR code et dissociation.
- **Zones de pâturage (geofencing)** : depuis la carte (`/carte/`), dessinez
  un polygone ou un cercle avec l'outil *Dessiner une zone*. La zone est
  enregistrée en GeoJSON et peut être associée à un ou plusieurs animaux.
- **Alertes hors zone** : à chaque position reçue, le système vérifie si
  l'animal se trouve dans l'une de ses zones autorisées (pâturage /
  stabulation). S'il est hors zone, une alerte `HORS_ZONE` (priorité haute)
  est créée automatiquement. Aucune dépendance lourde n'est requise
  (point-in-polygone et distance haversine implémentés en natif).

## Design responsive (mobile-first)

L'interface est conçue **mobile-first** : le smartphone est la plateforme
principale (éleveurs sur le terrain). Les breakpoints sont centralisés et
documentés dans `static/css/design-system.css` :

| Nom        | Plage                         |
|------------|-------------------------------|
| Mobile     | `< 600px`                     |
| Tablette   | `600px – 1023px`              |
| Desktop    | `>= 1024px`                   |
| Grand      | `>= 1440px`                   |

Points clés :

- **Navigation adaptative** : sidebar fixe sur desktop/tablette large ; sur
  mobile/tablette étroite, elle est remplacée par une **navigation basse
  fixe** (Dashboard, Carte, Animaux, Colliers, Menu). Le Menu ouvre la
  sidebar complète (options secondaires).
- **Carte Leaflet** : occupe `100dvh` sur mobile (gère les barres d'adresse
  dynamiques), panneau d'infos en **bottom sheet** repliable, barre d'outils
  regroupée dans un **FAB**, contrôles de zoom agrandis (44px) et poignées
  de dessin de zone plus larges pour le tactile.
- **Formulaires** : un champ par ligne sous 600px, labels au-dessus, boutons
  d'action plein écran, `inputmode`/`autocapitalize` adaptés (ex. code
  collier).
- **Tableaux** : transformation en **cartes empilées** sur mobile
  (`responsive-table` + `data-label` sur chaque cellule).
- **Dashboard** : grille statistique fluide 1 / 2 / 4 colonnes.
- **Caméra** : flux responsive, bouton **plein écran**, détails techniques
  repliés derrière un bouton sur mobile.
- Zones tactiles minimales de 44×44px, aucun scroll horizontal involontaire,
  `viewport-fit=cover` + safe-area insets pour l'encoche.

## Dockerisation

Le projet est containerisable (image `python:3.12-slim`, serveur **Daphne**
qui gère à la fois HTTP et WebSockets/Channels).

Fichiers fournis :

- `Dockerfile` — image et point d'entrée (`docker-entrypoint.sh`).
- `docker-compose.yml` — service `web` sur le port `8000`, volume nommé
  `geobetail_data` monté sur `/app/data` (base SQLite + médias persistés).
- `docker-entrypoint.sh` — applique les migrations, collecte les statiques
  puis lance Daphne.
- `requirements.txt` — dépendances épinglées.
- `.dockerignore` — exclut `.env`, `db.sqlite3`, `staticfiles/`, `media/`…

Lancer avec Docker Compose (PostgreSQL + application) :

```bash
# Construction et démarrage
docker compose up --build

# Le site est accessible sur http://localhost:8000
```

Personnaliser la clé secrète et les identifiants base (recommandé) :

```bash
SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(50))')" \
DB_PASSWORD="motdepassefort" \
docker compose up --build
```

**Base de données** : le stack utilise **PostgreSQL** (service `db`,
image `postgres:16-alpine`). Le service `web` se connecte via les variables
d'environnement `DB_ENGINE=postgres`, `DB_HOST=db`, `DB_NAME`, `DB_USER`,
`DB_PASSWORD`. Le script `docker-entrypoint.sh` attend que PostgreSQL soit
prêt puis applique les migrations et collecte les statiques. Les données
PostgreSQL sont persistées dans le volume `geobetail_pg` ; les médias
uploadés dans le volume `geobetail_data` (`/app/data/media`).

> Le moteur de base est configurable via `DB_ENGINE` : `postgres` (défaut en
> Docker) ou `sqlite3` pour un dev local sans PostgreSQL (zéro configuration).

## Notes

- `db.sqlite3` et les fichiers `media/` sont générés localement.
- `firebase-service-account.json` est ignoré par git (voir `.gitignore`) :
  ne jamais le committer.
