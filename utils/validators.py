# utils/validators.py
"""Input validation functions for job titles and request data.

This module provides helper functions to validate and sanitize input data,
such as job titles from API requests. These functions are used by the route
handlers to ensure data integrity before it is processed or stored.
"""

import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

MAX_TITLE_LENGTH = 100


def validate_job_title(title: Any) -> Optional[str]:
    """Validates and sanitizes a job title.

    Checks if the input is a string, is not empty after stripping whitespace,
    and does not exceed a maximum length.

    Args:
        title: The input value to validate as a job title.

    Returns:
        The sanitized (stripped) job title string if it is valid,
        otherwise None.
    """
    if not isinstance(title, str):
        logger.debug(f"Validation failed: title is not a string (type: {type(title)}).")
        return None

    cleaned_title = title.strip()

    if not (0 < len(cleaned_title) <= MAX_TITLE_LENGTH):
        logger.debug(
            f"Validation failed: title length is invalid. "
            f"Length: {len(cleaned_title)}, Max: {MAX_TITLE_LENGTH}."
        )
        return None

    logger.debug(f"Successfully validated job title: '{cleaned_title}'")
    return cleaned_title


def validate_job_title_payload(
    payload: Optional[Dict[str, Any]]
) -> Tuple[Optional[str], Optional[str]]:
    """Validates a request payload expecting a 'title' key.

    This function checks if the payload is a dictionary and contains a valid
    job title under the 'title' key. It uses the `validate_job_title`
    function for the title's specific validation logic.

    Args:
        payload: The request payload, typically from `request.get_json()`.

    Returns:
        A tuple containing two elements:
        - The cleaned job title string if validation is successful, otherwise None.
        - An error message string if validation fails, otherwise None.
    """
    if not isinstance(payload, dict):
        # This case handles when request.is_json is false, as get_json() would return None.
        return None, "Request payload must be a valid JSON object."

    title_from_payload = payload.get("title")

    cleaned_title = validate_job_title(title_from_payload)

    if cleaned_title is None:
        error_msg = (
            f"Payload must include a 'title' key with a non-empty string value "
            f"up to {MAX_TITLE_LENGTH} characters."
        )
        return None, error_msg

    return cleaned_title, None