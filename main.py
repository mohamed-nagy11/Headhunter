"""Main orchestration script for the HR Headhunter Agent application."""

import logging
import json
import config
from services.query_agent import generate_search_query
from services.linkedin_client import search_candidates, fetch_candidate_profile
from services.ranking_engine import rank_candidate

def run_full_pipeline() -> None:
    config.setup_logging(log_level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting FULL Sourcing & Ranking Pipeline ===")
    
    raw_jd = "Looking for a Python Developer who knows FastAPI and Docker."
    target_location = "Egypt"
    
    parsed_query = generate_search_query(raw_jd, target_location)
    if not parsed_query: return
        
    discovered_handles = search_candidates(
        target_title=parsed_query["target_title"],
        location=parsed_query["location"], 
        mandatory_skills=parsed_query["mandatory_skills"],
        limit=config.DEFAULT_SEARCH_LIMIT
    )
    
    if not discovered_handles: return
        
    shortlist_reports = []
    
    for handle in discovered_handles:
        logger.info(f"Processing candidate: {handle}...")
        
        profile_data = fetch_candidate_profile(handle)
        if not profile_data: continue

        # Safely extract location without filtering them out
        full_location = profile_data.get("geo_full") or profile_data.get("geo_country") or "Location not specified"
        city = profile_data.get("geo_city") or "N/A"
        country = profile_data.get("geo_country") or "N/A"
            
        ranking = rank_candidate(profile_data, raw_jd)
        if not ranking: continue
            
        first_name = profile_data.get("firstName") or profile_data.get("first_name") or profile_data.get("name", "").split(" ")[0] or ""
        last_name = profile_data.get("lastName") or profile_data.get("last_name") or ""
        
        positions = profile_data.get("full_positions") or []
        current_title = "N/A"
        current_employer = "N/A"
        
        if positions and isinstance(positions, list) and len(positions) > 0:
            latest_job = positions[0]
            current_title = latest_job.get("title") or latest_job.get("job_title") or "N/A"
            current_employer = latest_job.get("organization_name") or latest_job.get("company_name") or "N/A"

        candidate_report = {
            "Name": f"{first_name} {last_name}".strip() or handle,
            "Location": full_location,
            "City": city,
            "Country": country,
            "Current Position": current_title,
            "Current Employer": current_employer,
            "AI Score (0-100)": ranking.get("score"),
            "AI Justification": ranking.get("justification"),
            "Profile URL": f"https://linkedin.com/in/{handle}"
        }
        
        shortlist_reports.append(candidate_report)

    print("\n--- FINAL CANDIDATE SHORTLIST ---")
    print(json.dumps(shortlist_reports, indent=2))

if __name__ == "__main__":
    run_full_pipeline()