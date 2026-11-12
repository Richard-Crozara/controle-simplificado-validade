import sqlite3
from pathlib import Path


DATABASE = Path(__file__).with_name("validade.db")


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    with conectar() as conexao:
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
