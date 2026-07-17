import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.services.db_service import init_db
from app.api import chat, analysis, complaints, reports, auth, monitoring
from app.utils.logger import setup_logging

# Configure structured rotating logs
setup_logging()
logger = logging.getLogger("aquasentinel")

# Ensure static directories exist
os.makedirs("static/reports", exist_ok=True)

app = FastAPI(
    title="AquaSentinel AI Agentic Platform API",
    description="Backend API for multi-agent water quality and safety platform (UN SDG 6)",
    version="1.0.0"
)

# Configure CORS middleware
origins = [org.strip() for org in settings.CORS_ORIGINS.split(",") if org.strip()]
if not origins or "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory to serve reports directly
app.mount("/static", StaticFiles(directory="static"), name="static")

# Startup database initialization
@app.on_event("startup")
def on_startup():
    logger.info("Initializing database schema...")
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "database": "connected",
        "message": "Backend Connected ✅"
    }

# Register routers under version prefix
api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(chat.router, prefix=api_prefix)
app.include_router(analysis.router, prefix=api_prefix)
app.include_router(complaints.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)
app.include_router(monitoring.router, prefix=api_prefix)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
