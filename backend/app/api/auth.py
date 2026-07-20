import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client
from app.services.db_service import get_supabase
from app.services.auth_service import verify_supabase_token, get_current_user
from app.crud.user_crud import get_user_by_id, create_user

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/auth", tags=["Authentication"])

class OnboardingRequest(BaseModel):
    name: str
    location: str | None = None
    water_source: str | None = None
    household_size: int = 4

@router.post("/onboard")
async def onboard_user(
    req: OnboardingRequest, 
    payload: dict = Depends(verify_supabase_token), 
    supabase: Client = Depends(get_supabase)
):
    """Creates the user's public profile after they sign up via Supabase."""
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Check if user already exists
    existing = get_user_by_id(supabase, user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile already exists."
        )
        
    # Create new profile in public.users
    user_data = {
        "id": user_id,
        "name": req.name,
        "location": req.location,
        "water_source": req.water_source,
        "household_size": req.household_size
    }
    
    user = create_user(supabase, user_data)
    
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create profile")
    
    logger.info(f"Onboarded new user profile: {user['id']}")
    return {
        "message": "Onboarding complete",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "location": user["location"],
            "water_source": user["water_source"]
        }
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retrieves current authenticated user's profile."""
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "location": current_user["location"],
        "water_source": current_user["water_source"],
        "household_size": current_user["household_size"]
    }
