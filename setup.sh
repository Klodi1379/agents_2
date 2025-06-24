#!/bin/bash

# AI Company Setup Script
# This script sets up the development environment for the AI Company project

echo "🤖 AI Company - Autonomous Business Analysis Platform Setup"
echo "============================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python $required_version or higher is required. You have Python $python_version."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if PostgreSQL is running
if command -v pg_isready &> /dev/null; then
    if pg_isready -q; then
        echo "✅ PostgreSQL is running"
    else
        echo "⚠️  PostgreSQL is not running. Please start PostgreSQL service."
        echo "   On macOS: brew services start postgresql"
        echo "   On Ubuntu: sudo service postgresql start"
        echo "   On Windows: Start PostgreSQL service from Services app"
    fi
else
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL."
    echo "   On macOS: brew install postgresql"
    echo "   On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "   On Windows: Download from https://www.postgresql.org/download/"
fi

# Check if Redis is running
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running. Please start Redis server."
        echo "   On macOS: brew services start redis"
        echo "   On Ubuntu: sudo service redis-server start"
        echo "   On Windows: Start Redis service"
    fi
else
    echo "⚠️  Redis not found. Please install Redis."
    echo "   On macOS: brew install redis"
    echo "   On Ubuntu: sudo apt-get install redis-server"
    echo "   On Windows: Download from https://redis.io/download"
fi

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating environment file..."
    cp .env.example .env
    echo "✅ Environment file created. Please edit .env with your API keys and settings."
else
    echo "✅ Environment file already exists"
fi

# Create database
echo "🗄️  Setting up database..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser account..."
echo "Please enter details for the admin account:"
python manage.py createsuperuser

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit the .env file with your API keys:"
echo "   - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys"
echo "   - ANTHROPIC_API_KEY: Get from https://console.anthropic.com/"
echo ""
echo "2. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. In another terminal, start Celery worker:"
echo "   celery -A ai_company worker --loglevel=info"
echo ""
echo "4. In another terminal, start Celery beat (for scheduled tasks):"
echo "   celery -A ai_company beat --loglevel=info"
echo ""
echo "5. Visit http://localhost:8000 to access the application"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "🐳 To run with Docker instead:"
echo "   docker-compose up --build"
