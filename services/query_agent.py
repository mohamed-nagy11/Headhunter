"""Query Agent Service for the HR Headhunter application.

This module leverages the Groq LLM to parse unstructured job descriptions 
and output structured, deterministic search parameters using Pydantic.
"""

import logging
from pydantic import BaseModel, Field
from groq import Groq
from config import GROQ_API_KEY, GROQ_LLM_MODEL

# Obtain the logger initialized by our configuration
logger = logging.getLogger(__name__)

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

class SearchParameters(BaseModel):
    """Pydantic model defining the strict JSON output schema for the LLM."""
    target_title: str = Field(description="The normalized, core job title (e.g., 'Software Engineer').")
    mandatory_skills: str = Field(description="A boolean search string of absolutely required skills (e.g., '\"Python\" AND \"AWS\"').")
    preferred_skills: str = Field(description="A boolean search string of nice-to-have skills (e.g., '\"Docker\" OR \"Kubernetes\"').")

def generate_search_query(job_description: str, location: str, tools: str = "") -> dict:
    """Parses raw HR inputs into structured boolean search parameters using Groq.

    Args:
        job_description (str): The raw text of the job description.
        location (str): The geographical requirement.
        tools (str, optional): Manually specified tools or skills. Defaults to "".

    Returns:
        dict: A dictionary matching the SearchParameters schema, or None if it fails.
    """
    logger.info("Initializing query generation via Groq LLM...")
    
    # Generate the JSON schema directly from our Pydantic model
    output_schema = SearchParameters.model_json_schema()
    
    # Inject the schema requirement directly into the system prompt
    system_prompt = (
        "You are an expert technical HR sourcer. Your job is to extract search parameters "
        "from job descriptions. Convert skills into boolean strings. Separate strictly "
        "mandatory requirements from preferred bonuses.\n\n"
        f"You MUST return ONLY a valid JSON object that strictly adheres to this schema:\n{output_schema}"
    )
    
    user_prompt = (
        f"Job Description: {job_description}\n"
        f"Target Location: {location}\n"
        f"Additional Tools/Skills: {tools}"
    )

    try:
        # Enforce structured output via standard json_object mode
        response = client.chat.completions.create(
            model=GROQ_LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        raw_result = response.choices[0].message.content
        logger.debug(f"Raw LLM output: {raw_result}")
        
        # Validate the raw JSON string back into our strict Pydantic model
        parsed_result = SearchParameters.model_validate_json(raw_result)
        
        logger.info(f"Successfully generated search query for title: {parsed_result.target_title}")
        
        return parsed_result.model_dump()

    except Exception as e:
        logger.error(f"Failed to generate search query: {str(e)}")
        return None