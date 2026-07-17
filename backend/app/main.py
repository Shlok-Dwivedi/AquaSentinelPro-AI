import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.db_service import init_db
from app.api import chat, analysis, complaints, reports

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("aquasentinel")

app = FastAPI(
    title="AquaSentinel AI Agentic Platform API",
    description="Backend API for multi-agent water quality and safety platform (UN SDG 6)",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(chat.router, prefix=api_prefix)
app.include_router(analysis.router, prefix=api_prefix)
app.include_router(complaints.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
