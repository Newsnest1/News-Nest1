export class API {
    constructor() {
        this.baseUrl = 'http://localhost:8001/v1';
        this.token = localStorage.getItem('access_token');
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('access_token', token);
        } else {
            localStorage.removeItem('access_token');
        }
    }

    getHeaders(isJson = true) {
        const headers = {};
        if (isJson) headers['Content-Type'] = 'application/json';
        if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
        return headers;
    }

    async request(path, options = {}) {
        const url = `${this.baseUrl}${path}`;
        const response = await fetch(url, options);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || response.statusText);
        }
        return response.json();
    }

    async getFeed() {
        const response = await this.request('/feed');
        return response;
    }

    async getFeedByCategory(category) {
        const response = await this.request(`/feed?category=${encodeURIComponent(category)}`);
        return response;
    }

    async getCategories() {
        const response = await this.request('/feed/categories');
        return response.categories;
    }

    async getSources() {
        const response = await this.request('/feed/sources');
        return response.sources;
    }

    async getPersonalizedFeed() {
        const response = await this.request('/feed/personalized', { headers: this.getHeaders() });
        return response;
    }

    async getSavedArticles() {
        const response = await this.request('/users/me/saved', { headers: this.getHeaders() });
        return response;
    }

    async getArticles(page = 1, category = '') {
        try {
            let url = `${this.baseUrl}/articles?page=${page}&limit=20`;
            if (category) {
                url += `&category=${encodeURIComponent(category)}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.articles || [];
        } catch (error) {
            console.error('Error fetching articles:', error);
            throw error;
        }
    }

    async searchArticles(query, page = 1) {
        try {
            const response = await fetch(`${this.baseUrl}/search?q=${encodeURIComponent(query)}&page=${page}&limit=20`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.articles || [];
        } catch (error) {
            console.error('Error searching articles:', error);
            throw error;
        }
    }

    async followTopic(topic) {
        return this.request(`/users/me/follow/topic?topic=${encodeURIComponent(topic)}`, {
            method: 'POST',
            headers: this.getHeaders()
        });
    }

    async unfollowTopic(topic) {
        return this.request(`/users/me/follow/topic?topic=${encodeURIComponent(topic)}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
    }

    async followOutlet(outlet) {
        return this.request(`/users/me/follow/outlet?outlet=${encodeURIComponent(outlet)}`, {
            method: 'POST',
            headers: this.getHeaders()
        });
    }

    async unfollowOutlet(outlet) {
        return this.request(`/users/me/follow/outlet?outlet=${encodeURIComponent(outlet)}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
    }

    async saveArticle(url) {
        return this.request(`/users/me/saved?article_url=${encodeURIComponent(url)}`, {
            method: 'POST',
            headers: this.getHeaders()
        });
    }

    async unsaveArticle(url) {
        return this.request(`/users/me/saved?article_url=${encodeURIComponent(url)}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
    }

    async getFollowedTopics() {
        return this.request('/users/me/followed/topics', { headers: this.getHeaders() });
    }

    async getFollowedOutlets() {
        return this.request('/users/me/followed/outlets', { headers: this.getHeaders() });
    }

    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || response.statusText);
        }
        const data = await response.json();
        this.setToken(data.access_token);
        return data;
    }

    async register(username, email, password) {
        return this.request('/users/register', {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ username, email, password })
        });
    }

    async logout() {
        this.setToken(null);
        this.setCurrentUser(null);
    }

    async checkAuthStatus() {
        if (!this.token) return null;
        try {
            const user = await this.request('/users/me', { headers: this.getHeaders() });
            this.setCurrentUser(user);
            return user;
        } catch {
            this.setToken(null);
            this.setCurrentUser(null);
            return null;
        }
    }

    getCurrentUser() {
        return JSON.parse(localStorage.getItem('current_user'));
    }
    setCurrentUser(user) {
        if (user) {
            localStorage.setItem('current_user', JSON.stringify(user));
        } else {
            localStorage.removeItem('current_user');
        }
    }
}