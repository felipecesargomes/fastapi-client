from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.dependecies import obter_cliente_repositorio
from app.models.cliente import ClienteCriarAtualizar
from app.repository.cliente import ClienteRepositorio
from app.routers import cliente

app = FastAPI(
    title="Techlog Solutions API",
    description="CRM para Techlog Solutions",
    version="1.0.0",
)

app.add_middleware(SessionMiddleware, secret_key="techlog-local-secret-key")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
app.include_router(cliente.router)


def _usuario_logado(request: Request) -> bool:
    return request.session.get("cliente_id") is not None


def _contexto_base(request: Request, **contexto_extra):
    contexto = {
        "versao": app.version,
        "usuario_logado": _usuario_logado(request),
        "nome_usuario": request.session.get("cliente_nome"),
        "pode_registrar": False,
    }
    contexto.update(contexto_extra)
    return contexto


def _redirecionar_login() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=303)


@app.get("/")
async def health_check():
    return {"status": "OK"}


@app.get("/front", response_class=HTMLResponse)
async def front_page(request: Request):
    if not _usuario_logado(request):
        return _redirecionar_login()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=_contexto_base(request),
    )


@app.get("/login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    if _usuario_logado(request):
        return RedirectResponse(url="/front", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context=_contexto_base(
            request,
            email="",
            erro=None,
            pode_registrar=True,
        ),
    )

@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
    email: str = Form(...),
    senha: str = Form(...),
):
    cliente = await cliente_repositorio.autenticar_cliente(email=email, senha=senha)
    if cliente is not None:
        request.session["cliente_id"] = cliente.id_
        request.session["cliente_nome"] = cliente.nome
        return RedirectResponse(url="/front", status_code=303)

    pode_registrar = True

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context=_contexto_base(
            request,
            email=email,
            erro="Email ou senha inválidos.",
            pode_registrar=pode_registrar,
        ),
        status_code=401,
    )


@app.get("/register", response_class=HTMLResponse)
async def register_form(
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    return templates.TemplateResponse(
        request=request,
        name="novo_cliente.html",
        context=_contexto_base(
            request,
            cliente=None,
            form_action="/register",
            page_title="Registrar usuário",
            submit_label="Registrar",
            pode_registrar=True,
        ),
    )


@app.post("/register")
async def register_submit(
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
):
    cliente = ClienteCriarAtualizar(nome=nome, email=email, telefone=telefone, senha=senha)
    cliente_criado = await cliente_repositorio.criar_cliente(cliente)

    request.session["cliente_id"] = cliente_criado.id_
    request.session["cliente_nome"] = cliente_criado.nome
    return RedirectResponse("/front", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/clientes", response_class=HTMLResponse)
async def listar_clientes_html(
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    if not _usuario_logado(request):
        return _redirecionar_login()

    clientes = await cliente_repositorio.listar_clientes()
    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context=_contexto_base(request, clientes=clientes),
    )

@app.get("/clientes/novo", response_class=HTMLResponse)
async def novo_cliente_form(request: Request):
    if not _usuario_logado(request):
        return _redirecionar_login()

    return templates.TemplateResponse(
        request=request,
        name="novo_cliente.html",
        context=_contexto_base(
            request,
            cliente=None,
            form_action="/clientes/novo",
            page_title="Novo Cliente",
            submit_label="Salvar cliente",
        ),
    )

@app.post("/clientes/novo")
async def criar_cliente_html(
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
):
    if not _usuario_logado(request):
        return _redirecionar_login()

    cliente = ClienteCriarAtualizar(nome=nome, email=email, telefone=telefone, senha=senha)
    await cliente_repositorio.criar_cliente(cliente)
    return RedirectResponse("/clientes", status_code=303)

@app.get("/clientes/{cliente_id}/editar", response_class=HTMLResponse)
async def editar_cliente_form(
    cliente_id: int,
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    if not _usuario_logado(request):
        return _redirecionar_login()

    cliente = await cliente_repositorio.obter_cliente(cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return templates.TemplateResponse(
        request=request,
        name="novo_cliente.html",
        context=_contexto_base(
            request,
            cliente=cliente,
            form_action=f"/clientes/{cliente_id}/editar",
            page_title="Editar Cliente",
            submit_label="Salvar alterações",
        ),
    )

@app.post("/clientes/{cliente_id}/editar")
async def editar_cliente_html(
    cliente_id: int,
    request: Request,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
):
    if not _usuario_logado(request):
        return _redirecionar_login()

    cliente = ClienteCriarAtualizar(nome=nome, email=email, telefone=telefone, senha=senha)
    cliente_atualizado = await cliente_repositorio.atualizar_cliente(cliente_id, cliente)
    if cliente_atualizado is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return RedirectResponse("/clientes", status_code=303)