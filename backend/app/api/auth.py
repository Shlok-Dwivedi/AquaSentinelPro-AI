import logging
from fastapi import APIRouter, Depends, HTTPException, status, Form
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.services.db_service import get_db
from app.services.auth_service import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    verify_token, hash_token, get_current_user
)
from app.models.db_models import User

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register")
async def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user profile with password hashing."""
    # Check if user already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )
        
    # Create new user
    hashed = hash_password(req.password)
    user = User(
        name=req.name,
        email=req.email,
        hashed_password=hashed
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    
    # Store hashed refresh token
    user.refresh_token_hash = hash_token(refresh)
    db.commit()
    
    logger.info(f"Registered user: {user.email}")
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }

@router.post("/login")
async def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """Logs in an existing user and returns JWT access and refresh tokens."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password credentials."
        )
        
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    
    user.refresh_token_hash = hash_token(refresh)
    db.commit()
    
    logger.info(f"Logged in user: {user.email}")
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_tokens(req: RefreshRequest, db: Session = Depends(get_db)):
    """Rotates refresh tokens and returns a new access token."""
    payload = verify_token(req.refresh_token)
    if not payload or "sub" not in payload or not payload.get("refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )
        
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.refresh_token_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User session invalid."
        )
        
    # Verify hash match
    if hash_token(req.refresh_token) != user.refresh_token_hash:
        # Revoke session due to token reuse warning
        user.refresh_token_hash = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token reuse detected. Session revoked."
        )
        
    # Generate new pair (Refresh token rotation)
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    
    user.refresh_token_hash = hash_token(refresh)
    db.commit()
    
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logs out the user and clears refresh token hashes."""
    current_user.refresh_token_hash = None
    db.commit()
    logger.info(f"Logged out user: {current_user.email}")
    return {"message": "Logged out successfully."}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieves current authenticated user details."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "location": current_user.location,
        "water_source": current_user.water_source
    }
