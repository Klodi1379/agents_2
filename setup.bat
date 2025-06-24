@echo off
REM AI Company Setup Script for Windows
REM This script sets up the development environment for the AI Company project

echo 🤖 AI Company - Autonomous Business Analysis Platform Setup
echo =============================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Check if PostgreSQL is running (simple check)
echo 🗄️  Checking PostgreSQL...
pg_isready -q >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PostgreSQL might not be running or installed.
    echo Please make sure PostgreSQL is installed and running.
    echo Download from: https://www.postgresql.org/download/windows/
)

REM Check if Redis is running
echo 🔴 Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Redis might not be running or installed.
    echo For Windows, you can use Redis on WSL or download Windows version.
    echo Alternative: Use Docker for Redis
)

REM Copy environment file
if not exist .env (
    echo 📄 Creating environment file...
    copy .env.example .env
    echo ✅ Environment file created. Please edit .env with your API keys and settings.
) else (
    echo ✅ Environment file already exists
)

REM Create database
echo 🗄️  Setting up database...
python manage.py migrate

REM Create superuser
echo 👤 Creating superuser account...
echo Please enter details for the admin account:
python manage.py createsuperuser

REM Collect static files
echo 🎨 Collecting static files...
python manage.py collectstatic --noinput

REM Create logs directory
if not exist logs mkdir logs
echo ✅ Logs directory created

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit the .env file with your API keys:
echo    - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys
echo    - ANTHROPIC_API_KEY: Get from https://console.anthropic.com/
echo.
echo 2. Start the development server:
echo    python manage.py runserver
echo.
echo 3. In another command prompt, start Celery worker:
echo    celery -A ai_company worker --loglevel=info
echo.
echo 4. In another command prompt, start Celery beat (for scheduled tasks):
echo    celery -A ai_company beat --loglevel=info
echo.
echo 5. Visit http://localhost:8000 to access the application
echo.
echo 📖 For more information, see README.md
echo.
echo 🐳 To run with Docker instead:
echo    docker-compose up --build
echo.
pause
