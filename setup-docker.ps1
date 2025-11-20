# setup-docker.ps1 - Complete Docker setup and launcher

Write-Host "🐳 Configuration Docker pour django-todo-notes-api" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Gray

# Verify that Docker is installed
Write-Host "`n🔍 Verifying Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verify that Docker Compose is available
Write-Host "`n🔍 Verifying Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker compose version
    Write-Host "✅ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available" -ForegroundColor Red
    exit 1
}

# Verify that Docker files exist
Write-Host "`n📁 Verifying Docker files..." -ForegroundColor Yellow
$requiredFiles = @("Dockerfile", "docker-compose.yml", "docker-entrypoint.sh", ".dockerignore")
$allFilesExist = $true

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file manquant" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "`n❌ Some Docker files are missing" -ForegroundColor Red
    exit 1
}

# Interactive menu
Write-Host "`n" + "=" * 70 -ForegroundColor Gray
Write-Host "🚀 STARTUP OPTIONS" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Gray
Write-Host ""
Write-Host "1. 🏗️  Build and start (first time)" -ForegroundColor White
Write-Host "2. ▶️  Start (existing containers)" -ForegroundColor White
Write-Host "3. ⏹️  Stop containers" -ForegroundColor White
Write-Host "4. 🗑️  Stop and remove (clean)" -ForegroundColor White
Write-Host "5. 📊 Load demo data" -ForegroundColor White
Write-Host "6. 📋 View logs" -ForegroundColor White
Write-Host "7. 🔍 Container status" -ForegroundColor White
Write-Host "8. 🚪 Quit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose an option (1-8)"

switch ($choice) {
    "1" {
        Write-Host "`n🏗️  Building and starting containers..." -ForegroundColor Cyan
        docker compose build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build succeeded!" -ForegroundColor Green
            docker compose up -d
            if ($LASTEXITCODE -eq 0) {
                Write-Host "`n✅ Application started!" -ForegroundColor Green
                Write-Host "`n🌐 The API is accessible at:" -ForegroundColor Cyan
                Write-Host "   - http://localhost:8000" -ForegroundColor White
                Write-Host "   - Swagger Documentation: http://localhost:8000/api/docs/" -ForegroundColor White
                Write-Host "   - Django Admin: http://localhost:8000/admin/" -ForegroundColor White
                Write-Host "     (admin/admin)" -ForegroundColor Gray
                Write-Host "`n📋 To view logs: docker compose logs -f" -ForegroundColor Yellow
            }
        }
    }
    "2" {
        Write-Host "`n▶️  Starting containers..." -ForegroundColor Cyan
        docker compose up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Containers started!" -ForegroundColor Green
        }
    }
    "3" {
        Write-Host "`n⏹️  Stopping containers..." -ForegroundColor Cyan
        docker compose stop
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Containers stopped!" -ForegroundColor Green
        }
    }
    "4" {
        Write-Host "`n🗑️  Stopping and removing containers..." -ForegroundColor Cyan
        $confirm = Read-Host "Do you also want to remove volumes (data)? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            docker compose down -v
            Write-Host "✅ Containers and volumes removed!" -ForegroundColor Green
        } else {
            docker compose down
            Write-Host "✅ Containers removed (volumes preserved)!" -ForegroundColor Green
        }
    }
    "5" {
        Write-Host "`n📊 Loading demo data..." -ForegroundColor Cyan
        docker compose exec web python manage.py seed_demo
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Demo data loaded!" -ForegroundColor Green
        }
    }
    "6" {
        Write-Host "`n📋 Viewing logs (Ctrl+C to quit)..." -ForegroundColor Cyan
        docker compose logs -f
    }
    "7" {
        Write-Host "`n🔍 Container status:" -ForegroundColor Cyan
        docker compose ps
        Write-Host "`n📊 Resource usage:" -ForegroundColor Cyan
        docker stats --no-stream
    }
    "8" {
        Write-Host "`n👋 Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "`n❌ Invalid option" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
