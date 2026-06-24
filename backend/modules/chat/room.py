from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.modules.chat.service import room_service


Room_router = APIRouter( tags=['Room'])

@Room_router.websocket("/ws/room/{user_room}")
async def creating_rooms(websocket: WebSocket, user_room: str):

    await room_service.connect(websocket, user_room)
    

    try:
        while True:
            get_created_room = await websocket.receive_json()
            get_user_name = get_created_room['username']
            get_user_rooms = get_created_room['new_user_room']

            # Создаём для пользователя комнату где он может начать общение после клика
            await room_service.create_room(websocket, get_user_name, get_user_rooms)
            
            await room_service.connect_user_to_room(user_room, websocket)
            
            # room_service.disconnect_user_from_room(user_room, websocket)

            room_service.room_get_chat_json(user_room)
            # await room_service.send_rooms(get_user_name)
            
            
    except WebSocketDisconnect:
        print("Disconect")

