Job News Aggregator
The Job News Aggregator is a full-stack web application designed to help users track professions and stay up-to-date with relevant industry news. Users can add job titles to a tracking list, and the application will fetch and display recent articles related to that title from the NewsAPI.org service.

This project is built with a clean, modular, and extendable architecture, making it easy to maintain and scale.

Features
Track Job Titles: Add, view, and delete job titles from a persistent list.

Dynamic News Feed: Select a tracked job title to instantly fetch and display relevant news articles.


Clean User Interface: A responsive, two-column layout allows for easy navigation between the job list and the articles.


RESTful API: A well-defined backend API for managing jobs and fetching articles.

Architecture Overview
This application is built using a professional, modular structure to ensure a clean separation of concerns. This design makes the codebase easy to understand, debug, and extend.

main.py: The main entry point for the application. It uses the Application Factory pattern (

create_app) to initialize the Flask app, load configuration, and register all necessary components.


config.py: Handles all application configuration. It securely loads sensitive data like API keys from a 

.env file.


/models: Contains all database-related logic.


database.py: Manages the SQLite database connection and initialization.


job_title.py: Defines the job_titles table schema and provides all CRUD (Create, Read, Update, Delete) functions for managing job titles.

/routes: Defines all the API endpoints and web routes using Flask Blueprints.


job_routes.py: Handles requests for adding, deleting, and retrieving job titles.


article_routes.py: Handles requests for fetching news articles for a specific job title.



web_routes.py: Renders the main index.html page.

/services: Contains logic for interacting with external APIs.


news_service.py: Encapsulates all the logic for communicating with the NewsAPI.org service, including building requests, handling errors, and formatting the data.


/static & /templates: Hold all frontend assets, including CSS, JavaScript, and the main index.html file.

/utils: Provides helper functions used across the application to maintain consistency.


response_helpers.py: Standardizes API success and error responses.


validators.py: Provides functions for validating and sanitizing user input.

Setup and Installation
Follow these steps to get the application running on your local machine.

1. Prerequisites
Python 3.8+

A NewsAPI.org API Key. You can get a free one from newsapi.org.

2. Clone the Repository
```bash
git clone https://github.com/your-username/job-news-aggregator.git
cd job-news-aggregator
```
3. Set Up a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

4. Install Dependencies
Install all required Python packages from the requirements.txt file.
```bash
pip install -r requirements.txt
```
5. Configure Environment Variables
The application requires environment variables for configuration. Create a file named .env in the root of the project directory.
```bash
touch .env
```
Open the .env file and add the following, replacing the placeholder values with your own:
```bash
python main.py
```
The server will start, typically on http://127.0.0.1:5000. Open this URL in your web browser to use the application.

API Endpoints
The application exposes the following RESTful API endpoints under the /api prefix.

Job Title Management
Add Job Title

Endpoint: POST /api/add_job

Description: Adds a new job title to the database.


Payload: {"title": "Software Engineer"} 

Responses:


201 Created: If the title is added successfully.


400 Bad Request: If the payload is invalid or the title is empty.


409 Conflict: If the title already exists.

Get All Job Titles

Endpoint: GET /api/get_jobs


Description: Retrieves a list of all tracked job titles, sorted alphabetically.

Responses:

200 OK: Returns a JSON object with a list of titles, e.g., {"job_titles": ["Data Scientist", "Software Engineer"]}.

Delete Job Title

Endpoint: DELETE /api/delete_job


Description: Deletes a specific job title from the database.

Payload: {"title": "Software Engineer"}

Responses:

200 OK: If the title was deleted successfully.


400 Bad Request: If the payload is invalid.


404 Not Found: If the specified title does not exist.

Article Fetching
Fetch Articles

Endpoint: GET /api/fetch_articles/<job_title>


Description: Fetches news articles related to the specified job_title.

Responses:


200 OK: Returns a JSON object containing a list of articles.


400 Bad Request: If the job_title is empty.


500 Internal Server Error: If there is a server-side issue, such as a missing API key.