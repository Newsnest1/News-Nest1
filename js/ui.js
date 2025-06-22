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
        this.toastContainer.textContent = message;
        this.toastContainer.className = `toast show ${type}`;
        setTimeout(() => {
            this.toastContainer.className = this.toastContainer.className.replace('show', '');
        }, 3000);
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
} 