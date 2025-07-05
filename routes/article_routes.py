# routes/article_routes.py
"""Flask routes for article fetching (/fetch_articles/<job_title>).

This blueprint provides the API endpoint for fetching news articles from the
NewsAPI service based on a given job title.
"""

import logging
from typing import Tuple

from flask import Blueprint, Response, jsonify

from services.news_service import fetch_articles_for_job_title

logger = logging.getLogger(__name__)

article_bp = Blueprint('article_routes', __name__)


@article_bp.route('/fetch_articles/<string:job_title>', methods=['GET'])
def fetch_articles(job_title: str) -> Tuple[Response, int]:
    """Fetches news articles related to a specific job title.

    This endpoint uses the NewsAPI service to find relevant articles. The job
    title is passed as a URL parameter. It handles validation of the job title
    and translates service layer responses into appropriate HTTP responses.

    Args:
        job_title: The job title to search for articles about. This is
                   provided via the URL path.

    Returns:
        A tuple containing a JSON response and an HTTP status code.
        - 200 OK: On success, returns a JSON object with an 'articles' key
          containing a list of article data. The list may be empty if no
          articles are found.
        - 400 Bad Request: If the provided job_title is empty or consists
          only of whitespace.
        - 500 Internal Server Error: If there's a configuration issue (like a
          missing API key) or an unexpected error during the fetch process.
    """
    clean_title = job_title.strip()
    if not clean_title:
        logger.warning("Fetch articles request received with an empty job title.")
        return jsonify({"error": "Job title cannot be empty."}), 400

    logger.info(f"Request received to fetch articles for job title: '{clean_title}'")

    try:
        articles, error_message = fetch_articles_for_job_title(clean_title)

        if error_message:
            # The service layer encountered an error.
            logger.error(
                f"Service error while fetching articles for '{clean_title}': {error_message}"
            )
            # The service layer provides a user-friendly error message.
            # We return a 500 status code as this indicates a server-side
            # or dependency failure, not a client error.
            return jsonify({"error": error_message}), 500

        # Success case: articles is a list (can be empty).
        logger.info(f"Successfully fetched {len(articles)} articles for '{clean_title}'.")
        return jsonify({"articles": articles}), 200

    except Exception as e:
        # This is a fallback for any unexpected errors not caught by the service layer.
        logger.critical(
            f"An unexpected exception occurred in fetch_articles route for '{clean_title}': {e}",
            exc_info=True
        )
        return jsonify({"error": "An unexpected internal server error occurred."}), 500