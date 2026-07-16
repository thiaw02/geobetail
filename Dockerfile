# Image de base légère
FROM python:3.12-slim

# Empêche la création de fichiers .pyc et bufferise la sortie (logs Docker)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=suivi_betail.settings \
    PYTHONPATH=/app/suivi_betail

WORKDIR /app

# Les dépendances Python (psycopg[binary], Pillow...) sont fournies sous forme
# de wheels précompilés : pas besoin de build-essential.

# Installation des dépendances Python (couche mise en cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Le projet Django (manage.py, settings...) se trouve dans le sous-dossier suivi_betail/
WORKDIR /app/suivi_betail

# Script d'entrée : migrations + collectstatic + lancement
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "suivi_betail.asgi:application"]
