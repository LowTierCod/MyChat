from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.modules.chat.service import room_service

Room_router = APIRouter( tags=['Room'])

@Room_router.websocket("/ws/room/{user_room}")
async def creating_rooms(websocket: WebSocket, user_room: str):

    await room_service.connect(websocket)
    

    try:
        room_list = []

        get_created_room = await websocket.receive_json()
        get_user_name = get_created_room['userName']
        get_user_rooms = get_created_room['new_user_room']
        room_list.append(get_user_rooms)

        await room_service.create_room(websocket, get_user_name, room_list)
        
        print(user_room)

        print(f"get json message in room service, thats message: {get_user_rooms}")
    except WebSocketDisconnect:
        print("Disconect")

