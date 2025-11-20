# Script CI local for windows powershell
# Usage: .\run-ci.ps1

Write-Host "=== CI Pipeline Local ===" -ForegroundColor Cyan

# Variables
$env:DJANGO_SETTINGS_MODULE = "config.settings"
$env:SECRET_KEY = "local-ci-test-secret-key"

# Step 1: Install dependencies
Write-Host "`n[1/4] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ DDependencies installed" -ForegroundColor Green

# Step 2: Migrations
Write-Host "`n[2/4] Applying migrations..." -ForegroundColor Yellow
python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to apply migrations" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Migrations applied" -ForegroundColor Green

# Step 3: Tests
Write-Host "`n[3/4] Running tests..." -ForegroundColor Yellow
python manage.py test
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ All tests passed" -ForegroundColor Green

# Step 4: Validate seed_demo
Write-Host "`n[4/4] Validating seed_demo..." -ForegroundColor Yellow
python manage.py seed_demo --force
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ seed_demo failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ seed_demo succeeded" -ForegroundColor Green

Write-Host "`n=== ✅ CI Pipeline SUCCESS ===" -ForegroundColor Green
