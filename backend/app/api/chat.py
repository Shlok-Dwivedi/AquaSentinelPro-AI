from fastapi import APIRouter, Header, UploadFile, File, Form
from typing import Dict, Any, Optional

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/message")
async def send_chat_message(
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    ph: Optional[float] = Form(None),
    tds: Optional[float] = Form(None),
    turbidity: Optional[float] = Form(None),
    hardness: Optional[float] = Form(None),
    chlorine: Optional[float] = Form(None),
    fluoride: Optional[float] = Form(None)
):
    """Sends a chat message, triggering the multi-agent orchestration pipeline."""
    return {
        "message_id": "dummy-msg-uuid",
        "session_id": session_id or "dummy-session-uuid",
        "synthesized_response": "### AquaSentinel Safety Assessment Report\n\nWater quality is optimal. No action required.",
        "agent_execution": {
            "plan": ["water_analysis", "policy_standards", "purification"],
            "reflection_cycles": 1,
            "tool_calls_logged": []
        },
        "structured_data": {
            "water_analysis": {
                "water_score": 85.0,
                "drinking_safety": "Safe",
                "risk_level": "Low",
                "contaminants_found": [],
                "detected_hazards": []
            },
            "purification": {
                "recommended_methods": ["Activated Carbon"],
                "suitability_reasons": {"Activated Carbon": "Recommended for standard domestic tap water taste enhancement."},
                "warning": None
            }
        }
    }

@router.get("/history")
async def get_chat_history(session_id: str):
    """Returns chat message logs for a session."""
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": "msg-1",
                "role": "user",
                "content": "Check my tap water safety.",
                "image_path": None,
                "timestamp": "2026-07-17T12:00:00Z"
            },
            {
                "id": "msg-2",
                "role": "assistant",
                "content": "### AquaSentinel Safety Assessment Report\n\nWater quality is optimal. No action required.",
                "image_path": None,
                "timestamp": "2026-07-17T12:00:05Z"
            }
        ]
    }
