"""LinkedIn client service using the Renidly API.

This module is responsible for fetching enriched candidate profiles
and safely unwrapping the response envelope, logging all network activity.
"""

import logging
import requests
from config import RENIDLY_BASE_URL, RENIDLY_API_KEY

# Obtain the logger initialized by the configuration
logger = logging.getLogger(__name__)

def fetch_candidate_profile(handle: str) -> dict:
    """
    Fetches an enriched professional profile from Renidly.

    Args:
        handle (str): The public URL slug for the person (e.g., 'jane-doe').

    Returns:
        dict: The enriched data dictionary containing geo, currentPositions, etc., 
              or None if the request fails.
    """
    logger.debug(f"Initiating profile fetch for handle: {handle}")
    
    url = f"{RENIDLY_BASE_URL}/person/enrich"
    headers = {"X-renidly-apikey": RENIDLY_API_KEY}
    params = {"handle": handle}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() 
        body = response.json()

        # Safely handle Renidly's envelope pattern
        if not body.get("success"):
            logger.error(f"Renidly Error [{body.get('statusCode')}]: {body.get('message')}")
            return None

        # Extract the inner data object
        data = body.get("data", {})
        
        # Log successful extraction using safe `.get()` to prevent KeyError
        first_name = data.get('firstName', 'Unknown')
        headline = data.get('headline', 'No headline')
        logger.info(f"Successfully fetched: {first_name} - {headline}")
        
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching profile for {handle}: {str(e)}")
        return None