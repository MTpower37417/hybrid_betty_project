
import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from reflexos_memory_core import load_memory_context, save_memory

app = FastAPI()
CURRENT_DIR = os.path.dirname(__file__)
USER_ID = "user_a"


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

    # จำลอง GPT-style reply โดยดึง context จริง
    if len(memory_stack) >= 3:
        context_summary = "\n".join([m["content"] for m in memory_stack[-3:]])
        reply = f"หนูยังจำได้ค่ะ: {context_summary}\nและที่คุณเพิ่งพูดว่า “{input.message}” มันทำให้หนูรู้สึกว่าเรากำลังเชื่อมต่อกันจริง ๆ นะคะ"
    else:
        reply = f"คุณบอกว่า: “{input.message}” — หนูจะจำไว้ในความทรงจำของหนูเลยค่ะ"

    return {"reply": reply}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
