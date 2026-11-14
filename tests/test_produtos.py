
import pytest
from datetime import date, timedelta

import database
from app import app, classificar_validade


@pytest.fixture
def cliente_sem_login(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE", tmp_path / "teste.db")
    database.inicializar_banco()
    return app.test_client()


@pytest.fixture
def cliente(cliente_sem_login):
    database.criar_usuario("usuario_teste", "senha1234")
    usuario = database.buscar_usuario("usuario_teste")

    with cliente_sem_login.session_transaction() as sessao:
        sessao["usuario_id"] = usuario["id"]
        sessao["usuario"] = "usuario_teste"

    return cliente_sem_login


def test_produtos_exige_login(cliente_sem_login):
    resposta = cliente_sem_login.get("/produtos")

    assert resposta.status_code == 302
    assert "/login" in resposta.location


def test_cadastro_de_produto_valido(cliente):
    validade = (date.today() + timedelta(days=120)).isoformat()

    resposta = cliente.post(
        "/produtos",
        data={
            "nome": "Arroz teste",
            "quantidade": "10",
            "validade": validade
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200

    usuario = database.buscar_usuario("usuario_teste")
    produtos = database.listar_produtos(usuario["id"])

    assert len(produtos) == 1
    assert produtos[0]["nome"] == "Arroz teste"
    assert produtos[0]["quantidade"] == 10


def test_cadastro_rejeita_quantidade_zero(cliente):
    resposta = cliente.post(
        "/produtos",
        data={
            "nome": "Produto teste",
            "quantidade": "0",
            "validade": (date.today() + timedelta(days=120)).isoformat()
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200

    usuario = database.buscar_usuario("usuario_teste")
    produtos = database.listar_produtos(usuario["id"])

    assert len(produtos) == 0


def test_cadastro_rejeita_quantidade_nao_inteira(cliente):
    resposta = cliente.post(
        "/produtos",
        data={
            "nome": "Produto teste",
            "quantidade": "abc",
            "validade": (date.today() + timedelta(days=120)).isoformat()
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200

    usuario = database.buscar_usuario("usuario_teste")
    produtos = database.listar_produtos(usuario["id"])

    assert len(produtos) == 0


def test_cadastro_rejeita_data_invalida(cliente):
    resposta = cliente.post(
        "/produtos",
        data={
            "nome": "Produto teste",
            "quantidade": "5",
            "validade": "data-invalida"
        },
        follow_redirects=True
    )

    assert resposta.status_code == 200

    usuario = database.buscar_usuario("usuario_teste")
    produtos = database.listar_produtos(usuario["id"])

    assert len(produtos) == 0


def test_classificacao_de_validade():
    hoje = date.today()

    assert classificar_validade(
        (hoje - timedelta(days=1)).isoformat()
    ) == "Vencido"

    assert classificar_validade(
        hoje.isoformat()
    ) == "Atenção"

    assert classificar_validade(
        (hoje + timedelta(days=90)).isoformat()
    ) == "Atenção"

    assert classificar_validade(
        (hoje + timedelta(days=91)).isoformat()
    ) == "Dentro do prazo"


def test_listagem_exibe_produto_cadastrado(cliente):
    validade = (date.today() + timedelta(days=120)).isoformat()

    database.cadastrar_produto(
        1,
        "Produto para listagem",
        5,
        validade
    )

    resposta = cliente.get("/produtos")

    assert resposta.status_code == 200
    assert b"Produto para listagem" in resposta.data


def test_usuario_nao_visualiza_produtos_de_outro_usuario(cliente):
    database.criar_usuario("outro_usuario", "senha5678")
    outro = database.buscar_usuario("outro_usuario")

    database.cadastrar_produto(
        outro["id"],
        "Produto particular",
        3,
        (date.today() + timedelta(days=120)).isoformat()
    )

    resposta = cliente.get("/produtos")

    assert resposta.status_code == 200
    assert b"Produto particular" not in resposta.data
