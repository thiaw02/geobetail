#!/usr/bin/env sh
set -e

echo "==> Application des migrations de la base de données"
# Réessaie tant que PostgreSQL n'est pas encore prêt (démarrage Docker)
for i in $(seq 1 15); do
  if python manage.py migrate --noinput; then
    break
  fi
  echo "Base pas encore prête, nouvel essai dans 3s (${i}/15)..."
  sleep 3
done

echo "==> Collecte des fichiers statiques"
python manage.py collectstatic --noinput || true

echo "==> Démarrage du serveur"
exec "$@"
