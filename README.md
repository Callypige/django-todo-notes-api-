# Django Todo & Notes REST API

API REST avec deux apps Django interconnectées : **Notes** et **Todos**.

## Architecture

- Une **Note** peut avoir plusieurs **Todos**
- Une **Todo** peut référencer une **Note** (optionnel)
- Le statut d'une Note se met à jour automatiquement selon ses Todos (via signaux Django)
- Impossible de supprimer une Note si des Todos y sont liées (validation métier)

## Démarrage rapide

**Avec Docker :**
```bash
docker compose up -d
docker compose exec web python manage.py seed_demo
```

**Sans Docker :**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

> 💡 Variables d'environnement : voir `.env.example` pour la configuration

Accéder à l'API : **http://localhost:8000**

> ⚠️ Le serveur Docker affiche `0.0.0.0:8000` mais utilisez `localhost:8000` dans votre navigateur

## Documentation API

- **Swagger** : http://localhost:8000/api/docs/ (interactif)
- **ReDoc** : http://localhost:8000/api/redoc/
- **Schéma OpenAPI** : http://localhost:8000/api/schema/

## Endpoints

**Notes :** `/api/notes/` - CRUD complet  
**Todos :** `/api/todos/` - CRUD complet + `/api/todos/by_note/?note_id={id}`

**Filtres :** `?search=...&ordering=-created_at&page=2` (pagination 20/page)

## Exemples cURL

**Créer une note :**
```bash
curl -X POST http://localhost:8000/api/notes/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Ma note", "content": "Contenu"}'
```

**Créer une todo liée :**
```bash
curl -X POST http://localhost:8000/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Tâche", "status": "pending", "note": 1}'
```

**Supprimer une note (erreur si todos liées) :**
```bash
curl -X DELETE http://localhost:8000/api/notes/1/
# Retourne 400 si la note a des todos
```

## Règles métier

1. **Protection des Notes** : Impossible de supprimer une note si des todos y sont liées
2. **Statut automatique** : Le statut d'une note se met à jour selon ses todos (via signaux Django)
   - Toutes complétées → `completed`
   - Au moins une en cours → `in_progress`
   - Sinon → `active`

## Tests

```bash
python manage.py test  # 52 tests
```

## CI/CD

GitHub Actions exécute automatiquement les tests sur chaque push (Python 3.11 & 3.12).

Script local :
```bash
.\run-ci.ps1  # Windows
./run-ci.sh   # Linux/macOS
```

## Stack

Python 3.11+ • Django 5.2 • Django REST Framework • drf-spectacular • SQLite • Docker

## Documentation

Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour les choix techniques détaillés.
