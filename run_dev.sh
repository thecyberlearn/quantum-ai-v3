#!/bin/bash
# Development server startup script
# Ensures clean environment for Django development

echo "🚀 Starting Django Development Server"
echo "======================================"

# Clear any DATABASE_URL that might interfere with local development
unset DATABASE_URL

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check database configuration
echo "🔍 Checking database configuration..."
python manage.py check_db

echo ""
echo "🌐 Starting Django server..."
echo "Visit: http://localhost:8000"
echo "Admin: http://localhost:8000/admin"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"

# Start the development server
python manage.py runserver