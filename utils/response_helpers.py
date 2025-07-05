# utils/response_helpers.py
"""Helper functions for formatting API responses and error handling.

This module provides standardized functions for creating JSON responses in the
Flask application. Using these helpers ensures that all API endpoints return
data and errors in a consistent format, simplifying frontend development and
API consumption.
"""

import logging
from typing import Any, Dict, Tuple

from flask import Response, jsonify

# Set up basic logging
logger = logging.getLogger(__name__)


def api_success(data: Dict[str, Any], status_code: int = 200) -> Tuple[Response, int]:
    """Creates a standardized successful JSON response.

    This function takes a data payload and wraps it in a Flask Response object
    with the appropriate JSON content type and status code.

    Args:
        data: A dictionary containing the data to be sent in the response.
              Example: `{'articles': [...]}` or `{'message': 'Success'}`.
        status_code: The HTTP status code for the response. Defaults to 200 (OK).

    Returns:
        A tuple containing the Flask Response object and the HTTP status code.
    """
    return jsonify(data), status_code


def api_error(message: str, status_code: int = 400) -> Tuple[Response, int]:
    """Creates a standardized error JSON response.

    This function takes an error message and creates a JSON response with a
    standard error format. It also logs the error message for debugging purposes.

    Args:
        message: The error message string to be sent to the client.
        status_code: The HTTP status code for the error. Defaults to 400
                     (Bad Request). Common codes include 404 (Not Found),
                     409 (Conflict), and 500 (Internal Server Error).

    Returns:
        A tuple containing the Flask Response object and the HTTP status code.
    """
    # Log the error for server-side visibility.
    # We use logger.error for server-side failures (5xx) and logger.warning
    # for client-side errors (4xx).
    if status_code >= 500:
        logger.error(f"API Error Response ({status_code}): {message}")
    else:
        logger.warning(f"API Error Response ({status_code}): {message}")

    error_payload = {"error": message}
    return jsonify(error_payload), status_code