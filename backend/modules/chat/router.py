from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.modules.chat.service import chat_service

Chat_router = APIRouter(
    tags=["Chat"]
)

@Chat_router.websocket("/ws/chat/{user_room}")
async def Pinguin_chat(websocket: WebSocket, user_room: str):
    # 1. Подключаем пингвина к комнате
    await chat_service.connect(websocket, user_room)
    print("chat enviroment")
    try:
        # 2. Слушаем сообщения от клиента в бесконечном цикле
        while True:
            json_data = await websocket.receive_json()
            username = json_data.get("username")
            text = json_data.get("text")
            msg_type = json_data.get("type")

            if msg_type == "typing":
                # Передаем сервису логику "кто-то печатает"
                await chat_service.broadcast_typing(user_room, websocket, username)
            else:
                # Передаем сервису отправку обычного сообщения
                await chat_service.broadcast_message(user_room, "user", username, text+"fff", "black", "") 
            

    except WebSocketDisconnect:
        # 3. Если пингвин отвалился — чистим списки
        await chat_service.disconnect(websocket, user_room)



# @Chat_router.websocket("/ws/chat")
# async def Pinguin_chat(websocket: WebSocket): # Оставили ТОЛЬКО websocket
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # временно просто печатаем в консоль сервера, что клиент что-то прислал
#             print(f"Получили: {data}") 
#     except Exception as e:
#         print(f"Отключение или ошибка: {e}")