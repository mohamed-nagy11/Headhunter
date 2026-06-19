"""Ranking Engine Service for the HR Headhunter application.

This module evaluates candidate profiles against job descriptions using 
LLM-based semantic analysis to generate structured ranking scores.
"""

import logging
import json
from pydantic import BaseModel, Field
from groq import Groq
from config import GROQ_API_KEY, GROQ_LLM_MODEL

logger = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)

class CandidateScore(BaseModel):
    """Schema for the LLM scoring output with strict key enforcement."""
    score: int = Field(..., description="A candidate match score from 0 to 100.")
    justification: str = Field(..., description="A concise professional justification for the score.")

def rank_candidate(profile: dict, job_description: str) -> dict:
    """Ranks a candidate profile against a job description.

    Args:
        profile (dict): The enriched profile data from Renidly.
        job_description (str): The original job description text.

    Returns:
        dict: The ranked score and justification, or None if evaluation fails.
    """
    logger.info("Ranking candidate profile via Groq LLM...")
    
    summary = profile.get("summary", "No summary provided.")
    headline = profile.get("headline", "No headline provided.")
    positions = profile.get("currentPositions", [])
    
    prompt = (
        f"You are an expert technical recruiter. Score this candidate (0-100) "
        f"for the following Job Description: '{job_description}'\n\n"
        f"Candidate Headline: {headline}\n"
        f"Candidate Summary: {summary}\n"
        f"Current Positions: {json.dumps(positions)}"
    )

    # Force the LLM to use the specific keys we need via the system prompt
    system_instruction = (
        "You are a professional HR ranker. Output ONLY a valid JSON object. "
        "The object must contain exactly two keys: 'score' (integer 0-100) "
        "and 'justification' (a string explaining the score)."
    )

    try:
        response = client.chat.completions.create(
            model=GROQ_LLM_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        # Parse the response string to JSON
        raw_content = response.choices[0].message.content
        result = json.loads(raw_content)
        
        # Pydantic validation now matches 'score' and 'justification' keys
        validated_score = CandidateScore.model_validate(result)
        
        logger.info(f"Candidate successfully ranked. Score: {validated_score.score}/100")
        return validated_score.model_dump()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from LLM: {e}")
        return None
    except Exception as e:
        logger.error(f"Ranking validation or API error: {e}")
        return None