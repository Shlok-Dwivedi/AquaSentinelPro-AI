import logging
from app.graph.state import AgentState
from app.services.db_service import get_supabase_unauth
from app.crud.user_crud import load_user_memory_context

logger = logging.getLogger("aquasentinel")

def memory_load_node(state: AgentState) -> AgentState:
    """Loads user historical memory context from the database and injects it into AgentState."""
    user_id = state.get("user_id", "default_user")
    logger.info(f"Loading user memory context for user_id: {user_id}")
    
    try:
        supabase = get_supabase_unauth()
        memory_data = load_user_memory_context(supabase, user_id)
        state["user_memory"] = memory_data
        logger.info(f"Memory context loaded successfully for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Error loading user memory context: {e}")
        # Inject standard fallback memory context if database fails
        state["user_memory"] = {
            "user_id": user_id,
            "name": "Default User",
            "location": "Mumbai, India",
            "water_source": "Municipal Tap",
            "household_size": 4,
            "memory_context": {},
            "history": {
                "total_analyses": 0,
                "latest_water_score": None,
                "latest_risk_level": None,
                "total_complaints": 0
            }
        }
        
    return state
