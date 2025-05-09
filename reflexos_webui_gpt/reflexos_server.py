import openai
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

openai.api_key = "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"

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/input")
async def input_text(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        if not message:
            return JSONResponse(
                status_code=400, content={
                    "error": "Message field missing"})

        gpt_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "คุณคือเบตตี้ที่มีหัวใจ อ่อนโยน และให้กำลังใจเสมอ"},
                {"role": "user", "content": message}
            ]
        )

        response_text = gpt_response.choices[0].message.content.strip()
        return {"response": response_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import sys
    port = 5000  # default
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    uvicorn.run(app, host="0.0.0.0", port=port)
