from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime

app = FastAPI()

active_connections = []

chat_history = []

# Вместо списка active_connections
rooms = {}
# Будет выглядит так: {"room1": [ws1, ws2], "secret_room":[ws3]}

# История тоже должна стать раздельной!
rooms_history = {} 
# {"room1": [{"text": "привет", ...}], "secret_room": []}

@app.websocket("/ws/{room_name}")
async def Pinguin_chat(websocket: WebSocket, room_name: str):
    
    await websocket.accept()
    
    if room_name not in rooms:
        rooms[room_name] = []
        rooms_history[room_name] = []

    rooms[room_name].append(websocket)

    active_connections.append(websocket)
    
    print("A someone get in")

    async def json_message(type_of, name, text, color, content):
        
        time_now = datetime.now().strftime("%H:%M")
        time = time_now

        json_array = {
            "type": type_of, 
            "username": name, 
            "text": text, 
            "color": color, 
            "content": content, 
            "time": time # Вот оно, свежее время!
        }

        rooms_history[room_name].append(json_array)
        if len(rooms_history[room_name]) > 20:
            rooms_history[room_name].pop(0)

        for send_json_message in active_connections:
            if send_json_message != None or send_json_message != "undefined": 
                await send_json_message.send_json(json_array)
        
        chat_history.append(json_array)
        if len(chat_history) > 20:
                chat_history.pop(0)
        

    for old_msg in chat_history:
        await websocket.send_json(old_msg)
        
    try:
        # await json_message("system", "", "", "green", "New penguin")

        while True:
            json_data = await websocket.receive_json()
            username = json_data.get("username")
            text = json_data.get("text")

            if json_data.get("type") == "typing":
                for connection in active_connections:
                    if connection != websocket:
                        await connection.send_json({"type": "typing", "username": username})
            else:
                await json_message("user", username, text, "black", "") 

    except WebSocketDisconnect:
        
        rooms[room_name].remove(websocket)
        # await json_message("system", "", "", "red", "Penguin leave")


        print("A someone get out")