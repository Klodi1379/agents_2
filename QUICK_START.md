# 🚀 Quick Local Setup Guide

## Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

## Quick Setup (5 minutes)

### 1. Clone and Setup Virtual Environment
```bash
# Clone project
git clone <repository-url>
cd ai_company

# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# At minimum, add your API keys:
# OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 4. Database Setup
```bash
# Create database (PostgreSQL)
createdb ai_company_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### 5. Start Services

#### Terminal 1: Django Server
```bash
python manage.py runserver
```

#### Terminal 2: Celery Worker
```bash
celery -A ai_company worker --loglevel=info
```

#### Terminal 3: Celery Beat (Optional)
```bash
celery -A ai_company beat --loglevel=info
```

## Access the Application

- **Web App**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

## Quick Test

1. Go to http://localhost:8000
2. Create an account or login
3. Click "Submit New Idea"
4. Fill out the form with a business idea
5. Watch the AI agents analyze it!

## Common Issues

### PostgreSQL not running
```bash
# macOS
brew services start postgresql

# Ubuntu
sudo service postgresql start

# Windows
# Start PostgreSQL service from Services app
```

### Redis not running
```bash
# macOS
brew services start redis

# Ubuntu
sudo service redis-server start

# Windows
# Start Redis service or use Docker
```

### Python dependencies issues
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Without API Keys

The system will work without API keys, but:
- AI analysis will fail
- You can test the interface
- Database and workflow still work

## Production Notes

For production:
- Set `DEBUG=False`
- Use proper database settings
- Configure HTTPS
- Use proper SECRET_KEY
- Set up proper logging
- Use process manager (gunicorn + nginx)

## Need Help?

Check:
- `README.md` for full documentation
- `DOCKER_SETUP.md` for Docker-specific setup
- Django logs for error details
- Celery logs for task failures
