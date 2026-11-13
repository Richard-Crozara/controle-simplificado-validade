import database
from app import app


def preparar_banco(monkeypatch, tmp_path):
    banco_teste = tmp_path / "teste.db"

    monkeypatch.setattr(database, "DATABASE", banco_teste)

    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "chave-secreta-apenas-para-testes"

    database.inicializar_banco()


def test_configuracao_cria_usuario(monkeypatch, tmp_path):
    preparar_banco(monkeypatch, tmp_path)

    cliente = app.test_client()

    resposta = cliente.post(
        "/configurar",
        data={
            "usuario": "funcionario",
            "senha": "senha1234"
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

    resposta = cliente.post(
        "/login",
        data={
            "usuario": "funcionario",
            "senha": "senhaerrada"
        }
    )

    assert resposta.status_code == 200
    assert b"Usuario ou senha invalidos." in resposta.data or (
        "Usuário ou senha inválidos.".encode("utf-8") in resposta.data
    )


def test_login_e_logout(monkeypatch, tmp_path):
    preparar_banco(monkeypatch, tmp_path)

    database.criar_usuario("funcionario", "senha1234")

    cliente = app.test_client()

    resposta_login = cliente.post(
        "/login",
        data={
            "usuario": "funcionario",
            "senha": "senha1234"
        }
    )

    assert resposta_login.status_code == 302

    resposta_inicio = cliente.get("/")
    assert resposta_inicio.status_code == 200

    resposta_logout = cliente.post("/logout")
    assert resposta_logout.status_code == 302

    resposta_protegida = cliente.get("/")
    assert resposta_protegida.status_code == 302
    assert "/login" in resposta_protegida.location
