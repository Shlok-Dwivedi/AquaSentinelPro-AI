from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TaskPlan(BaseModel):
    selected_agents: List[str] = Field(
        description="List of specialized agents selected to handle the query. Options: 'water_analysis', 'vision_analysis', 'purification', 'conservation', 'policy_standards', 'complaint', 'report_generation'."
    )
    dependencies: Dict[str, List[str]] = Field(
        description="Mapping of specialized agent names to lists of their upstream agent dependencies. E.g., {'policy_standards': ['water_analysis']}"
    )
    execution_order: List[str] = Field(
        description="The sequential list representing execution order, e.g. ['water_analysis', 'policy_standards']."
    )

class WaterAnalysisResult(BaseModel):
    water_score: float = Field(description="Quality score from 0-100")
    drinking_safety: str = Field(description="Safety status: 'Safe', 'Unsafe with treatment', 'Highly Dangerous'")
    risk_level: str = Field(description="Risk classification: 'Low', 'Medium', 'High'")
    contaminants_found: List[str]
    detected_hazards: List[str]

class VisionAnalysisResult(BaseModel):
    detected_contaminants: List[str]
    contamination_severity: str
    structural_issues: List[str]
    description: str

class PolicyComplianceResult(BaseModel):
    is_compliant: bool
    standards_checked: List[str]
    deviations: List[Dict[str, Any]]

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
    is_valid: bool = Field(default=True)
    safety_violations: List[str] = Field(default_factory=list)
    refinement_instructions: Optional[str] = None
