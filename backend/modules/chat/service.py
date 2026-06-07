from fastapi import WebSocket
from datetime import datetime

class ChatService:
    def __init__(self):
        # Храним комнаты и их активные websocket-сессии: {"room1": [ws1, ws2]}
        self.rooms = {}
        # Раздельная история для каждой комнаты: {"room1": [{"text": "привет", ...}]}
        self.chat_history = {}

        self.room_connections = {}

    async def connect(self, websocket: WebSocket, room_name: str):
        """Регистрирует пингвина в комнате и отправляет ему старую историю этой комнаты"""
        await websocket.accept()
        
        # Если комнаты еще нет, создаем её структуру
        if room_name not in self.rooms:
            self.rooms[room_name] = []
            self.chat_history[room_name] = []
            
        self.rooms[room_name].append(websocket)
        print(f"A someone get in room: {room_name}")

        print(self.chat_history)

        # Отправляем новому пингвину историю именно ЭТОЙ комнаты
        for old_msg in self.chat_history[room_name]:
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
        self.chat_history[room_name].append(json_array)
        
        room_service.get_msg.setdefault(room_name, []).append(json_array)
        room_service.room_get_chat_json(room_name)

        if len(self.chat_history[room_name]) > 20:
            self.chat_history[room_name].pop(0)

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

class RoomService:
    def __init__(self):
        self.user_rooms = {}

        self.connection = {}

        self.contact_list = {}

        self.get_msg = {}

    async def connect(self, websocket: WebSocket, room_name: str):
        await websocket.accept()

        self.connection.setdefault(room_name, []).append(websocket)
        print(f"Имя комнаты: {room_name}")
        await websocket.send_json(self.contact_list)

    async def create_room(self, websocket: WebSocket, username: str, room_name: str):
        """Создаём и добавляем комнаты самих пользователей"""
        self.user_rooms["user"] = username
        self.user_rooms["users_rooms"] = room_name
        
        self.contact_list.setdefault("contact", []).append(room_name)

        chat_service.room_connections.setdefault("new_room", []).append(room_name)

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

    async def connect_user_to_room(self, room_name: str, websocket: WebSocket):
        """Делаем подключение к комнате для пользователя"""
        if room_name in self.connection:
            self.connection[room_name].append(websocket)
            print(f"[БЭКЕНД] Юзер подключился к комнате {room_name}")
    
    def disconnect_user_from_room(self, room_name: str, websocket: WebSocket):
        """Удаляет сокет при отключении"""
        if room_name in self.connection:
            self.connection[room_name].remove(websocket)
            print(f"[БЭКЕНД] Юзер покинул комнату {room_name}")

    def room_get_chat_json(self, room_name: str):

        print(f"получены сообщение из {room_name}: {self.get_msg}")

# Создаем экземпляр для сервиса по созданию комнта
room_service = RoomService()