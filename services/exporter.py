"""Excel Exporter Service for the HR Headhunter application.

This module converts a list of candidate dictionaries into a formatted Excel report.
"""

import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def generate_excel_report(candidates: list[dict], filename: str = "data/Headhunter_Shortlist.xlsx") -> bool:
    """Exports candidate data to an Excel file inside a specified directory.

    Args:
        candidates (list[dict]): The array of enriched candidate profiles.
        filename (str): The desired output file path. Defaults to the data/ directory.

    Returns:
        bool: True if export was successful, False otherwise.
    """
    if not candidates:
        logger.warning("No candidates provided for export. Skipping Excel generation.")
        return False

    try:
        logger.info(f"Generating Excel report for {len(candidates)} candidates...")
        
        # 1. Safely extract the directory path and create it if it doesn't exist
        output_dir = os.path.dirname(filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"Ensured target directory exists: {output_dir}")
            
        # 2. Load the dictionary list into a pandas DataFrame
        df = pd.DataFrame(candidates)
        
        # 3. Export to Excel without the integer index column
        df.to_excel(filename, index=False)
        
        logger.info(f"Successfully saved candidate report to '{filename}'")
        return True
        
    except ImportError:
        logger.error("Pandas or openpyxl is not installed. Run: pip install pandas openpyxl")
        return False
    except Exception as e:
        logger.error(f"Failed to generate Excel report: {str(e)}")
        return False