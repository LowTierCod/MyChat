from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.modules.chat.chat import Chat_router as chat_router
from backend.modules.chat.room import Room_router as room_router
from backend.core.router import Core_router as core_router


app = FastAPI(title="PyWebChat Монолит")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(chat_router)
app.include_router(room_router)
app.include_router(core_router)

@app.get("/")
async def get_main_page():
    return FileResponse("frontend/index.html")

    # В main.py (или в твой core_router)

@app.get("/room")
async def get_room_page():
    # Возвращаем наш новый HTML-файл комнаты
    return FileResponse("frontend/room_page.html")