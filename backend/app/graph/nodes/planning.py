import logging
from app.graph.state import AgentState
from app.models.agent_schemas import TaskPlan
from app.services.gemini_service import call_structured_gemini

logger = logging.getLogger("aquasentinel")

SYSTEM_INSTRUCTION = """You are the Lead Planning Agent of the AquaSentinel-AI Multi-Agent Platform.
Your task is to analyze user queries, uploaded image paths, manual parameters, and user memory context, and plan an execution route.

Available Specialized Agents:
1. 'water_analysis': Triggered if manual chemical water parameters are provided (pH, TDS, turbidity, hardness, chlorine, fluoride).
2. 'policy_standards': Triggered to evaluate chemical scores against BIS/WHO standard tables. Must depend on 'water_analysis'.
3. 'vision_analysis': Triggered if an image file path is uploaded.
4. 'purification': Triggered to suggest filters (RO, UV, UF, activated carbon). Must depend on 'water_analysis' or 'vision_analysis' if they are running.
5. 'conservation': Triggered if the user asks for water-saving advice, conservation measures, or rainwater harvesting.
6. 'complaint': Triggered if the user reports a service issue, pollution, leakage, or requests to file a complaint letter to municipal authorities.
7. 'report_generation': Triggered if the user explicitly requests a PDF file download, report generation, or summary compilation. Depend on all other selected active specialist agents.

Task:
Determine:
1. 'selected_agents': Which agents are needed.
2. 'dependencies': Which agent results are required by other agents.
3. 'execution_order': Flat list showing the exact order to execute the nodes. Ensure dependencies are completed before their child nodes.

Return a strict JSON output matching the TaskPlan schema.
"""

def planning_node(state: AgentState) -> AgentState:
    """Invokes the Planning Agent using Gemini Flash to dynamically decide execution routing."""
    query = state.get("user_query", "")
    params = state.get("raw_parameters", {})
    image = state.get("image_path", None)
    memory = state.get("user_memory", {})
    
    logger.info(f"Invoking Planning Agent for query: '{query}'")
    
    # Construct details context
    context = f"""User Request: {query}
Manual Water Parameters: {params}
Uploaded Image Path: {image}
User Profile Context: {memory}
"""
    try:
        # Call Gemini (or rule-based fallback) using Pydantic schema
        plan_result = call_structured_gemini(
            prompt=context,
            response_schema=TaskPlan,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # Save the plan inside state
        state["plan"] = plan_result
        state["current_step"] = 0
        
        logger.info(f"Planning Agent generated plan: {plan_result}")
    except Exception as e:
        logger.error(f"Error in Planning Agent: {e}")
        # Default fallback plan: execute water analysis and policy standards
        state["plan"] = {
            "selected_agents": ["water_analysis", "policy_standards"],
            "dependencies": {"policy_standards": ["water_analysis"]},
            "execution_order": ["water_analysis", "policy_standards"]
        }
        state["current_step"] = 0
        
    return state
