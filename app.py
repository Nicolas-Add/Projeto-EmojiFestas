from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

from models import RepositorioFuncionarios, FESTAS

app = Flask(__name__)
app.secret_key = "emojifestas-demo"  # só para apresentação
repo = RepositorioFuncionarios()


def usuario_atual():
    return repo.buscar(session.get("email"))


def login_obrigatorio(admin=False):
    def deco(view):
        @wraps(view)
        def wrapper(*a, **kw):
            u = usuario_atual()
            if not u:
                return redirect(url_for("login"))
            if admin and not u.is_admin:
                abort(403)
            return view(*a, **kw)
        return wrapper
    return deco


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if usuario_atual():
        return redirect(url_for("painel"))
    erro = None
    if request.method == "POST":
        u = repo.autenticar(request.form["email"], request.form["senha"])
        if u:
            session["email"] = u.email
            return redirect(url_for("painel"))
        erro = "E-mail ou senha incorretos."
    return render_template("login.html", erro=erro, email=request.form.get("email", ""))


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


@app.route("/painel")
@login_obrigatorio()
def painel():
    return render_template("painel.html", me=usuario_atual(), festas=FESTAS, equipe=repo.todos())


@app.post("/contas")
@login_obrigatorio(admin=True)
def criar_conta():
    f = request.form
    erro = repo.criar(f["nome"], f["email"], f["senha"], f["perfil"])
    flash(erro or "Conta criada.", "erro" if erro else "ok")
    return redirect(url_for("painel") + "#contas")


@app.post("/contas/remover")
@login_obrigatorio(admin=True)
def remover_conta():
    if request.form["email"] != usuario_atual().email:
        repo.remover(request.form["email"])
    return redirect(url_for("painel") + "#contas")


if __name__ == "__main__":
    app.run(debug=True)
