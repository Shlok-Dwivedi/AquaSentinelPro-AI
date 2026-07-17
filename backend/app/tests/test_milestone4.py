import os
import sys
import asyncio
import shutil

# Add the grandparent directory of this file to the Python path (backend/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.graph.workflow import app_workflow
from app.graph.state import AgentState
from app.services.db_service import init_db

# Create temporary folder for test files
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_temp")
os.makedirs(TEST_DIR, exist_ok=True)

def create_temp_image(name: str) -> str:
    path = os.path.join(TEST_DIR, name)
    with open(path, "w") as f:
        f.write("mock image content")
    return path

async def run_vision_test(scenario_name: str, query: str, filename: str, params: dict = None):
    print(f"\n==================================================")
    print(f"TEST: {scenario_name}")
    print(f"Image Filename: {filename}")
    print(f"Params: {params}")
    print(f"==================================================")
    
    # Create the mock file on disk
    image_path = create_temp_image(filename)
    
    # Construct AgentState
    initial_state = AgentState(
        user_id="test_user_milestone4",
        session_id=f"session_{scenario_name.lower().replace(' ', '_')}",
        user_query=query,
        image_path=image_path,
        raw_parameters=params,
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
    
    try:
        final_state = await app_workflow.ainvoke(initial_state)
        plan = final_state.get("plan", {})
        selected = plan.get("selected_agents", [])
        outputs = final_state.get("agent_outputs", {})
        
        print(f"[Workflow] Selected Agents: {selected}")
        print(f"[Workflow] Response Length: {len(final_state['synthesized_response'])}")
        
        # Scenario assertions
        if "unsupported" in filename:
            assert plan.get("is_water_image") is False, "Unsupported image was not flagged as False!"
            assert "vision_analysis" not in selected, "Vision node was not skipped for unsupported image!"
            assert outputs.get("vision_analysis", {}).get("unsupported_image") is True, "unsupported_image flag not saved!"
            print("--> Unsupported validation PASSED")
            
        else:
            assert plan.get("is_water_image") is True, "Valid water image flagged as unsupported!"
            assert "vision_analysis" in selected, "Vision analysis skipped for valid image!"
            
            vision_out = outputs.get("vision_analysis", {})
            assert vision_out is not None, "Vision output was not populated!"
            
            # Substring asserts matching MockVisionProvider
            if "clean" in filename:
                assert vision_out.get("contamination_level") == "None", "Clean image test failed!"
            elif "murky" in filename:
                assert vision_out.get("contamination_level") == "High", "Murky image test failed!"
                assert "Sediment" in vision_out.get("contaminants_detected", []), "Sediment contaminant not flagged!"
            elif "plastic" in filename:
                assert vision_out.get("contamination_level") == "High", "Plastic image test failed!"
                assert "Plastic waste" in vision_out.get("contaminants_detected", []), "Plastic contaminants not flagged!"
            elif "algae" in filename:
                assert vision_out.get("contamination_level") == "Medium", "Algae image test failed!"
                assert "Algae" in vision_out.get("contaminants_detected", []), "Algae contaminants not flagged!"
            elif "oil" in filename:
                assert vision_out.get("contamination_level") == "High", "Oil slick test failed!"
                assert "Oil slick" in vision_out.get("contaminants_detected", []), "Oil contaminants not flagged!"
            elif "foam" in filename:
                assert vision_out.get("contamination_level") == "Medium", "Foam test failed!"
                
            # Combined analysis check
            if params and params.get("tds"):
                assert "water_analysis" in selected, "Water analysis was not run alongside vision!"
                water_out = outputs.get("water_analysis", {})
                assert water_out.get("water_score") is not None, "Water quality score not calculated!"
                
        print("--> VERIFIED [PASS]")
        
    except AssertionError as ae:
        print(f"--> FAILED [FAIL]: {ae}")
        raise ae
    except Exception as e:
        print(f"--> ERROR [FAIL]: {e}")
        raise e

async def main():
    print("Verifying database schema...")
    try:
        init_db()
        print("Database schema loaded.")
    except Exception as e:
        print(f"Database bootstrap warning: {e}")
        
    print("Starting Automated Integration Tests for Milestone 4...")
    
    try:
        # 1. Clean water image
        await run_vision_test("Clean Water Image", "Look at this tap water filter, looks fine.", "clean_tap.jpg")
        
        # 2. Murky water
        await run_vision_test("Murky River", "The stream looks brownish after the rains.", "murky_river.png")
        
        # 3. Plastic waste
        await run_vision_test("Plastic Pollution", "Floating bottles in the storage tank.", "plastic_tank.jpg")
        
        # 4. Algae contamination
        await run_vision_test("Algae Bloom", "Green film growing in open well.", "algae_well.webp")
        
        # 5. Oil contamination
        await run_vision_test("Oil Slick", "Water surface shows rainbow chemical sheen.", "oil_sheen.jpg")
        
        # 6. Combined image + TDS parameters
        await run_vision_test("Image + High TDS", "Image of murky water. TDS parameters show 750.", "murky_pond.jpg", {"tds": 750.0})
        
        # 7. Unsupported image
        await run_vision_test("Unsupported Content", "My keyboard is dirty.", "unsupported_keyboard.jpg")
        
        # 8. Image only
        await run_vision_test("Image Only", "Analyzing the well surface.", "murky_well.png")
        
    finally:
        # Cleanup temporary files
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
            print("\nCleaned up temporary test files.")
            
    print("\n==================================================")
    print("ALL MILESTONE 4 INTEGRATION SCENARIOS VERIFIED SUCCESSFULLY! [PASS]")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
