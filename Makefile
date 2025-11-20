.PHONY: help build up down restart logs shell test clean migrate seed health

# Variables
DOCKER_COMPOSE = docker compose
SERVICE = web

help: ## Display this help message
	@echo "🐳 Django Todo Notes API - Docker Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	@echo "🏗️  Building Docker images..."
	$(DOCKER_COMPOSE) build

up: ## Start the application
	@echo "🚀 Starting application..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Application started!"
	@echo "📍 API: http://localhost:8000"
	@echo "📍 Docs: http://localhost:8000/api/docs/"
	@echo "📍 Admin: http://localhost:8000/admin/ (admin/admin)"

down: ## Stop the application
	@echo "⏹️  Stopping application..."
	$(DOCKER_COMPOSE) down

restart: ## Restart the application
	@echo "🔄 Restarting application..."
	$(DOCKER_COMPOSE) restart

logs: ## View logs
	$(DOCKER_COMPOSE) logs -f $(SERVICE)

shell: ## Open a Django shell
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py shell

bash: ## Open a bash shell in the container
	$(DOCKER_COMPOSE) exec $(SERVICE) /bin/sh

test: ## Run tests
	@echo "🧪 Running tests..."
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py test

migrate: ## Run migrations
	@echo "📦 Running migrations..."
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py migrate

makemigrations: ## Create new migrations
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py makemigrations

seed: ## Load demo data
	@echo "📊 Loading demo data..."
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py seed_demo

superuser: ## Create a superuser
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py createsuperuser

health: ## Check health status
	@echo "🏥 Checking application health..."
	@curl -s http://localhost:8000/api/health/ | python -m json.tool || echo "❌ Application not responding"

status: ## Check container status
	$(DOCKER_COMPOSE) ps

clean: ## Clean containers and volumes
	@echo "🗑️  Cleaning up..."
	$(DOCKER_COMPOSE) down -v
	@echo "✅ Cleaned!"

clean-all: clean ## Clean everything (containers, volumes, images)
	@echo "🗑️  Removing images..."
	$(DOCKER_COMPOSE) down --rmi all -v
	@echo "✅ Everything cleaned!"

dev: build up logs ## Build, start and view logs

prod-build: ## Build for production
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml build

backup: ## Export datas to a JSON file
	@echo "💾 Backing up database..."
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py dumpdata > backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "✅ Backup created!"

restore: ## Import data (usage: make restore FILE=backup.json)
	@echo "📥 Restoring database..."
	$(DOCKER_COMPOSE) exec -T $(SERVICE) python manage.py loaddata < $(FILE)
	@echo "✅ Database restored!"
