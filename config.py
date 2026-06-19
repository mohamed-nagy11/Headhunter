"""Configuration module for the HR Headhunter Agent.

This module handles the secure retrieval and management of API keys and 
system-wide constants using environmental variables loaded via python-dotenv.
"""

import os
from dotenv import load_workbook, load_dotenv

# Load environment variables from a physical .env file if it exists
load_dotenv()

# Securely extract keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PROXYCURL_API_KEY = os.getenv("PROXYCURL_API_KEY")

# Raise ValueError if critical keys are missing
if not GROQ_API_KEY:
    raise ValueError("CRITICAL ERROR: 'GROQ_API_KEY' is missing from the environment configuration.")

if not PROXYCURL_API_KEY:
    raise ValueError("CRITICAL ERROR: 'PROXYCURL_API_KEY' is missing from the environment configuration.")

# Immutable System-Wide Constants
PROXYCURL_SEARCH_URL = "https://nubela.co/proxycurl/api/v2/search/person"
PROXYCURL_PROFILE_URL = "https://nubela.co/proxycurl/api/v2/person"

# Model Selection
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"