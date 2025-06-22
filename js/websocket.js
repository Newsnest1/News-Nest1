export class WebSocket {
    constructor(userId) {
        this.userId = userId;
        this.socket = null;
        this.onMessage = null;
        this.connect();
    }

    connect() {
        this.socket = new window.WebSocket(`ws://localhost:8001/ws/${this.userId}`);
        this.socket.onmessage = (event) => {
            if (this.onMessage) {
                this.onMessage(event.data);
            }
        };
        this.socket.onclose = () => {
            // Optionally, try to reconnect after a delay
        };
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
} 