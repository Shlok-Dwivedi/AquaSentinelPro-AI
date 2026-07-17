import os
import logging
import json
from abc import ABC, abstractmethod
import google.generativeai as genai
from app.config import settings
from app.models.agent_schemas import VisionAnalysisResult

logger = logging.getLogger("aquasentinel")

class VisionProvider(ABC):
    """Abstract Base Class defining the interface for Vision analysis providers."""
    @abstractmethod
    def analyze_image(self, image_path: str, mime_type: str, prompt: str) -> VisionAnalysisResult:
        """Analyzes an image file path and returns structured VisionAnalysisResult."""
        pass

class GeminiVisionProvider(VisionProvider):
    """Implements VisionProvider using real Gemini 2.5 Flash Vision capabilities."""
    def analyze_image(self, image_path: str, mime_type: str, prompt: str) -> VisionAnalysisResult:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        logger.info(f"GeminiVisionProvider: Loading image from {image_path} with mime_type: {mime_type}")
        
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            config = genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=VisionAnalysisResult,
                temperature=0.1
            )
            
            # Call model with both prompt and image block
            response = model.generate_content([prompt, image_part], generation_config=config)
            data = json.loads(response.text)
            return VisionAnalysisResult(**data)
        except Exception as e:
            logger.error(f"GeminiVisionProvider failed: {e}. Raising exception for fallback.")
            raise e

class MockVisionProvider(VisionProvider):
    """Implements a deterministic offline Mock Vision Provider for local testing."""
    def analyze_image(self, image_path: str, mime_type: str, prompt: str) -> VisionAnalysisResult:
        logger.info(f"MockVisionProvider: Simulating analysis for image: {image_path}")
        filename = os.path.basename(image_path).lower()
        
        # Scenario mapping based on filename contents
        if "clean" in filename:
            return VisionAnalysisResult(
                contaminants_detected=[],
                structural_issues=[],
                water_appearance="Clear and transparent water",
                estimated_turbidity="Clear",
                estimated_water_color="Clear",
                contamination_level="None",
                confidence_score=0.98,
                observations="The water appears clear of any visible impurities, algae, or floating waste.",
                recommended_actions=["Routine checks", "Ensure water storage remains covered"]
            )
            
        elif "murky" in filename:
            return VisionAnalysisResult(
                contaminants_detected=["Sediment", "Muddy water"],
                structural_issues=[],
                water_appearance="Cloudy, brown water indicating heavy mud/silt",
                estimated_turbidity="Severe",
                estimated_water_color="Brown",
                contamination_level="High",
                confidence_score=0.95,
                observations="Visible brown suspended silt and heavy turbidity indicating runoff or plumbing leaks.",
                recommended_actions=["Coagulation/settling", "Sand filtration", "Inspect inlet piping for dirt seepage"]
            )
            
        elif "plastic" in filename:
            return VisionAnalysisResult(
                contaminants_detected=["Plastic waste", "Floating trash"],
                structural_issues=["Damaged open storage tank"],
                water_appearance="Floating plastic debris and bottles inside water tank",
                estimated_turbidity="Slight",
                estimated_water_color="Clear",
                contamination_level="High",
                confidence_score=0.93,
                observations="Plastic bottles and household waste floating. The storage tank cover is missing/damaged.",
                recommended_actions=["Remove physical debris", "Install a secure tank lid", "Sanitize tank after cleanup"]
            )
            
        elif "algae" in filename:
            return VisionAnalysisResult(
                contaminants_detected=["Algae", "Green scum"],
                structural_issues=["Open water source exposed to direct sunlight"],
                water_appearance="Green colored water with organic moss/algae growth",
                estimated_turbidity="Moderate",
                estimated_water_color="Green",
                contamination_level="Medium",
                confidence_score=0.91,
                observations="Green organic coating and algae film on the water surface indicating nutrient loading.",
                recommended_actions=["Apply algicides or chlorination", "Provide shade coverage", "Thoroughly scrub tank walls"]
            )
            
        elif "oil" in filename:
            return VisionAnalysisResult(
                contaminants_detected=["Oil slick", "Floating film"],
                structural_issues=[],
                water_appearance="Rainbow sheen and oil patches on water surface",
                estimated_turbidity="Slight",
                estimated_water_color="Clear",
                contamination_level="High",
                confidence_score=0.94,
                observations="Rainbow chemical sheen and oil slick patches indicating petroleum/machinery grease runoff.",
                recommended_actions=["Skim the surface oil", "Activated carbon absorption", "Investigate machinery leak sources"]
            )
            
        elif "foam" in filename:
            return VisionAnalysisResult(
                contaminants_detected=["Foam", "Suds"],
                structural_issues=["Piping turbulence or chemical discharges"],
                water_appearance="White thick foam and soap-like bubbles",
                estimated_turbidity="Slight",
                estimated_water_color="Milky",
                contamination_level="Medium",
                confidence_score=0.89,
                observations="Thick white chemical foam layer indicating potential surfactant/detergent contamination.",
                recommended_actions=["Test for surfactants", "Flush supply line", "Aeration and settling"]
            )
            
        elif "unsupported" in filename:
            # Raise value error indicating unsupported image content
            raise ValueError("Unsupported Image: Image content is unrelated to water quality or sanitation.")
            
        else:
            # General default mock
            return VisionAnalysisResult(
                contaminants_detected=["Suspended solids"],
                structural_issues=[],
                water_appearance="Slightly turbid water",
                estimated_turbidity="Slight",
                estimated_water_color="Clear",
                contamination_level="Low",
                confidence_score=0.85,
                observations="Slight visual turbidity but no critical contaminants or structural issues observed.",
                recommended_actions=["Sediment filtration"]
            )
