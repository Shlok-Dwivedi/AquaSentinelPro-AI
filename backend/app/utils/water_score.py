from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class WaterScoreResult(BaseModel):
    score: float
    risk_level: str
    drinking_safety: str
    detected_contaminants: List[str]
    parameter_breakdown: Dict[str, Dict[str, Any]]

def calculate_water_score(params: Optional[Dict[str, float]]) -> WaterScoreResult:
    """Calculates a deterministic water quality score (0-100) based on chemical parameters."""
    if not params:
        return WaterScoreResult(
            score=100.0,
            risk_level="Low",
            drinking_safety="Safe (No parameters provided for testing)",
            detected_contaminants=[],
            parameter_breakdown={}
        )
        
    base_score = 100.0
    penalties = 0.0
    detected_contaminants = []
    parameter_breakdown = {}
    
    # 1. pH Level (Optimal: 7.0 - 7.6, Permissible: 6.5 - 8.5)
    if "ph" in params:
        val = params["ph"]
        status = "Optimal"
        penalty = 0.0
        if val < 6.5:
            status = "Acidic"
            penalty = 25.0 if val < 6.0 else 15.0
            detected_contaminants.append("High Acidity")
        elif val > 8.5:
            status = "Alkaline"
            penalty = 25.0 if val > 9.0 else 15.0
            detected_contaminants.append("High Alkalinity")
        penalties += penalty
        parameter_breakdown["ph"] = {"value": val, "status": status, "penalty": penalty}

    # 2. TDS (Total Dissolved Solids) (WHO standard: < 500 mg/L)
    if "tds" in params:
        val = params["tds"]
        status = "Excellent"
        penalty = 0.0
        if val > 500:
            status = "Fair"
            penalty = 15.0
            detected_contaminants.append("High Dissolved Solids")
        if val > 1000:
            status = "Poor"
            penalty = 30.0
        if val > 2000:
            status = "Unacceptable"
            penalty = 50.0
        penalties += penalty
        parameter_breakdown["tds"] = {"value": val, "status": status, "penalty": penalty}

    # 3. Turbidity (BIS: < 1 NTU, WHO: < 5 NTU)
    if "turbidity" in params:
        val = params["turbidity"]
        status = "Clear"
        penalty = 0.0
        if val > 1.0:
            status = "Slightly Turbid"
            penalty = 10.0
            detected_contaminants.append("Suspended Turbidity")
        if val > 5.0:
            status = "Highly Turbid"
            penalty = 30.0
        penalties += penalty
        parameter_breakdown["turbidity"] = {"value": val, "status": status, "penalty": penalty}

    # 4. Hardness (BIS limit: 200 mg/L, WHO: 300 mg/L)
    if "hardness" in params:
        val = params["hardness"]
        status = "Soft"
        penalty = 0.0
        if val > 150:
            status = "Hard"
        if val > 200:
            status = "Very Hard"
            penalty = 10.0
            detected_contaminants.append("High Hardness (Scale Formation)")
        if val > 300:
            status = "Extremely Hard"
            penalty = 20.0
        penalties += penalty
        parameter_breakdown["hardness"] = {"value": val, "status": status, "penalty": penalty}

    # 5. Chlorine (BIS: < 0.2 mg/L residual, WHO: < 5 mg/L)
    if "chlorine" in params:
        val = params["chlorine"]
        status = "Normal"
        penalty = 0.0
        if val > 0.2:
            status = "Residual Level"
        if val > 2.0:
            status = "High Chlorine"
            penalty = 10.0
            detected_contaminants.append("Excessive Chlorination")
        if val > 5.0:
            status = "Unsafe Chlorine"
            penalty = 20.0
        penalties += penalty
        parameter_breakdown["chlorine"] = {"value": val, "status": status, "penalty": penalty}

    # 6. Fluoride (BIS: < 1.0 mg/L, WHO: < 1.5 mg/L)
    if "fluoride" in params:
        val = params["fluoride"]
        status = "Optimal"
        penalty = 0.0
        if val > 1.0:
            status = "High Fluoride"
            penalty = 15.0
            detected_contaminants.append("Excessive Fluoride")
        if val > 1.5:
            status = "Unsafe Fluoride"
            penalty = 35.0
        penalties += penalty
        parameter_breakdown["fluoride"] = {"value": val, "status": status, "penalty": penalty}

    # Calculate final aggregate score (bounded 0 to 100)
    score = max(0.0, base_score - penalties)
    
    # Classify Risk Level
    if score >= 85:
        risk_level = "Low"
    elif score >= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Classify Drinking Safety
    if score >= 85:
        drinking_safety = "Safe"
    elif score >= 50:
        drinking_safety = "Unsafe without treatment"
    else:
        drinking_safety = "Highly Dangerous"

    return WaterScoreResult(
        score=score,
        risk_level=risk_level,
        drinking_safety=drinking_safety,
        detected_contaminants=detected_contaminants,
        parameter_breakdown=parameter_breakdown
    )
