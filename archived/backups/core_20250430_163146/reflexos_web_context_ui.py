
import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from reflexos_memory_core import load_memory_context, save_memory

app = FastAPI()
USER_ID = "user_a"
CURRENT_DIR = os.path.dirname(__file__)


class UserInput(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(os.path.join(CURRENT_DIR, "index.html"))


@app.post("/chat")
async def chat(input: UserInput):
    memory_stack = load_memory_context(USER_ID)
    messages = memory_stack + [{"role": "user", "content": input.message}]
    save_memory(input.message, USER_ID)
    reply = f"🤖 หนูจำได้ว่าคุณเคยพูดว่า: “{messages[-2]['content'][:60]}...”" if len(
        messages) > 1 else "🤖 นี่คือข้อความแรกของคุณค่ะ"
    return {"reply": reply}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
