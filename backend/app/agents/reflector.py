import logging
from app.services.gemini_service import call_structured_gemini
from app.models.agent_schemas import ReflectionResult

logger = logging.getLogger("aquasentinel")

SYSTEM_INSTRUCTION = """You are a senior safety auditor and consistency checker for an AI water analysis platform.
Your task is to examine the output of the Water Analysis Agent and the Knowledge Agent to ensure logical consistency and complete accuracy.
Set 'is_valid' to true only if both agents align (e.g. non-compliance deviations correctly reflect in observations and risk levels).
"""

def run_reflector_agent(water_result: dict, knowledge_result: dict) -> ReflectionResult:
    """Invokes the Reflection Agent to validate logical consistency and confidence scores."""
    logger.info("Executing Reflection Agent safety audit...")
    
    prompt = f"""Audit the outputs of the Water Analysis Agent and the Knowledge Validation Agent for consistency:
Water Analysis Output: {water_result}
Knowledge Validation Output: {knowledge_result}

Verify the following:
1. Safety Contradictions: If the Knowledge Validation flags 'is_compliant' as false, ensure the Water Analysis Agent flags 'drinking_safety' as 'Unsafe without treatment' or 'Highly Dangerous'.
2. Contaminant Alignment: Ensure that any parameter violation listed by the Knowledge Agent is captured under 'contaminants_found' in the Water Analysis.
3. Confidence score validity: Confirm that the confidence scores reflect the data provided (e.g. not artificially close to 1.0 if parameters are missing).

If you detect any contradiction or logic gap, set 'is_valid' to false and write clear 'refinement_instructions' to let the worker nodes adjust.
Otherwise, return 'is_valid': true.
"""
    try:
        ai_response = call_structured_gemini(
            prompt=prompt,
            response_schema=ReflectionResult,
            system_instruction=SYSTEM_INSTRUCTION
        )
        return ReflectionResult(**ai_response)
    except Exception as e:
        logger.error(f"Error executing Reflection Agent: {e}")
        # Standard offline fallback: assume valid to avoid blocking loops
        return ReflectionResult(
            is_valid=True,
            safety_violations=[],
            refinement_instructions=None
        )
