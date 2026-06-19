"""Main orchestration script for the HR Headhunter Agent application."""

import logging
import json
import argparse
import config
from services.query_agent import generate_search_query
from services.linkedin_client import search_candidates, fetch_candidate_profile
from services.ranking_engine import rank_candidate
from services.exporter import generate_excel_report

def run_full_pipeline(raw_jd: str, target_location: str) -> None:
    """Executes the complete pipeline: Search -> Enrich -> Rank -> Export."""
    config.setup_logging(log_level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting FULL Sourcing & Ranking Pipeline ===")
    logger.info(f"Target Role: {raw_jd[:50]}...")
    logger.info(f"Target Location: {target_location}")
    
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

        candidate_location = profile_data.get("geo_full") or profile_data.get("geo_country") or "Location not specified"
            
        ranking = rank_candidate(profile_data, raw_jd)
        if not ranking: continue
            
        first_name = profile_data.get("firstName") or profile_data.get("first_name") or profile_data.get("name", "").split(" ")[0] or ""
        last_name = profile_data.get("lastName") or profile_data.get("last_name") or ""
        
        city = profile_data.get("geo_city") or "N/A"
        country = profile_data.get("geo_country") or "N/A"
        
        positions = profile_data.get("full_positions") or []
        current_title = "N/A"
        current_employer = "N/A"
        
        if positions and isinstance(positions, list) and len(positions) > 0:
            latest_job = positions[0]
            current_title = latest_job.get("title") or latest_job.get("job_title") or "N/A"
            current_employer = latest_job.get("organization_name") or latest_job.get("company_name") or "N/A"
            
        candidate_report = {
            "Name": f"{first_name} {last_name}".strip() or handle,
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
    
    # Export the final data
    generate_excel_report(shortlist_reports)

if __name__ == "__main__":
    # Set up the CLI argument parser
    parser = argparse.ArgumentParser(
        description="HR Headhunter Agent: AI-powered candidate sourcing and ranking pipeline.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "-j", "--jd", 
        type=str, 
        required=True, 
        help="The raw Job Description or primary requirements."
    )
    
    parser.add_argument(
        "-l", "--location", 
        type=str, 
        required=True, 
        help="The target geographical location (e.g., 'Egypt', 'San Francisco')."
    )
    
    # Parse the arguments provided by the user in the terminal
    args = parser.parse_args()
    
    # Run the pipeline with the user's inputs
    run_full_pipeline(raw_jd=args.jd, target_location=args.location)

    # Example usage:
    # python main.py -j "Looking for a Python Developer who knows FastAPI and Docker." -l "Egypt"
    # python main.py --jd "Senior React Frontend Engineer with 5+ years of experience in Redux and Tailwind CSS." --location "UAE"