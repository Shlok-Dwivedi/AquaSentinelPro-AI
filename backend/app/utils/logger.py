import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configures structured logs with stdout and rotating file handlers."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger("aquasentinel")
    logger.setLevel(logging.INFO)
    
    # Prevent handler duplication on hot-reloading
    if not logger.handlers:
        # 1. Console Handler (for readable dev prints)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 2. Structured Rotating File Handler (for log collectors)
        file_path = os.path.join(log_dir, "aquasentinel.log")
        file_handler = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=5)
        
        # JSON formatting structure
        json_format = (
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"module": "%(module)s", "message": "%(message)s"}'
        )
        file_formatter = logging.Formatter(json_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    logger.info("Structured logging initialized with rotating log files.")
