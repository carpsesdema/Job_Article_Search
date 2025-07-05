# models/job_title.py
"""Defines the JobTitle model and database schema operations.

This module contains functions for managing job titles in the SQLite database.
It includes:
- A function to create the `job_titles` table.
- CRUD (Create, Read, Delete) operations for job titles.
"""

import logging
import sqlite3
from typing import List, Optional

from .database import get_db

logger = logging.getLogger(__name__)


def create_job_titles_table(conn: sqlite3.Connection) -> None:
    """Creates the job_titles table in the database if it doesn't exist.

    This function is designed to be called once during application initialization
    to set up the necessary database schema. It includes a UNIQUE constraint
    on the title to prevent duplicate entries.

    Args:
        conn: An active sqlite3.Connection object to execute the command on.

    Raises:
        sqlite3.Error: If any SQLite-related error occurs during table creation.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE
            )
        """)
        conn.commit()
        logger.info("Successfully ensured 'job_titles' table exists.")
    except sqlite3.Error as e:
        logger.error(f"Error creating 'job_titles' table: {e}")
        raise


def add_job_title(title: str) -> Optional[int]:
    """Adds a new, unique job title to the database.

    Args:
        title: The job title string to add. The string is case-sensitive.

    Returns:
        The integer ID of the newly inserted job title if successful.
        Returns None if the title already exists (violating the UNIQUE
        constraint) or if a database error occurs.
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO job_titles (title) VALUES (?)", (title,))
        conn.commit()
        new_id = cursor.lastrowid
        logger.info(f"Added job title '{title}' with ID {new_id}.")
        return new_id
    except sqlite3.IntegrityError:
        logger.warning(f"Attempted to add duplicate job title: '{title}'")
        return None
    except sqlite3.Error as e:
        logger.error(f"Database error while adding job title '{title}': {e}")
        return None


def get_all_job_titles() -> List[str]:
    """Retrieves all job titles from the database, sorted alphabetically.

    Returns:
        A list of all job title strings. Returns an empty list if no titles
        are found or if a database error occurs.
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM job_titles ORDER BY title ASC")
        # fetchall() returns a list of tuples, e.g., [('Developer',), ('Manager',)]
        # A list comprehension is used to flatten it into a list of strings.
        titles = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Retrieved {len(titles)} job titles from the database.")
        return titles
    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving job titles: {e}")
        return []


def delete_job_title(title: str) -> bool:
    """Deletes a specific job title from the database.

    Args:
        title: The exact, case-sensitive job title string to delete.

    Returns:
        True if a row was successfully deleted, False if no matching
        row was found or if a database error occurred.
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM job_titles WHERE title = ?", (title,))
        conn.commit()
        # cursor.rowcount indicates the number of rows affected by the last query.
        if cursor.rowcount > 0:
            logger.info(f"Successfully deleted job title: '{title}'")
            return True
        else:
            logger.warning(f"Attempted to delete non-existent job title: '{title}'")
            return False
    except sqlite3.Error as e:
        logger.error(f"Database error while deleting job title '{title}': {e}")
        return False