import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.config import settings
from app.api import chat, analysis, complaints, reports, auth, monitoring
from app.utils.logger import setup_logging

# Configure structured rotating logs
setup_logging()
logger = logging.getLogger("aquasentinel")

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Ensure static directories exist
os.makedirs("static/reports", exist_ok=True)

app = FastAPI(
    title="AquaSentinel AI Agentic Platform API",
    description="Backend API for multi-agent water quality and safety platform (UN SDG 6)",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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
    logger.info("Initializing app...")
    pass

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
