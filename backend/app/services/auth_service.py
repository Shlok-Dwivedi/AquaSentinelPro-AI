import logging
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import jwt
from jwt import PyJWKClient
from app.config import settings
from app.services.db_service import get_supabase
from app.crud.user_crud import get_user_by_id

logger = logging.getLogger("aquasentinel")

SUPABASE_JWT_SECRET = getattr(settings, "SUPABASE_JWT_SECRET", settings.SECRET_KEY)
jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
jwks_client = PyJWKClient(jwks_url)

security_scheme = HTTPBearer()

def verify_supabase_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    """Verifies the Supabase JWT token supporting both HS256 and RS256."""
    token = credentials.credentials
    alg = 'Unknown'
    
    if not token or token == 'null' or token.count('.') != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get('alg', 'HS256')
        
        if alg == 'HS256':
            if not SUPABASE_JWT_SECRET or SUPABASE_JWT_SECRET == settings.SECRET_KEY:
                logger.error("WARNING: Verifying HS256 token but SUPABASE_JWT_SECRET is missing or using fallback!")
                
            payload = jwt.decode(
                token, 
                SUPABASE_JWT_SECRET, 
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
        else:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token, 
                signing_key.key, 
                algorithms=[alg],
                options={"verify_aud": False}
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token Verification Error ({alg}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    payload: dict = Depends(verify_supabase_token),
    supabase: Client = Depends(get_supabase)
) -> dict:
    """Dependency to retrieve the currently logged-in user's profile from public.users."""
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = get_user_by_id(supabase, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete onboarding.",
        )
    return user
