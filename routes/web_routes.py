# routes/web_routes.py
"""Flask routes for serving the main web interface."""

import logging

from flask import Blueprint, Response, render_template

from models.job_title import get_all_job_titles

# Set up basic logging
logger = logging.getLogger(__name__)

# Create a Blueprint for the main web interface routes
web_bp = Blueprint('web_routes', __name__)


@web_bp.route('/', methods=['GET'])
def index() -> Response:
    """Renders the main index page of the application.

    This route fetches the current list of all job titles from the database
    and passes them to the `index.html` template for rendering. This allows
    the user to see the list of tracked jobs upon loading the page.

    Returns:
        A Flask Response object containing the rendered HTML of the main page.
        In case of a database error, it logs the error and renders the page
        with an empty list of job titles to ensure the UI remains functional.
    """
    logger.info("Request received for the main index page.")
    try:
        # Fetch all job titles to populate the list on the frontend.
        # The model function is designed to handle DB errors gracefully by
        # returning an empty list, but we wrap this in a try/except block
        # as a safeguard against unexpected exceptions (e.g., connection failure).
        job_titles = get_all_job_titles()
        logger.info(f"Passing {len(job_titles)} job titles to the index template.")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while fetching job titles for index page: {e}",
            exc_info=True
        )
        # Ensure the page can still render, albeit without the job list.
        job_titles = []

    # The template will receive the list of job titles.
    # Flask's render_template looks in the 'templates' directory configured at the app level.
    return render_template('index.html', job_titles=job_titles)