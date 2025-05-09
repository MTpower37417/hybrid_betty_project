
import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from reflexos_memory_core import load_memory_context, save_memory

app = FastAPI()
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "memory")
USER_ID = "user_a"


class UserInput(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def root():
    return '''
    <html>
        <head><title>Betty Memory Server</title></head>
        <body>
            <h2>✅ Server พร้อมใช้งานแล้ว</h2>
            <p>ส่ง POST มาที่ <code>/chat</code> พร้อมข้อความเพื่อทดสอบ memory context</p>
        </body>
    </html>
    '''


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
