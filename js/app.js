// News-Nest1 Frontend Application
// Main application entry point

import { API } from './api.js';
import { Router } from './router.js';
import { Auth } from './auth.js';
import { UI } from './ui.js';
import { WebSocket } from './websocket.js';

class App {
    constructor() {
        this.api = new API();
        this.router = new Router();
        this.auth = new Auth(this.api);
        this.ui = new UI();
        this.websocket = null;
        
        this.currentUser = null;
        this.currentView = 'feed';
        
        this.currentPage = 1;
        this.currentCategory = '';
        this.searchPage = 1;
        this.searchQuery = '';
        
        this.init();
    }
    
    async init() {
        try {
            // Wait for DOM to be fully loaded
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Make app instance globally available for UI callbacks
            window.app = this;
            
            // Initialize UI
            this.ui.init();
            
            // Check authentication status
            this.currentUser = await this.auth.checkAuthStatus();
            
            // Initialize router
            this.router.init(this);
            
            // Initialize WebSocket if authenticated
            if (this.currentUser) {
                this.updateUIForUser();
                this.initWebSocket();
            } else {
                this.updateUIForGuest();
            }
            
            // Load initial view
            await this.loadView('feed');
            
            // Set up event listeners
            this.setupEventListeners();
            
            console.log('News-Nest1 app initialized successfully');
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.ui.showToast('Failed to initialize application', 'error');
        }
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.target.dataset.view;
                this.router.navigate(view);
            });
        });
        
        // User menu
        const userToggle = document.getElementById('userToggle');
        const userDropdown = document.getElementById('userDropdown');
        
        if (userToggle) {
            userToggle.addEventListener('click', () => {
                userDropdown.classList.toggle('show');
            });
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.user-menu')) {
                userDropdown?.classList.remove('show');
            }
        });
        
        // Auth buttons
        document.getElementById('loginBtn')?.addEventListener('click', () => {
            this.showLoginModal();
        });
        
        document.getElementById('registerBtn')?.addEventListener('click', () => {
            this.showRegisterModal();
        });
        
        document.getElementById('logoutBtn')?.addEventListener('click', () => {
            this.logout();
        });
        
        // Search
        document.getElementById('searchBtn')?.addEventListener('click', () => {
            this.handleSearch();
        });
        
        document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });
        
        // Refresh feed
        document.getElementById('refreshFeed')?.addEventListener('click', () => {
            this.loadView(this.currentView);
        });
        
        // Category filter
        document.getElementById('categoryFilter')?.addEventListener('change', (e) => {
            this.currentCategory = e.target.value;
            this.loadFeed();
        });
        
        // Article saving
        document.getElementById('viewContainer').addEventListener('click', (e) => {
            if (e.target.closest('.save-article-btn')) {
                const button = e.target.closest('.save-article-btn');
                const articleUrl = button.dataset.articleUrl;
                this.toggleSaveArticle(articleUrl, button);
            }
        });

        // Preferences
        document.getElementById('managePreferences')?.addEventListener('click', () => {
            this.router.navigate('preferences');
        });
        
        // Event delegation for dynamically created elements
        document.addEventListener('click', (e) => {
            // Follow topic button
            if (e.target.closest('#followTopic')) {
                e.preventDefault();
                this.followTopic();
            }
            
            // Follow outlet button
            if (e.target.closest('#followOutlet')) {
                e.preventDefault();
                this.followOutlet();
            }
            
            // Unfollow topic button
            if (e.target.closest('.topic-tag .unfollow-btn')) {
                e.preventDefault();
                const topicTag = e.target.closest('.topic-tag');
                const topicName = topicTag.querySelector('.topic-name').textContent;
                this.unfollowTopic(topicName);
            }
            
            // Unfollow outlet button
            if (e.target.closest('.outlet-tag .unfollow-btn')) {
                e.preventDefault();
                const outletTag = e.target.closest('.outlet-tag');
                const outletName = outletTag.querySelector('.outlet-name').textContent;
                this.unfollowOutlet(outletName);
            }
        });
        
        // Modal close
        document.getElementById('modalClose')?.addEventListener('click', () => {
            this.ui.hideModal();
        });
        
        document.getElementById('modalOverlay')?.addEventListener('click', (e) => {
            if (e.target.id === 'modalOverlay') {
                this.ui.hideModal();
            }
        });

        // Load more articles
        document.getElementById('loadMoreBtn').addEventListener('click', () => this.loadMoreArticles());
    }
    
    async loadView(viewName) {
        try {
            this.ui.showLoading();
            this.currentView = viewName;
            this.ui.updateView(`${viewName}View`);

            switch (viewName) {
                case 'feed':
                    await this.loadFeed();
                    break;
                case 'personalized':
                    if (!this.currentUser) {
                        this.ui.showToast('Please login to view personalized feed', 'warning');
                        this.router.navigate('feed');
                        return;
                    }
                    await this.loadPersonalizedFeed();
                    break;
                case 'search':
                     await this.loadSearchView();
                    break;
                case 'saved':
                    if (!this.currentUser) {
                        this.ui.showToast('Please login to view saved articles', 'warning');
                        this.router.navigate('feed');
                        return;
                    }
                    await this.loadSavedArticles();
                    break;
                case 'profile':
                    if (!this.currentUser) {
                        this.router.navigate('feed');
                        return;
                    }
                    this.loadProfile();
                    break;
                case 'preferences':
                    if (!this.currentUser) {
                        this.router.navigate('feed');
                        return;
                    }
                    await this.loadPreferences();
                    break;
                default:
                    await this.loadFeed();
            }
        } catch (error) {
            console.error(`Failed to load view ${viewName}:`, error);
            this.ui.showToast('Failed to load content', 'error');
        } finally {
            this.ui.hideLoading();
        }
    }
    
    async loadFeed() {
        try {
            this.ui.showLoading();
            this.currentPage = 1;
            
            // Populate category dropdown
            await this.populateCategoryDropdown();
            
            const articles = await this.api.getArticles(this.currentPage, this.currentCategory);
            const articlesGrid = document.getElementById('articlesGrid');
            
            if (articles && articles.length > 0) {
                articlesGrid.innerHTML = articles.map(article => this.renderArticle(article)).join('');
                
                // Show load more button if there are articles
                const loadMoreBtn = document.getElementById('loadMoreBtn');
                loadMoreBtn.style.display = 'inline-flex';
            } else {
                articlesGrid.innerHTML = '<div class="empty-state"><i class="fas fa-newspaper"></i><h3>No articles found</h3><p>Try refreshing or changing the category filter.</p></div>';
                document.getElementById('loadMoreBtn').style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading feed:', error);
            this.ui.showToast('Failed to load articles', 'error');
        } finally {
            this.ui.hideLoading();
        }
    }
    
    async loadPersonalizedFeed() {
        try {
            this.ui.showLoading();
            const articles = await this.api.getPersonalizedFeed();
            const personalizedGrid = document.getElementById('personalizedGrid');
            
            if (articles && articles.length > 0) {
                personalizedGrid.innerHTML = articles.map(article => this.renderArticle(article)).join('');
            } else {
                personalizedGrid.innerHTML = '<div class="empty-state"><i class="fas fa-user-check"></i><h3>No personalized articles found</h3><p>Follow some topics and outlets in your preferences to get personalized recommendations.</p></div>';
            }
        } catch (error) {
            console.error('Error loading personalized feed:', error);
            this.ui.showToast('Failed to load personalized feed', 'error');
        } finally {
            this.ui.hideLoading();
        }
    }
    
    async loadSearchView(query = '') {
        if (query) {
            await this.handleSearch();
        }
    }
    
    async loadSavedArticles() {
        const articles = await this.api.getSavedArticles();
        this.ui.renderArticles(articles, 'savedGrid');
    }
    
    loadProfile() {
        const user = this.api.getCurrentUser();
        if (user) {
            document.getElementById('profileUsername').textContent = user.username;
            document.getElementById('profileEmail').textContent = user.email;
        }
    }
    
    async loadPreferences() {
        try {
            this.ui.showLoading();
            
            // Get followed topics and outlets
            const topicsResponse = await this.api.getFollowedTopics();
            const outletsResponse = await this.api.getFollowedOutlets();
            
            const topics = topicsResponse.topics || [];
            const outlets = outletsResponse.outlets || [];
            
            // Render the preferences
            this.renderPreferencesView(topics, outlets);
            
        } catch (error) {
            console.error('Error loading preferences:', error);
            this.ui.showToast('Failed to load preferences', 'error');
        } finally {
            this.ui.hideLoading();
        }
    }
    
    renderPreferencesView(topics, outlets) {
        const preferencesView = document.getElementById('preferencesView');
        if (!preferencesView) return;
        
        preferencesView.innerHTML = `
            <div class="view-header">
                <h1><i class="fas fa-cog"></i> Preferences</h1>
                <p>Manage your followed topics and news outlets</p>
            </div>
            
            <div class="preferences-container">
                <div class="preference-section">
                    <h2><i class="fas fa-tags"></i> Followed Topics</h2>
                    <div class="topics-container">
                        <div class="topics-list" id="followedTopicsList">
                            ${topics.length === 0 ? '<p class="empty-message">You are not following any topics yet.</p>' : ''}
                        </div>
                        <div class="add-preference">
                            <select id="newTopicInput" class="form-select">
                                <option value="">Select a topic...</option>
                                <!-- Topics will be populated by JavaScript -->
                            </select>
                            <button id="followTopic" class="btn btn-primary">
                                <i class="fas fa-plus"></i> Follow Topic
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="preference-section">
                    <h2><i class="fas fa-newspaper"></i> Followed Outlets</h2>
                    <div class="outlets-container">
                        <div class="outlets-list" id="followedOutletsList">
                            ${outlets.length === 0 ? '<p class="empty-message">You are not following any outlets yet.</p>' : ''}
                        </div>
                        <div class="add-preference">
                            <select id="newOutletInput" class="form-select">
                                <option value="">Select an outlet...</option>
                                <!-- Outlets will be populated by JavaScript -->
                            </select>
                            <button id="followOutlet" class="btn btn-primary">
                                <i class="fas fa-plus"></i> Follow Outlet
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Populate dropdowns and render existing topics and outlets
        this.populatePreferenceDropdowns();
        this.renderTopicsList(topics);
        this.renderOutletsList(outlets);
    }
    
    async populatePreferenceDropdowns() {
        try {
            // Get categories and sources
            const categories = await this.api.getCategories();
            const sources = await this.api.getSources();
            
            // Get current followed topics and outlets
            const topicsResponse = await this.api.getFollowedTopics();
            const outletsResponse = await this.api.getFollowedOutlets();
            const followedTopics = topicsResponse.topics || [];
            const followedOutlets = outletsResponse.outlets || [];
            
            // Populate topic dropdown (categories) - filter out already followed
            const topicDropdown = document.getElementById('newTopicInput');
            if (topicDropdown) {
                // Clear existing options except the first one
                topicDropdown.innerHTML = '<option value="">Select a topic...</option>';
                
                const availableTopics = categories.filter(category => !followedTopics.includes(category));
                
                if (availableTopics.length === 0) {
                    topicDropdown.innerHTML = '<option value="" disabled>All topics already followed</option>';
                    topicDropdown.disabled = true;
                } else {
                    availableTopics.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category;
                        option.textContent = category;
                        topicDropdown.appendChild(option);
                    });
                }
            }
            
            // Populate outlet dropdown (sources) - filter out already followed
            const outletDropdown = document.getElementById('newOutletInput');
            if (outletDropdown) {
                // Clear existing options except the first one
                outletDropdown.innerHTML = '<option value="">Select an outlet...</option>';
                
                const availableOutlets = sources.filter(source => !followedOutlets.includes(source));
                
                if (availableOutlets.length === 0) {
                    outletDropdown.innerHTML = '<option value="" disabled>All outlets already followed</option>';
                    outletDropdown.disabled = true;
                } else {
                    availableOutlets.forEach(source => {
                        const option = document.createElement('option');
                        option.value = source;
                        option.textContent = source;
                        outletDropdown.appendChild(option);
                    });
                }
            }
        } catch (error) {
            console.error('Failed to populate preference dropdowns:', error);
        }
    }
    
    renderTopicsList(topics) {
        const topicsList = document.getElementById('followedTopicsList');
        if (!topicsList) return;
        
        if (topics.length === 0) {
            topicsList.innerHTML = '<p class="empty-message">You are not following any topics yet.</p>';
            return;
        }
        
        topicsList.innerHTML = topics.map(topic => `
            <div class="topic-tag">
                <span class="topic-name">${topic}</span>
                <button class="unfollow-btn" onclick="app.unfollowTopic('${topic}')" title="Unfollow ${topic}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
    
    renderOutletsList(outlets) {
        const outletsList = document.getElementById('followedOutletsList');
        if (!outletsList) return;
        
        if (outlets.length === 0) {
            outletsList.innerHTML = '<p class="empty-message">You are not following any outlets yet.</p>';
            return;
        }
        
        outletsList.innerHTML = outlets.map(outlet => `
            <div class="outlet-tag">
                <span class="outlet-name">${outlet}</span>
                <button class="unfollow-btn" onclick="app.unfollowOutlet('${outlet}')" title="Unfollow ${outlet}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
    
    async populateCategoryDropdown() {
        try {
            const categories = await this.api.getCategories();
            const dropdown = document.getElementById('categoryFilter');
            if (dropdown) {
                // Clear existing options except "All Categories"
                dropdown.innerHTML = '<option value="">All Categories</option>';
                
                // Add category options
                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    dropdown.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to populate categories:', error);
        }
    }
    
    async handleSearch() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) {
            this.ui.showToast('Please enter a search term', 'warning');
            return;
        }

        try {
            this.ui.showLoading();
            this.searchQuery = query;
            this.searchPage = 1;
            
            const results = await this.api.searchArticles(query, this.searchPage);
            const searchResults = document.getElementById('searchResults');
            
            if (results && results.length > 0) {
                searchResults.innerHTML = results.map(article => this.renderArticle(article)).join('');
                
                // Show load more button if there are results
                const loadMoreBtn = document.getElementById('loadMoreBtn');
                loadMoreBtn.style.display = 'inline-flex';
                
                this.router.navigate('search');
            } else {
                searchResults.innerHTML = '<div class="empty-state"><i class="fas fa-search"></i><h3>No results found</h3><p>Try different keywords or check your spelling.</p></div>';
                document.getElementById('loadMoreBtn').style.display = 'none';
                this.router.navigate('search');
            }
        } catch (error) {
            console.error('Error searching:', error);
            this.ui.showToast('Failed to search articles', 'error');
        } finally {
            this.ui.hideLoading();
        }
    }
    
    async filterByCategory(category) {
        try {
            this.ui.showLoading();
            const articles = category ? await this.api.getFeedByCategory(category) : await this.api.getFeed();
            this.ui.renderArticles(articles, 'articlesGrid');
        } catch (error) {
            console.error('Filter failed:', error);
            this.ui.showToast('Failed to filter articles', 'error');
        } finally {
            this.ui.hideLoading();
        }
    }
    
    async toggleSaveArticle(articleUrl, button) {
        if (!this.currentUser) {
            this.ui.showToast('Please login to save articles', 'warning');
            return;
        }

        try {
            const isSaved = button.classList.contains('saved');
            
            if (isSaved) {
                await this.api.unsaveArticle(articleUrl);
                button.classList.remove('saved');
                button.querySelector('i').className = 'far fa-bookmark';
                this.ui.showToast('Article removed from saved', 'info');
            } else {
                await this.api.saveArticle(articleUrl);
                button.classList.add('saved');
                button.querySelector('i').className = 'fas fa-bookmark';
                this.ui.showToast('Article saved successfully', 'success');
            }
        } catch (error) {
            console.error('Error saving article:', error);
            this.ui.showToast('Error saving article', 'error');
        }
    }
    
    async followTopic() {
        const dropdown = document.getElementById('newTopicInput');
        const topic = dropdown.value;
        if (!topic) {
            this.ui.showToast('Please select a topic to follow', 'warning');
            return;
        }
        
        try {
            await this.api.followTopic(topic);
            dropdown.value = ''; // Reset dropdown
            await this.loadPreferences();
            this.ui.showToast(`Followed ${topic}`, 'success');
        } catch (error) {
            this.ui.showToast(error.message, 'error');
        }
    }
    
    async unfollowTopic(topic) {
        try {
            await this.api.unfollowTopic(topic);
            await this.loadPreferences();
            this.ui.showToast(`Unfollowed ${topic}`, 'success');
        } catch (error) {
            this.ui.showToast(error.message, 'error');
        }
    }
    
    async followOutlet() {
        const dropdown = document.getElementById('newOutletInput');
        const outlet = dropdown.value;
        if (!outlet) {
            this.ui.showToast('Please select an outlet to follow', 'warning');
            return;
        }

        try {
            await this.api.followOutlet(outlet);
            dropdown.value = ''; // Reset dropdown
            await this.loadPreferences();
            this.ui.showToast(`Followed ${outlet}`, 'success');
        } catch (error) {
            this.ui.showToast(error.message, 'error');
        }
    }
    
    async unfollowOutlet(outlet) {
        try {
            await this.api.unfollowOutlet(outlet);
            await this.loadPreferences();
            this.ui.showToast(`Unfollowed ${outlet}`, 'success');
        } catch (error) {
            this.ui.showToast(error.message, 'error');
        }
    }
    
    showLoginModal() {
        const content = `
            <div class="auth-modal">
                <h2><i class="fas fa-sign-in-alt"></i> Login</h2>
                <div class="auth-form">
                    <div class="form-group">
                        <label for="loginUsername">Username</label>
                        <input type="text" id="loginUsername" placeholder="Enter your username" required>
                    </div>
                    <div class="form-group">
                        <label for="loginPassword">Password</label>
                        <input type="password" id="loginPassword" placeholder="Enter your password" required>
                    </div>
                    <button id="submitLogin" class="auth-btn">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </button>
                </div>
                <div class="auth-footer">
                    <p>Don't have an account? <a href="#" id="switchToRegister">Register here</a></p>
                </div>
            </div>
        `;
        this.ui.showModal(content);
        document.getElementById('submitLogin').addEventListener('click', () => this.login());
        document.getElementById('switchToRegister').addEventListener('click', (e) => {
            e.preventDefault();
            this.ui.hideModal();
            this.showRegisterModal();
        });
    }
    
    showRegisterModal() {
        const content = `
            <div class="auth-modal">
                <h2><i class="fas fa-user-plus"></i> Register</h2>
                <div class="auth-form">
                    <div class="form-group">
                        <label for="registerUsername">Username</label>
                        <input type="text" id="registerUsername" placeholder="Choose a username" required 
                               pattern="[a-zA-Z0-9_-]{3,30}" 
                               title="Username must be 3-30 characters, letters, numbers, hyphens, and underscores only">
                        <div class="input-feedback" id="usernameFeedback"></div>
                    </div>
                    <div class="form-group">
                        <label for="registerEmail">Email</label>
                        <input type="email" id="registerEmail" placeholder="Enter your email" required
                               pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
                               title="Please enter a valid email address">
                        <div class="input-feedback" id="emailFeedback"></div>
                    </div>
                    <div class="form-group">
                        <label for="registerPassword">Password</label>
                        <input type="password" id="registerPassword" placeholder="Choose a password" required
                               minlength="8"
                               title="Password must be at least 8 characters long">
                        <div class="password-strength" id="passwordStrength"></div>
                        <div class="input-feedback" id="passwordFeedback"></div>
                    </div>
                    <button id="submitRegister" class="auth-btn">
                        <i class="fas fa-user-plus"></i> Register
                    </button>
                </div>
                <div class="auth-footer">
                    <p>Already have an account? <a href="#" id="switchToLogin">Login here</a></p>
                </div>
            </div>
        `;
        this.ui.showModal(content);
        
        // Add form validation
        this.setupRegistrationValidation();
        
        document.getElementById('submitRegister').addEventListener('click', () => this.register());
        document.getElementById('switchToLogin').addEventListener('click', (e) => {
            e.preventDefault();
            this.ui.hideModal();
            this.showLoginModal();
        });
        
        // Add password strength indicator
        const passwordInput = document.getElementById('registerPassword');
        const strengthIndicator = document.getElementById('passwordStrength');
        passwordInput.addEventListener('input', () => {
            const strength = this.checkPasswordStrength(passwordInput.value);
            strengthIndicator.className = `password-strength ${strength}`;
            strengthIndicator.textContent = strength === 'weak' ? 'Weak' : strength === 'medium' ? 'Medium' : 'Strong';
        });
    }
    
    setupRegistrationValidation() {
        const usernameInput = document.getElementById('registerUsername');
        const emailInput = document.getElementById('registerEmail');
        const passwordInput = document.getElementById('registerPassword');
        
        // Username validation
        usernameInput.addEventListener('blur', () => {
            const username = usernameInput.value.trim();
            const feedback = document.getElementById('usernameFeedback');
            
            if (!username) {
                this.showFieldError(usernameInput, false, 'Username is required');
            } else if (!/^[a-zA-Z0-9_-]{3,30}$/.test(username)) {
                this.showFieldError(usernameInput, false, 'Username must be 3-30 characters, letters, numbers, hyphens, and underscores only');
            } else {
                this.showFieldError(usernameInput, true, '');
            }
        });
        
        // Email validation
        emailInput.addEventListener('blur', () => {
            const email = emailInput.value.trim();
            const feedback = document.getElementById('emailFeedback');
            
            if (!email) {
                this.showFieldError(emailInput, false, 'Email is required');
            } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
                this.showFieldError(emailInput, false, 'Please enter a valid email address');
            } else {
                this.showFieldError(emailInput, true, '');
            }
        });
        
        // Password validation
        passwordInput.addEventListener('blur', () => {
            const password = passwordInput.value;
            const feedback = document.getElementById('passwordFeedback');
            
            if (!password) {
                this.showFieldError(passwordInput, false, 'Password is required');
            } else if (password.length < 8) {
                this.showFieldError(passwordInput, false, 'Password must be at least 8 characters long');
            } else {
                this.showFieldError(passwordInput, true, '');
            }
        });
    }
    
    showFieldError(input, isValid, message) {
        const feedback = input.parentElement.querySelector('.input-feedback');
        if (feedback) {
            feedback.textContent = message;
            feedback.className = `input-feedback ${isValid ? 'valid' : 'error'}`;
        }
        input.classList.toggle('error', !isValid);
        input.classList.toggle('valid', isValid);
    }
    
    validateRegistrationForm() {
        const username = document.getElementById('registerUsername').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value;
        
        let isValid = true;
        
        // Validate username
        if (!username || !/^[a-zA-Z0-9_-]{3,30}$/.test(username)) {
            this.showFieldError(document.getElementById('registerUsername'), false, 'Invalid username');
            isValid = false;
        }
        
        // Validate email
        if (!email || !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
            this.showFieldError(document.getElementById('registerEmail'), false, 'Invalid email address');
            isValid = false;
        }
        
        // Validate password
        if (!password || password.length < 8) {
            this.showFieldError(document.getElementById('registerPassword'), false, 'Password must be at least 8 characters');
            isValid = false;
        }
        
        return isValid;
    }
    
    async login() {
        try {
            console.log('Login attempt started...');
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            console.log('Attempting to login with username:', username);
            await this.auth.login(username, password);
            console.log('Login successful, checking auth status...');
            this.currentUser = await this.auth.checkAuthStatus();
            console.log('Current user:', this.currentUser);
            
            this.updateUIForUser();
            this.initWebSocket();
            this.ui.hideModal();
            this.router.navigate('feed');
            
        } catch (error) {
            console.error('Login error:', error);
            this.ui.showToast(error.message, 'error');
        }
    }

    async register() {
        try {
            // Validate form before submitting
            if (!this.validateRegistrationForm()) {
                this.ui.showToast('Please fix the validation errors before submitting', 'error');
                return;
            }
            
            const username = document.getElementById('registerUsername').value.trim();
            const email = document.getElementById('registerEmail').value.trim();
            const password = document.getElementById('registerPassword').value;

            await this.auth.register(username, email, password);
            await this.auth.login(username, password); // Auto-login after register
            this.currentUser = await this.auth.checkAuthStatus();

            this.updateUIForUser();
            this.initWebSocket();
            this.ui.hideModal();
            this.router.navigate('feed');
            this.ui.showToast('Registration successful! Welcome to News Nest!', 'success');

        } catch (error) {
            console.error('Registration error:', error);
            this.ui.showToast(error.message, 'error');
        }
    }

    async logout() {
        await this.auth.logout();
        this.currentUser = null;
        this.disconnectWebSocket();
        this.updateUIForGuest();
        this.router.navigate('feed');
        this.ui.showToast('You have been logged out', 'success');
    }
    
    updateUIForUser() {
        this.ui.updateUIForUser(this.currentUser.username);
    }
    
    updateUIForGuest() {
        this.ui.updateUIForGuest();
    }
    
    initWebSocket() {
        if (this.websocket) this.websocket.disconnect();
        const token = this.api.token;
        if (!token) return;
        
        this.websocket = new WebSocket(token);
        this.websocket.onMessage = (data) => this.handleWebSocketMessage(data);
        this.websocket.onError = () => this.ui.showToast('WebSocket connection lost. Please refresh.', 'error');
    }
    
    disconnectWebSocket() {
        if (this.websocket) {
            this.websocket.disconnect();
            this.websocket = null;
        }
    }
    
    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            if (message.type === 'new_article') {
                this.ui.showToast(`New article: ${message.article.title}`);
                if (this.currentView === 'feed') {
                    this.loadFeed();
                }
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    renderArticle(article) {
        const imageUrl = article.image_url || this.getPlaceholderImage(article.url, article.category);
        const category = article.category || 'General';
        const sourceName = article.source_name || article.source || 'Unknown Source';
        
        return `
            <article class="article-card">
                <div class="article-card-image">
                    ${article.image_url ? 
                        `<img src="${imageUrl}" alt="${article.title}" onerror="this.parentElement.innerHTML='<div class=\\'placeholder-image\\'>${category}</div>'">` :
                        `<div class="placeholder-image">${category}</div>`
                    }
                </div>
                <div class="article-card-content">
                    <span class="article-card-category">${category}</span>
                    <h3 class="article-card-title">${article.title}</h3>
                    <p class="article-card-summary">${article.content || 'No summary available'}</p>
                    <div class="article-card-footer">
                        <div class="article-meta">
                            <span class="article-card-source">${sourceName}</span>
                            <span class="article-card-date">${this.formatDate(article.published_at)}</span>
                        </div>
                        <div class="article-actions">
                            <button class="save-article-btn" data-article-url="${article.url}" title="Save article">
                                <i class="far fa-bookmark"></i>
                            </button>
                            <a href="${article.url}" target="_blank" class="read-more-btn" title="Read full article">
                                <span>Read More</span>
                                <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </article>
        `;
    }

    formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);
        
        if (diffInHours < 1) {
            return 'Just now';
        } else if (diffInHours < 24) {
            const hours = Math.floor(diffInHours);
            return `${hours}h ago`;
        } else if (diffInHours < 48) {
            return 'Yesterday';
        } else {
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric' 
            });
        }
    }

    async loadMoreArticles() {
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        const currentView = this.currentView;
        
        if (currentView === 'feed') {
            await this.loadMoreFeedArticles();
        } else if (currentView === 'search') {
            await this.loadMoreSearchResults();
        }
    }

    async loadMoreFeedArticles() {
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        
        try {
            loadMoreBtn.classList.add('loading');
            loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            loadMoreBtn.disabled = true;

            this.currentPage += 1;
            const articles = await this.api.getArticles(this.currentPage, this.currentCategory);
            
            if (articles && articles.length > 0) {
                const articlesGrid = document.getElementById('articlesGrid');
                articles.forEach(article => {
                    const articleElement = document.createElement('div');
                    articleElement.innerHTML = this.renderArticle(article);
                    articlesGrid.appendChild(articleElement.firstElementChild);
                });
                
                // Hide load more button if no more articles
                if (articles.length < 20) { // Assuming 20 articles per page
                    loadMoreBtn.style.display = 'none';
                }
            } else {
                loadMoreBtn.style.display = 'none';
                this.ui.showToast('No more articles to load', 'info');
            }
        } catch (error) {
            console.error('Error loading more articles:', error);
            this.ui.showToast('Failed to load more articles', 'error');
            this.currentPage -= 1; // Revert page number on error
        } finally {
            loadMoreBtn.classList.remove('loading');
            loadMoreBtn.innerHTML = '<i class="fas fa-plus"></i> Load More Articles';
            loadMoreBtn.disabled = false;
        }
    }

    async loadMoreSearchResults() {
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        
        try {
            loadMoreBtn.classList.add('loading');
            loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            loadMoreBtn.disabled = true;

            this.searchPage += 1;
            const results = await this.api.searchArticles(this.searchQuery, this.searchPage);
            
            if (results && results.length > 0) {
                const searchResults = document.getElementById('searchResults');
                results.forEach(article => {
                    const articleElement = document.createElement('div');
                    articleElement.innerHTML = this.renderArticle(article);
                    searchResults.appendChild(articleElement.firstElementChild);
                });
                
                // Hide load more button if no more results
                if (results.length < 20) {
                    loadMoreBtn.style.display = 'none';
                }
            } else {
                loadMoreBtn.style.display = 'none';
                this.ui.showToast('No more search results', 'info');
            }
        } catch (error) {
            console.error('Error loading more search results:', error);
            this.ui.showToast('Failed to load more search results', 'error');
            this.searchPage -= 1; // Revert page number on error
        } finally {
            loadMoreBtn.classList.remove('loading');
            loadMoreBtn.innerHTML = '<i class="fas fa-plus"></i> Load More Articles';
            loadMoreBtn.disabled = false;
        }
    }

    checkPasswordStrength(password) {
        if (password.length < 6) return 'weak';
        if (password.length < 8) return 'medium';
        if (password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password)) {
            return 'strong';
        }
        return 'medium';
    }

    getPlaceholderImage(url, category) {
        // Simple category-based color mapping
        const colors = {
            General: '#b0b0b0',
            Technology: '#4a90e2',
            Science: '#50e3c2',
            Business: '#f5a623',
            Sports: '#7ed321',
            Health: '#d0021b',
            Entertainment: '#9013fe',
            Politics: '#f8e71c',
        };
        const color = colors[category] || '#cccccc';
        const text = category ? category[0].toUpperCase() : 'N';
        // SVG placeholder with colored background and category initial
        const svg = `<svg width='120' height='80' xmlns='http://www.w3.org/2000/svg'><rect width='120' height='80' fill='${color}'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='40' fill='#fff' font-family='Arial'>${text}</text></svg>`;
        return `data:image/svg+xml;base64,${btoa(svg)}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new App();
});