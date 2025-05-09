import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

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
        response_text = f"Betty ตอบกลับ: '{message}' (ReflexOS)"
        return {"response": response_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
