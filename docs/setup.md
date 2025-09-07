# Incognito Technology Setup Guide

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+ with WSL2
- **Memory**: 16GB RAM minimum, 32GB recommended
- **Storage**: 100GB free space minimum
- **CPU**: 4+ cores recommended

### Required Software
- **Docker**: 20.10+ with Docker Compose v2
- **Node.js**: 18.x LTS
- **Python**: 3.11+
- **Git**: 2.30+
- **kubectl**: 1.25+ (for Kubernetes deployment)

## Quick Start

### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone https://github.com/your-org/incognito-technology.git
cd incognito-technology

# Install root dependencies
npm install

# Setup all services
npm run setup
```

### 2. Environment Configuration
```bash
# Copy environment templates
cp .env.example .env
cp frontend/.env.example frontend/.env.local
cp backend/fastapi-service/.env.example backend/fastapi-service/.env
cp backend/nodejs-service/.env.example backend/nodejs-service/.env

# Edit environment files with your configuration
nano .env
```

### 3. Start Development Environment
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
npm run dev:frontend    # Frontend only
npm run dev:backend     # Backend services only
npm run dev:blockchain  # Blockchain service only
```

### 4. Verify Installation
```bash
# Check service health
curl http://localhost:3000/health          # Frontend
curl http://localhost:8000/health          # FastAPI Backend
curl http://localhost:8001/health          # Node.js Backend
curl http://localhost:8002/health          # AI/ML Service

# Access web interfaces
open http://localhost:3000                 # Main Application
open http://localhost:3001                 # Grafana Dashboard
open http://localhost:5601                 # Kibana Logs
open http://localhost:9090                 # Prometheus Metrics
```

## Detailed Setup Instructions

### Frontend Setup (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local

# Required environment variables:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_BLOCKCHAIN_URL=http://localhost:8545
# NEXTAUTH_SECRET=your-secret-key
# NEXTAUTH_URL=http://localhost:3000

# Start development server
npm run dev
```

### Backend Setup (FastAPI)
```bash
cd backend/fastapi-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Required environment variables:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/incognito_db
# MONGODB_URL=mongodb://admin:password@localhost:27017/incognito_logs
# REDIS_URL=redis://localhost:6379
# JWT_SECRET=your-jwt-secret
# ENCRYPTION_KEY=your-32-byte-encryption-key

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Backend Setup (Node.js)
```bash
cd backend/nodejs-service

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env

# Required environment variables:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/incognito_db
# MONGODB_URL=mongodb://admin:password@localhost:27017/incognito_logs
# REDIS_URL=redis://localhost:6379
# JWT_SECRET=your-jwt-secret
# PORT=8001

# Start development server
npm run dev
```

### AI/ML Setup
```bash
cd ai-ml

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Download pre-trained models (optional)
python scripts/download_models.py

# Start AI service
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### Blockchain Setup
```bash
cd blockchain

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env

# Compile smart contracts
npm run compile

# Deploy contracts to local network
npm run deploy:local

# Start blockchain service
npm start
```

## Database Setup

### PostgreSQL Setup
```bash
# Using Docker (recommended)
docker run -d \
  --name postgres \
  -e POSTGRES_DB=incognito_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize database schema
psql -h localhost -U postgres -d incognito_db -f database/postgresql/init.sql
```

### MongoDB Setup
```bash
# Using Docker (recommended)
docker run -d \
  --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -p 27017:27017 \
  mongo:7.0

# Initialize collections
mongosh --host localhost:27017 -u admin -p password --authenticationDatabase admin < database/mongodb/init.js
```

## Security Configuration

### SSL/TLS Setup
```bash
# Generate self-signed certificates for development
mkdir -p devops/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout devops/nginx/ssl/key.pem \
  -out devops/nginx/ssl/cert.pem \
  -subj "/C=US/ST=CA/L=San Francisco/O=Incognito Technology/CN=localhost"
```

### Encryption Keys Setup
```bash
# Generate encryption keys
python scripts/generate_keys.py

# Store keys securely (use environment variables or key management service)
export ENCRYPTION_KEY=$(cat keys/encryption.key)
export JWT_SECRET=$(cat keys/jwt.secret)
```

## Development Workflow

### Code Quality
```bash
# Run linting
npm run lint

# Run type checking
npm run type-check

# Run tests
npm test

# Run security scans
npm run security:scan
```

### Database Migrations
```bash
# Create new migration (FastAPI)
cd backend/fastapi-service
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Docker Development
```bash
# Build all images
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Clean up volumes (WARNING: This will delete all data)
docker-compose down -v
```

## Production Deployment

### Kubernetes Deployment
```bash
# Setup kubectl context
kubectl config use-context your-cluster

# Create namespace
kubectl apply -f devops/kubernetes/production/namespace.yaml

# Deploy secrets
kubectl create secret generic app-secrets \
  --from-env-file=.env.production \
  -n incognito-production

# Deploy applications
kubectl apply -f devops/kubernetes/production/

# Check deployment status
kubectl get pods -n incognito-production
kubectl rollout status deployment/frontend -n incognito-production
```

### Environment Variables for Production
```bash
# Database connections
DATABASE_URL=postgresql://user:pass@prod-db:5432/incognito_db
MONGODB_URL=mongodb://user:pass@prod-mongo:27017/incognito_logs
REDIS_URL=redis://prod-redis:6379

# Security
JWT_SECRET=your-production-jwt-secret
ENCRYPTION_KEY=your-production-encryption-key
TLS_CERT_PATH=/etc/ssl/certs/cert.pem
TLS_KEY_PATH=/etc/ssl/private/key.pem

# External services
BLOCKCHAIN_NETWORK_URL=https://mainnet.infura.io/v3/your-project-id
AI_MODEL_REGISTRY_URL=https://your-model-registry.com
SIEM_ENDPOINT=https://your-siem-provider.com/api

# Monitoring
PROMETHEUS_URL=https://prometheus.your-domain.com
GRAFANA_URL=https://grafana.your-domain.com
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Monitoring and Observability

### Prometheus Metrics
- Access Prometheus at `http://localhost:9090`
- Custom metrics available at `/metrics` endpoints
- Alert rules configured in `devops/monitoring/alert_rules.yml`

### Grafana Dashboards
- Access Grafana at `http://localhost:3001` (admin/admin)
- Pre-configured dashboards for all services
- Custom dashboards in `devops/monitoring/grafana/dashboards/`

### Logging with ELK Stack
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`
- Logs automatically collected from all services

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using a port
lsof -i :3000

# Kill process using port
kill -9 $(lsof -t -i:3000)
```

#### Database Connection Issues
```bash
# Check database connectivity
pg_isready -h localhost -p 5432

# Check MongoDB connectivity
mongosh --host localhost:27017 --eval "db.adminCommand('ping')"
```

#### Docker Issues
```bash
# Clean Docker system
docker system prune -a

# Rebuild containers
docker-compose build --no-cache

# Check container logs
docker-compose logs [service-name]
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Advanced > Memory
```

### Getting Help

1. **Documentation**: Check `/docs` folder for detailed guides
2. **Issues**: Create GitHub issue with detailed error information
3. **Logs**: Always include relevant logs when reporting issues
4. **Environment**: Specify your OS, Docker version, and Node.js version

### Development Best Practices

1. **Never commit secrets** - Use environment variables
2. **Run tests** before pushing code
3. **Follow security guidelines** in `/security/policies/`
4. **Use feature branches** for development
5. **Keep dependencies updated** regularly
6. **Document API changes** in OpenAPI specs
7. **Monitor resource usage** during development

## Next Steps

After successful setup:

1. **Configure authentication** - Set up OAuth providers
2. **Load sample data** - Use scripts in `/scripts/sample-data/`
3. **Configure monitoring** - Set up alerts and dashboards
4. **Security hardening** - Follow production security checklist
5. **Performance testing** - Run load tests with sample data
6. **Compliance setup** - Configure HIPAA/GDPR compliance features

For detailed module-specific documentation, see:
- [Frontend Guide](./frontend.md)
- [Backend API Guide](./api.md)
- [AI/ML Guide](./ai-ml.md)
- [Blockchain Guide](./blockchain.md)
- [Security Guide](./security.md)
- [Deployment Guide](./deployment.md)
