from fastapi import APIRouter, Body
from typing import Dict, Any, List

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/generate")
async def generate_complaint(payload: Dict[str, str] = Body(...)):
    """Manually invokes the Complaint Agent to create a formal letter draft."""
    return {
        "id": "dummy-complaint-uuid",
        "department": "Municipal Water and Sanitation Division",
        "severity": "Critical",
        "subject": "Urgent: Contaminated Drinking Water Supply in Area",
        "body": "Respected Sir/Madam,\n\nI am writing to report visible brown discoloration and foam in our tap water supply. Please look into this immediately.\n\nSincerely,\nResident",
        "status": "Draft"
    }

@router.get("")
async def get_complaints():
    """Fetches all complaints for the user."""
    return [
        {
            "id": "complaint-1",
            "department": "Municipal Water and Sanitation Division",
            "severity": "Critical",
            "subject": "Urgent: Contaminated Drinking Water Supply in Area",
            "body": "Respected Sir/Madam,\n\nI am writing to report visible brown discoloration and foam in our tap water supply. Please look into this immediately.\n\nSincerely,\nResident",
            "status": "Draft",
            "created_at": "2026-07-17T11:00:00Z"
        }
    ]

@router.post("/submit/{complaint_id}")
async def submit_complaint(complaint_id: str):
    """Simulates complaint portal submission."""
    return {
        "complaint_id": complaint_id,
        "status": "Submitted",
        "submission_ref": "REF-99210-2026",
        "message": "Complaint successfully registered on the municipal portal mock."
    }
