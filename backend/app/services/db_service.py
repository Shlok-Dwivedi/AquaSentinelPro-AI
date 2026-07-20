import logging

from typing import Optional, Dict, Any, List
from fastapi import Request
from supabase import create_client, Client, ClientOptions
from app.config import settings

logger = logging.getLogger("aquasentinel")

def get_supabase(request: Request) -> Client:
    """FastAPI dependency to get a Supabase client with service_role access (bypassing RLS).
    User authentication is already handled by verify_supabase_token dependency."""
    client = create_client(
        settings.SUPABASE_URL,
        settings.SECRET_KEY
    )
    return client

def get_supabase_unauth() -> Client:
    """Get supabase client with service_role access."""
    return create_client(settings.SUPABASE_URL, settings.SECRET_KEY)
