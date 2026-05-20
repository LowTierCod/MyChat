from fastapi import WebSocket
from datetime import datetime

class ChatService:
    def __init__(self):
        # Храним комнаты и их активные websocket-сессии: {"room1": [ws1, ws2]}
        self.rooms = {}
        # Раздельная история для каждой комнаты: {"room1": [{"text": "привет", ...}]}
        self.rooms_history = {}

    async def connect(self, websocket: WebSocket, room_name: str):
        """Регистрирует пингвина в комнате и отправляет ему старую историю этой комнаты"""
        await websocket.accept()
        
        # Если комнаты еще нет, создаем её структуру
        if room_name not in self.rooms:
            self.rooms[room_name] = []
            self.rooms_history[room_name] = []
            
        self.rooms[room_name].append(websocket)
        print(f"A someone get in room: {room_name}")

        # Отправляем новому пингвину историю именно ЭТОЙ комнаты
        for old_msg in self.rooms_history[room_name]:
            await websocket.send_json(old_msg)

    async def disconnect(self, websocket: WebSocket, room_name: str):
        """Удаляет пингвина из комнаты при отключении"""
        if room_name in self.rooms:
            if websocket in self.rooms[room_name]:
                self.rooms[room_name].remove(websocket)
        print(f"A someone get out from room: {room_name}")

    async def broadcast_message(self, room_name: str, type_of: str, name: str, text: str, color: str, content: str):
        """Формирует JSON-сообщение, сохраняет в историю комнаты и рассылает всем внутри нее"""
        time_now = datetime.now().strftime("%H:%M")

        json_array = {
            "type": type_of, 
            "username": name, 
            "text": text, 
            "color": color, 
            "content": content, 
            "time": time_now
        }

        # Сохраняем в историю конкретной комнаты (держим лимит 20 сообщений)
        self.rooms_history[room_name].append(json_array)
        if len(self.rooms_history[room_name]) > 20:
            self.rooms_history[room_name].pop(0)

        # Рассылаем сообщение ТОЛЬКО пингвинам из этой комнаты
        if room_name in self.rooms:
            for connection in self.rooms[room_name]:
                await connection.send_json(json_array)

    async def broadcast_typing(self, room_name: str, sender_websocket: WebSocket, username: str):
        """Рассылает статус печати всем в комнате, кроме самого печатающего"""
        if room_name in self.rooms:
            for connection in self.rooms[room_name]:
                if connection != sender_websocket:
                    await connection.send_json({"type": "typing", "username": username})

# Создаем один экземпляр сервиса для всего приложения (Singleton)
chat_service = ChatService()