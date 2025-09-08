.PHONY: help setup dev build test lint clean docker-build docker-up docker-down deploy

# Default target
help:
	@echo "Incognito Technology - Available Commands:"
	@echo ""
	@echo "  setup          - Initial project setup"
	@echo "  dev            - Start development environment"
	@echo "  build          - Build all services"
	@echo "  test           - Run all tests"
	@echo "  lint           - Run linting on all code"
	@echo "  clean          - Clean build artifacts"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start Docker services"
	@echo "  docker-down    - Stop Docker services"
	@echo "  deploy         - Deploy to production"

# Setup
setup:
	@echo "Setting up Incognito Technology..."
	npm install
	cd frontend && npm install
	cd backend/node_services/auth-service && npm install
	cd backend/node_services/notification-service && npm install
	cd backend/fastapi_app && pip install -r requirements.txt
	@echo "Setup complete!"

# Development
dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "Services started. Access at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  Grafana: http://localhost:3001"

# Build
build:
	@echo "Building all services..."
	cd frontend && npm run build
	cd backend/node_services/auth-service && npm run build
	cd backend/node_services/notification-service && npm run build
	@echo "Build complete!"

# Testing
test:
	@echo "Running all tests..."
	cd frontend && npm test
	cd backend/node_services/auth-service && npm test
	cd backend/node_services/notification-service && npm test
	cd backend/fastapi_app && python -m pytest
	cd ai_ml && python -m pytest
	@echo "All tests completed!"

# Linting
lint:
	@echo "Running linting..."
	cd frontend && npm run lint
	cd backend/node_services/auth-service && npm run lint
	cd backend/node_services/notification-service && npm run lint
	cd backend/fastapi_app && black . && isort . && flake8 .
	cd ai_ml && black . && isort . && flake8 .
	@echo "Linting complete!"

# Clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/.next
	rm -rf frontend/out
	rm -rf backend/node_services/*/dist
	rm -rf backend/fastapi_app/__pycache__
	rm -rf ai_ml/__pycache__
	docker system prune -f
	@echo "Clean complete!"

# Docker operations
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

# Deployment
deploy:
	@echo "Deploying to production..."
	kubectl apply -f devops/k8s/
	@echo "Deployment initiated!"

# Database operations
db-migrate:
	@echo "Running database migrations..."
	cd backend/fastapi_app && alembic upgrade head

db-seed:
	@echo "Seeding database..."
	cd database && python seed_data/seed.py

# Security scans
security-scan:
	@echo "Running security scans..."
	docker run --rm -v $(PWD):/app aquasec/trivy fs /app
	npm audit
	cd backend/fastapi_app && safety check

# Monitoring
logs:
	docker-compose logs -f

status:
	docker-compose ps
