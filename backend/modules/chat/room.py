from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.modules.chat.service import room_service

Room_router = APIRouter( tags=['Room'])

@Room_router.websocket("/ws/room/{user_room}")
async def creating_rooms(websocket: WebSocket, user_room: str):

    await room_service.connect(websocket)
    print("room enviroment")
    try:
        username = await websocket.receive_json()
        
        room_service.create_room(websocket, user_room)

    except WebSocketDisconnect:
        print("Disconect")

