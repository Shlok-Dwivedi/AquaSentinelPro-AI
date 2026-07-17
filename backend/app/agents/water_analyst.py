import logging
from app.utils.water_score import calculate_water_score
from app.services.gemini_service import call_structured_gemini
from app.models.agent_schemas import WaterAnalysisResult

logger = logging.getLogger("aquasentinel")

SYSTEM_INSTRUCTION = """You are a senior hydrological chemist and water safety inspector.
Your role is to explain chemical conditions, note observations, and state possible environmental causes of contaminations.
You MUST NOT calculate or change the water quality score, drinking safety, or risk level. Use the values provided in the prompt exactly.
"""

def run_water_analyst(params: dict) -> WaterAnalysisResult:
    """Executes deterministic scoring and prompts Gemini Flash to generate reasoning and possible causes."""
    # 1. Run Python rule-based scoring engine
    score_result = calculate_water_score(params)
    logger.info(f"Water scoring engine output: Score={score_result.score}, Safety={score_result.drinking_safety}")
    
    # 2. Build reasoning prompt for Gemini
    prompt = f"""Review the domestic water testing logs and calculated score details:
Testing Parameters: {params}
Calculated Water Quality Score: {score_result.score} / 100
Assigned Drinking Safety: {score_result.drinking_safety}
Assigned Risk Level: {score_result.risk_level}
Flagged Contaminants: {score_result.detected_contaminants}
Parameter Breakdown: {score_result.parameter_breakdown}

Your Task:
Generate observations, possible causes, and a detailed explanation of these chemical parameters.
Ensure the returned JSON contains the exact calculated values:
- 'water_score': {score_result.score}
- 'drinking_safety': "{score_result.drinking_safety}"
- 'risk_level': "{score_result.risk_level}"
- 'contaminants_found': {score_result.detected_contaminants}
"""
    try:
        # Call Gemini Structured JSON
        ai_response = call_structured_gemini(
            prompt=prompt,
            response_schema=WaterAnalysisResult,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # Override to guarantee deterministic values are not altered by LLM
        ai_response["water_score"] = score_result.score
        ai_response["drinking_safety"] = score_result.drinking_safety
        ai_response["risk_level"] = score_result.risk_level
        ai_response["contaminants_found"] = score_result.detected_contaminants
        
        return WaterAnalysisResult(**ai_response)
    except Exception as e:
        logger.error(f"Error executing Water Analysis Agent: {e}")
        # Standard offline fallback
        return WaterAnalysisResult(
            water_score=score_result.score,
            drinking_safety=score_result.drinking_safety,
            risk_level=score_result.risk_level,
            contaminants_found=score_result.detected_contaminants,
            observations="Rule-based fallback: Parameters indicate potential deviations.",
            explanation="The database fallback generated observations due to API timeout.",
            possible_causes=["Agricultural runoff", "Plumbing degradation"],
            confidence_score=0.9
        )
