from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import List
from supabase import Client
from app.services.db_service import get_supabase
from app.services.auth_service import get_current_user
from app.agents.report_generator import generate_water_report
from app.crud.report_crud import get_execution_log, get_user_reports, get_report_by_id, delete_report as crud_delete_report
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger("aquasentinel")

router = APIRouter(prefix="/reports", tags=["Reports"])

class ManualExportRequest(BaseModel):
    execution_log_id: str
    session_id: str

@router.post("/export")
async def export_report_manually(
    req: ManualExportRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Exports a report manually from a past execution log."""
    log = get_execution_log(supabase, req.execution_log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Execution log trace not found.")
        
    try:
        db_report = generate_water_report(
            user_id=current_user["id"],
            chat_session_id=req.session_id,
            execution_log_id=log["id"],
            agent_outputs=log.get("final_outputs_json") or {},
            executed_agents=log.get("plan_json", {}).get("selected_agents", []) if log.get("plan_json") else [],
            db=supabase
        )
        return {
            "report_id": db_report["id"],
            "title": db_report["title"],
            "pdf_url": f"/api/v1/reports/download/{db_report['id']}/pdf",
            "summary": db_report["summary"]
        }
    except Exception as e:
        logger.error(f"Manual report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")

@router.get("")
async def get_user_reports_api(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Fetches historical reports for the authenticated user."""
    reports = get_user_reports(supabase, current_user["id"])
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "summary": r["summary"],
            "pdf_url": f"/api/v1/reports/download/{r['id']}/pdf",
            "markdown_url": f"/api/v1/reports/download/{r['id']}/markdown",
            "json_url": f"/api/v1/reports/download/{r['id']}/json",
            "created_at": r["created_at"]
        } for r in reports
    ]

@router.get("/{report_id}")
async def get_report_details(
    report_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Retrieves full details of a specific report by ID."""
    report = get_report_by_id(supabase, report_id, current_user["id"])
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or access denied.")
        
    return {
        "id": report["id"],
        "title": report["title"],
        "summary": report["summary"],
        "pdf_url": f"/api/v1/reports/download/{report['id']}/pdf",
        "markdown_url": f"/api/v1/reports/download/{report['id']}/markdown",
        "json_url": f"/api/v1/reports/download/{report['id']}/json",
        "created_at": report["created_at"],
        "execution_log_id": report["agent_execution_log_id"]
    }

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Deletes a report record from the database and removes files from disk."""
    report = get_report_by_id(supabase, report_id, current_user["id"])
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or access denied.")
        
    # Delete disk files
    for filepath in [report.get("pdf_path"), report.get("markdown_path"), report.get("json_path")]:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"Deleted report file from disk: {filepath}")
            except Exception as fe:
                logger.error(f"Failed to delete file {filepath}: {fe}")
                
    crud_delete_report(supabase, report_id, current_user["id"])
    return {"message": "Report successfully deleted."}

@router.get("/download/{report_id}/{file_format}")
async def download_report_file(
    report_id: str,
    file_format: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Downloads a specific format of the water assessment report (PDF, Markdown, or JSON)."""
    report = get_report_by_id(supabase, report_id, current_user["id"])
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or access denied.")
        
    # Map formats
    if file_format == "pdf":
        filepath = report.get("pdf_path")
        media_type = "application/pdf"
        suffix = "pdf"
    elif file_format == "markdown":
        filepath = report.get("markdown_path")
        media_type = "text/markdown"
        suffix = "md"
    elif file_format == "json":
        filepath = report.get("json_path")
        media_type = "application/json"
        suffix = "json"
    else:
        raise HTTPException(status_code=400, detail="Invalid format requested. Options: 'pdf', 'markdown', 'json'.")
        
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File download missing on disk: {filepath}")
        
    filename = f"aquasentinel_report_{report_id}.{suffix}"
    return FileResponse(filepath, media_type=media_type, filename=filename)
