#!/bin/sh
set -e

echo "🚀 Starting Django Todo Notes API..."

echo "⏳ Waiting for system to be ready..."
sleep 2

# Appliquer les migrations
echo "📦 Applying database migrations..."
python manage.py migrate --noinput

# Créer un superuser si nécessaire (mode non-interactif)
echo "👤 Creating superuser if needed..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('✅ Superuser created: admin/admin')
else:
    print('ℹ️  Superuser already exists')
EOF

# Charger les données de démonstration si la variable est définie
if [ "$LOAD_DEMO_DATA" = "true" ]; then
    echo "📊 Loading demo data..."
    python manage.py seed_demo || echo "⚠️  Demo data already exists or command not available"
fi

# Collecter les fichiers statiques (pour production)
if [ "$COLLECT_STATIC" = "true" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "✅ Initialization complete!"
echo "🌐 Starting server on 0.0.0.0:8000..."

# Exécuter la commande passée en argument
exec "$@"
