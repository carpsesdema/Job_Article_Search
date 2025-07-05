# services/news_service.py
"""Contains logic for fetching articles from NewsAPI.org and processing responses.

This service module is responsible for all interactions with the external NewsAPI.
It encapsulates the logic for building requests, sending them, handling potential
network or API errors, and formatting the response data into a clean, usable
format for the rest of the application.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import requests
from flask import current_app

logger = logging.getLogger(__name__)

NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"


def _format_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """Formats a raw article dictionary from NewsAPI into a cleaner structure.

    This helper function takes a single article object from the NewsAPI response
    and extracts only the necessary fields. It also handles potentially missing
    keys gracefully by using .get().

    Args:
        article: A dictionary representing a single article from the NewsAPI response.

    Returns:
        A dictionary with a curated set of key-value pairs for the article.
    """
    source_info = article.get("source", {})
    return {
        "title": article.get("title"),
        "author": article.get("author"),
        "source": source_info.get("name") if source_info else None,
        "url": article.get("url"),
        "image_url": article.get("urlToImage"),
        "published_at": article.get("publishedAt"),
        "description": article.get("description"),
    }


def fetch_articles_for_job_title(
    job_title: str,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """Fetches and processes news articles for a given job title from NewsAPI.

    This function constructs and sends a request to NewsAPI.org's 'everything'
    endpoint. It handles API key retrieval from the Flask app config, network
    exceptions, and API-level errors returned by NewsAPI.

    Args:
        job_title: The job title to search for. The query will be constructed
                   to find articles related to this title.

    Returns:
        A tuple containing two elements:
        - A list of formatted article dictionaries on success, or None on failure.
          An empty list is returned if the query is valid but yields no results.
        - An error message string on failure, or None on success.
    """
    api_key = current_app.config.get("NEWS_API_KEY")
    if not api_key:
        logger.critical("NEWS_API_KEY is not configured in the application.")
        return None, "Server configuration error: News API key is missing."

    # Using quotes around the job title for a more precise phrase search
    query = f'"{job_title}"'

    params = {
        "q": query,
        "apiKey": api_key,
        "pageSize": 20,  # Limit the number of results for performance
        "language": "en",
        "sortBy": "relevancy",  # Sort by relevance to the query
    }

    try:
        # Set a timeout to prevent requests from hanging indefinitely
        response = requests.get(NEWS_API_BASE_URL, params=params, timeout=10)
        # Raise an HTTPError for bad responses (4xx client error or 5xx server error)
        response.raise_for_status()

        data = response.json()

        # NewsAPI can return a 200 OK but still indicate an error in the body
        if data.get("status") == "error":
            error_code = data.get("code", "UnknownCode")
            error_message = data.get("message", "No message provided.")
            logger.error(
                f"NewsAPI returned an error. Code: {error_code}, Message: {error_message}"
            )
            return None, f"An error occurred with the news service: {error_message}"

        raw_articles = data.get("articles", [])
        if not raw_articles:
            logger.info(f"No articles found for job title: '{job_title}'")
            return [], None  # Return empty list, which is a valid success state

        formatted_articles = [_format_article(article) for article in raw_articles]
        logger.info(
            f"Successfully fetched {len(formatted_articles)} articles for '{job_title}'."
        )
        return formatted_articles, None

    except requests.exceptions.Timeout:
        logger.error(f"Request to NewsAPI timed out for job title: '{job_title}'.")
        return None, "The request to the news service timed out."
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP error occurred when fetching articles for '{job_title}': {e}"
        )
        return None, "A network error occurred while fetching news."
    except requests.exceptions.RequestException as e:
        logger.error(f"An unexpected network error occurred for '{job_title}': {e}")
        return None, "Failed to connect to the news service."
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(
            f"An unexpected error occurred in fetch_articles_for_job_title: {e}",
            exc_info=True,
        )
        return None, "An unexpected server error occurred."