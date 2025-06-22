export class WebSocket {
    constructor(token) {
        this.token = token;
        this.socket = null;
        this.onMessage = null;
        this.onError = null;
        this.connect();
    }

    connect() {
        const wsUrl = `ws://localhost:8001/v1/ws?token=${encodeURIComponent(this.token)}`;
        this.socket = new window.WebSocket(wsUrl);
        
        this.socket.onmessage = (event) => {
            if (this.onMessage) {
                this.onMessage(event.data);
            }
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
            if (this.onError) {
                this.onError();
            }
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (this.onError) {
                this.onError();
            }
        };
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
} 