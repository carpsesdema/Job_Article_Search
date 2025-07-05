# config.py
"""Handles configuration settings including API keys and database paths.

This module loads configuration settings from environment variables. It is designed
to be loaded by the Flask application factory in `main.py`. It defines key
configuration variables required for the application to run, such as the
NewsAPI key and the path to the SQLite database.

It uses the `python-dotenv` library to load a `.env` file from the project root,
allowing for secure and flexible configuration management.
"""

import logging
import os
from dotenv import load_dotenv

# Set up basic logging
logger = logging.getLogger(__name__)

# Load environment variables from a .env file if it exists.
# This is useful for development environments.
# In production, environment variables should be set directly.
if load_dotenv():
    logger.info("Loaded environment variables from .env file.")
else:
    logger.info(".env file not found, relying on system environment variables.")

# --- Application Configuration ---

# Secret key for Flask session management and other security features.
# It's crucial to set this to a long, random string in a production environment.
# For development, a default is provided, but a warning is issued.
SECRET_KEY = os.getenv('SECRET_KEY', 'a-very-insecure-default-key-for-dev')
if SECRET_KEY == 'a-very-insecure-default-key-for-dev':
    logger.warning(
        "SECURITY WARNING: Using a default, insecure SECRET_KEY. "
        "Please set a strong, unique key in your environment for production."
    )

# API Key for NewsAPI.org
# This is required to fetch news articles. The application will not be able
# to fetch articles without this key.
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if not NEWS_API_KEY:
    logger.error(
        "CONFIGURATION ERROR: NEWS_API_KEY is not set in the environment. "
        "The application will not be able to fetch articles."
    )

# Path to the SQLite database file.
# The database will be created in the project's root directory.
# Using an absolute path ensures it works regardless of the current working directory.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'app.db')

logger.info(f"Database path configured at: {DATABASE_PATH}")