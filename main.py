"""
Main application entry point.
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import db_manager
from app.routers import organization, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    db_manager.connect()
    yield
    # Shutdown
    db_manager.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A Multi-Tenant Organization Management Service",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(organization.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns service status and database connectivity.
    """
    db_status = "disconnected"
    try:
        # Check database connection
        if db_manager._client is not None:
            db_manager._client.server_info()
            db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    health_status = "healthy" if db_status == "connected" else "unhealthy"
    
    return {
        "status": health_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )
