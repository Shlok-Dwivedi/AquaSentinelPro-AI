import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.agent_schemas import WaterAssessmentReport

logger = logging.getLogger("aquasentinel")

REPORTS_DIR = "./static/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

class ExportProvider(ABC):
    """Abstract interface defining the export interface for report files."""
    @abstractmethod
    def export(self, report: WaterAssessmentReport, output_dir: str) -> str:
        """Generates the report file and returns the file path on disk."""
        pass

class JSONExporter(ExportProvider):
    """Exports assessment reports as raw structured JSON."""
    def export(self, report: WaterAssessmentReport, output_dir: str) -> str:
        filename = f"report_{report.report_id}.json"
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report.dict(), f, indent=2, default=str)
        logger.info(f"JSONExporter: Saved report to {path}")
        return path

class MarkdownExporter(ExportProvider):
    """Exports assessment reports as clean markdown reports."""
    def export(self, report: WaterAssessmentReport, output_dir: str) -> str:
        filename = f"report_{report.report_id}.md"
        path = os.path.join(output_dir, filename)
        
        md = f"""# {report.report_title}

**Report ID:** {report.report_id}  
**Timestamp:** {report.generated_timestamp}  
**Platform Version:** {report.report_version}  

---

## 📋 Executive Summary
{report.executive_summary}

---

## 📊 Assessment Summary
* **Water Quality Score:** {report.water_quality_score if report.water_quality_score is not None else 'N/A'} / 100
* **Drinking Safety:** {report.drinking_safety}
* **Overall Risk Level:** {report.risk_level}
* **Confidence Rating:** {report.confidence_score * 100:.1f}%

---

"""
        if report.chemical_findings:
            md += "## 🧪 Chemical Analysis\n"
            for k, v in report.chemical_findings.items():
                if isinstance(v, dict):
                    md += f"* **{k.upper()}**: {v.get('value')} ({v.get('status')})\n"
            md += "\n"

        if report.visual_findings:
            md += "## 👁️ Visual Findings (Gemini Vision)\n"
            md += f"* **Appearance:** {report.visual_findings.get('water_appearance', 'N/A')}\n"
            md += f"* **Estimated Turbidity:** {report.visual_findings.get('estimated_turbidity', 'N/A')}\n"
            md += f"* **Estimated Color:** {report.visual_findings.get('estimated_water_color', 'N/A')}\n"
            md += f"* **Detected Hazards:** {', '.join(report.visual_findings.get('contaminants_detected', [])) if report.visual_findings.get('contaminants_detected') else 'None'}\n\n"

        if report.standards_violated:
            md += "## 📜 Standard Guideline Deviations (WHO / BIS)\n"
            for dev in report.standards_violated:
                md += f"* ❌ **{dev.get('parameter', '').upper()}**: Current {dev.get('value')} exceeds {dev.get('standard')} limit of {dev.get('limit')}. *{dev.get('explanation')}*\n"
            md += "\n"

        md += "## 🛠️ Recommended Next Steps\n"
        for i, rec in enumerate(report.recommendations, 1):
            md += f"{i}. {rec}\n"
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
            
        logger.info(f"MarkdownExporter: Saved report to {path}")
        return path

class PDFExporter(ExportProvider):
    """Exports assessment reports as styled print-ready PDFs using ReportLab."""
    def export(self, report: WaterAssessmentReport, output_dir: str) -> str:
        filename = f"report_{report.report_id}.pdf"
        path = os.path.join(output_dir, filename)
        
        # Setup document flow template
        doc = SimpleDocTemplate(
            path,
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=40, bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Custom stylesheet definitions
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor("#0284c7"), # Aqua Blue
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor("#0f172a"), # Slate 900
            spaceBefore=15,
            spaceAfter=10
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155") # Slate 700
        )
        bullet_style = ParagraphStyle(
            'Bullet',
            parent=body_style,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=4
        )
        
        story = []
        
        # 1. Branding Header
        story.append(Paragraph("💧 AquaSentinel Water Assessment Report", title_style))
        story.append(Spacer(1, 5))
        
        # Meta Table
        meta_data = [
            [f"Report ID: {report.report_id}", f"Generated: {report.generated_timestamp}"],
            [f"Version: {report.report_version}", f"Executed Agents: {', '.join(report.executed_agents)}"]
        ]
        t_meta = Table(meta_data, colWidths=[270, 270])
        t_meta.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#64748b")),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Oblique'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 15))
        
        # 2. Executive Summary Block
        story.append(Paragraph("Executive Summary", h2_style))
        story.append(Paragraph(report.executive_summary, body_style))
        story.append(Spacer(1, 15))
        
        # 3. Assessment Metrics Table
        story.append(Paragraph("Assessment Metrics Summary", h2_style))
        metrics_data = [
            ["Metric Parameter", "Finding / Rating"],
            ["Water Quality Score", f"{report.water_quality_score if report.water_quality_score is not None else 'N/A'} / 100"],
            ["Drinking Safety Status", report.drinking_safety],
            ["Overall Risk Level", report.risk_level],
            ["Assessment Confidence Rating", f"{report.confidence_score * 100:.1f}%"]
        ]
        t_metrics = Table(metrics_data, colWidths=[200, 340])
        t_metrics.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
        ]))
        story.append(t_metrics)
        story.append(Spacer(1, 15))
        
        # 4. Chemical or Visual details
        if report.chemical_findings or report.visual_findings:
            story.append(Paragraph("Specialist Analysis Findings", h2_style))
            if report.chemical_findings:
                chem_p = "<b>Chemical Readings:</b> " + ", ".join([f"{k.upper()}: {v.get('value')} ({v.get('status')})" for k, v in report.chemical_findings.items() if isinstance(v, dict)])
                story.append(Paragraph(chem_p, body_style))
                story.append(Spacer(1, 6))
            if report.visual_findings:
                vis_p = f"<b>Visual Image Analysis:</b> Appearance: {report.visual_findings.get('water_appearance')}, Estimated Turbidity: {report.visual_findings.get('estimated_turbidity')}, Color: {report.visual_findings.get('estimated_water_color')}"
                story.append(Paragraph(vis_p, body_style))
                story.append(Spacer(1, 10))
                
        # 5. WHO/BIS Standards check
        if report.standards_violated:
            story.append(Paragraph("Standards Guideline Deviations", h2_style))
            std_data = [["Parameter", "Threshold Limit", "Current Value", "Violated Standard", "Explanation"]]
            for dev in report.standards_violated:
                std_data.append([
                    dev.get('parameter', '').upper(),
                    str(dev.get('limit', '')),
                    str(dev.get('value', '')),
                    dev.get('standard', ''),
                    dev.get('explanation', '')
                ])
            t_std = Table(std_data, colWidths=[70, 70, 70, 110, 220])
            t_std.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#fef2f2")), # Soft red
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#991b1b")),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#fca5a5")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_std)
            story.append(Spacer(1, 15))

        # 6. Recommendations
        story.append(Paragraph("Recommended Mitigation Steps", h2_style))
        for i, rec in enumerate(report.recommendations, 1):
            p_text = f"<b>{i}.</b> {rec}"
            story.append(Paragraph(p_text, bullet_style))
            
        # Build PDF
        doc.build(story)
        logger.info(f"PDFExporter: Styled PDF report built at {path}")
        return path
