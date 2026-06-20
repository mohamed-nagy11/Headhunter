"""Main orchestration script for the HR Headhunter Agent application."""

import logging
import json
import argparse
import sys
import pycountry
import questionary
import config
from services.query_agent import generate_search_query
from services.linkedin_client import search_candidates, fetch_candidate_profile
from services.ranking_engine import rank_candidate
from services.exporter import generate_excel_report

def run_full_pipeline(raw_jd: str, target_country_names: list[str], target_iso_codes: list[str], limit: int = config.DEFAULT_SEARCH_LIMIT) -> None:
    """Executes the complete pipeline: Search -> Enrich -> Rank -> Export."""
    config.setup_logging(log_level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    target_location_str = ", ".join(target_country_names)
    logger.info("=== Starting FULL Sourcing & Ranking Pipeline ===")
    logger.info(f"Target Role: {raw_jd[:50]}...")
    logger.info(f"Target Locations: {target_location_str}")
    
    parsed_query = generate_search_query(raw_jd, target_location_str)
    if not parsed_query: return
    all_discovered_handles = []
    
    for iso_code in target_iso_codes:
        logger.info(f"Searching candidates in {iso_code.upper()}...")
        handles = search_candidates(
            parsed_query["target_title"],
            iso_code, 
            parsed_query["mandatory_skills"],
            limit
        )
        if handles:
            all_discovered_handles.extend(handles)
            
    discovered_handles = list(set(all_discovered_handles))
    
    if not discovered_handles: return
        
    shortlist_reports = []
    
    for handle in discovered_handles:
        logger.info(f"Processing candidate: {handle}...")
        
        profile_data = fetch_candidate_profile(handle)
        if not profile_data: continue
            
        ranking = rank_candidate(profile_data, raw_jd)
        if not ranking: continue
            
        first_name = profile_data.get("firstName") or profile_data.get("first_name") or profile_data.get("name", "").split(" ")[0] or ""
        last_name = profile_data.get("lastName") or profile_data.get("last_name") or ""
        
        # Get the raw location fields
        raw_full = profile_data.get("geo_full") or profile_data.get("geo_country") or "Location not specified"
        raw_city = profile_data.get("geo_city") or ""
        raw_country = profile_data.get("geo_country") or ""
        
        city = raw_city
        country = raw_country

        # If country is empty, try to infer it from the full location
        if not country and raw_full != "Location not specified":
            parts = [p.strip() for p in raw_full.split(",")]
            country = parts[-1] # The country is almost always the last item
            
            # If there are no commas, the user likely only provided a country
            if len(parts) == 1:
                city = "N/A"
                
        # Final cleanup: If city somehow exactly matches country, wipe the city
        if city.lower() == country.lower():
            city = "N/A"
            
        # Ensure fallback strings
        city = city or "N/A"
        country = country or "N/A"
        
        positions = profile_data.get("full_positions") or []
        current_title = "N/A"
        current_employer = "N/A"
        
        if positions and isinstance(positions, list) and len(positions) > 0:
            latest_job = positions[0]
            current_title = latest_job.get("title") or latest_job.get("job_title") or "N/A"
            current_employer = latest_job.get("organization_name") or latest_job.get("company_name") or "N/A"
            
        candidate_report = {
            "Name": f"{first_name} {last_name}".strip() or handle,
            "Full Location": raw_full,
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
    
    # Clean the strings to make them safe for Windows/Mac filenames
    safe_title = parsed_query["target_title"].replace(" ", "_").replace("/", "-")
    safe_location = "_".join(target_country_names).replace(" ", "_").replace(",", "")
    
    # Construct a dynamic, unique filename
    excel_path = f"data/Shortlist_{safe_title}_{safe_location}.xlsx"
    
    # Export the final data using the dynamic path
    generate_excel_report(shortlist_reports, filename=excel_path)
    
    return shortlist_reports, excel_path

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
        "-n", "--limit", 
        type=int, 
        default=config.DEFAULT_SEARCH_LIMIT, 
        help="The maximum number of profiles to search per country."
    )
    
    # Parse the arguments provided by the user in the terminal
    args = parser.parse_args()
    
    # Generate mapping from pycountry (sorted alphabetically)
    country_map = {country.name: country.alpha_2.lower() for country in sorted(pycountry.countries, key=lambda x: x.name)}
    
    print("\n")
    # Interactively ask for target countries
    selected_country_names = questionary.checkbox(
        "Search and select target countries (Type to search, Space to select, Enter to confirm):",
        choices=list(country_map.keys())
    ).ask()
    
    if not selected_country_names:
        print("No countries selected. Exiting.")
        sys.exit(0)
        
    iso_codes = [country_map[name] for name in selected_country_names]
    
    # Run the pipeline with the user's inputs
    run_full_pipeline(
        raw_jd=args.jd, 
        target_country_names=selected_country_names, 
        target_iso_codes=iso_codes,
        limit=args.limit
    )

    # Example usage:
    # python main.py -j "Looking for a Python Developer who knows FastAPI and Docker."