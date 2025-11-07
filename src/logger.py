# src/logger.py
import logging
import os
from pathlib import Path


def setup_logging(module_name=__name__):
    """
    Configure and return a logger instance with both file and console handlers.
    
    Args:
        module_name (str): Name of the module requesting the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Get project root directory (parent of src)
    project_root = Path(__file__).parent.parent
    log_file_path = project_root / "bot.log"
    
    # Create file handler for DEBUG level (writes everything to file)
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler for INFO level (shows only important messages)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter with timestamp, level, module, and message
    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Apply formatter to both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
