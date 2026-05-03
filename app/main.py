from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import cliente

app = FastAPI(
    title="Techlog Solutions API",
    description="CRM para Techlog Solutions",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(cliente.router)

@app.get("/")
async def health_check():
    return {"status": "OK"}

@app.get("/front", response_class=HTMLResponse)
async def front_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"versao": app.version})