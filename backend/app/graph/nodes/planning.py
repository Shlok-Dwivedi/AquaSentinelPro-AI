import logging
from app.graph.state import AgentState
from app.models.agent_schemas import TaskPlan
from app.services.gemini_service import call_structured_gemini

logger = logging.getLogger("aquasentinel")

SYSTEM_INSTRUCTION = """You are the Lead Planning Agent of the AquaSentinel-AI Multi-Agent Platform.
Your task is to analyze user queries, uploaded image paths, manual parameters, and user memory context, and plan an execution route.

Core Rules for Images:
1. Inspect the uploaded image reference path details. If an image is provided but is clearly unrelated to water safety, rivers, taps, pipelines, or water tanks (for example, a photo of a keyboard, dog, car, or general text document), you MUST set 'is_water_image' to False, set 'selected_agents' to an empty list, and set 'execution_order' to an empty list.
2. If it is a water-related image, set 'is_water_image' to True, and add 'vision_analysis' to the selected agents list.

Available Specialized Agents:
1. 'water_analysis': Triggered if manual chemical water parameters are provided (pH, TDS, turbidity, hardness, chlorine, fluoride).
2. 'knowledge': Triggered to evaluate chemical scores against BIS/WHO standard specifications. Must depend on 'water_analysis'.
3. 'vision_analysis': Triggered if a valid water-related image file path is uploaded.
4. 'purification': Triggered to suggest filters (RO, UV, UF, activated carbon). Must depend on 'water_analysis' or 'vision_analysis' if they are running.
5. 'conservation': Triggered if the user asks for water-saving advice, conservation measures, or rainwater harvesting.
6. 'complaint': Triggered if the user reports a service issue, pollution, leakage, or requests to file a complaint letter to municipal authorities.
7. 'report_generation': Triggered if the user explicitly requests a PDF file download, report generation, or summary compilation. Depend on all other selected active specialist agents.

Task:
Determine:
1. 'selected_agents': Which agents are needed.
2. 'dependencies': Which agent results are required by other agents.
3. 'execution_order': Flat list showing the exact order to execute the nodes.
4. 'is_water_image': Boolean flagging if the image is a water/sanitation asset.

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
        
        # Check if the image is flagged as unsupported
        if plan_result.get("is_water_image") is False:
            logger.warning("Planning Agent flagged the uploaded image as unrelated to water. Skipping Vision node.")
            state["plan"] = {
                "selected_agents": [],
                "dependencies": {},
                "execution_order": [],
                "is_water_image": False
            }
            state["agent_outputs"]["vision_analysis"] = {
                "unsupported_image": True,
                "observations": "Unsupported Image. The uploaded image is clearly unrelated to water safety or sanitation."
            }
        else:
            state["plan"] = plan_result
            
        state["current_step"] = 0
        logger.info(f"Planning Agent generated plan: {state['plan']}")
    except Exception as e:
        logger.error(f"Error in Planning Agent: {e}")
        # Default fallback plan: execute water analysis and knowledge
        state["plan"] = {
            "selected_agents": ["water_analysis", "knowledge"],
            "dependencies": {"knowledge": ["water_analysis"]},
            "execution_order": ["water_analysis", "knowledge"],
            "is_water_image": True
        }
        state["current_step"] = 0
        
    return state
