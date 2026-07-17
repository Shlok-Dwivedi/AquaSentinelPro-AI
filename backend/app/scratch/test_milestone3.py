import os
import sys
import asyncio

# Add the grandparent directory of this file to the Python path (backend/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.graph.workflow import app_workflow
from app.graph.state import AgentState
from app.utils.water_score import calculate_water_score
from app.services.db_service import init_db

async def run_test_scenario(scenario_name: str, query: str, params: dict):
    print(f"\n==================================================")
    print(f"SCENARIO: {scenario_name}")
    print(f"Query: \"{query}\"")
    print(f"Params: {params}")
    print(f"==================================================")
    
    # 1. Verify deterministic scoring engine
    score_result = calculate_water_score(params)
    print(f"[Scoring Engine] Score: {score_result.score}, Safety: {score_result.drinking_safety}, Risk: {score_result.risk_level}")
    print(f"[Scoring Engine] Contaminants: {score_result.detected_contaminants}")
    
    # Initialize state
    initial_state = AgentState(
        user_id="test_user_id",
        session_id=f"test_session_{scenario_name.lower().replace(' ', '_')}",
        user_query=query,
        image_path=None,
        raw_parameters=params if params else None,
        user_memory={},
        plan={"selected_agents": [], "dependencies": {}, "execution_order": []},
        current_step=0,
        iterations=0,
        is_valid=False,
        agent_outputs={},
        reflection_feedback=None,
        metadata={},
        synthesized_response="",
        pdf_report_url=None
    )
    
    # 2. Run LangGraph Workflow
    try:
        final_state = await app_workflow.ainvoke(initial_state)
        print(f"[Workflow] Success! Compiled final response length: {len(final_state['synthesized_response'])}")
        
        # Print timeline checklist
        plan = final_state.get("plan", {})
        selected = plan.get("selected_agents", [])
        print(f"[Workflow] Selected Agents: {selected}")
        
        # Verify validations and compliance in agent_outputs
        outputs = final_state.get("agent_outputs", {})
        water_out = outputs.get("water_analysis", {})
        knowledge_out = outputs.get("knowledge", {})
        
        # Assertions
        assert final_state["is_valid"] == True, "Reflection check failed!"
        
        if "water_analysis" in selected:
            assert water_out["water_score"] == score_result.score, "Scoring discrepancy detected between engine and agent!"
            
        if "knowledge" in selected:
            if "750" in query or (params and params.get("tds", 0) > 500):
                assert knowledge_out["is_compliant"] == False, "TDS deviation not caught by Knowledge Agent!"
            if "5.0" in query or (params and params.get("ph", 7.0) < 6.5):
                assert knowledge_out["is_compliant"] == False, "pH deviation not caught by Knowledge Agent!"
                
        print(f"--> VERIFIED [PASS]")
        
    except AssertionError as ae:
        print(f"--> FAILED [FAIL]: {ae}")
        raise ae
    except Exception as e:
        print(f"--> ERROR [FAIL]: {e}")
        raise e

async def main():
    print("Initializing local database schema...")
    try:
        init_db()
        print("Database schema successfully verified/initialized.")
    except Exception as e:
        print(f"Database bootstrap warning: {e}")

    print("Starting Automated Integration Tests for Milestone 3...")
    
    # Scenario 1: Safe drinking water
    await run_test_scenario(
        "Safe Drinking Water",
        "Checking my tap water logs. Everything seems okay.",
        {"ph": 7.2, "tds": 200.0, "turbidity": 0.5, "hardness": 120.0, "chlorine": 0.1, "fluoride": 0.5}
    )
    
    # Scenario 2: High TDS
    await run_test_scenario(
        "High TDS Verification",
        "My water tastes salty. TDS is 750.",
        {"tds": 750.0}
    )
    
    # Scenario 3: Unsafe pH
    await run_test_scenario(
        "Unsafe pH Level",
        "The water source has a highly acidic pH level of 5.0.",
        {"ph": 5.0}
    )
    
    # Scenario 4: Multiple Contaminated Parameters
    await run_test_scenario(
        "Multiple Contaminants Infiltration",
        "Water looks cloudy and acidic. pH is 5.5, TDS is 800, Turbidity is 6.0.",
        {"ph": 5.5, "tds": 800.0, "turbidity": 6.0}
    )
    
    # Scenario 5: Missing parameters (incomplete data log)
    await run_test_scenario(
        "Incomplete Parameters",
        "Only checked TDS today, it is 300.",
        {"tds": 300.0}
    )
    
    print("\n==================================================")
    print("ALL MILESTONE 3 INTEGRATION SCENARIOS VERIFIED SUCCESSFULLY! [PASS]")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
