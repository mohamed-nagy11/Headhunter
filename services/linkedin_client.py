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