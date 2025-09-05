"""
Centralized logging configuration for the Healthcare Scheduling System.
Provides structured logging with different levels and formatters for easy debugging.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import traceback

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread_id': getattr(record, 'thread_id', None),
            'agent_name': getattr(record, 'agent_name', None),
            'operation': getattr(record, 'operation', None),
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, indent=2)

def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_structured: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        enable_structured: Whether to enable structured JSON logging
        max_file_size: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
    """
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Console handler with colors
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / "scheduling_system.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Structured JSON logging
    if enable_structured:
        json_handler = logging.handlers.RotatingFileHandler(
            log_path / "scheduling_system_structured.json",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        json_handler.setLevel(level)
        json_formatter = StructuredFormatter()
        json_handler.setFormatter(json_formatter)
        root_logger.addHandler(json_handler)
    
    # Error-specific handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "errors.log",
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s\n%(pathname)s:%(lineno)d\n%(exc_info)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

def get_logger(name: str, agent_name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with optional agent context.
    
    Args:
        name: Logger name (usually __name__)
        agent_name: Name of the agent for context
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add agent context to all log records
    if agent_name:
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.agent_name = agent_name
            return record
        
        logging.setLogRecordFactory(record_factory)
    
    return logger

def log_agent_operation(logger: logging.Logger, operation: str, details: dict = None, level: str = "INFO") -> None:
    """
    Log an agent operation with structured details.
    
    Args:
        logger: Logger instance
        operation: Name of the operation being performed
        details: Additional details about the operation
        level: Log level
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Add operation context
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.operation = operation
        if details:
            record.operation_details = json.dumps(details)
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    message = f"Operation: {operation}"
    if details:
        message += f" | Details: {json.dumps(details, indent=2)}"
    
    logger.log(log_level, message)
    
    # Restore original factory
    logging.setLogRecordFactory(old_factory)

def log_tool_execution(logger: logging.Logger, tool_name: str, parameters: dict = None, result: str = None, success: bool = True) -> None:
    """
    Log tool execution with parameters and results.
    
    Args:
        logger: Logger instance
        tool_name: Name of the tool being executed
        parameters: Tool parameters
        result: Tool result
        success: Whether the tool execution was successful
    """
    level = "INFO" if success else "ERROR"
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    message = f"Tool Execution: {tool_name}"
    if parameters:
        message += f" | Parameters: {json.dumps(parameters, indent=2)}"
    if result:
        message += f" | Result: {result[:200]}{'...' if len(result) > 200 else ''}"
    
    logger.log(log_level, message)

def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None) -> None:
    """
    Log an error with additional context information.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    context_info = ""
    if context:
        context_info = f" | Context: {json.dumps(context, indent=2)}"
    
    logger.error(f"Error occurred: {str(error)}{context_info}", exc_info=True)

# Initialize logging on import
if not logging.getLogger().handlers:
    setup_logging()
