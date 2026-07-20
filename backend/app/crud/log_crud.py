from supabase import Client
import json

def serialize_json(val):
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return json.loads(val)
        except:
            return val
    return val

def save_agent_execution_log(
    supabase: Client,
    chat_message_id: str,
    plan_json: dict,
    reflection_attempts: int,
    reflection_feedback_json: dict,
    final_outputs_json: dict,
    execution_time_ms: int,
    water_score: float = None,
    confidence_score: float = None,
    graph_version: str = "v2.0-milestone4",
    gemini_model: str = "gemini-flash-latest",
    reflection_iterations: int = 0,
    agents_executed: list = None,
    synthesized_response: str = None,
    image_filename: str = None,
    image_width: int = None,
    image_height: int = None,
    mime_type: str = None,
    file_size: int = None,
    vision_confidence: float = None,
    detected_hazards: list = None,
    contamination_level: str = None,
    analysis_model: str = "gemini-flash-latest"
) -> dict:
    """Saves a detailed agentic workflow run trace log with extended metrics to the database."""
    log_record = {
        "chat_message_id": chat_message_id,
        "plan_json": serialize_json(plan_json),
        "reflection_attempts": reflection_attempts,
        "reflection_feedback_json": serialize_json(reflection_feedback_json),
        "final_outputs_json": serialize_json(final_outputs_json),
        "execution_time_ms": execution_time_ms,
        "water_score": water_score,
        "confidence_score": confidence_score,
        "graph_version": graph_version,
        "gemini_model": gemini_model,
        "reflection_iterations": reflection_iterations,
        "agents_executed": serialize_json(agents_executed),
        "synthesized_response": synthesized_response,
        "image_filename": image_filename,
        "image_width": image_width,
        "image_height": image_height,
        "mime_type": mime_type,
        "file_size": file_size,
        "vision_confidence": vision_confidence,
        "detected_hazards": serialize_json(detected_hazards),
        "contamination_level": contamination_level,
        "analysis_model": analysis_model
    }
    
    resp = supabase.table("agent_execution_logs").insert(log_record).execute()
    if not resp.data:
        raise Exception("Failed to save execution log trace.")
    return resp.data[0]
