# routes/job_routes.py
"""Flask routes for job title CRUD operations (/add_job, /get_jobs, /delete_job).

This blueprint handles the API endpoints related to managing the list of job
titles stored in the database. It provides functionality to add, retrieve,
and delete job titles.
"""

import logging
from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from models.job_title import (
    add_job_title,
    delete_job_title,
    get_all_job_titles,
)

logger = logging.getLogger(__name__)

job_bp = Blueprint('job_routes', __name__)


@job_bp.route('/add_job', methods=['POST'])
def add_job() -> Tuple[Response, int]:
    """Adds a new job title to the database.

    Expects a JSON payload with a 'title' key.
    Example: `{'title': 'Software Engineer'}`

    Returns:
        A tuple containing a JSON response and an HTTP status code.
        - 201 Created: If the job title was added successfully.
        - 400 Bad Request: If the request is not JSON, is missing the 'title'
          key, or the title is empty.
        - 409 Conflict: If the job title already exists or a database error occurs.
    """
    if not request.is_json:
        logger.warning("Add job request received without JSON payload.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    title = data.get('title')

    if not title or not isinstance(title, str) or not title.strip():
        logger.warning(f"Add job request with invalid title: {title}")
        return jsonify({"error": "A non-empty 'title' string is required"}), 400

    # Sanitize input by stripping whitespace
    clean_title = title.strip()
    logger.info(f"Attempting to add job title: '{clean_title}'")

    new_id = add_job_title(clean_title)

    if new_id is not None:
        logger.info(f"Successfully added job title '{clean_title}' with ID {new_id}.")
        response_data = {
            "message": "Job title added successfully",
            "job_title": clean_title
        }
        return jsonify(response_data), 201
    else:
        # add_job_title returns None for duplicates or other DB errors.
        # The model logs the specific error, so we return a conflict error.
        logger.warning(f"Failed to add job title '{clean_title}', it may already exist.")
        return jsonify({"error": f"Job title '{clean_title}' already exists or a database error occurred."}), 409


@job_bp.route('/get_jobs', methods=['GET'])
def get_jobs() -> Response:
    """Retrieves all stored job titles, sorted alphabetically.

    Returns:
        A JSON response containing a list of all job titles.
        Example: `{'job_titles': ['Data Scientist', 'Product Manager']}`
        Returns a 500 error if the database cannot be accessed.
    """
    logger.info("Request received to get all job titles.")
    try:
        titles = get_all_job_titles()
        logger.info(f"Successfully retrieved {len(titles)} job titles.")
        return jsonify({"job_titles": titles})
    except Exception as e:
        # This is a fallback. get_all_job_titles is designed to return [] on
        # error, but this catches unexpected issues like a DB connection failure.
        logger.error(f"An unexpected error occurred while getting job titles: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500


@job_bp.route('/delete_job', methods=['DELETE'])
def delete_job() -> Tuple[Response, int]:
    """Deletes a job title from the database.

    Expects a JSON payload with a 'title' key.
    Example: `{'title': 'Software Engineer'}`

    Returns:
        A tuple containing a JSON response and an HTTP status code.
        - 200 OK: If the job title was deleted successfully.
        - 400 Bad Request: If the request is not JSON or is missing the 'title' key.
        - 404 Not Found: If the specified job title does not exist.
    """
    if not request.is_json:
        logger.warning("Delete job request received without JSON payload.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    title = data.get('title')

    if not title or not isinstance(title, str):
        logger.warning(f"Delete job request with invalid title: {title}")
        return jsonify({"error": "A 'title' string is required"}), 400

    logger.info(f"Attempting to delete job title: '{title}'")
    was_deleted = delete_job_title(title)

    if was_deleted:
        logger.info(f"Successfully deleted job title: '{title}'")
        return jsonify({"message": f"Job title '{title}' deleted successfully"}), 200
    else:
        # delete_job_title returns False if the title doesn't exist or on error.
        # The model logs the specific reason. 404 is the most likely client error.
        logger.warning(f"Could not delete job title '{title}', it may not exist.")
        return jsonify({"error": f"Job title '{title}' not found"}), 404