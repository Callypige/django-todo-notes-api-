# 🐳 Guide Docker - Django Todo Notes API

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installé et en cours d'exécution
- Docker Compose (inclus avec Docker Desktop)

## 🚀 Démarrage Rapide

### Option 1 : Script PowerShell Interactif (Windows)

```powershell
.\setup-docker.ps1
```

Le script propose un menu interactif avec toutes les options disponibles.

### Option 2 : Commandes Docker Compose Manuelles

```bash
# Build et démarrer
docker compose up --build -d

# Arrêter
docker compose stop

# Arrêter et supprimer
docker compose down

# Voir les logs
docker compose logs -f
```

## 📦 Configuration

### Variables d'Environnement

Le fichier `.env.docker` contient les variables d'environnement par défaut :

```env
DEBUG=True
DJANGO_SECRET_KEY=docker-secret-key-change-in-production-please
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
SQLITE_PATH=/app/data/db.sqlite3
LOAD_DEMO_DATA=false
COLLECT_STATIC=false
```

Pour les modifier, créez un fichier `.env` à la racine du projet.

### Volumes Persistants

La base de données SQLite est stockée dans un volume Docker nommé `sqlite_data`, ce qui garantit la persistance des données entre les redémarrages.

```bash
# Lister les volumes
docker volume ls

# Inspecter le volume de données
docker volume inspect django-todo-notes-api_sqlite_data

# Supprimer les volumes (⚠️ perte de données)
docker compose down -v
```

## 🔧 Opérations Courantes

### Accéder au Shell Django

```bash
docker compose exec web python manage.py shell
```

### Créer un Superuser

Le superuser `admin/admin` est créé automatiquement au démarrage.

Pour en créer un autre :

```bash
docker compose exec web python manage.py createsuperuser
```

### Charger les Données de Démo

```bash
docker compose exec web python manage.py seed_demo
```

### Exécuter les Migrations

Les migrations sont automatiquement exécutées au démarrage via `docker-entrypoint.sh`.

Pour les exécuter manuellement :

```bash
docker compose exec web python manage.py migrate
```

### Créer de Nouvelles Migrations

```bash
docker compose exec web python manage.py makemigrations
```

### Accéder aux Logs

```bash
# Tous les logs
docker compose logs -f

# Logs du service web uniquement
docker compose logs -f web

# Dernières 100 lignes
docker compose logs --tail=100 web
```

### Exécuter les Tests

```bash
docker compose exec web python manage.py test
```

## 🌐 Endpoints Disponibles

Une fois l'application démarrée :

| Endpoint | Description |
|----------|-------------|
| http://localhost:8000 | Redirection vers la documentation |
| http://localhost:8000/api/docs/ | Documentation Swagger UI |
| http://localhost:8000/api/redoc/ | Documentation ReDoc |
| http://localhost:8000/admin/ | Interface d'administration Django |
| http://localhost:8000/api/notes/ | API Notes |
| http://localhost:8000/api/todos/ | API Todos |
| http://localhost:8000/api/health/ | Health check (pour monitoring) |

### Credentials Admin

- **Username:** admin
- **Password:** admin

## 🐛 Dépannage

### Le container ne démarre pas

```bash
# Vérifier les logs
docker compose logs web

# Vérifier le status
docker compose ps
```

### Erreur de port déjà utilisé

Si le port 8000 est déjà utilisé, modifiez le `docker-compose.yml` :

```yaml
ports:
  - "8080:8000"  # Utiliser le port 8080 sur l'hôte
```

### Réinitialiser complètement

```bash
# Arrêter et supprimer tout
docker compose down -v

# Supprimer les images
docker compose down --rmi all

# Rebuild from scratch
docker compose up --build -d
```

### Accéder au container

```bash
# Shell bash dans le container
docker compose exec web /bin/sh

# Ou directement avec docker
docker exec -it django-todo-notes-api /bin/sh
```

## 🏗️ Architecture Docker

### Dockerfile

Le `Dockerfile` utilise :
- Image de base : `python:3.11-slim`
- Multi-étapes pour optimisation
- Healthcheck intégré
- Entrypoint personnalisé pour l'initialisation

### docker-compose.yml

Services :
- **web** : Application Django avec SQLite persistante

Volumes :
- **sqlite_data** : Stockage persistant de la base de données

### docker-entrypoint.sh

Script d'initialisation qui :
1. ✅ Applique les migrations
2. ✅ Crée le superuser admin
3. ✅ Charge les données de démo (optionnel)
4. ✅ Collecte les fichiers statiques (optionnel)
5. ✅ Démarre le serveur

## 📊 Healthcheck

Le container inclut un healthcheck qui vérifie l'endpoint `/api/health/` toutes les 30 secondes.

```bash
# Vérifier le status health
docker compose ps

# Inspecter le healthcheck
docker inspect django-todo-notes-api
```

## 🚀 Production

Pour un déploiement en production :

1. **Changez la SECRET_KEY** dans les variables d'environnement
2. **Désactivez DEBUG** : `DEBUG=False`
3. **Configurez ALLOWED_HOSTS** correctement
4. **Utilisez un serveur WSGI** (Gunicorn) au lieu de `runserver`
5. **Ajoutez un reverse proxy** (Nginx) devant Django
6. **Activez HTTPS**
7. **Configurez une vraie base de données** (PostgreSQL)

### Exemple avec Gunicorn

Ajoutez dans `requirements.txt` :
```
gunicorn==21.2.0
```

Modifiez le `CMD` dans `Dockerfile` :
```dockerfile
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

## 📝 Commandes Utiles

```bash
# Build sans cache
docker compose build --no-cache

# Redémarrer un service
docker compose restart web

# Voir l'utilisation des ressources
docker stats

# Nettoyer les images non utilisées
docker system prune -a

# Exporter la base de données
docker compose exec web python manage.py dumpdata > backup.json

# Importer la base de données
docker compose exec -T web python manage.py loaddata < backup.json
```

## ✅ Checklist de Vérification

Avant de déployer, vérifiez :

- [ ] Docker et Docker Compose installés
- [ ] Port 8000 disponible
- [ ] Fichiers `Dockerfile`, `docker-compose.yml`, `docker-entrypoint.sh` présents
- [ ] Variables d'environnement configurées
- [ ] Build réussi : `docker compose build`
- [ ] Application démarrée : `docker compose up -d`
- [ ] Health check OK : `docker compose ps`
- [ ] API accessible : http://localhost:8000/api/health/
- [ ] Documentation accessible : http://localhost:8000/api/docs/
- [ ] Admin accessible : http://localhost:8000/admin/

## 📚 Ressources

- [Documentation Docker](https://docs.docker.com/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Best Practices Django + Docker](https://docs.docker.com/samples/django/)
