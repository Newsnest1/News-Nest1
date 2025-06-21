import asyncio
import websockets
import json
import requests
import signal
import sys

# Global flag to control the WebSocket loop
running = True

def signal_handler(signum, frame):
    global running
    print("\nStopping WebSocket test...")
    running = False

# Set up signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

async def test_websocket():
    # Connect to WebSocket with authentication token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc1MDU0OTU2Nn0.TJHMg5UIicsO0kNuMN8lvhZPZrCyvlY6fcLGYRJ1ZUk"
    uri = f"ws://localhost:8001/ws?token={token}"
    
    print("Connecting to WebSocket...")
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected! Waiting for notifications...")
            print("💡 Press Ctrl+C to stop and clean up test user")
            
            # Trigger test notifications immediately
            print("🚀 Triggering test notifications...")
            trigger_test_notifications(token)
            
            # Keep connection alive and listen for messages
            while running:
                try:
                    # Add timeout to prevent indefinite waiting
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"📨 Received notification: {message}")
                    
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
                        
                except asyncio.TimeoutError:
                    # Timeout is expected, just continue
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("❌ WebSocket connection closed")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ Failed to connect: {e}")

def delete_test_user(token):
    try:
        url = "http://localhost:8001/v1/users/me"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(url, headers=headers)
        print(f"🧹 Cleanup: {response.json()}")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def trigger_test_notifications(token):
    try:
        url = "http://localhost:8001/v1/feed/test-notifications"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(url, headers=headers)
        print(f"🚀 Triggered test notifications: {response.json()}")
    except Exception as e:
        print(f"❌ Error triggering notifications: {e}")

if __name__ == "__main__":
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc1MDU0OTU2Nn0.TJHMg5UIicsO0kNuMN8lvhZPZrCyvlY6fcLGYRJ1ZUk"
    
    try:
        # Start WebSocket connection
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    finally:
        # Clean up: delete the test user
        print("🧹 Cleaning up test user...")
        delete_test_user(token) 