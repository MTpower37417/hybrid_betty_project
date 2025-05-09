import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="core/static"), name="static")
templates = Jinja2Templates(directory="core/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/architect", response_class=HTMLResponse)
async def architect_console(request: Request):
    return templates.TemplateResponse("console.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("reflexos_server:app", host="0.0.0.0", port=5000, reload=False)
