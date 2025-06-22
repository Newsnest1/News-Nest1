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
        
        this.init();
    }
    
    async init() {
        try {
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
            this.performSearch();
        });
        
        document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
        
        // Refresh feed
        document.getElementById('refreshFeed')?.addEventListener('click', () => {
            this.loadView(this.currentView);
        });
        
        // Category filter
        document.getElementById('categoryFilter')?.addEventListener('change', (e) => {
            this.filterByCategory(e.target.value);
        });
        
        // Article saving
        document.getElementById('viewContainer').addEventListener('click', (e) => {
            if (e.target.closest('.save-article-btn')) {
                const button = e.target.closest('.save-article-btn');
                const url = button.dataset.url;
                this.toggleSaveArticle(url, button);
            }
        });

        // Preferences
        document.getElementById('managePreferences')?.addEventListener('click', () => {
            this.router.navigate('preferences');
        });
        
        document.getElementById('followTopic')?.addEventListener('click', () => {
            this.followTopic();
        });
        
        document.getElementById('followOutlet')?.addEventListener('click', () => {
            this.followOutlet();
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
        const articles = await this.api.getFeed();
        this.ui.renderArticles(articles, 'articlesGrid');
        await this.populateCategoryDropdown();
    }
    
    async loadPersonalizedFeed() {
        const articles = await this.api.getPersonalizedFeed();
        this.ui.renderArticles(articles, 'personalizedGrid');
    }
    
    async loadSearchView(query = '') {
        if (query) {
            await this.performSearch(query);
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
        const topics = await this.api.getFollowedTopics();
        const outlets = await this.api.getFollowedOutlets();
        this.ui.renderPreferences(topics, outlets);
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
    
    async performSearch(query = '') {
        const searchQuery = query || document.getElementById('searchInput').value.trim();
        if (!searchQuery) return;
        
        try {
            this.ui.showLoading();
            const results = await this.api.searchArticles(searchQuery);
            this.ui.renderArticles(results, 'searchResults');
            this.router.navigate('search');
        } catch (error) {
            console.error('Search failed:', error);
            this.ui.showToast('Search failed', 'error');
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
    
    async toggleSaveArticle(url, button) {
        if (!this.currentUser) {
            this.ui.showToast('Please login to save articles', 'warning');
            return;
        }

        try {
            const isSaved = button.classList.contains('saved');
            if (isSaved) {
                await this.api.unsaveArticle(url);
                button.classList.remove('saved');
                button.innerHTML = '<i class="far fa-bookmark"></i>';
                this.ui.showToast('Article removed from saved', 'success');
            } else {
                await this.api.saveArticle(url);
                button.classList.add('saved');
                button.innerHTML = '<i class="fas fa-bookmark"></i>';
                this.ui.showToast('Article saved!', 'success');
            }
        } catch (error) {
            this.ui.showToast(error.message, 'error');
        }
    }
    
    async followTopic() {
        const input = document.getElementById('newTopicInput');
        const topic = input.value.trim();
        if (!topic) return;
        
        try {
            await this.api.followTopic(topic);
            input.value = '';
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
        const input = document.getElementById('newOutletInput');
        const outlet = input.value.trim();
        if (!outlet) return;

        try {
            await this.api.followOutlet(outlet);
            input.value = '';
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
            <h2>Login</h2>
            <input type="text" id="loginUsername" placeholder="Username">
            <input type="password" id="loginPassword" placeholder="Password">
            <button id="submitLogin">Login</button>
        `;
        this.ui.showModal(content);
        document.getElementById('submitLogin').addEventListener('click', () => this.login());
    }
    
    showRegisterModal() {
        const content = `
            <h2>Register</h2>
            <input type="text" id="registerUsername" placeholder="Username">
            <input type="email" id="registerEmail" placeholder="Email">
            <input type="password" id="registerPassword" placeholder="Password">
            <button id="submitRegister">Register</button>
        `;
        this.ui.showModal(content);
        document.getElementById('submitRegister').addEventListener('click', () => this.register());
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
            const username = document.getElementById('registerUsername').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;

            await this.auth.register(username, email, password);
            await this.auth.login(username, password); // Auto-login after register
            this.currentUser = await this.auth.checkAuthStatus();

            this.updateUIForUser();
            this.initWebSocket();
            this.ui.hideModal();
            this.router.navigate('feed');

        } catch (error) {
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
        this.websocket = new WebSocket(`ws://localhost:8001/v1/ws/${token}`);
        this.websocket.connect(
            (data) => this.handleWebSocketMessage(data),
            () => this.ui.showToast('WebSocket connection lost. Please refresh.', 'error')
        );
    }
    
    disconnectWebSocket() {
        if (this.websocket) {
            this.websocket.disconnect();
            this.websocket = null;
        }
    }
    
    handleWebSocketMessage(data) {
        if (data.type === 'new_article') {
            this.ui.showToast(`New article: ${data.article.title}`);
            if (this.currentView === 'feed') {
                this.loadFeed();
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new App();
});