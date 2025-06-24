#!/bin/bash
# Quick test to verify Docker setup

echo "🧪 Testing Docker setup..."

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down

# Rebuild and start
echo "Building and starting containers..."
docker-compose up --build -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check service health
echo "Checking service health..."

# Check web service
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Web service is responding"
else
    echo "❌ Web service is not responding"
    echo "Web service logs:"
    docker-compose logs web | tail -20
fi

# Check database
if docker-compose exec -T db pg_isready -q; then
    echo "✅ Database is healthy"
else
    echo "❌ Database is not ready"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis is not responding"
fi

# Check Celery worker
if docker-compose logs celery | grep -q "ready"; then
    echo "✅ Celery worker is ready"
else
    echo "❌ Celery worker is not ready"
    echo "Celery logs:"
    docker-compose logs celery | tail -10
fi

echo "📊 Service Status:"
docker-compose ps

echo "🔗 Access URLs:"
echo "  Web Application: http://localhost:8000"
echo "  Admin Panel: http://localhost:8000/admin/"
echo "  API: http://localhost:8000/api/"

echo "🔍 For detailed logs, run:"
echo "  docker-compose logs [service_name]"
