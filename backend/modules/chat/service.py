from fastapi import WebSocket
from datetime import datetime

class ChatService:
    def __init__(self):
        # Храним комнаты и их активные websocket-сессии: {"room1": [ws1, ws2]}
        self.rooms = {}
        # Раздельная история для каждой комнаты: {"room1": [{"text": "привет", ...}]}
        self.chat_history = {}

    async def connect(self, websocket: WebSocket, user_room: str):
        """Регистрирует пингвина в комнате и отправляет ему старую историю этой комнаты"""
        await websocket.accept()
        
        # Если комнаты еще нет, создаем её структуру
        if user_room not in self.rooms:
            self.rooms[user_room] = []
            self.chat_history[user_room] = []
            
        self.rooms[user_room].append(websocket)
        print(f"A someone get in room: {user_room}")

        # Отправляем новому пингвину историю именно ЭТОЙ комнаты
        for old_msg in self.chat_history[user_room]:
            await websocket.send_json(old_msg)

    async def disconnect(self, websocket: WebSocket, user_room: str):
        """Удаляет пингвина из комнаты при отключении"""
        if user_room in self.rooms:
            if websocket in self.rooms[user_room]:
                self.rooms[user_room].remove(websocket)
        print(f"A someone get out from room: {user_room}")

    async def broadcast_message(self, user_room: str, type_of: str, name: str, text: str, color: str, content: str):
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
        self.chat_history[user_room].append(json_array)
        if len(self.chat_history[user_room]) > 20:
            self.chat_history[user_room].pop(0)

        # Рассылаем сообщение ТОЛЬКО пингвинам из этой комнаты
        if user_room in self.rooms:
            for connection in self.rooms[user_room]:
                print(f"send message {self.rooms[user_room]}")
                await connection.send_json(json_array)

    async def broadcast_typing(self, user_room: str, sender_websocket: WebSocket, username: str):
        """Рассылает статус печати всем в комнате, кроме самого печатающего"""
        if user_room in self.rooms:
            for connection in self.rooms[user_room]:
                if connection != sender_websocket:
                    await connection.send_json({"type": "typing", "username": username})

class RoomService:
    def __init__(self):
        self.user_rooms = {}

        self.connection = {}

        self.contact_list = {}

    async def connect(self, websocket: WebSocket, users_rooms: str):
        await websocket.accept()

        self.connection.setdefault(users_rooms, []).append(websocket)

        await websocket.send_json(self.contact_list)

    async def create_room(self, websocket: WebSocket, username: str, users_rooms: str):
        """Создаём и добавляем комнаты самих пользователей"""
        self.user_rooms["user"] = username
        self.user_rooms["users_rooms"] = users_rooms
        
        self.contact_list.setdefault("contact", []).append(users_rooms)

        try:    
            for socket in self.connection[username]:
                await socket.send_json(self.user_rooms)
        except:
            print("something is wrong")
            print(self.user_rooms)

    async def send_rooms(self, username: str):
        for send_lists in self.connection[username]:
            await send_lists.send_json(self.contact_list)

            print(self.contact_list)

# Создаем один экземпляр сервиса для всего приложения (Singleton)
chat_service = ChatService()
# Создаем экземпляр для сервиса по созданию комнта
room_service = RoomService()