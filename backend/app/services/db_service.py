import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.db_models import Base, User, ChatSession, ChatMessage, WaterAnalysis, Complaint, Report, AgentExecutionLog

logger = logging.getLogger("aquasentinel")

# Determine database engine
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the database schema."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI database session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_user(db: Session, user_id: str) -> User:
    """Retrieves a user profile or initializes a new one if it doesn't exist."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            name="Default User",
            location="Mumbai, India",
            water_source="Municipal Tap",
            household_size=4,
            memory_context={
                "purifier_type": "None",
                "reported_alerts": []
            }
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user profile for user_id: {user_id}")
    return user

def load_user_memory_context(db: Session, user_id: str) -> dict:
    """Loads user memory data including profile details, historical scores, and complaint counts."""
    user = get_or_create_user(db, user_id)
    
    # Query past analysis count and latest score
    analyses = db.query(WaterAnalysis).filter(WaterAnalysis.user_id == user_id).order_by(WaterAnalysis.created_at.desc()).all()
    analysis_count = len(analyses)
    latest_score = analyses[0].score if analysis_count > 0 else None
    latest_risk = analyses[0].risk_level if analysis_count > 0 else None
    
    # Query complaints count
    complaint_count = db.query(Complaint).filter(Complaint.user_id == user_id).count()
    
    return {
        "user_id": user.id,
        "name": user.name,
        "location": user.location,
        "water_source": user.water_source,
        "household_size": user.household_size,
        "memory_context": user.memory_context or {},
        "history": {
            "total_analyses": analysis_count,
            "latest_water_score": latest_score,
            "latest_risk_level": latest_risk,
            "total_complaints": complaint_count
        }
    }

def save_agent_execution_log(
    db: Session,
    chat_message_id: str,
    plan_json: dict,
    reflection_attempts: int,
    reflection_feedback_json: dict,
    final_outputs_json: dict,
    execution_time_ms: int,
    water_score: float = None,
    confidence_score: float = None,
    graph_version: str = "v2.0-milestone4",
    gemini_model: str = "gemini-2.5-flash",
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
    analysis_model: str = "gemini-2.5-flash"
) -> AgentExecutionLog:
    """Saves a detailed agentic workflow run trace log with extended metrics to the database."""
    log_record = AgentExecutionLog(
        chat_message_id=chat_message_id,
        plan_json=plan_json,
        reflection_attempts=reflection_attempts,
        reflection_feedback_json=reflection_feedback_json,
        final_outputs_json=final_outputs_json,
        execution_time_ms=execution_time_ms,
        water_score=water_score,
        confidence_score=confidence_score,
        graph_version=graph_version,
        gemini_model=gemini_model,
        reflection_iterations=reflection_iterations,
        agents_executed=agents_executed,
        synthesized_response=synthesized_response,
        image_filename=image_filename,
        image_width=image_width,
        image_height=image_height,
        mime_type=mime_type,
        file_size=file_size,
        vision_confidence=vision_confidence,
        detected_hazards=detected_hazards,
        contamination_level=contamination_level,
        analysis_model=analysis_model
    )
    db.add(log_record)
    db.commit()
    db.refresh(log_record)
    return log_record
