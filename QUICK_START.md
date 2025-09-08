# Quick Start Guide - Incognito Technology

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+
- Git

## 🚀 Quick Start (Docker Compose)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your actual values

# 2. Start all services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f
```

**Access Points:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Auth Service: http://localhost:3001/health

## 🛠️ Development Mode

### Frontend Development
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Backend Development
```bash
# FastAPI Backend
cd backend/fastapi_app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Node.js Auth Service
cd backend/node_services/auth-service
npm install
npm run dev
# Runs on http://localhost:3001
```

### Database Setup
```bash
# Start databases only
docker-compose up -d postgres mongodb redis

# Run migrations
cd backend/fastapi_app
alembic upgrade head

# Seed data (optional)
python scripts/seed_data.py
```

## 🧪 Testing

```bash
# Run all tests
make test

# Frontend tests
cd frontend && npm test

# Backend tests
cd backend/fastapi_app && pytest

# E2E tests
cd tests && npm test
```

## 🔧 Available Commands

```bash
# Development
make setup          # Initial project setup
make dev            # Start development servers
make test           # Run all tests
make lint           # Run linters

# Docker
make docker-build   # Build all images
make docker-up      # Start containers
make docker-down    # Stop containers

# Database
make db-migrate     # Run migrations
make db-seed        # Seed test data
make db-reset       # Reset database

# Deployment
make deploy-staging # Deploy to staging
make deploy-prod    # Deploy to production
```

## 🔐 Environment Variables

Key variables to set in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/incognito
MONGODB_URL=mongodb://localhost:27017/incognito
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your-super-secret-jwt-key
ENCRYPTION_KEY=your-32-character-encryption-key

# External Services
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## 🚨 Troubleshooting

### Port Conflicts
```bash
# Check what's using ports
lsof -i :3000,8000,3001,5432,27017,6379

# Stop conflicting services
sudo systemctl stop postgresql
sudo systemctl stop redis
```

### Database Connection Issues
```bash
# Check database connectivity
docker-compose exec postgres psql -U postgres -d incognito -c "SELECT 1;"
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

## 📊 Monitoring

- **Health Checks**: 
  - Frontend: http://localhost:3000/api/health
  - Backend: http://localhost:8000/health
  - Auth: http://localhost:3001/health

- **Logs**:
  ```bash
  docker-compose logs -f [service_name]
  tail -f logs/*.log
  ```

## 🔄 Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose build --no-cache

# Update dependencies
cd frontend && npm update
cd backend/fastapi_app && pip install -r requirements.txt --upgrade
```
