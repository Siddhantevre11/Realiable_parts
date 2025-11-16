"""
FastAPI Backend for ReliableParts Sales Dashboard
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
import time
from datetime import datetime
import sqlite3
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ReliableParts API",
    description="""
    AI-powered search and analytics API for appliance parts.

    Features:
    - **Semantic Search**: GPT-powered natural language search
    - **Intelligent Chat**: Conversational AI for product assistance
    - **Product Management**: Complete CRUD operations
    - **Analytics**: Business intelligence and statistics

    Built with:
    - FastAPI for high-performance REST API
    - OpenAI GPT-3.5-turbo for intelligence
    - Sentence Transformers for embeddings
    - SQLite for data storage
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration (allow v0.dev, Vercel, and localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",  # Vite
        "http://localhost:5174",
        "https://*.vercel.app",
        "https://*.v0.dev",
        "https://v0.dev",
        "*"  # Allow all for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing information."""
    start_time = time.time()

    # Log request
    logger.info(f"→ {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        f"← {request.method} {request.url.path} "
        f"- {response.status_code} - {duration:.2f}s"
    )

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url.path)
        }
    )


# Import and register routes
from api.routes import search, chat, products, analytics

app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])


# Root endpoint
@app.get("/")
async def root():
    """
    API root endpoint.

    Returns basic information about the API.
    """
    return {
        "message": "ReliableParts API",
        "version": "1.0.0",
        "description": "AI-powered search and analytics for appliance parts",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Check API health and dependencies.

    Verifies:
    - Database connectivity
    - OpenAI API key presence
    - Embeddings availability

    Returns health status of all components.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "unknown",
        "embeddings": "unknown",
        "openai_api": "unknown"
    }

    # Check database
    try:
        conn = sqlite3.connect("database/products.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        conn.close()
        health_status["database"] = f"connected ({count} products)"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check embeddings
    try:
        conn = sqlite3.connect("database/products.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE embedding IS NOT NULL")
        embedding_count = cursor.fetchone()[0]
        conn.close()

        if embedding_count > 0:
            health_status["embeddings"] = f"loaded ({embedding_count} products)"
        else:
            health_status["embeddings"] = "not generated"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["embeddings"] = f"error: {str(e)}"

    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.startswith('sk-'):
        health_status["openai_api"] = "configured"
    else:
        health_status["openai_api"] = "not configured"
        health_status["status"] = "degraded"

    return health_status


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("="*60)
    logger.info("ReliableParts API Starting")
    logger.info("="*60)
    logger.info(f"Version: 1.0.0")
    logger.info(f"Docs: http://localhost:8000/docs")
    logger.info(f"Health: http://localhost:8000/api/health")
    logger.info("="*60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("ReliableParts API Shutting Down")


# Development helper endpoints
@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints."""
    return {
        "app": "ReliableParts API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "chat": "/api/chat",
            "products": "/api/products",
            "analytics": "/api/analytics/overview",
            "categories": "/api/categories",
            "brands": "/api/brands",
            "health": "/api/health"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
