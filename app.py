import os
import secrets
from functools import wraps

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
    criar_usuario
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
    return "Controle Simplificado de Validade"


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
