#!/bin/bash

# Database setup script for OmniScope AI
# This script initializes PostgreSQL database and runs Prisma migrations

set -e

echo "🚀 Setting up OmniScope AI database..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set. Using default from .env.example"
    export DATABASE_URL="postgresql://omniscope:omniscope_password@localhost:5432/omniscope_db?schema=public"
fi

echo "📦 Installing dependencies..."
npm install

echo "🔄 Generating Prisma Client..."
npx prisma generate

echo "🗄️  Creating database schema..."
npx prisma db push

echo "✅ Database setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the development server: npm run dev"
echo "2. Or start with custom server: npm run dev:custom"
