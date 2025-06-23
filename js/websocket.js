export class WebSocketManager {
    constructor(token) {
        this.token = token;
        this.socket = null;
        this.onMessage = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectInterval = 1000; // Start with 1 second
    }

    connect() {
        if (!this.token) {
            console.error("WebSocket connection requires a token.");
            return;
        }
        
        const wsUrl = `ws://localhost:8001/v1/ws?token=${encodeURIComponent(this.token)}`;
        this.socket = new window.WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log('WebSocket connection established');
            this.reconnectAttempts = 0;
            this.reconnectInterval = 1000;
        };
        
        this.socket.onmessage = (event) => {
            if (this.onMessage) {
                try {
                    const data = JSON.parse(event.data);
                    this.onMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            }
        };
        
        this.socket.onclose = (event) => {
            console.log(`WebSocket connection closed. Code: ${event.code}`);
            if (event.code !== 1000) { // Don't reconnect on normal close
                this.scheduleReconnect();
            }
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            // onclose will be called next, which will handle reconnection
        };
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const backoffTime = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
            console.log(`WebSocket disconnected. Attempting to reconnect in ${backoffTime / 1000}s...`);
            
            setTimeout(() => {
                this.connect();
            }, backoffTime);
        } else {
            console.error('WebSocket max reconnect attempts reached.');
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close(1000, "User disconnected");
            this.socket = null;
        }
    }
} 