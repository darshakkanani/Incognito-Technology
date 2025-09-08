# Deployment Guide

## Prerequisites

### System Requirements
- Kubernetes cluster (1.25+)
- Docker registry access
- PostgreSQL database
- MongoDB instance
- Redis cache
- SSL certificates

### Required Tools
- kubectl (1.25+)
- Docker (20.10+)
- Helm (3.8+)
- Terraform (1.0+)

## Environment Setup

### Development Environment
```bash
# Start local development
make setup
make dev

# Verify services
curl http://localhost:3000/health    # Frontend
curl http://localhost:8000/health    # Backend API
curl http://localhost:8001/health    # Auth Service
```

### Staging Environment
```bash
# Deploy to staging
kubectl config use-context staging-cluster
kubectl apply -f devops/k8s/staging/
```

### Production Environment
```bash
# Deploy to production
kubectl config use-context production-cluster
kubectl apply -f devops/k8s/production/
```

## Database Setup

### PostgreSQL Migration
```bash
# Run migrations
kubectl exec -it deployment/fastapi-backend -- alembic upgrade head

# Seed initial data
kubectl exec -it deployment/fastapi-backend -- python scripts/seed_data.py
```

### MongoDB Initialization
```bash
# Initialize collections
kubectl exec -it deployment/mongodb -- mongosh < database/mongodb_init.js
```

## SSL Configuration

### Certificate Management
```bash
# Generate certificates (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt

# Create Kubernetes secret
kubectl create secret tls incognito-tls \
  --cert=tls.crt --key=tls.key
```

## Monitoring Setup

### Prometheus & Grafana
```bash
# Deploy monitoring stack
kubectl apply -f devops/k8s/monitoring/

# Access Grafana
kubectl port-forward svc/grafana 3000:3000
```

## Backup & Recovery

### Database Backup
```bash
# PostgreSQL backup
kubectl exec deployment/postgres -- pg_dump incognito_db > backup.sql

# MongoDB backup
kubectl exec deployment/mongodb -- mongodump --db incognito_logs
```

### Disaster Recovery
```bash
# Restore from backup
kubectl exec -i deployment/postgres -- psql incognito_db < backup.sql
```
