import time
import uuid
import logging
import os
from fastapi import APIRouter, Depends, Form, File, UploadFile, Request
from typing import Optional
from supabase import Client
from app.services.db_service import get_supabase
from app.crud.chat_crud import get_or_create_chat_session, insert_chat_message, get_chat_history
from app.crud.log_crud import save_agent_execution_log
from app.services.auth_service import get_current_user
from app.agents.report_generator import generate_water_report
from PIL import Image as PILImage
from app.graph.state import AgentState
from app.graph.workflow import app_workflow

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/chat", tags=["Chat"])


from fastapi.responses import StreamingResponse
import json

@router.post("/message")
async def send_chat_message(
    request: Request,
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    ph: Optional[float] = Form(None),
    tds: Optional[float] = Form(None),
    turbidity: Optional[float] = Form(None),
    hardness: Optional[float] = Form(None),
    chlorine: Optional[float] = Form(None),
    fluoride: Optional[float] = Form(None),
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Sends a user query, streams LangGraph status updates, and yields final response JSON via SSE."""
    
    async def event_generator():
        user = current_user
        
        try:
            session_uuid = get_or_create_chat_session(supabase, session_id, user["id"])
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to initialize session'})}\n\n"
            return

        saved_image_path = None
        img_name = None
        img_mime = None
        img_size = None
        img_width = None
        img_height = None
        
        if image and image.filename:
            yield f"data: {json.dumps({'type': 'status', 'message': 'Uploading image to secure storage...'})}\n\n"
            try:
                file_extension = os.path.splitext(image.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                content = await image.read()
                
                supabase.storage.from_("report").upload(
                    path=unique_filename,
                    file=content,
                    file_options={"content-type": image.content_type}
                )
                saved_image_path = supabase.storage.from_("report").get_public_url(unique_filename)
                
                img_name = image.filename
                img_mime = image.content_type
                try:
                    img_size = len(content)
                    import io
                    with PILImage.open(io.BytesIO(content)) as img:
                        img_width, img_height = img.size
                except Exception as img_err:
                    logger.error(f"Failed to extract image dimensions from bytes: {img_err}")
                    
            except Exception as e:
                logger.error(f"Failed to upload image to Supabase Storage: {e}")

        raw_params = {}
        for name, val in [("ph", ph), ("tds", tds), ("turbidity", turbidity), 
                          ("hardness", hardness), ("chlorine", chlorine), ("fluoride", fluoride)]:
            if val is not None:
                raw_params[name] = val

        try:
            insert_chat_message(supabase, session_uuid, "user", message, saved_image_path)
        except Exception as e:
            logger.error(f"Failed to save user message: {e}")

        initial_state = AgentState(
            user_id=user["id"],
            session_id=session_uuid,
            user_query=message,
            image_path=saved_image_path,
            raw_parameters=raw_params if raw_params else None,
            user_memory={},
            plan={"selected_agents": [], "dependencies": {}, "execution_order": []},
            current_step=0,
            iterations=0,
            is_valid=False,
            agent_outputs={},
            reflection_feedback=None,
            metadata={},
            synthesized_response="",
            pdf_report_url=None
        )

        start_time = time.time()
        final_state = initial_state
        status = "Finished"
        
        try:
            async for output in app_workflow.astream(initial_state, stream_mode="updates"):
                node_name = list(output.keys())[0]
                status_map = {
                    "memory_load": "Loading conversational memory...",
                    "planning": "Planning analytical task execution route...",
                    "water_analysis": "Running chemical analysis agent...",
                    "vision_analysis": "Scanning image for physical hazards...",
                    "knowledge": "Cross-referencing WHO/BIS limits...",
                    "reflection": "Critiquing agent findings for accuracy...",
                    "synthesizer": "Synthesizing executive response..."
                }
                msg = status_map.get(node_name, f"Processing {node_name}...")
                yield f"data: {json.dumps({'type': 'status', 'message': msg})}\n\n"
                
                state_update = output[node_name]
                if "agent_outputs" in state_update:
                    final_state["agent_outputs"].update(state_update["agent_outputs"])
                if "plan" in state_update:
                    final_state["plan"].update(state_update["plan"])
                if "synthesized_response" in state_update:
                    final_state["synthesized_response"] = state_update["synthesized_response"]
                if "is_valid" in state_update:
                    final_state["is_valid"] = state_update["is_valid"]
                if "iterations" in state_update:
                    final_state["iterations"] += 1
        except Exception as e:
            logger.error(f"LangGraph execution crashed: {e}")
            status = "Failed"
            final_state["synthesized_response"] = f"An internal error occurred during orchestration. Details: {e}"
            
        execution_time_ms = int((time.time() - start_time) * 1000)

        yield f"data: {json.dumps({'type': 'status', 'message': 'Saving telemetry logs...'})}\n\n"
        
        try:
            msg_id = insert_chat_message(supabase, session_uuid, "assistant", final_state.get("synthesized_response", ""))
        except Exception as e:
            logger.error(f"Failed to save assistant message: {e}")
            msg_id = None

        try:
            agent_outputs = final_state.get("agent_outputs", {})
            plan = final_state.get("plan", {})
            water_out = agent_outputs.get("water_analysis", {})
            water_score = water_out.get("water_score")
            vision_out = agent_outputs.get("vision_analysis", {})
            
            conf_scores = []
            if water_out and "confidence_score" in water_out:
                conf_scores.append(water_out["confidence_score"])
            if vision_out and "confidence_score" in vision_out:
                conf_scores.append(vision_out["confidence_score"])
            knowledge_out = agent_outputs.get("knowledge", {})
            if knowledge_out and "confidence_score" in knowledge_out:
                conf_scores.append(knowledge_out["confidence_score"])
            avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else None

            log_record = save_agent_execution_log(
                supabase=supabase,
                chat_message_id=msg_id,
                plan_json=final_state.get("plan", {}),
                reflection_attempts=final_state.get("iterations", 0),
                reflection_feedback_json={"feedback": final_state.get("reflection_feedback")},
                final_outputs_json=agent_outputs,
                execution_time_ms=execution_time_ms,
                water_score=water_score,
                confidence_score=avg_conf,
                graph_version="v2.0-milestone4",
                gemini_model="gemini-flash-latest",
                reflection_iterations=final_state.get("iterations", 0),
                agents_executed=plan.get("selected_agents", []),
                synthesized_response=final_state.get("synthesized_response", ""),
                image_filename=img_name,
                image_width=img_width,
                image_height=img_height,
                mime_type=img_mime,
                file_size=img_size,
                vision_confidence=vision_out.get("confidence_score") if vision_out else None,
                detected_hazards=vision_out.get("contaminants_detected", []) if vision_out else None,
                contamination_level=vision_out.get("contamination_level") if vision_out else None,
                analysis_model="gemini-flash-latest"
            )
            
            selected = plan.get("selected_agents", [])
            if "water_analysis" in selected or "vision_analysis" in selected:
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating PDF/MD assessment reports...'})}\n\n"
                try:
                    generate_water_report(
                        user_id=user["id"],
                        chat_session_id=session_uuid,
                        execution_log_id=log_record["id"],
                        agent_outputs=agent_outputs,
                        executed_agents=selected,
                        db=supabase
                    )
                except Exception as rep_err:
                    logger.error(f"Failed to compile report: {rep_err}")
                    
        except Exception as db_err:
            logger.error(f"Failed to write execution log entry: {db_err}")

        # Final Result JSON Event
        final_result = {
            "message_id": msg_id,
            "session_id": session_uuid,
            "synthesized_response": final_state.get("synthesized_response", ""),
            "agent_execution": {
                "plan": final_state.get("plan", {}).get("execution_order", []),
                "selected_agents": final_state.get("plan", {}).get("selected_agents", []),
                "graph_status": status,
                "execution_duration_ms": execution_time_ms
            },
            "structured_data": final_state.get("agent_outputs", {})
        }
        yield f"data: {json.dumps({'type': 'result', 'data': final_result})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/history")
async def get_chat_history(
    session_id: str,
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Retrieves chat message history logs from the database for a session."""
    try:
        messages = get_chat_history(supabase, session_id)
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        messages = []
        
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": m["id"],
                "role": m["role"],
                "content": m["content"],
                "image_path": m["image_path"],
                "timestamp": m["timestamp"]
            }
            for m in messages
        ]
    }
