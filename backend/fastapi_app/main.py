"""
Incognito Technology FastAPI Application
Main entry point for the healthcare platform backend service
"""

from fastapi import FastAPI, Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import logging
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import setup_logging
from routers import auth, ehr, ai_inference, blockchain
from services.ai_service import AIService
from services.blockchain_service import BlockchainService


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Incognito Technology FastAPI service...")
    
    # Initialize services
    ai_service = AIService()
    blockchain_service = BlockchainService()
    
    # Store services in app state
    app.state.ai_service = ai_service
    app.state.blockchain_service = blockchain_service
    
    logger.info("FastAPI service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI service...")
    # Cleanup resources if needed
    logger.info("FastAPI service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Incognito Technology API",
    description="AI-powered healthcare platform with blockchain security",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ehr.router, prefix="/ehr", tags=["Electronic Health Records"])
app.include_router(ai_inference.router, prefix="/ai", tags=["AI/ML Services"])
app.include_router(blockchain.router, prefix="/blockchain", tags=["Blockchain Services"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Incognito Technology API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fastapi-backend",
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement Prometheus metrics
    return {"metrics": "prometheus_metrics_here"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
