from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Dict, Any, List
from supabase import Client
from app.services.db_service import get_supabase
from app.services.auth_service import get_current_user
from app.crud.complaint_crud import insert_complaint, get_user_complaints, submit_complaint_status
import uuid

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/generate")
async def generate_complaint(
    payload: Dict[str, str] = Body(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Manually invokes the Complaint Agent to create a formal letter draft and saves to DB."""
    try:
        c = insert_complaint(supabase, current_user["id"], payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create complaint")
    
    return {
        "id": c["id"],
        "department": c["department"],
        "severity": c["severity"],
        "subject": c["subject"],
        "body": c["body"],
        "status": c["status"],
        "created_at": c["created_at"]
    }

@router.get("")
async def get_complaints(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Fetches all complaints for the user from the database."""
    complaints = get_user_complaints(supabase, current_user["id"])
    
    return [
        {
            "id": c["id"],
            "department": c["department"],
            "severity": c["severity"],
            "subject": c["subject"],
            "body": c["body"],
            "status": c["status"],
            "created_at": c["created_at"]
        } for c in complaints
    ]

@router.post("/submit/{complaint_id}")
async def submit_complaint(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Simulates complaint portal submission and updates status in DB."""
    success = submit_complaint_status(supabase, complaint_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return {
        "complaint_id": complaint_id,
        "status": "Submitted",
        "submission_ref": f"REF-{str(uuid.uuid4())[:8].upper()}-2026",
        "message": "Complaint successfully registered on the municipal portal mock."
    }
