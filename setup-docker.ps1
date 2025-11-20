# setup-docker.ps1 - Complete Docker configuration

Write-Host "🐳 Configuration Docker pour django-todo-notes-api" -ForegroundColor Cyan

# Create Dockerfile
Write-Host "
📄 Creating Dockerfile..." -ForegroundColor Yellow
@'
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
'@ | Out-File -FilePath Dockerfile -Encoding utf8

# Create docker-compose.yml
Write-Host "📄 Creating docker-compose.yml..." -ForegroundColor Yellow
@'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: todonotesdb
      POSTGRES_USER: todouser
      POSTGRES_PASSWORD: todopass
    ports:
      - "5432:5432"

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - POSTGRES_DB=todonotesdb
      - POSTGRES_USER=todouser
      - POSTGRES_PASSWORD=todopass
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
    depends_on:
      - db

volumes:
  postgres_data:
'@ | Out-File -FilePath docker-compose.yml -Encoding utf8

# Create .dockerignore
Write-Host "📄 Creating .dockerignore..." -ForegroundColor Yellow
@'
__pycache__/
*.py[cod]
venv/
*.log
db.sqlite3
.git
.dockerignore
Dockerfile
docker-compose.yml
.vscode/
.idea/
*.md
'@ | Out-File -FilePath .dockerignore -Encoding utf8

# Add psycopg2
Write-Host "📦 Adding psycopg2-binary..." -ForegroundColor Yellow
if (!(Select-String -Path requirements.txt -Pattern "psycopg2-binary" -Quiet)) {
    Add-Content -Path requirements.txt -Value "psycopg2-binary==2.9.9"
}

Write-Host "
✅ Docker configuration completed!" -ForegroundColor Green
Write-Host "
🚀 To launch the project :" -ForegroundColor Cyan
Write-Host "   docker-compose build" -ForegroundColor White
Write-Host "   docker-compose up" -ForegroundColor White
