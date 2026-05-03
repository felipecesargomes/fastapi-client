from typing import Annotated
from fastapi import Depends

from app.bd.local import BancoDeDadosLocal
from app.repository.cliente import ClienteRepositorio

banco_de_dados = BancoDeDadosLocal()

def obter_banco_de_dados() -> BancoDeDadosLocal:
    return banco_de_dados

def obter_cliente_repositorio(banco_de_dados_local: Annotated[BancoDeDadosLocal, Depends(obter_banco_de_dados)]) -> ClienteRepositorio:
    return ClienteRepositorio(banco_de_dados_local)