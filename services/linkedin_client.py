"""LinkedIn client service utilizing the Renidly v2 Engine.

This module communicates with the Renidly API to discover and enrich candidate
profiles, adhering strictly to upstream cache optimization and error-handling specs.
"""

import logging
import requests
from config import RENIDLY_BASE_URL, RENIDLY_API_KEY

logger = logging.getLogger(__name__)

def fetch_candidate_profile(handle: str) -> dict:
    """Fetches an enriched professional profile from Renidly v2.

    Applies input normalization to maximize transparent cache hits and strictly
    validates the signature success wrapper.

    Args:
        handle (str): The public URL identifier slug for the target person.

    Returns:
        dict: Clean profile entity data if successful, otherwise None.
    """
    # Input Normalization (Lowercase and strip whitespace for cache optimization)
    normalized_handle = str(handle).strip().lower()
    
    url = f"{RENIDLY_BASE_URL}/person/enrich"
    headers = {
        "X-renidly-apikey": RENIDLY_API_KEY,
        "Accept": "application/json"
    }
    params = {"handle": normalized_handle}

    try:
        # Enforce strict 15-second timeout constraint
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        body = response.json()

        # Explicitly branch on body.success envelope flag
        if not body.get("success"):
            logger.error(
                f"Renidly Request Failed | Status: {body.get('statusCode')} "
                f"| Message: {body.get('message')} | Errors: {body.get('errors')}"
            )
            return None

        # Return only the inner data payload as requested by the architecture
        candidate_data = body.get("data", {})
        logger.info(f"Successfully enriched profile for handle: [{normalized_handle}]")
        return candidate_data

    except requests.exceptions.Timeout:
        logger.error(f"Renidly request timed out for handle [{normalized_handle}] after 15 seconds.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Transport layer error encountered for handle [{normalized_handle}]: {str(e)}")
        return None

def search_candidates(target_title: str, location: str, mandatory_skills: str, limit: int = 15) -> list[str]:
    """Searches the Renidly v2 database for matching candidate handles.

    Args:
        target_title (str): The normalized job title to filter profiles.
        location (str): The geographic region or city requirement.
        mandatory_skills (str): A boolean string containing required skills.
        limit (int, optional): Maximum number of records to return. Defaults to 15.

    Returns:
        list[str]: A list of profile handles (slugs) matching the criteria.
                   Returns an empty list if the search fails or finds no results.
    """
    logger.info(f"Initiating candidate search | Title: '{target_title}' | Location: '{location}'")
    
    url = f"{RENIDLY_BASE_URL}/person/search"
    headers = {
        "X-renidly-apikey": RENIDLY_API_KEY,
        "Accept": "application/json"
    }
    
    # Payload structured per Renidly v2 filter specifications
    payload = {
        "title": target_title.strip(),
        "location": location.strip(),
        "keywords": mandatory_skills.strip(),
        "limit": limit
    }

    try:
        # Enforce the strict 15-second timeout constraint
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        body = response.json()

        # Enforce envelope validation pattern
        if not body.get("success"):
            logger.error(
                f"Renidly Search Failed | Status: {body.get('statusCode')} "
                f"| Message: {body.get('message')}"
            )
            return []

        # Extract items from the data payload
        data_payload = body.get("data", {})
        results = data_payload.get("results", [])
        
        # Safely parse out the 'handle' field for each candidate found
        handles = [item.get("handle") for item in results if item.get("handle")]
        
        logger.info(f"Search complete. Discovered {len(handles)} candidate handles.")
        logger.debug(f"Discovered handles: {handles}")
        
        return handles

    except requests.exceptions.Timeout:
        logger.error("Renidly search operation timed out after 15 seconds.")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Transport layer error encountered during candidate search: {str(e)}")
        return []