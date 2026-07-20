import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.db_models import User, ChatSession, ChatMessage, WaterAnalysis, Complaint, Report, AgentExecutionLog

# Load frontend env for Supabase keys (since user doesn't have password for postgres)
load_dotenv('../frontend/.env')
url = os.getenv('VITE_SUPABASE_URL')
key = os.getenv('VITE_SUPABASE_ANON_KEY')

supabase: Client = create_client(url, key)

# Load backend local sqlite DB
engine = create_engine("sqlite:///./aquasentinel.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def serialize_json(val):
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return json.loads(val)
        except:
            return val
    return val

def migrate():
    print("Migrating users...")
    users = db.query(User).all()
    for u in users:
        data = {
            "id": u.id,
            "name": u.name,
            "location": u.location,
            "water_source": u.water_source,
            "household_size": u.household_size,
            "memory_context": serialize_json(u.memory_context),
            "updated_at": u.updated_at.isoformat() if u.updated_at else None
        }
        supabase.table("users").upsert(data).execute()

    print("Migrating chat_sessions...")
    sessions = db.query(ChatSession).all()
    for s in sessions:
        data = {
            "id": s.id,
            "user_id": s.user_id,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        supabase.table("chat_sessions").upsert(data).execute()

    print("Migrating chat_messages...")
    messages = db.query(ChatMessage).all()
    for m in messages:
        data = {
            "id": m.id,
            "session_id": m.session_id,
            "role": m.role,
            "content": m.content,
            "image_path": m.image_path,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None
        }
        supabase.table("chat_messages").upsert(data).execute()

    print("Migrating water_analyses...")
    analyses = db.query(WaterAnalysis).all()
    for a in analyses:
        data = {
            "id": a.id,
            "user_id": a.user_id,
            "parameters_json": serialize_json(a.parameters_json),
            "score": a.score,
            "risk_level": a.risk_level,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        supabase.table("water_analyses").upsert(data).execute()

    print("Migrating complaints...")
    complaints = db.query(Complaint).all()
    for c in complaints:
        data = {
            "id": c.id,
            "user_id": c.user_id,
            "water_analysis_id": c.water_analysis_id,
            "department": c.department,
            "severity": c.severity,
            "subject": c.subject,
            "body": c.body,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        supabase.table("complaints").upsert(data).execute()

    print("Migrating reports...")
    reports = db.query(Report).all()
    for r in reports:
        data = {
            "id": r.id,
            "user_id": r.user_id,
            "water_analysis_id": r.water_analysis_id,
            "agent_execution_log_id": r.agent_execution_log_id,
            "title": r.title,
            "pdf_path": r.pdf_path,
            "markdown_path": r.markdown_path,
            "json_path": r.json_path,
            "summary": r.summary,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        supabase.table("reports").upsert(data).execute()

    print("Migrating agent_execution_logs...")
    logs = db.query(AgentExecutionLog).all()
    for l in logs:
        data = {
            "id": l.id,
            "chat_message_id": l.chat_message_id,
            "plan_json": serialize_json(l.plan_json),
            "reflection_attempts": l.reflection_attempts,
            "reflection_feedback_json": serialize_json(l.reflection_feedback_json),
            "final_outputs_json": serialize_json(l.final_outputs_json),
            "execution_time_ms": l.execution_time_ms,
            "water_score": l.water_score,
            "confidence_score": l.confidence_score,
            "graph_version": l.graph_version,
            "gemini_model": l.gemini_model,
            "reflection_iterations": l.reflection_iterations,
            "agents_executed": serialize_json(l.agents_executed),
            "synthesized_response": l.synthesized_response,
            "image_filename": l.image_filename,
            "image_width": l.image_width,
            "image_height": l.image_height,
            "mime_type": l.mime_type,
            "file_size": l.file_size,
            "vision_confidence": l.vision_confidence,
            "detected_hazards": serialize_json(l.detected_hazards),
            "contamination_level": l.contamination_level,
            "analysis_model": l.analysis_model,
            "created_at": l.created_at.isoformat() if l.created_at else None
        }
        supabase.table("agent_execution_logs").upsert(data).execute()

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
