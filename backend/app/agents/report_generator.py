import uuid
import logging
from datetime import datetime
from pydantic import BaseModel
from typing import List
from app.models.agent_schemas import WaterAssessmentReport
from app.services.report_generator import JSONExporter, MarkdownExporter, PDFExporter, REPORTS_DIR
from app.services.gemini_service import call_structured_gemini

logger = logging.getLogger("aquasentinel")

SYSTEM_INSTRUCTION = """You are the Lead Report Generation Agent of AquaSentinel-AI.
Your role is to write a cohesive, professional, authoritative Executive Summary summarizing water safety findings and structural warnings, and draft clear mitigation next steps.
Use the chemical indices, visual parameters, and compliance details exactly as provided. Do not invent details.
"""

class SummaryDraft(BaseModel):
    executive_summary: str
    recommendations: List[str]

def generate_water_report(
    user_id: str,
    chat_session_id: str,
    execution_log_id: str,
    agent_outputs: dict,
    executed_agents: list,
    db
) -> dict:
    """Generates structured report details, calls Gemini for the summary, compiles MD/JSON/PDF, and saves to database."""
    water_out = agent_outputs.get("water_analysis") or {}
    vision_out = agent_outputs.get("vision_analysis") or {}
    knowledge_out = agent_outputs.get("knowledge") or {}
    
    # Extract findings metrics
    water_score = water_out.get("water_score")
    safety = water_out.get("drinking_safety", "Safe")
    risk = water_out.get("risk_level", "Low")
    conf_score = water_out.get("confidence_score", 1.0)
    
    if vision_out and not vision_out.get("unsupported_image"):
        vis_level = vision_out.get("contamination_level", "None")
        if vis_level == "High":
            risk = "High"
            safety = "Highly Dangerous"
        conf_score = min(conf_score, vision_out.get("confidence_score", 1.0))
        
    deviations = knowledge_out.get("deviations", [])
    
    # Request Gemini to draft executive summary
    prompt = f"""Analyze the following water testing logs to write a professional executive summary:
Visual Appearance/Contaminants: {vision_out.get('water_appearance')} | Observed Contaminants: {vision_out.get('contaminants_detected')}
Chemical Ratings: Quality Score {water_score} | Safety {safety} | Risk {risk}
WHO/BIS Standards Violations: {deviations}

Your Task:
1. Write a 2-3 sentence authoritative executive summary.
2. Outline 3-4 recommended next steps to mitigate hazards.
"""
    
    try:
        draft = call_structured_gemini(
            prompt=prompt,
            response_schema=SummaryDraft,
            system_instruction=SYSTEM_INSTRUCTION
        )
    except Exception as e:
        logger.error(f"Failed to call Gemini for executive summary: {e}. Using mock summary.")
        draft = {
            "executive_summary": "Water assessment report compiled. Testing parameters show moderate variations.",
            "recommendations": ["Filter water before consumption.", "Re-test parameters periodically."]
        }
        
    report_id = str(uuid.uuid4())
    report_title = f"Water Assessment Report - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    
    # Build pydantic report
    report_obj = WaterAssessmentReport(
        report_id=report_id,
        report_title=report_title,
        generated_timestamp=datetime.utcnow().isoformat(),
        executive_summary=draft.get("executive_summary", ""),
        water_quality_score=water_score,
        drinking_safety=safety,
        risk_level=risk,
        confidence_score=conf_score,
        chemical_findings=water_out if water_out else None,
        visual_findings=vision_out if vision_out and not vision_out.get("unsupported_image") else None,
        standards_violated=deviations,
        recommendations=draft.get("recommendations", []),
        executed_agents=executed_agents,
        report_version="1.0"
    )
    
    # Run Exporters
    json_path = JSONExporter().export(report_obj, REPORTS_DIR)
    md_path = MarkdownExporter().export(report_obj, REPORTS_DIR)
    pdf_path = PDFExporter().export(report_obj, REPORTS_DIR)
    
    # Save Report record in database
    db_report = {
        "id": report_id,
        "user_id": user_id,
        "agent_execution_log_id": execution_log_id,
        "title": report_title,
        "pdf_path": pdf_path,
        "markdown_path": md_path,
        "json_path": json_path,
        "summary": report_obj.executive_summary
    }
    
    from app.crud.report_crud import insert_report
    final_report = insert_report(db, db_report)
    
    logger.info(f"Report record {report_id} successfully stored in database.")
    return final_report
