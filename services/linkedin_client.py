"""LinkedIn client service utilizing the Renidly v2 Engine.

This module communicates with the Renidly API to discover and enrich candidate
profiles, adhering strictly to upstream cache optimization and error-handling specs.
"""

import logging
import requests
from config import RENIDLY_BASE_URL, RENIDLY_API_KEY

logger = logging.getLogger(__name__)

def search_candidates(target_title: str, location: str, mandatory_skills: str, limit: int = 15) -> list[str]:
    """Searches the Renidly database with defensive parsing for the result list."""
    url = f"{RENIDLY_BASE_URL}/people/search"
    headers = {"X-renidly-apikey": RENIDLY_API_KEY}
    params = {
        "title": target_title,
        "location": location,
        "keywords": mandatory_skills,
        "limit": limit
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        body = response.json()

        # Defensive Parsing:
        # If 'data' is a list, use it directly. If it's a dict, look for 'results'.
        data = body.get("data", [])
        
        if isinstance(data, dict):
            results = data.get("results", [])
        elif isinstance(data, list):
            results = data
        else:
            results = []

        # Extract handles
        handles = [item.get("handle") for item in results if isinstance(item, dict) and item.get("handle")]
        
        logger.info(f"Search complete. Discovered {len(handles)} candidate handles.")
        return handles
    
    except Exception as e:
        logger.error(f"Search request failed: {e}")
        return []

def fetch_candidate_profile(handle: str) -> dict:
    """Fetches profile using the correct v1/data/people/profile endpoint."""
    url = f"{RENIDLY_BASE_URL}/people/profile"
    headers = {"X-renidly-apikey": RENIDLY_API_KEY}
    params = {"handle": handle} 

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        body = response.json()
        
        return body.get("data") if body.get("success") else None
    except Exception as e:
        logger.error(f"Profile fetch failed: {e}")
        return None