"""Main orchestration script for the HR Headhunter Agent application."""

import logging
import config
from services.query_agent import generate_search_query
from services.linkedin_client import search_candidates, fetch_candidate_profile

def test_sourcing_pipeline() -> None:
    """Validates Component 1 and Component 2 execution end-to-end."""
    config.setup_logging(log_level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting E2E Sourcing Pipeline Test ===")
    
    # 1. Generate search parameters from raw JD
    raw_jd = "Looking for a Python Developer who knows FastAPI and Docker."
    parsed_query = generate_search_query(raw_jd, "Egypt")
    
    if not parsed_query:
        logger.error("Pipeline aborted: Query generation failed.")
        return
        
    # 2. Search for handles using the parsed query parameters
    discovered_handles = search_candidates(
        target_title=parsed_query["target_title"],
        location=parsed_query["location"],
        mandatory_skills=parsed_query["mandatory_skills"],
        limit=3  # Keep it small for an isolated test
    )
    
    if not discovered_handles:
        logger.warning("Pipeline paused: No handles found for these criteria.")
        return
        
    # 3. Fetch the full profile details for the first discovered candidate
    test_handle = discovered_handles[0]
    logger.info(f"Testing profile enrichment layer using top handle: [{test_handle}]")
    
    profile_data = fetch_candidate_profile(test_handle)
    
    if profile_data:
        logger.info("=== Pipeline Component 1 & 2 Verified Successfully! ===")
    else:
        logger.error("Pipeline failure: Search succeeded but enrichment failed.")

if __name__ == "__main__":
    test_sourcing_pipeline()