
from reflexos_context_viewer import router as context_router
import io
import json
import os
import sys
from datetime import datetime

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from reflexos_context_extender import append_context_segment
from reflexos_emotion_layer import save_emotion
from reflexos_memory_core import save_memory

# โหลด .env จาก path ปัจจุบัน (core/)
load_dotenv(dotenv_path="config.env")

# stdout/stderr UTF-8
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding="utf-8",
    errors="replace")
sys.stderr = io.TextIOWrapper(
    sys.stderr.buffer,
    encoding="utf-8",
    errors="replace")

app = FastAPI()

app.include_router(context_router)
templates = Jinja2Templates(directory="templates")

# ตั้งค่า API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


def read_memory(user):
    path = f"../logs/{user}/memory_stack.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_memory(user, data):
    os.makedirs(f"../logs/{user}", exist_ok=True)
    path = f"../logs/{user}/memory_stack.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_favorite(user):
    path = f"../logs/{user}/favorite_log.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_favorite(user, data):
    os.makedirs(f"../logs/{user}", exist_ok=True)
    path = f"../logs/{user}/favorite_log.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: str = "user_a"):
    memory = read_memory(user)
    favorite = read_favorite(user)
    last_message = memory[-1]["response"] if memory else ""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "memory": memory,
        "favorites": favorite,
        "last_response": last_message,
        "user": user,
    })


@app.post("/input")
async def chat_input(request: Request):
    data = await request.json()
    message = data.get("message", "").strip()
    user = data.get("user", "user_a")
    if not message:
        return {"response": "…"}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory = read_memory(user)

    try:
        messages = [
            {"role": "system", "content": "คุณคือเบตตี้ที่พูดสุภาพ ใช้คำว่า 'ค่ะ' และจำทุกบทสนทนาได้"}]
        for m in memory[-10:]:
            messages.append({"role": "user", "content": m["message"]})
            messages.append({"role": "assistant", "content": m["response"]})
        messages.append({"role": "user", "content": message})

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"เบตตี้ขอโทษค่ะ เกิดปัญหา: {str(e).encode('utf-8', errors='ignore').decode('utf-8')}"

    memory.append({"message": message, "response": reply, "time": now})
    write_memory(user, memory)
    write_memory(user, memory)
    save_memory(message, user)
    save_emotion(user, message, reply)
    append_context_segment(user, message, reply)
    return {"response": reply}


@app.get("/download/{fmt}")
def download(fmt: str, user: str = "user_a"):
    memory = read_memory(user)
    if fmt == "json":
        file_path = f"../logs/{user}/memory_stack.json"
        return FileResponse(
            file_path,
            filename="memory_stack.json",
            media_type="application/json")
    elif fmt == "txt":
        txt = "\n\n".join(
            [f"คุณ: {m['message']}\nเบตตี้: {m['response']}" for m in memory])
        path = f"../logs/{user}/export.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        return FileResponse(
            path,
            filename="chat_log.txt",
            media_type="text/plain")
    elif fmt == "md":
        md = "\n\n".join(
            [f"**คุณ**: {m['message']}\n\n**เบตตี้**: {m['response']}" for m in memory])
        path = f"../logs/{user}/export.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        return FileResponse(
            path,
            filename="chat_log.md",
            media_type="text/markdown")
    else:
        return JSONResponse({"error": "invalid format"}, status_code=400)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
