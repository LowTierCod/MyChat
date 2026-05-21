from fastapi import FastAPI
from fastapi.responses import FileResponse
from backend.modules.chat.router import Chat_router as chat_router
from backend.core.router import Core_router as core_router

app = FastAPI(title="PyWebChat Монолит")

app.include_router(chat_router)
app.include_router(core_router)

@app.get("/")
async def get_main_page():
    return FileResponse("index.html")