#!/bin/bash

# Stop development infrastructure services

echo "🛑 Stopping OmniScope AI infrastructure services..."

docker-compose -f docker-compose.dev.yml down

echo "✅ All services stopped"
echo ""
echo "To remove all data volumes as well, run:"
echo "   docker-compose -f docker-compose.dev.yml down -v"
