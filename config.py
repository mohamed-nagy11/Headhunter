"""Configuration module for the HR Headhunter Agent.

This module handles the secure retrieval and management of API keys and 
system-wide constants using environmental variables loaded via python-dotenv.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables from a physical .env file if it exists
load_dotenv()

# Securely extract keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RENIDLY_API_KEY = os.getenv("RENIDLY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("CRITICAL ERROR: 'GROQ_API_KEY' is missing from the environment configuration.")

if not RENIDLY_API_KEY:
    raise ValueError("CRITICAL ERROR: 'RENIDLY_API_KEY' is missing from the environment configuration.")

# Renidly Base URL
RENIDLY_BASE_URL = "https://renidly.com/api/v2"

# Model Selection
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"

def setup_logging(log_level: int = logging.INFO) -> None:
    """Configures system-wide logging with both console and rotating file handlers.

    This function sets up a root logging architecture. It streams human-readable
    logs directly to the console and simultaneously records detailed execution
    traces to a rolling log file located in a local 'logs/' directory.

    Args:
        log_level (int): The logging threshold level (e.g., logging.INFO, logging.DEBUG).
            Defaults to logging.INFO.

    Returns:
        None
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any existing handlers to prevent duplicate logging logs during testing
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Stream Handler for terminal output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # Rotating File Handler to prevent logs from running out of disk space
    # Max file size: 5MB, keeps up to 3 backup historical log files
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    logging.info("Logging infrastructure successfully initialized.")