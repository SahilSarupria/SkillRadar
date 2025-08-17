#!/bin/bash

# AI Resume Converter - Docker Setup Script
echo "🐳 Setting up AI Resume Converter with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration."
    echo "   Required: OPENAI_API_KEY"
fi

# Build and start services
echo "🏗️  Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d db redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm web python manage.py makemigrations
docker-compose run --rm web python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
docker-compose run --rm web python manage.py createsuperuser

# Setup initial data
echo "🌱 Setting up initial data..."
docker-compose run --rm web python manage.py setup_initial_data

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

echo "✅ Docker setup complete!"
echo ""
echo "🌐 Services running:"
echo "   - Web API: http://localhost:8000"
echo "   - Admin Panel: http://localhost:8000/admin/"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "🎯 Don't forget to set your OPENAI_API_KEY in the .env file!"
