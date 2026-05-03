from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.dependecies import obter_cliente_repositorio
from app.models.cliente import ClienteCriarAtualizar
from app.repository.cliente import ClienteRepositorio
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

@app.get("/clientes", response_class=HTMLResponse)
async def listar_clientes_html(
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    clientes = await cliente_repositorio.listar_clientes()
    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context={"clientes": clientes, "versao": app.version},
    )

@app.get("/clientes/novo", response_class=HTMLResponse)
async def novo_cliente_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="novo_cliente.html",
        context={
            "cliente": None,
            "form_action": "/clientes/novo",
            "page_title": "Novo Cliente",
            "submit_label": "Salvar cliente",
            "versao": app.version,
        },
    )

@app.post("/clientes/novo")
async def criar_cliente_html(
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
):
    cliente = ClienteCriarAtualizar(nome=nome, email=email, telefone=telefone)
    await cliente_repositorio.criar_cliente(cliente)
    return RedirectResponse("/clientes", status_code=303)

@app.get("/clientes/{cliente_id}/editar", response_class=HTMLResponse)
async def editar_cliente_form(
    cliente_id: int,
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    cliente = await cliente_repositorio.obter_cliente(cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return templates.TemplateResponse(
        request=request,
        name="novo_cliente.html",
        context={
            "cliente": cliente,
            "form_action": f"/clientes/{cliente_id}/editar",
            "page_title": "Editar Cliente",
            "submit_label": "Salvar alterações",
            "versao": app.version,
        },
    )

@app.post("/clientes/{cliente_id}/editar")
async def editar_cliente_html(
    cliente_id: int,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
):
    cliente = ClienteCriarAtualizar(nome=nome, email=email, telefone=telefone)
    cliente_atualizado = await cliente_repositorio.atualizar_cliente(cliente_id, cliente)
    if cliente_atualizado is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return RedirectResponse("/clientes", status_code=303)