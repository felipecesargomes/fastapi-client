from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.cliente import Cliente, ClienteCriarAtualizar
from app.dependecies import obter_cliente_repositorio
from app.repository.cliente import ClienteRepositorio

router = APIRouter(
    prefix="/api/clientes"
)

@router.get("/", response_model=list[Cliente])
async def listar_clientes(cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)]):
    clientes = await cliente_repositorio.listar_clientes()
    if not clientes:
        raise HTTPException(status_code=404, detail="Nenhum cliente encontrado")
    return clientes

@router.get("/{cliente_id}", response_model=Cliente)
async def obter_cliente(
    cliente_id: int,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    cliente = await cliente_repositorio.obter_cliente(cliente_id)
    if cliente:
        return cliente

    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
async def criar_cliente(
    cliente: ClienteCriarAtualizar,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    return await cliente_repositorio.criar_cliente(cliente)

@router.put("/{cliente_id}", response_model=Cliente)
async def atualizar_cliente(
    cliente_id: int,
    cliente: ClienteCriarAtualizar,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    cliente_atualizado = await cliente_repositorio.atualizar_cliente(cliente_id, cliente)
    if cliente_atualizado:
        return cliente_atualizado

    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cliente(
    cliente_id: int,
    cliente_repositorio: Annotated[ClienteRepositorio, Depends(obter_cliente_repositorio)],
):
    cliente_removido = await cliente_repositorio.deletar_cliente(cliente_id)
    if not cliente_removido:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")