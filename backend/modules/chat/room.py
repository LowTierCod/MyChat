from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.modules.chat.service import room_service

Room_router = APIRouter(prefix="/room", tags=['Room'])

@Room_router.websocket("/ws/{user_room}")
async def creating_rooms(websocket: WebSocket, user_room: str):

    await room_service.connect(websocket, user_room)

    try:
        username = websocket.receive_json()
        
        room_service.create_room(websocket, username)
    except WebSocketDisconnect:
        print("Disconect")

