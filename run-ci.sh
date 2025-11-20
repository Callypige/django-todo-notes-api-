#!/bin/bash
# Script CI local for Linux/macOS
# Usage: ./run-ci.sh

set -e  # Exit on error

echo "=== CI Pipeline Local ==="

# Variables
export DJANGO_SETTINGS_MODULE="config.settings"
export SECRET_KEY="local-ci-test-secret-key"

# Step 1: Install dependencies
echo -e "\n[1/4] Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo "✅ DDependencies installed"
# Step 2: Migrations
echo -e "\n[2/4] Applying migrations..."
python manage.py migrate --noinput
echo "✅ Migrations applied"
# Step 3: Tests
echo -e "\n[3/4] Running tests..."
python manage.py test
echo "✅ All tests passed"
# Step 4: Validate seed_demo
echo -e "\n[4/4] Validating seed_demo..."
python manage.py seed_demo --force
echo "✅ seed_demo succeeded"
echo -e "\n=== ✅ CI Pipeline SUCCESS ==="