export class Router {
    constructor() {
        this.app = null;
        this.views = ['feed', 'personalized', 'search', 'saved', 'profile', 'preferences'];
    }

    init(app) {
        this.app = app;
        this.navigate('feed');
    }

    navigate(viewName) {
        this.views.forEach(view => {
            const el = document.getElementById(view + 'View');
            if (el) {
                el.classList.toggle('active', view === viewName);
            }
        });
        // Highlight nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.view === viewName);
        });
        // Load the view in the app
        if (this.app) {
            this.app.loadView(viewName);
        }
    }
} 