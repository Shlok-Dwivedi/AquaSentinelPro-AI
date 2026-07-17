import time
import uuid
import logging
import os
from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import Optional
from sqlalchemy.orm import Session
from app.services.db_service import get_db, save_agent_execution_log, get_or_create_user
from app.models.db_models import ChatSession, ChatMessage
from app.graph.workflow import app_workflow
from app.graph.state import AgentState

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/chat", tags=["Chat"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/message")
async def send_chat_message(
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    ph: Optional[float] = Form(None),
    tds: Optional[float] = Form(None),
    turbidity: Optional[float] = Form(None),
    hardness: Optional[float] = Form(None),
    chlorine: Optional[float] = Form(None),
    fluoride: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """Sends a user query, triggers the LangGraph orchestration pipeline, and saves logs to the database."""
    # 1. Resolve User and Session
    user_uuid = user_id or "default_user"
    user = get_or_create_user(db, user_uuid)
    
    if not session_id:
        new_session = ChatSession(user_id=user.id)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_uuid = new_session.id
        logger.info(f"Created new chat session: {session_uuid}")
    else:
        # Verify session exists
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            new_session = ChatSession(id=session_id, user_id=user.id)
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_uuid = new_session.id
        else:
            session_uuid = session.id

    # 2. Save Uploaded Image if exists
    saved_image_path = None
    if image and image.filename:
        try:
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            saved_image_path = os.path.join(UPLOAD_DIR, unique_filename)
            with open(saved_image_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
            logger.info(f"Saved uploaded image to: {saved_image_path}")
        except Exception as e:
            logger.error(f"Failed to save uploaded image: {e}")

    # 3. Assemble parameters dictionary if any are supplied
    raw_params = {}
    for name, val in [("ph", ph), ("tds", tds), ("turbidity", turbidity), 
                      ("hardness", hardness), ("chlorine", chlorine), ("fluoride", fluoride)]:
        if val is not None:
            raw_params[name] = val

    # 4. Save User Message in database
    user_msg_record = ChatMessage(
        session_id=session_uuid,
        role="user",
        content=message,
        image_path=saved_image_path
    )
    db.add(user_msg_record)
    db.commit()
    db.refresh(user_msg_record)

    # 5. Initialize LangGraph AgentState
    initial_state = AgentState(
        user_id=user.id,
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

    # 6. Execute LangGraph and measure latency
    start_time = time.time()
    logger.info(f"Invoking LangGraph pipeline for user query: '{message}'")
    try:
        final_state = await app_workflow.ainvoke(initial_state)
        status = "Finished"
    except Exception as e:
        logger.error(f"LangGraph execution crashed: {e}")
        status = "Failed"
        # Standard fallback response
        final_state = initial_state
        final_state["synthesized_response"] = f"An internal error occurred during orchestration. Details: {e}"
        final_state["plan"] = {"selected_agents": [], "dependencies": {}, "execution_order": []}
        
    execution_time_ms = int((time.time() - start_time) * 1000)
    logger.info(f"LangGraph execution status: {status} in {execution_time_ms} ms")

    # 7. Save Assistant Message response in database
    assistant_msg_record = ChatMessage(
        session_id=session_uuid,
        role="assistant",
        content=final_state.get("synthesized_response", "")
    )
    db.add(assistant_msg_record)
    db.commit()
    db.refresh(assistant_msg_record)

    # 8. Save Execution Log in database
    try:
        # Extract metrics safely from agent outputs if they ran
        agent_outputs = final_state.get("agent_outputs", {})
        water_out = agent_outputs.get("water_analysis", {})
        water_score = water_out.get("water_score")
        
        # Determine average confidence rating if agents executed
        conf_scores = []
        if water_out and "confidence_score" in water_out:
            conf_scores.append(water_out["confidence_score"])
        knowledge_out = agent_outputs.get("knowledge", {})
        if knowledge_out and "confidence_score" in knowledge_out:
            conf_scores.append(knowledge_out["confidence_score"])
        avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else None

        save_agent_execution_log(
            db=db,
            chat_message_id=assistant_msg_record.id,
            plan_json=final_state.get("plan", {}),
            reflection_attempts=final_state.get("iterations", 0),
            reflection_feedback_json={"feedback": final_state.get("reflection_feedback")},
            final_outputs_json=agent_outputs,
            execution_time_ms=execution_time_ms,
            water_score=water_score,
            confidence_score=avg_conf,
            graph_version="v1.0-milestone3",
            gemini_model="gemini-2.5-flash",
            reflection_iterations=final_state.get("iterations", 0),
            agents_executed=final_state.get("plan", {}).get("selected_agents", []),
            synthesized_response=final_state.get("synthesized_response", "")
        )
        logger.info("Saved agent execution log entry in database.")
    except Exception as db_err:
        logger.error(f"Failed to write execution log entry to database: {db_err}")

    # 9. Return JSON response matching Milestone 2 specs
    plan = final_state.get("plan", {})
    return {
        "message_id": assistant_msg_record.id,
        "session_id": session_uuid,
        "synthesized_response": final_state.get("synthesized_response", ""),
        "agent_execution": {
            "plan": plan.get("execution_order", []),
            "selected_agents": plan.get("selected_agents", []),
            "graph_status": status,
            "execution_duration_ms": execution_time_ms
        },
        "structured_data": final_state.get("agent_outputs", {})
    }

@router.get("/history")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Retrieves chat message history logs from the database for a session."""
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.ascii() if hasattr(ChatMessage.timestamp, "ascii") else ChatMessage.timestamp.asc()).all()
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "image_path": m.image_path,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
    }
