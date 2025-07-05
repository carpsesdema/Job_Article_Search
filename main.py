# main.py
"""Main entry point. Initializes and runs the Flask application.

This file is responsible for:
- Creating the Flask application instance using the application factory pattern.
- Loading configuration from config.py.
- Initializing the database.
- Registering all the route blueprints from the `routes` directory.
- Starting the development server when run as a script.
"""

import logging
import os
from typing import Any

from flask import Flask

# Set up basic logging
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure an instance of the Flask application.

    This function follows the Application Factory pattern. It creates the Flask app,
    loads configuration, initializes extensions (like the database), and registers
    blueprints for different parts of the application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    logger.info("Flask app instance created.")

    # Load configuration from config.py
    # This will load variables like NEWS_API_KEY and DATABASE_PATH
    try:
        app.config.from_pyfile('config.py')
        logger.info("Configuration loaded from config.py.")
    except FileNotFoundError:
        logger.error("Configuration file 'config.py' not found. Please create it.")
        # In a real app, you might exit or use default fallbacks.
        # For this project, we assume config.py will exist.
        pass
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise

    # Import and register blueprints
    try:
        from routes.web_routes import web_bp
        from routes.job_routes import job_bp
        from routes.article_routes import article_bp

        app.register_blueprint(web_bp)
        app.register_blueprint(job_bp, url_prefix='/api')
        app.register_blueprint(article_bp, url_prefix='/api')
        logger.info("All blueprints registered successfully.")
    except ImportError as e:
        logger.error(f"Failed to import or register blueprints: {e}")
        logger.error("Please ensure all route files (web_routes.py, job_routes.py, article_routes.py) exist and define a Blueprint.")
        raise

    # Initialize the database
    try:
        from models.database import init_db
        with app.app_context():
            init_db()
        logger.info("Database initialized successfully.")
    except ImportError as e:
        logger.error(f"Failed to import database initializer: {e}")
        logger.error("Please ensure 'models/database.py' exists and contains an 'init_db' function.")
        raise
    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
        raise

    return app


if __name__ == '__main__':
    # Configure logging for running the script directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create the application
    app = create_app()

    # Get server configuration from environment variables with defaults
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    try:
        port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    except ValueError:
        logger.warning("Invalid PORT environment variable. Using default 5000.")
        port = 5000

    # FLASK_DEBUG is a standard Flask env var.
    # It's better to use it than a custom one like FLASK_ENV for debug mode.
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'

    logger.info(f"Starting Flask server on {host}:{port} (Debug mode: {debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)