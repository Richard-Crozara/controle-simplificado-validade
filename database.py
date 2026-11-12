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
