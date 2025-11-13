# Infrastructure Setup Guide

This guide explains how to set up the infrastructure for OmniScope AI's advanced features.

## Overview

The infrastructure includes:
- **PostgreSQL**: Primary database for users, workspaces, models, reports, and audit logs
- **Redis**: Cache for sessions, external API data, and rate limiting
- **RabbitMQ**: Message queue for distributed processing tasks

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ and npm
- Python 3.9+ (for backend)

## Quick Start

### Option 1: Development Mode (Recommended for Development)

Run only infrastructure services in Docker, run frontend/backend locally:

```bash
# Start infrastructure services
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be healthy
docker-compose -f docker-compose.dev.yml ps

# Set up environment variables
cp .env.example .env

# Install dependencies and set up database
npm install
npm run db:generate
npm run db:push

# Start backend (in one terminal)
cd backend_db
python -m uvicorn main:app --reload --port 8001

# Start frontend (in another terminal)
npm run dev
```

### Option 2: Full Docker Mode (Production-like)

Run all services in Docker:

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

## Service Details

### PostgreSQL

- **Port**: 5432
- **Database**: omniscope_db
- **User**: omniscope
- **Password**: omniscope_password (change in production!)
- **Connection String**: `postgresql://omniscope:omniscope_password@localhost:5432/omniscope_db?schema=public`

**Access PostgreSQL CLI**:
```bash
docker exec -it omniscope-postgres-dev psql -U omniscope -d omniscope_db
```

**Common Commands**:
```sql
-- List all tables
\dt

-- Describe a table
\d users

-- Query users
SELECT * FROM users;

-- Exit
\q
```

### Redis

- **Port**: 6379
- **No password** (set REDIS_PASSWORD in production)

**Access Redis CLI**:
```bash
docker exec -it omniscope-redis-dev redis-cli
```

**Common Commands**:
```bash
# Check connection
PING

# List all keys
KEYS *

# Get a value
GET session:abc123

# Check TTL
TTL session:abc123

# Exit
exit
```

### RabbitMQ

- **AMQP Port**: 5672
- **Management UI**: http://localhost:15672
- **User**: omniscope
- **Password**: omniscope_password

**Access Management UI**:
Open http://localhost:15672 in your browser and login with the credentials above.

## Database Schema

The PostgreSQL database includes the following tables:

### Users & Authentication
- `users` - User accounts with MFA support
- `roles` - Role definitions (Admin, PI, Researcher, Analyst, Viewer)
- `user_roles` - User-role assignments

### Collaboration
- `workspaces` - Shared analysis workspaces
- `workspace_members` - Workspace membership and permissions

### ML & Analysis
- `ml_models` - Trained machine learning models
- `reports` - Generated reports

### Extensions
- `plugins` - Installed custom plugins
- `audit_logs` - Security and compliance audit trail

## Redis Cache Structure

Redis uses the following key naming conventions:

```
session:{session_id}              # User sessions (TTL: 24h)
integration:gene:{gene_id}        # Gene annotations (TTL: 7d)
integration:pathway:{pathway_id}  # Pathway data (TTL: 7d)
literature:paper:{pmid}           # Research papers (TTL: 30d)
rate_limit:{user_id}:{endpoint}   # Rate limiting (TTL: 1m)
```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL="postgresql://omniscope:omniscope_password@localhost:5432/omniscope_db?schema=public"

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=omniscope
RABBITMQ_PASSWORD=omniscope_password

# Application
NODE_ENV=development
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Database Migrations

### Using Prisma

```bash
# Generate Prisma Client
npm run db:generate

# Push schema to database (development)
npm run db:push

# Create a migration (production)
npm run db:migrate

# Reset database (WARNING: deletes all data)
npm run db:reset
```

### Manual SQL Migration

If you need to run the SQL migration manually:

```bash
docker exec -i omniscope-postgres-dev psql -U omniscope -d omniscope_db < prisma/migrations/init_schema.sql
```

## Health Checks

Check if all services are running:

```bash
# Check Docker services
docker-compose -f docker-compose.dev.yml ps

# Check PostgreSQL
docker exec omniscope-postgres-dev pg_isready -U omniscope

# Check Redis
docker exec omniscope-redis-dev redis-cli ping

# Check RabbitMQ
docker exec omniscope-rabbitmq-dev rabbitmq-diagnostics ping
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# View PostgreSQL logs
docker logs omniscope-postgres-dev

# Restart PostgreSQL
docker-compose -f docker-compose.dev.yml restart postgres
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker ps | grep redis

# View Redis logs
docker logs omniscope-redis-dev

# Test connection
docker exec omniscope-redis-dev redis-cli ping
```

### RabbitMQ Connection Issues

```bash
# Check if RabbitMQ is running
docker ps | grep rabbitmq

# View RabbitMQ logs
docker logs omniscope-rabbitmq-dev

# Check management UI
curl http://localhost:15672
```

### Port Conflicts

If ports are already in use:

```bash
# Check what's using a port
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :5672  # RabbitMQ

# Kill the process or change ports in docker-compose.dev.yml
```

## Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.dev.yml down -v
```

## Production Considerations

For production deployment:

1. **Change default passwords** in all services
2. **Enable SSL/TLS** for PostgreSQL and Redis
3. **Set up backups** for PostgreSQL
4. **Configure Redis persistence** (AOF or RDB)
5. **Enable RabbitMQ clustering** for high availability
6. **Use managed services** (AWS RDS, ElastiCache, Amazon MQ) for better reliability
7. **Set up monitoring** with Prometheus and Grafana
8. **Configure proper network security** (VPC, security groups)

## Next Steps

After setting up the infrastructure:

1. Review the [Requirements Document](.kiro/specs/advanced-features-upgrade/requirements.md)
2. Review the [Design Document](.kiro/specs/advanced-features-upgrade/design.md)
3. Start implementing features from [Tasks](.kiro/specs/advanced-features-upgrade/tasks.md)
4. Begin with Task 2: Authentication and Security Foundation
