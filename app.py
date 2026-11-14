import os
import secrets
from functools import wraps
from datetime import date, timedelta

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from werkzeug.security import check_password_hash

from database import (
    inicializar_banco,
    existe_usuario,
    buscar_usuario,
    criar_usuario,
    cadastrar_produto,
    listar_produtos,
    obter_produto,
    atualizar_produto,
    excluir_produto
)


app = Flask(__name__)

app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY") or secrets.token_hex(32)
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("COOKIE_SECURE", "0") == "1"
)


def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar_login(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return verificar_login


@app.route("/")
@login_obrigatorio
def inicio():
    return redirect(url_for("produtos"))


def classificar_validade(validade):
    data_validade = date.fromisoformat(validade)
    hoje = date.today()

    if data_validade < hoje:
        return "Vencido"

    if data_validade <= hoje + timedelta(days=90):
        return "Atenção"

    return "Dentro do prazo"


@app.route("/produtos", methods=["GET", "POST"])
@login_obrigatorio
def produtos():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        quantidade_texto = request.form.get("quantidade", "").strip()
        validade = request.form.get("validade", "").strip()

        if not nome:
            flash("Informe o nome do produto.")
            return redirect(url_for("produtos"))

        try:
            quantidade = int(quantidade_texto)

            if quantidade <= 0:
                raise ValueError

        except ValueError:
            flash(
                "A quantidade deve ser um número inteiro maior que zero."
            )
            return redirect(url_for("produtos"))

        try:
            data_validade = date.fromisoformat(validade)

            if data_validade.isoformat() != validade:
                raise ValueError

        except ValueError:
            flash("Informe uma data de validade válida.")
            return redirect(url_for("produtos"))

        cadastrar_produto(
            session["usuario_id"],
            nome,
            quantidade,
            validade
        )

        flash("Produto cadastrado com sucesso.")
        return redirect(url_for("produtos"))

    registros = listar_produtos(session["usuario_id"])

    produtos_lista = []

    for produto in registros:
        item = dict(produto)
        item["situacao"] = classificar_validade(item["validade"])
        produtos_lista.append(item)

    return render_template(
        "produtos.html",
        produtos=produtos_lista
    )


@app.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
@login_obrigatorio
def editar_produto(produto_id):
    usuario_id = session["usuario_id"]
    produto = obter_produto(produto_id, usuario_id)

    if produto is None:
        flash("Produto não encontrado.")
        return redirect(url_for("produtos"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        quantidade_texto = request.form.get("quantidade", "").strip()
        validade = request.form.get("validade", "").strip()

        if not nome:
            flash("Informe o nome do produto.")
            return redirect(
                url_for("editar_produto", produto_id=produto_id)
            )

        try:
            quantidade = int(quantidade_texto)

            if quantidade <= 0:
                raise ValueError

        except ValueError:
            flash(
                "A quantidade deve ser um número inteiro maior que zero."
            )
            return redirect(
                url_for("editar_produto", produto_id=produto_id)
            )

        try:
            data_validade = date.fromisoformat(validade)

            if data_validade.isoformat() != validade:
                raise ValueError

        except ValueError:
            flash("Informe uma data de validade válida.")
            return redirect(
                url_for("editar_produto", produto_id=produto_id)
            )

        atualizado = atualizar_produto(
            produto_id,
            usuario_id,
            nome,
            quantidade,
            validade
        )

        if atualizado:
            flash("Produto atualizado com sucesso.")
        else:
            flash("Não foi possível atualizar o produto.")

        return redirect(url_for("produtos"))

    return render_template(
        "editar_produto.html",
        produto=produto
    )


@app.route("/produtos/<int:produto_id>/excluir", methods=["POST"])
@login_obrigatorio
def excluir_produto_rota(produto_id):
    excluido = excluir_produto(
        produto_id,
        session["usuario_id"]
    )

    if excluido:
        flash("Produto excluído com sucesso.")
    else:
        flash("Produto não encontrado.")

    return redirect(url_for("produtos"))


@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    if existe_usuario():
        return redirect(url_for("login"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        if len(usuario) < 3:
            flash("O usuário deve ter pelo menos 3 caracteres.")
            return render_template("configurar.html")

        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.")
            return render_template("configurar.html")

        try:
            criar_usuario(usuario, senha)
        except Exception:
            flash("Não foi possível criar o usuário. Tente novamente.")
            return render_template("configurar.html")

        flash("Usuário criado. Faça login para continuar.")
        return redirect(url_for("login"))

    return render_template("configurar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        registro = buscar_usuario(usuario)

        if registro and check_password_hash(
            registro["senha_hash"], senha
        ):
            session.clear()
            session["usuario_id"] = registro["id"]
            session["usuario"] = registro["usuario"]

            return redirect(url_for("inicio"))

        flash("Usuário ou senha inválidos.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_obrigatorio
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True)
