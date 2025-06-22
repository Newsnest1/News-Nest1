export class Auth {
    constructor(api) {
        this.api = api;
        this.currentUser = null;
    }

    async login(username, password) {
        const data = await this.api.login(username, password);
        const user = await this.api.checkAuthStatus();
        this.currentUser = user;
        this.api.setCurrentUser(user);
        return user;
    }

    async register(username, email, password) {
        return this.api.register(username, email, password);
    }

    async logout() {
        await this.api.logout();
        this.currentUser = null;
        this.api.setCurrentUser(null);
    }

    async checkAuthStatus() {
        const user = await this.api.checkAuthStatus();
        this.currentUser = user;
        this.api.setCurrentUser(user);
        return user;
    }

    getCurrentUser() {
        if (this.currentUser) return this.currentUser;
        return this.api.getCurrentUser();
    }
} 