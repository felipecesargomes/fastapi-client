from app.bd.local import BancoDeDadosLocal
from app.models.cliente import Cliente, ClienteCriarAtualizar


class ClienteRepositorio:
    def __init__(self, database: BancoDeDadosLocal):
        self.db = database

    async def existe_cliente(self) -> bool:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM clientes")
            (total,) = cursor.fetchone()
            return total > 0

    async def listar_clientes(self) -> list[Cliente]:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, nome, email, telefone FROM clientes")
            linhas = cursor.fetchall()
            clientes = [Cliente(id_=linha[0], nome=linha[1], email=linha[2], telefone=linha[3]) for linha in linhas]
            return clientes

    async def criar_cliente(self, cliente: ClienteCriarAtualizar) -> Cliente:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO clientes (nome, email, telefone, senha) VALUES (?, ?, ?, ?)",
                (cliente.nome, cliente.email, cliente.telefone, cliente.senha),
            )
            cliente_id = cursor.lastrowid

        return Cliente(
            id_=cliente_id,
            nome=cliente.nome,
            email=cliente.email,
            telefone=cliente.telefone,
        )

    async def obter_cliente(self, cliente_id: int) -> Cliente | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome, email, telefone FROM clientes WHERE id = ?",
                (cliente_id,),
            )
            linha = cursor.fetchone()

        if not linha:
            return None

        return Cliente(id_=linha[0], nome=linha[1], email=linha[2], telefone=linha[3])

    async def atualizar_cliente(
        self,
        cliente_id: int,
        cliente: ClienteCriarAtualizar,
    ) -> Cliente | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                UPDATE clientes
                SET nome = ?, email = ?, telefone = ?, senha = ?
                WHERE id = ?
                """,
                (cliente.nome, cliente.email, cliente.telefone, cliente.senha, cliente_id),
            )

            if cursor.rowcount == 0:
                return None

        return Cliente(
            id_=cliente_id,
            nome=cliente.nome,
            email=cliente.email,
            telefone=cliente.telefone,
        )

    async def deletar_cliente(self, cliente_id: int) -> bool:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            return cursor.rowcount > 0

    async def autenticar_cliente(self, email: str, senha: str) -> Cliente | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome, email, telefone FROM clientes WHERE email = ? AND senha = ?",
                (email, senha),
            )
            linha = cursor.fetchone()

        if not linha:
            return None

        return Cliente(id_=linha[0], nome=linha[1], email=linha[2], telefone=linha[3])
