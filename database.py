import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


DATABASE = Path(__file__).with_name("validade.db")


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    conexao = conectar()

    try:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                validade TEXT NOT NULL,
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios (id)
                    ON DELETE CASCADE
            )
        """)

        conexao.commit()
    finally:
        conexao.close()


def existe_usuario():
    conexao = conectar()

    try:
        resultado = conexao.execute(
            "SELECT id FROM usuarios LIMIT 1"
        ).fetchone()

        return resultado is not None
    finally:
        conexao.close()


def buscar_usuario(usuario):
    conexao = conectar()

    try:
        resultado = conexao.execute(
            "SELECT * FROM usuarios WHERE usuario = ?",
            (usuario,)
        ).fetchone()

        return resultado
    finally:
        conexao.close()


def criar_usuario(usuario, senha):
    senha_hash = generate_password_hash(senha)

    conexao = conectar()

    try:
        conexao.execute(
            "INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
            (usuario, senha_hash)
        )

        conexao.commit()
    finally:
        conexao.close()

def cadastrar_produto(usuario_id, nome, quantidade, validade):
    conexao = conectar()

    try:
        conexao.execute(
            """
            INSERT INTO produtos
                (usuario_id, nome, quantidade, validade)
            VALUES (?, ?, ?, ?)
            """,
            (usuario_id, nome, quantidade, validade)
        )

        conexao.commit()
    finally:
        conexao.close()


def listar_produtos(usuario_id):
    conexao = conectar()

    try:
        resultado = conexao.execute(
            """
            SELECT id, nome, quantidade, validade
            FROM produtos
            WHERE usuario_id = ?
            ORDER BY validade ASC
            """,
            (usuario_id,)
        ).fetchall()

        return resultado
    finally:
        conexao.close()


def obter_produto(produto_id, usuario_id):
    conexao = conectar()

    try:
        resultado = conexao.execute(
            """
            SELECT id, nome, quantidade, validade
            FROM produtos
            WHERE id = ? AND usuario_id = ?
            """,
            (produto_id, usuario_id)
        ).fetchone()

        return resultado
    finally:
        conexao.close()


def atualizar_produto(
    produto_id, usuario_id, nome, quantidade, validade
):
    conexao = conectar()

    try:
        resultado = conexao.execute(
            """
            UPDATE produtos
            SET nome = ?, quantidade = ?, validade = ?
            WHERE id = ? AND usuario_id = ?
            """,
            (nome, quantidade, validade, produto_id, usuario_id)
        )

        conexao.commit()
        return resultado.rowcount > 0
    finally:
        conexao.close()


def excluir_produto(produto_id, usuario_id):
    conexao = conectar()

    try:
        resultado = conexao.execute(
            """
            DELETE FROM produtos
            WHERE id = ? AND usuario_id = ?
            """,
            (produto_id, usuario_id)
        )

        conexao.commit()
        return resultado.rowcount > 0
    finally:
        conexao.close()
