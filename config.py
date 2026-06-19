"""Configuration module for the HR Headhunter Agent.

This module handles the secure retrieval and management of API keys and 
system-wide constants using environmental variables loaded via python-dotenv.
"""

import os
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