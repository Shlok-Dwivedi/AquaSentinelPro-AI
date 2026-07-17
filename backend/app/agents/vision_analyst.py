import os
import logging
from app.config import settings
from app.models.agent_schemas import VisionAnalysisResult
from app.services.vision_provider import GeminiVisionProvider, MockVisionProvider

logger = logging.getLogger("aquasentinel")

SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]

# Initialize provider based on key presence
is_gemini_active = (
    settings.GEMINI_API_KEY 
    and settings.GEMINI_API_KEY not in ["YOUR_GEMINI_API_KEY_HERE", "placeholder_key", ""]
)

# Instantiate the correct provider matching the design rule
vision_provider = GeminiVisionProvider() if is_gemini_active else MockVisionProvider()
logger.info(f"Vision Agent configured with provider: {vision_provider.__class__.__name__}")

def run_vision_analyst(image_path: str) -> VisionAnalysisResult:
    """Validates the image file format and invokes the configured VisionProvider to analyze the water image."""
    if not image_path:
        raise ValueError("Image path is required for Vision Analysis.")
        
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
        
    # Validate extension
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {file_ext}. Supported formats: {SUPPORTED_FORMATS}")

    # Determine MIME type
    mime_type = "image/jpeg"
    if file_ext == ".png":
        mime_type = "image/png"
    elif file_ext == ".webp":
        mime_type = "image/webp"

    logger.info(f"Executing Vision Agent on image '{image_path}' using provider '{vision_provider.__class__.__name__}'")

    prompt = """Analyze this image in detail regarding water quality, sanitation, and physical infrastructure.
Identify any visible contaminants (such as algae, plastic waste, oil slick, foam, sludge, sediment, murky water) 
or structural issues (like damaged pipes, open storage tanks, rusted fittings).

Provide a visual description of the water appearance, estimate the turbidity level (Clear, Slight, Moderate, Severe), 
estimate the water color (Clear, Brown, Green, Milky), rate the contamination level (None, Low, Medium, High), 
assign your confidence score (0.0 to 1.0), note observations, and list recommended maintenance actions.

Return a strict JSON output matching the VisionAnalysisResult schema.
"""

    try:
        # Call the abstract provider
        result = vision_provider.analyze_image(image_path, mime_type, prompt)
        return result
    except ValueError as ve:
        # If it was flagged as unsupported (e.g. mock unsupported case)
        logger.error(f"Vision Agent validation error: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"Vision provider failed: {e}. Falling back to default mock results.")
        # Trigger offline fallback manually
        mock = MockVisionProvider()
        return mock.analyze_image(image_path, mime_type, prompt)
