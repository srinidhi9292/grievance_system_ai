#!/bin/bash
# ============================================================
# SmartGriev - Quick Setup Script
# ============================================================
set -e

echo "============================================================"
echo "  SmartGriev - AI-Powered Grievance Management Setup"
echo "============================================================"

# 1. Install dependencies
echo ""
echo "1. Installing Python dependencies..."
pip install -r requirements.txt

# 2. Create .env file
echo ""
echo "2. Creating environment file..."
if [ ! -f .env ]; then
cat > .env << 'EOF'
SECRET_KEY=django-insecure-change-this-for-production-use-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
echo "   .env created"
else
echo "   .env already exists, skipping"
fi

# 3. Run migrations
echo ""
echo "3. Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 4. Collect static files
echo ""
echo "4. Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || echo "   Static files collection skipped"

# 5. Seed demo data
echo ""
echo "5. Seeding demo data..."
python manage.py seed_data

echo ""
echo "============================================================"
echo "  ✅ Setup Complete!"
echo "============================================================"
echo ""
echo "  Start the server: python manage.py runserver"
echo "  URL: http://127.0.0.1:8000"
echo ""
echo "  Login Credentials:"
echo "  ┌─────────────────────────────────────────┐"
echo "  │ Admin:   admin / admin123               │"
echo "  │ Citizen: citizen / citizen123           │"
echo "  └─────────────────────────────────────────┘"
echo ""
