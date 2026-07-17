from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
from typing import Dict, Any, List

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/generate")
async def generate_report():
    """Compiles the latest findings into a PDF report."""
    return {
        "report_id": "dummy-report-uuid",
        "pdf_url": "/api/v1/reports/download/dummy-report-uuid",
        "summary": "This report summarizes water testing values and purification suggestions."
    }

@router.get("")
async def get_reports():
    """Fetches list of generated reports."""
    return [
        {
            "id": "report-1",
            "pdf_url": "/api/v1/reports/download/report-1",
            "summary": "This report summarizes water testing values and purification suggestions.",
            "created_at": "2026-07-17T11:30:00Z"
        }
    ]

@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Downloads a dummy compiled PDF report file."""
    # Create a small dummy PDF file in memory
    buffer = io.BytesIO()
    # Write some mock PDF headers/content so it resembles a PDF binary
    buffer.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 50 >>\nstream\nBT /F1 24 Tf 70 700 Td (AquaSentinel Dummy Report PDF) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n312\n%%EOF")
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=aquasentinel_report_{report_id}.pdf"}
    )
