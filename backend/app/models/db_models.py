import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    location = Column(String(255), nullable=True)
    water_source = Column(String(100), nullable=True)
    household_size = Column(Integer, nullable=True, default=4)
    memory_context = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("WaterAnalysis", back_populates="user", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)
    image_path = Column(String(512), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
    execution_logs = relationship("AgentExecutionLog", back_populates="chat_message", cascade="all, delete-orphan")


class WaterAnalysis(Base):
    __tablename__ = "water_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parameters_json = Column(JSON, nullable=False)  # ph, tds, turbidity, hardness, chlorine, fluoride
    score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # 'Low', 'Medium', 'High'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    water_analysis_id = Column(String(36), ForeignKey("water_analyses.id", ondelete="SET NULL"), nullable=True)
    department = Column(String(150), nullable=False)
    severity = Column(String(20), nullable=False)  # 'Low', 'Medium', 'Critical'
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(20), default="Draft")  # 'Draft', 'Submitted'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="complaints")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    water_analysis_id = Column(String(36), ForeignKey("water_analyses.id", ondelete="SET NULL"), nullable=True)
    pdf_path = Column(String(512), nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reports")


class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_message_id = Column(String(36), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    plan_json = Column(JSON, nullable=True)
    reflection_attempts = Column(Integer, default=0)
    reflection_feedback_json = Column(JSON, nullable=True)
    final_outputs_json = Column(JSON, nullable=True)
    execution_time_ms = Column(Integer, default=0)
    
    # Extended metrics fields for Milestone 3
    water_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    graph_version = Column(String(50), nullable=True)
    gemini_model = Column(String(100), nullable=True)
    reflection_iterations = Column(Integer, default=0)
    agents_executed = Column(JSON, nullable=True)
    synthesized_response = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    chat_message = relationship("ChatMessage", back_populates="execution_logs")
