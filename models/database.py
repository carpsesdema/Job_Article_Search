# models/database.py
"""Handles database initialization and connection management.

This module provides functions to manage the application's SQLite database
connection. It follows the Flask pattern of managing a single connection per
application context (request), making it available via the `g` object.

Functions:
    get_db: Returns the current database connection, creating one if it doesn't exist.
    close_db: Closes the current database connection.
    init_db: Initializes the database by creating necessary tables.
"""

import logging
import sqlite3
from typing import Optional

from flask import current_app, g

# This import is safe as it's part of the same package and does not create a
# circular dependency with the functions used by job_title.py.
from .job_title import create_job_titles_table

logger = logging.getLogger(__name__)


def get_db() -> sqlite3.Connection:
    """Gets the database connection for the current application context.

    If a connection is not already present in Flask's `g` object, a new
    connection to the SQLite database specified in the app configuration
    is established. The connection is then stored in `g` for reuse during
    the same context.

    Using `sqlite3.Row` as the `row_factory` allows accessing query results
    like dictionaries (e.g., `row['column_name']`).

    Returns:
        An active sqlite3.Connection object.

    Raises:
        KeyError: If DATABASE_PATH is not found in the Flask app config.
        sqlite3.Error: If the database connection fails.
    """
    if 'db' not in g:
        try:
            db_path = current_app.config['DATABASE_PATH']
            g.db = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
            logger.debug(f"New database connection created to {db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database at {current_app.config.get('DATABASE_PATH')}: {e}")
            raise
        except KeyError:
            logger.error("DATABASE_PATH not found in Flask app config. Cannot create DB connection.")
            raise
    return g.db


def close_db(e: Optional[Exception] = None) -> None:
    """Closes the database connection at the end of the request.

    This function is intended to be registered with Flask's `teardown_appcontext`
    to ensure that the database connection is automatically closed when the
    application context ends.

    Args:
        e: An optional exception object if the teardown is happening
           due to an unhandled exception. It is unused in this function
           but required by the `teardown_appcontext` signature.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()
        logger.debug("Database connection closed.")


def init_db() -> None:
    """Initializes the database schema.

    This function should be called to set up the database for the first time.
    It gets a database connection and calls the necessary functions to create
    the tables defined in the application's models.
    """
    try:
        db = get_db()
        logger.info("Initializing database schema...")
        create_job_titles_table(db)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
        # Re-raise the exception to be handled by the caller (e.g., in main.py)
        raise