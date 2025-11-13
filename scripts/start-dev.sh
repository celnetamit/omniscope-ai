#!/bin/bash

# Development startup script for OmniScope AI
# This script starts infrastructure services and provides instructions for running the app

set -e

echo "🚀 Starting OmniScope AI Development Environment"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

echo "📦 Starting infrastructure services (PostgreSQL, Redis, RabbitMQ)..."
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check service health
echo ""
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker exec omniscope-postgres-dev pg_isready -U omniscope > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "⚠️  PostgreSQL is not ready yet, please wait a moment"
fi

# Check Redis
if docker exec omniscope-redis-dev redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "⚠️  Redis is not ready yet, please wait a moment"
fi

# Check RabbitMQ
if docker exec omniscope-rabbitmq-dev rabbitmq-diagnostics ping > /dev/null 2>&1; then
    echo "✅ RabbitMQ is ready"
else
    echo "⚠️  RabbitMQ is not ready yet, please wait a moment"
fi

echo ""
echo "📊 Service URLs:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - RabbitMQ AMQP: localhost:5672"
echo "  - RabbitMQ Management: http://localhost:15672 (user: omniscope, pass: omniscope_password)"

echo ""
echo "📝 Next steps:"
echo ""
echo "1. Set up environment variables (if not done):"
echo "   cp .env.example .env"
echo ""
echo "2. Install dependencies and set up database:"
echo "   npm install"
echo "   npm run db:generate"
echo "   npm run db:push"
echo ""
echo "3. Start the backend (in a new terminal):"
echo "   python main.py"
echo ""
echo "4. Start the frontend (in another terminal):"
echo "   npm run dev"
echo ""
echo "5. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "To stop infrastructure services:"
echo "   docker-compose -f docker-compose.dev.yml down"
echo ""
echo "For more information, see INFRASTRUCTURE_SETUP.md"
