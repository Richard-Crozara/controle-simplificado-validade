
import re

import database
from app import app


def preparar_banco(monkeypatch, tmp_path):
    banco_teste = tmp_path / "teste.db"

    monkeypatch.setattr(database, "DATABASE", banco_teste)

    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "chave-secreta-apenas-para-testes"
    app.config["WTF_CSRF_ENABLED"] = True

    database.inicializar_banco()


def obter_token_csrf(cliente, pagina):
    resposta = cliente.get(pagina)

    assert resposta.status_code == 200

    token = re.search(
        rb'name="csrf_token" value="([^"]+)"',
        resposta.data
    )

    assert token is not None

    return token.group(1).decode("utf-8")


def test_configuracao_cria_usuario(monkeypatch, tmp_path):
    preparar_banco(monkeypatch, tmp_path)

    cliente = app.test_client()
    token = obter_token_csrf(cliente, "/configurar")

    resposta = cliente.post(
        "/configurar",
        data={
            "usuario": "funcionario",
            "senha": "senha1234",
            "csrf_token": token
        }
    )

    assert resposta.status_code == 302
    assert database.existe_usuario()


def test_configuracao_bloqueada_apos_criar_usuario(
    monkeypatch, tmp_path
):
    preparar_banco(monkeypatch, tmp_path)

    database.criar_usuario("funcionario", "senha1234")

    cliente = app.test_client()
    resposta = cliente.get("/configurar")

    assert resposta.status_code == 302
    assert "/login" in resposta.location


def test_login_com_senha_incorreta(monkeypatch, tmp_path):
    preparar_banco(monkeypatch, tmp_path)

    database.criar_usuario("funcionario", "senha1234")

    cliente = app.test_client()
    token = obter_token_csrf(cliente, "/login")

    resposta = cliente.post(
        "/login",
        data={
            "usuario": "funcionario",
            "senha": "senhaerrada",
            "csrf_token": token
        }
    )

    assert resposta.status_code == 200
    assert (
        b"Usuario ou senha invalidos." in resposta.data
        or "Usuário ou senha inválidos.".encode("utf-8")
        in resposta.data
    )


def test_login_e_logout(monkeypatch, tmp_path):
    preparar_banco(monkeypatch, tmp_path)

    database.criar_usuario("funcionario", "senha1234")

    cliente = app.test_client()
    token_login = obter_token_csrf(cliente, "/login")

    resposta_login = cliente.post(
        "/login",
        data={
            "usuario": "funcionario",
            "senha": "senha1234",
            "csrf_token": token_login
        }
    )

    assert resposta_login.status_code == 302
    assert resposta_login.location == "/"

    resposta_inicio = cliente.get("/")

    assert resposta_inicio.status_code == 302
    assert resposta_inicio.location == "/produtos"

    resposta_produtos = cliente.get("/produtos")

    assert resposta_produtos.status_code == 200

    token_logout = obter_token_csrf(cliente, "/produtos")

    resposta_logout = cliente.post(
        "/logout",
        data={
            "csrf_token": token_logout
        }
    )

    assert resposta_logout.status_code == 302
    assert "/login" in resposta_logout.location

    resposta_protegida = cliente.get("/")

    assert resposta_protegida.status_code == 302
    assert "/login" in resposta_protegida.location


def test_login_rejeita_post_sem_token_csrf(monkeypatch, tmp_path):
    preparar_banco(monkeypatch, tmp_path)

    database.criar_usuario("funcionario", "senha1234")

    cliente = app.test_client()

    resposta = cliente.post(
        "/login",
        data={
            "usuario": "funcionario",
            "senha": "senha1234"
        }
    )

    assert resposta.status_code == 400
