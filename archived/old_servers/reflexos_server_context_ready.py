
import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from reflexos_memory_core import (load_memory_context,  # memory engine
                                  save_memory)

app = FastAPI()
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "memory")
USER_ID = "user_a"


class UserInput(BaseModel):
    message: str


def mock_gpt_response(context):
    # ✅ จำลองการเรียก GPT ที่ใช้ context
    last = context[-1]["content"] if context else "ไม่มีคำถาม"
    return f"🤖 จำได้ว่าคุณเคยพูดว่า: '{last[:50]}' ... (ตัวอย่าง)"


@app.post("/chat")
async def chat(input: UserInput):
    # ➊ load memory stack ของ user
    memory_stack = load_memory_context(USER_ID)

    # ➋ แปลงเป็น message format ของ GPT
    messages = memory_stack + [{"role": "user", "content": input.message}]

    # ➌ save memory เข้า stack ใหม่
    save_memory(input.message, USER_ID)

    # ➍ ตอบแบบ mock ที่สะท้อน context
    reply = mock_gpt_response(messages)
    return {"reply": reply}

if __name__ == "__main__":
    uvicorn.run("reflexos_server_context_ready:app", host="0.0.0.0", port=5000)
