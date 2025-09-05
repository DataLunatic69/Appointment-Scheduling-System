import logging
import os
from datetime import datetime

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger('healthcare_scheduler')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s')
    
    # File handler with UTF-8 encoding
    log_file = os.path.join(log_dir, f"healthcare_scheduler_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create a global logger instance
logger = setup_logging()

def log_agent_operation(operation: str, details: dict) -> None:
    """Log agent operations in a structured format."""
    logger.info(f"Operation: {operation} | Details: {details}")

def log_tool_execution(tool_name: str, parameters: dict, result: str) -> None:
    """Log tool execution details."""
    logger.info(f"Tool: {tool_name} | Parameters: {parameters} | Result: {result}")

def log_error(message: str, exc_info: bool = True) -> None:
    """Log an error message."""
    logger.error(message, exc_info=exc_info)

def log_info(message: str) -> None:
    """Log an info message."""
    logger.info(message)

def log_warning(message: str) -> None:
    """Log a warning message."""
    logger.warning(message)

def log_debug(message: str) -> None:
    """Log a debug message."""
    logger.debug(message)