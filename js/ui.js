export class UI {
    init() {
        this.modalOverlay = document.getElementById('modalOverlay');
        this.modalContent = document.getElementById('modalContent');
        this.modalBody = document.getElementById('modalBody');
        this.toastContainer = document.getElementById('toast');
        this.loadingIndicator = document.getElementById('loadingIndicator');

        document.getElementById('modalClose').addEventListener('click', () => this.hideModal());
        document.getElementById('modalOverlay').addEventListener('click', (e) => {
            if (e.target.id === 'modalOverlay') this.hideModal();
        });

        // Initialize theme
        this.initTheme();
    }

    initTheme() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) {
            console.warn('Theme toggle button not found');
            return;
        }
        
        const savedTheme = localStorage.getItem('theme') || 'light';
        
        // Set initial theme
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
        
        // Remove any existing event listeners to prevent duplicates
        themeToggle.removeEventListener('click', this.handleThemeToggle);
        
        // Add event listener with proper binding
        this.handleThemeToggle = this.handleThemeToggle.bind(this);
        themeToggle.addEventListener('click', this.handleThemeToggle);
    }

    handleThemeToggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeIcon(newTheme);
        
        console.log('Theme switched to:', newTheme); // Debug log
    }

    updateThemeIcon(theme) {
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle.querySelector('i');
        
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            themeToggle.title = 'Switch to light mode';
        } else {
            icon.className = 'fas fa-moon';
            themeToggle.title = 'Switch to dark mode';
        }
    }

    createArticleCard(article) {
        const card = document.createElement('div');
        card.className = 'article-card';
        
        // Generate category-specific placeholder images
        const getCategoryPlaceholder = (category) => {
            const categoryMap = {
                'Technology': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=200&fit=crop',
                'Business': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=200&fit=crop',
                'Sports': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=200&fit=crop',
                'Science': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=200&fit=crop',
                'Health': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=400&h=200&fit=crop',
                'Entertainment': 'https://images.unsplash.com/photo-1489599830792-4b8b0f4b0b0b?w=400&h=200&fit=crop',
                'Politics': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=200&fit=crop',
                'Weather': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=400&h=200&fit=crop',
                'General': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=200&fit=crop'
            };
            return categoryMap[category] || categoryMap['General'];
        };
        
        const placeholderUrl = getCategoryPlaceholder(article.category);
        
        card.innerHTML = `
            <div class="article-card-image">
                <img src="${article.image_url || placeholderUrl}" 
                     alt="${article.title}"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                <div class="placeholder-image" style="display: none;">
                    ${article.category || 'News'}
                </div>
            </div>
            <div class="article-card-content">
                <span class="article-card-category">${article.category || 'General'}</span>
                <h3 class="article-card-title">${article.title}</h3>
                <p class="article-card-summary">${article.content || 'No summary available.'}</p>
                <div class="article-card-footer">
                    <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="read-more">Read More</a>
                    <span class="article-card-source">${article.source_name || ''}</span>
                    <button class="save-article-btn" data-url="${article.url}">
                        <i class="far fa-bookmark"></i>
                    </button>
                </div>
            </div>
        `;
        return card;
    }

    showLoading() {
        document.getElementById('loadingIndicator').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingIndicator').classList.add('hidden');
    }

    renderArticles(articles, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        if (articles && articles.length > 0) {
            articles.forEach(article => {
                const card = this.createArticleCard(article);
                container.appendChild(card);
            });
        } else {
            container.innerHTML = '<p>No articles found.</p>';
        }
    }

    updateView(viewId) {
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById(viewId).classList.add('active');
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.view === viewId.replace('View', ''));
        });
    }

    showModal(content) {
        this.modalBody.innerHTML = content;
        this.modalOverlay.classList.remove('hidden');
    }

    hideModal() {
        this.modalOverlay.classList.add('hidden');
        this.modalBody.innerHTML = '';
    }

    showToast(message, type = 'info') {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        this.toastContainer.innerHTML = `
            <i class="${icons[type]} toast-icon"></i>
            <span>${message}</span>
        `;
        this.toastContainer.className = `toast show ${type}`;
        
        setTimeout(() => {
            this.toastContainer.className = this.toastContainer.className.replace('show', '');
        }, 4000);
    }

    showNotificationBanner(message, onRefresh) {
        const banner = document.getElementById('notificationBanner');
        if (!banner) return;

        banner.innerHTML = `
            <span>${message}</span>
            <button class="refresh-btn">Refresh</button>
        `;
        banner.classList.remove('hidden');

        const refreshButton = banner.querySelector('.refresh-btn');
        refreshButton.addEventListener('click', () => {
            onRefresh();
            banner.classList.add('hidden');
        });
    }

    updateUIForUser(username) {
        document.getElementById('userToggle').innerHTML = `<i class="fas fa-user"></i> ${username}`;
        document.getElementById('loginBtn').classList.add('hidden');
        document.getElementById('registerBtn').classList.add('hidden');
        document.getElementById('logoutBtn').classList.remove('hidden');
        document.getElementById('profileLink').classList.remove('hidden');
        document.getElementById('managePreferences').classList.remove('hidden');
    }

    updateUIForGuest() {
        document.getElementById('userToggle').innerHTML = `<i class="fas fa-user"></i>`;
        document.getElementById('loginBtn').classList.remove('hidden');
        document.getElementById('registerBtn').classList.remove('hidden');
        document.getElementById('logoutBtn').classList.add('hidden');
        document.getElementById('profileLink').classList.add('hidden');
        document.getElementById('managePreferences').classList.add('hidden');
    }

    renderFollowedTopics(topics, unfollowCallback) {
        const list = document.getElementById('followedTopicsList');
        list.innerHTML = '';
        if (topics.length === 0) {
            list.innerHTML = '<li>You are not following any topics.</li>';
        } else {
            topics.forEach(topic => {
                const li = document.createElement('li');
                li.textContent = topic.topic;
                const button = document.createElement('button');
                button.textContent = 'Unfollow';
                button.onclick = () => unfollowCallback(topic.topic);
                li.appendChild(button);
                list.appendChild(li);
            });
        }
    }

    renderFollowedOutlets(outlets, unfollowCallback) {
        const list = document.getElementById('followedOutletsList');
        list.innerHTML = '';
        if (outlets.length === 0) {
            list.innerHTML = '<li>You are not following any outlets.</li>';
        } else {
            outlets.forEach(outlet => {
                const li = document.createElement('li');
                li.textContent = outlet.outlet;
                const button = document.createElement('button');
                button.textContent = 'Unfollow';
                button.onclick = () => unfollowCallback(outlet.outlet);
                li.appendChild(button);
                list.appendChild(li);
            });
        }
    }

    renderPreferences(topics, outlets) {
        this.renderFollowedTopics(topics, (topic) => {
            // This will be handled by the app
            window.app.unfollowTopic(topic);
        });
        this.renderFollowedOutlets(outlets, (outlet) => {
            // This will be handled by the app
            window.app.unfollowOutlet(outlet);
        });
    }

    // Enhanced Modal Functions
    showLoginModal() {
        this.modalBody.innerHTML = `
            <div class="modal-header">
                <h2><i class="fas fa-sign-in-alt"></i> Login to News Nest</h2>
            </div>
            <div class="modal-body">
                <form id="loginForm" class="auth-form">
                    <div class="form-group">
                        <label for="loginEmail">
                            <i class="fas fa-envelope"></i> Email Address
                        </label>
                        <input 
                            type="email" 
                            id="loginEmail" 
                            name="email" 
                            placeholder="Enter your email address"
                            required
                            pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
                            title="Please enter a valid email address"
                        >
                        <div class="input-feedback"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="loginPassword">
                            <i class="fas fa-lock"></i> Password
                        </label>
                        <div class="password-input-container">
                            <input 
                                type="password" 
                                id="loginPassword" 
                                name="password" 
                                placeholder="Enter your password"
                                required
                                minlength="6"
                                title="Password must be at least 6 characters"
                            >
                            <button type="button" class="password-toggle" onclick="this.previousElementSibling.type = this.previousElementSibling.type === 'password' ? 'text' : 'password'; this.innerHTML = this.previousElementSibling.type === 'password' ? '<i class=\\'fas fa-eye\\'></i>' : '<i class=\\'fas fa-eye-slash\\'></i>'">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                        <div class="input-feedback"></div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').classList.remove('show')">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </button>
                    </div>
                </form>
                
                <div class="auth-footer">
                    <p>Don't have an account? <a href="#" onclick="app.ui.showRegisterModal(); return false;">Register here</a></p>
                </div>
            </div>
        `;
        
        this.showModal();
        this.setupFormValidation('loginForm');
    }

    showRegisterModal() {
        this.modalBody.innerHTML = `
            <div class="modal-header">
                <h2><i class="fas fa-user-plus"></i> Create Account</h2>
            </div>
            <div class="modal-body">
                <form id="registerForm" class="auth-form">
                    <div class="form-group">
                        <label for="registerUsername">
                            <i class="fas fa-user"></i> Username
                        </label>
                        <input 
                            type="text" 
                            id="registerUsername" 
                            name="username" 
                            placeholder="Choose a username"
                            required
                            minlength="3"
                            maxlength="30"
                            pattern="[a-zA-Z0-9_-]+"
                            title="Username can only contain letters, numbers, hyphens, and underscores"
                        >
                        <div class="input-feedback"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="registerEmail">
                            <i class="fas fa-envelope"></i> Email Address
                        </label>
                        <input 
                            type="email" 
                            id="registerEmail" 
                            name="email" 
                            placeholder="Enter your email address"
                            required
                            pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
                            title="Please enter a valid email address"
                        >
                        <div class="input-feedback"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="registerPassword">
                            <i class="fas fa-lock"></i> Password
                        </label>
                        <div class="password-input-container">
                            <input 
                                type="password" 
                                id="registerPassword" 
                                name="password" 
                                placeholder="Create a strong password"
                                required
                                minlength="8"
                                title="Password must be at least 8 characters"
                            >
                            <button type="button" class="password-toggle" onclick="this.previousElementSibling.type = this.previousElementSibling.type === 'password' ? 'text' : 'password'; this.innerHTML = this.previousElementSibling.type === 'password' ? '<i class=\\'fas fa-eye\\'></i>' : '<i class=\\'fas fa-eye-slash\\'></i>'">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                        <div class="password-strength" id="passwordStrength"></div>
                        <div class="input-feedback"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="confirmPassword">
                            <i class="fas fa-lock"></i> Confirm Password
                        </label>
                        <div class="password-input-container">
                            <input 
                                type="password" 
                                id="confirmPassword" 
                                name="confirmPassword" 
                                placeholder="Confirm your password"
                                required
                                title="Please confirm your password"
                            >
                            <button type="button" class="password-toggle" onclick="this.previousElementSibling.type = this.previousElementSibling.type === 'password' ? 'text' : 'password'; this.innerHTML = this.previousElementSibling.type === 'password' ? '<i class=\\'fas fa-eye\\'></i>' : '<i class=\\'fas fa-eye-slash\\'></i>'">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                        <div class="input-feedback"></div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').classList.remove('show')">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-user-plus"></i> Create Account
                        </button>
                    </div>
                </form>
                
                <div class="auth-footer">
                    <p>Already have an account? <a href="#" onclick="app.ui.showLoginModal(); return false;">Login here</a></p>
                </div>
            </div>
        `;
        
        this.showModal();
        this.setupFormValidation('registerForm');
        this.setupPasswordStrength('registerPassword');
    }

    setupFormValidation(formId) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        const inputs = form.querySelectorAll('input[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (this.validateForm(form)) {
                this.handleFormSubmit(form);
            }
        });
    }

    setupPasswordStrength(passwordId) {
        const passwordInput = document.getElementById(passwordId);
        const strengthIndicator = document.getElementById('passwordStrength');
        
        if (passwordInput && strengthIndicator) {
            passwordInput.addEventListener('input', () => {
                const password = passwordInput.value;
                const strength = this.calculatePasswordStrength(password);
                this.updatePasswordStrength(strengthIndicator, strength);
            });
        }
    }

    calculatePasswordStrength(password) {
        let score = 0;
        let feedback = [];
        
        if (password.length >= 8) score += 1;
        else feedback.push('At least 8 characters');
        
        if (/[a-z]/.test(password)) score += 1;
        else feedback.push('Lowercase letter');
        
        if (/[A-Z]/.test(password)) score += 1;
        else feedback.push('Uppercase letter');
        
        if (/[0-9]/.test(password)) score += 1;
        else feedback.push('Number');
        
        if (/[^A-Za-z0-9]/.test(password)) score += 1;
        else feedback.push('Special character');
        
        return { score, feedback };
    }

    updatePasswordStrength(indicator, strength) {
        const levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const colors = ['#ef4444', '#f59e0b', '#eab308', '#10b981', '#059669'];
        
        indicator.innerHTML = `
            <div class="strength-bar">
                <div class="strength-fill" style="width: ${(strength.score / 5) * 100}%; background-color: ${colors[strength.score - 1] || '#e5e7eb'}"></div>
            </div>
            <span class="strength-text" style="color: ${colors[strength.score - 1] || '#6b7280'}">
                ${levels[strength.score - 1] || 'Very Weak'}
            </span>
        `;
    }

    validateField(input) {
        const feedback = input.parentElement.querySelector('.input-feedback');
        let isValid = true;
        let message = '';
        
        // Check required
        if (input.required && !input.value.trim()) {
            isValid = false;
            message = 'This field is required';
        }
        
        // Check email pattern
        if (input.type === 'email' && input.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(input.value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            }
        }
        
        // Check password confirmation
        if (input.id === 'confirmPassword') {
            const password = document.getElementById('registerPassword');
            if (password && input.value !== password.value) {
                isValid = false;
                message = 'Passwords do not match';
            }
        }
        
        // Check pattern
        if (input.pattern && input.value) {
            const regex = new RegExp(input.pattern);
            if (!regex.test(input.value)) {
                isValid = false;
                message = input.title || 'Invalid format';
            }
        }
        
        this.showFieldFeedback(input, isValid, message);
        return isValid;
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    showFieldFeedback(input, isValid, message) {
        const feedback = input.parentElement.querySelector('.input-feedback');
        input.classList.toggle('error', !isValid);
        input.classList.toggle('success', isValid && input.value);
        
        if (feedback) {
            feedback.textContent = message;
            feedback.className = `input-feedback ${isValid ? 'success' : 'error'}`;
        }
    }

    clearFieldError(input) {
        const feedback = input.parentElement.querySelector('.input-feedback');
        input.classList.remove('error', 'success');
        if (feedback) {
            feedback.textContent = '';
            feedback.className = 'input-feedback';
        }
    }

    handleFormSubmit(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        if (form.id === 'loginForm') {
            window.app.auth.login(data.email, data.password);
        } else if (form.id === 'registerForm') {
            window.app.auth.register(data.username, data.email, data.password);
        }
    }
} 