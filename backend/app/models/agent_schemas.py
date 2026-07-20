from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TaskPlan(BaseModel):
    selected_agents: List[str] = Field(
        description="List of specialized agents selected to handle the query. Options: 'water_analysis', 'vision_analysis', 'purification', 'conservation', 'knowledge', 'complaint', 'report_generation'."
    )
    dependencies: Dict[str, List[str]] = Field(
        description="Mapping of specialized agent names to lists of their upstream agent dependencies."
    )
    execution_order: List[str] = Field(
        description="The sequential list representing execution order, e.g. ['water_analysis', 'knowledge']."
    )
    is_water_image: bool = Field(
        description="Set to False if an image is uploaded but it is clearly unrelated to water safety, sanitation, rivers, tanks, or tap water."
    )

class WaterAnalysisResult(BaseModel):
    water_score: float = Field(description="Quality score from 0-100 calculated by the scoring engine")
    drinking_safety: str = Field(description="Safety rating from the scoring engine")
    risk_level: str = Field(description="Risk classification from the scoring engine")
    contaminants_found: List[str] = Field(description="List of contaminants from the scoring engine")
    observations: str = Field(description="Gemini observations on the parameters and calculated score")
    explanation: str = Field(description="Gemini explanation of the chemical findings")
    possible_causes: List[str] = Field(description="Gemini list of potential sources/causes of contamination")
    confidence_score: float = Field(description="Confidence score of the analysis (0.0 to 1.0)")

class VisionAnalysisResult(BaseModel):
    contaminants_detected: List[str] = Field(description="Algae, floating waste, plastic, oil, foam, sediment etc.")
    structural_issues: List[str] = Field(description="Damaged pipes, damaged storage tanks, open/uncovered source, etc.")
    water_appearance: str = Field(description="Visual description of the water (e.g. clear, cloudy, muddy, green)")
    estimated_turbidity: str = Field(description="Visual estimation of turbidity (e.g. Clear, Slight, Moderate, Severe)")
    estimated_water_color: str = Field(description="Estimated color of the water (e.g. Clear, Brown, Green, Milky)")
    contamination_level: str = Field(description="Contamination level rating: 'None', 'Low', 'Medium', 'High'")
    confidence_score: float = Field(description="Confidence score of vision validation (0.0 to 1.0)")
    observations: str = Field(description="Detailed visual analysis observations")
    recommended_actions: List[str] = Field(description="Recommended local visual/structural maintenance actions")

class KnowledgeValidationResult(BaseModel):
    is_compliant: bool = Field(description="True if complies with all standard limits")
    standards_checked: List[str] = Field(description="Reference standard sheets loaded")
    deviations: List[Dict[str, Any]] = Field(
        description="List of parameter violations, e.g., [{'parameter': 'TDS', 'standard': 'WHO', 'limit': 500, 'value': 750, 'explanation': 'Exceeded WHO drinking limit'}]"
    )
    explanation: str = Field(description="Detailed rationale on compliance status")
    confidence_score: float = Field(description="Confidence score of validation (0.0 to 1.0)")

class PurificationRecommendation(BaseModel):
    recommended_methods: List[str]
    suitability_reasons: Dict[str, str]
    warning: Optional[str] = None

class ConservationPlan(BaseModel):
    strategies: List[str]
    estimated_daily_savings_liters: float

class ComplaintDraft(BaseModel):
    target_department: str
    severity: str
    subject: str
    body: str

class ReflectionResult(BaseModel):
    is_valid: bool = Field(description="True if water analysis and knowledge validations are consistent and complete")
    safety_violations: List[str] = Field(description="Logical contradictions or contradictions found")
    refinement_instructions: Optional[str] = Field(description="Instructions to retry agent execution if invalid")


class WaterAssessmentReport(BaseModel):
    report_id: str
    report_title: str
    generated_timestamp: str
    executive_summary: str
    water_quality_score: Optional[float] = None
    drinking_safety: str
    risk_level: str
    confidence_score: float
    chemical_findings: Optional[Dict[str, Any]] = None
    visual_findings: Optional[Dict[str, Any]] = None
    standards_violated: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    executed_agents: List[str] = Field(default_factory=list)
    report_version: str = "1.0"

