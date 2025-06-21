import asyncio
import websockets
import json

async def test_websocket():
    # Connect to WebSocket with authentication token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc1MDU0OTU2Nn0.TJHMg5UIicsO0kNuMN8lvhZPZrCyvlY6fcLGYRJ1ZUk"
    uri = f"ws://localhost:8001/ws?token={token}"
    
    print("Connecting to WebSocket...")
    async with websockets.connect(uri) as websocket:
        print("Connected! Waiting for notifications...")
        
        # Keep connection alive and listen for messages
        while True:
            try:
                message = await websocket.recv()
                print(f"Received notification: {message}")
                
                # Parse the notification
                try:
                    notification = json.loads(message)
                    if notification.get("type") == "personalized_articles":
                        print(f"🎉 PERSONALIZED NOTIFICATION!")
                        print(f"   Message: {notification.get('message')}")
                        print(f"   Articles: {len(notification.get('articles', []))}")
                        for article in notification.get('articles', [])[:3]:  # Show first 3
                            print(f"   - {article.get('title')} ({article.get('source')})")
                    elif notification.get("type") == "new_articles":
                        print(f"📰 BROADCAST NOTIFICATION: {notification.get('message')}")
                except json.JSONDecodeError:
                    print(f"Raw message: {message}")
                    
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(test_websocket()) 