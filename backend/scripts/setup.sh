#!/bin/bash

# AI Resume Converter - Setup Script
echo "🚀 Setting up AI Resume Converter Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Please install PostgreSQL 12+ first."
    echo "   Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "   macOS: brew install postgresql"
    echo "   Windows: Download from https://www.postgresql.org/download/"
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis is not installed. Please install Redis 6+ first."
    echo "   Ubuntu/Debian: sudo apt-get install redis-server"
    echo "   macOS: brew install redis"
    echo "   Windows: Download from https://redis.io/download"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   Required: OPENAI_API_KEY, DATABASE_URL"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs media staticfiles

# Database setup
echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "Please create an admin user:"
python manage.py createsuperuser

# Setup initial data
echo "🌱 Setting up initial data..."
python manage.py setup_initial_data

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the development server:"
echo "   1. Start Redis: redis-server"
echo "   2. Start Celery worker: celery -A resume_converter worker -l info"
echo "   3. Start Celery beat: celery -A resume_converter beat -l info"
echo "   4. Start Django: python manage.py runserver"
echo ""
echo "🐳 Or use Docker:"
echo "   docker-compose up"
echo ""
echo "📖 API Documentation will be available at: http://localhost:8000/admin/"
echo "🎯 Don't forget to set your OPENAI_API_KEY in the .env file!"
