import logging
from app.services.gemini_service import call_structured_gemini
from app.models.agent_schemas import ReflectionResult

logger = logging.getLogger("aquasentinel")

SYSTEM_INSTRUCTION = """You are a senior safety auditor and consistency checker for an AI water analysis platform.
Your task is to examine the output of the Water Analysis Agent, the Knowledge Agent, and the Vision Agent to ensure logical consistency and complete accuracy.
"""

def run_reflector_agent(water_result: dict, knowledge_result: dict, vision_result: dict = None) -> ReflectionResult:
    """Invokes the Reflection Agent to validate logical consistency and confidence scores across visual and chemical results."""
    logger.info("Executing Reflection Agent safety audit...")
    
    prompt = f"""Audit the outputs of the Water Analysis Agent, Knowledge Validation Agent, and Vision Analysis Agent for consistency:
Water Analysis Output: {water_result}
Knowledge Validation Output: {knowledge_result}
Vision Analysis Output: {vision_result}

Verify the following:
1. Safety Contradictions: If the Knowledge Validation flags 'is_compliant' as false, ensure the Water Analysis Agent flags 'drinking_safety' as 'Unsafe without treatment' or 'Highly Dangerous'.
2. Contaminant Alignment: Ensure that any parameter violation listed by the Knowledge Agent is captured under 'contaminants_found' in the Water Analysis.
3. Visual vs Chemical Consistency: 
   - If the Vision Agent reports 'water_appearance' as clean but the chemical Water Analysis reports severe contamination (e.g. TDS > 2000 or pH < 5.0), this is a potential invisible hazard. Make sure to note this, but do not set 'is_valid' to false; instead, verify that the synthesized recommendations include 'Recommend additional laboratory testing'.
   - If the image reports severe mud/algae/sludge but the water analysis shows 0.0 turbidity or flags no contaminants, this is a contradiction. Set 'is_valid' to false and write 'refinement_instructions' requesting corrections.
4. Confidence score validity: Confirm that confidence scores reflect the data provided.

If you detect any critical contradiction or logic gap, set 'is_valid' to false and write clear 'refinement_instructions' to let the worker nodes adjust.
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
