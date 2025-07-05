// static/js/script.js
// JavaScript logic for frontend interactions and API calls.

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element Selectors ---
    const addJobForm = document.getElementById('add-job-form');
    const newJobTitleInput = document.getElementById('new-job-title');
    const jobList = document.getElementById('job-list');
    const articlesContainer = document.getElementById('articles-container');
    const articlesColumnHeader = document.querySelector('#articles-column h2');
    const articlesColumn = document.getElementById('articles-column');

    // --- State ---
    let activeJobTitle = null;

    // --- API Helper ---
    /**
     * A generic wrapper for the fetch API to handle common tasks.
     * @param {string} url - The URL to fetch.
     * @param {object} options - The options for the fetch request.
     * @returns {Promise<any>} - The JSON response data.
     * @throws {Error} - Throws an error if the network response is not ok.
     */
    async function apiRequest(url, options = {}) {
        try {
            const response = await fetch(url, options);
            const data = await response.json();
            if (!response.ok) {
                // Use the error message from the API if available, otherwise use a generic one.
                const errorMessage = data.error || `HTTP error! Status: ${response.status}`;
                throw new Error(errorMessage);
            }
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            // Re-throw the error to be caught by the calling function.
            throw error;
        }
    }

    // --- Render Functions ---

    /**
     * Renders a message (e.g., loading, error, or info) in a specified container.
     * @param {HTMLElement} container - The container to display the message in.
     * @param {string} text - The message text.
     * @param {string} type - The type of message ('info', 'error', 'loader').
     */
    function showMessage(container, text, type = 'info') {
        container.innerHTML = ''; // Clear previous content
        const messageDiv = document.createElement('div');
        if (type === 'loader') {
            messageDiv.className = 'loader';
        } else {
            messageDiv.className = 'message';
            messageDiv.textContent = text;
            if (type === 'error') {
                messageDiv.classList.add('error-message');
            }
        }
        container.appendChild(messageDiv);
    }

    /**
     * Renders the list of job titles in the UI.
     * @param {string[]} jobs - An array of job title strings.
     */
    function renderJobList(jobs) {
        jobList.innerHTML = ''; // Clear existing list
        if (jobs.length === 0) {
            const li = document.createElement('li');
            li.className = 'job-item';
            li.textContent = 'No job titles added yet.';
            jobList.appendChild(li);
            return;
        }

        jobs.forEach(title => {
            const li = document.createElement('li');
            li.className = 'job-item';
            li.dataset.title = title;

            const titleSpan = document.createElement('span');
            titleSpan.textContent = title;

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-job-btn';
            deleteBtn.innerHTML = '&times;'; // 'x' symbol
            deleteBtn.title = `Delete ${title}`;

            // Event listener for selecting a job
            li.addEventListener('click', (e) => {
                // Prevent selection when the delete button is clicked
                if (e.target !== deleteBtn) {
                    handleSelectJob(title);
                }
            });

            // Event listener for deleting a job
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent the li's click event from firing
                if (confirm(`Are you sure you want to delete "${title}"?`)) {
                    handleDeleteJob(title);
                }
            });

            li.appendChild(titleSpan);
            li.appendChild(deleteBtn);
            jobList.appendChild(li);
        });

        // Re-apply the active class if the active job is still in the list
        if (activeJobTitle) {
            const activeItem = jobList.querySelector(`.job-item[data-title="${activeJobTitle}"]`);
            if (activeItem) {
                activeItem.classList.add('active');
            } else {
                // The active job was deleted, so reset the state
                activeJobTitle = null;
                resetArticlesView();
            }
        }
    }

    /**
     * Renders the fetched articles in the UI.
     * @param {object[]} articles - An array of article objects.
     */
    function renderArticles(articles) {
        articlesContainer.innerHTML = ''; // Clear previous content
        if (articles.length === 0) {
            showMessage(articlesContainer, 'No articles found for this job title.');
            return;
        }

        articles.forEach(article => {
            const articleCard = document.createElement('div');
            articleCard.className = 'article-card';

            const placeholderImage = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='; // Transparent 1x1 pixel

            articleCard.innerHTML = `
                <img src="${article.image_url || placeholderImage}" alt="${article.title || 'Article image'}" class="article-image" onerror="this.onerror=null;this.src='${placeholderImage}';">
                <div class="article-content">
                    <h3 class="article-title">
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer">${article.title || 'No Title'}</a>
                    </h3>
                    <p class="article-meta">
                        By ${article.author || 'Unknown Author'} | ${article.source || 'Unknown Source'}
                    </p>
                    <p class="article-description">${article.description || 'No description available.'}</p>
                </div>
            `;
            articlesContainer.appendChild(articleCard);
        });
    }

    // --- Core Logic Handlers ---

    /**
     * Fetches job titles from the API and renders them.
     */
    async function loadJobTitles() {
        try {
            const data = await apiRequest('/api/get_jobs');
            renderJobList(data.job_titles);
        } catch (error) {
            showMessage(jobList, `Error: ${error.message}`, 'error');
        }
    }

    /**
     * Handles the submission of the "add job" form.
     * @param {Event} event - The form submission event.
     */
    async function handleAddJob(event) {
        event.preventDefault();
        const title = newJobTitleInput.value.trim();
        if (!title) {
            alert('Please enter a job title.');
            return;
        }

        try {
            await apiRequest('/api/add_job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title }),
            });
            newJobTitleInput.value = ''; // Clear input on success
            await loadJobTitles(); // Refresh the list
        } catch (error) {
            alert(`Error adding job: ${error.message}`);
        }
    }

    /**
     * Handles the deletion of a job title.
     * @param {string} title - The title of the job to delete.
     */
    async function handleDeleteJob(title) {
        try {
            await apiRequest('/api/delete_job', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title }),
            });

            // If the deleted job was the active one, reset the articles view
            if (activeJobTitle === title) {
                activeJobTitle = null;
                resetArticlesView();
            }
            await loadJobTitles(); // Refresh the list
        } catch (error) {
            alert(`Error deleting job: ${error.message}`);
        }
    }

    /**
     * Handles the selection of a job title from the list.
     * @param {string} title - The selected job title.
     */
    function handleSelectJob(title) {
        if (activeJobTitle === title) return; // Do nothing if already active

        activeJobTitle = title;

        // Update UI to show which item is active
        document.querySelectorAll('#job-list .job-item').forEach(item => {
            item.classList.remove('active');
        });
        const selectedItem = jobList.querySelector(`.job-item[data-title="${title}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }

        fetchAndDisplayArticles(title);
    }

    /**
     * Fetches and displays articles for the given job title.
     * @param {string} title - The job title to fetch articles for.
     */
    async function fetchAndDisplayArticles(title) {
        articlesColumnHeader.textContent = `News for: ${title}`;
        showMessage(articlesContainer, '', 'loader');

        try {
            const data = await apiRequest(`/api/fetch_articles/${encodeURIComponent(title)}`);
            renderArticles(data.articles);
        } catch (error) {
            showMessage(articlesContainer, `Error fetching articles: ${error.message}`, 'error');
        }
    }

    /**
     * Resets the articles view to its initial state.
     */
    function resetArticlesView() {
        articlesColumnHeader.textContent = 'News Articles';
        showMessage(articlesContainer, 'Select a job title from the list to see relevant news articles.');
    }

    // --- Initialization ---
    function init() {
        addJobForm.addEventListener('submit', handleAddJob);
        loadJobTitles();
        resetArticlesView();
    }

    init();
});