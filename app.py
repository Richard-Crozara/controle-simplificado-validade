from flask import Flask
from database import inicializar_banco

app = Flask(__name__)


@app.route("/")
def inicio():
    return "Controle Simplificado de Validade"


if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True)
