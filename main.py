from fastapi import FastAPI
from fastapi.responses import FileResponse
from backend.modules.chat.router import router as chat_router

app = FastAPI(title="PyWebChat Монолит")

# Подключаем наш изолированный роутер чата
app.include_router(chat_router)

# Оставляем отдачу фронтенда из корня
@app.get("/")
async def get_main_page():
    return FileResponse("index.html")