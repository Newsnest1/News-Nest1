from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.websocket_manager import manager
from app.services.auth_service import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websockets"])

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None, description="JWT token for user authentication")
):
    user_id = None
    
    # Try to authenticate user if token is provided
    if token:
        try:
            # Create a mock request context for authentication
            from fastapi import Request
            from starlette.websockets import WebSocketState
            
            # Simple token validation (in production, you'd want more robust validation)
            from app.services import auth_service
            from jose import jwt
            from app import security
            
            try:
                payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
                username = payload.get("sub")
                if username:
                    # Get user from database
                    db = next(get_db())
                    from app import crud
                    user = crud.get_user_by_username(db, username)
                    if user:
                        user_id = user.id
                        logger.info(f"User {username} (ID: {user_id}) connected to WebSocket")
                    db.close()
            except Exception as e:
                logger.warning(f"Invalid token in WebSocket connection: {e}")
        except Exception as e:
            logger.warning(f"Error authenticating WebSocket user: {e}")
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket client disconnected. User ID: {user_id}") 