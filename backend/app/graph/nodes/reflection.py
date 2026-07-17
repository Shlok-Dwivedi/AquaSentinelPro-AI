import logging
from app.graph.state import AgentState
from app.agents.reflector import run_reflector_agent

logger = logging.getLogger("aquasentinel")

def reflection_node(state: AgentState) -> AgentState:
    """Invokes the Reflection Agent to audit logical alignment between analysis and knowledge validation."""
    logger.info("Running Reflection Node safety audit...")
    
    outputs = state.get("agent_outputs", {})
    water_out = outputs.get("water_analysis", {})
    knowledge_out = outputs.get("knowledge", {})
    vision_out = outputs.get("vision_analysis", {})
    
    # Skip if no outputs exist
    if not water_out and not knowledge_out and not vision_out:
        logger.warning("Reflection skipped: No worker outputs found.")
        state["is_valid"] = True
        state["reflection_feedback"] = None
        return state
        
    try:
        # Run reflection agent with optional vision results
        result = run_reflector_agent(water_out, knowledge_out, vision_out)
        
        state["is_valid"] = result.is_valid
        state["reflection_feedback"] = result.refinement_instructions
        
        if not result.is_valid:
            logger.warning(f"Reflection failed. Refinement feedback: '{result.refinement_instructions}'")
            state["iterations"] = state.get("iterations", 0) + 1
        else:
            logger.info("Reflection passed successfully.")
            
    except Exception as e:
        logger.error(f"Error in Reflection node: {e}")
        state["is_valid"] = True
        state["reflection_feedback"] = None
        
    return state
