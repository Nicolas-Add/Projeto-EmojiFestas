from datetime import date
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

from models import Banco, DURACAO_BASE, VALOR_HORA_EXTRA

app = Flask(__name__)
app.secret_key = "emojifestas-demo"  # só para apresentação
db = Banco()

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


@app.template_filter("brl")
def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("data")
def data_br(iso):
    d = date.fromisoformat(iso)
    return f"{DIAS[d.weekday()]} {d:%d/%m/%Y}"


def usuario_atual():
    return db.funcionario(session.get("email"))


@app.context_processor
def contexto():
    return {"me": usuario_atual(), "db": db}


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


# ---------- Público
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if usuario_atual():
        return redirect(url_for("painel"))
    erro = None
    if request.method == "POST":
        u = db.autenticar(request.form["email"], request.form["senha"])
        if u:
            session["email"] = u.email
            return redirect(url_for("painel"))
        erro = "E-mail ou senha incorretos."
    return render_template("login.html", erro=erro, email=request.form.get("email", ""))


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


# ---------- Painel
@app.route("/painel")
@login_obrigatorio()
def painel():
    hoje = date.today().isoformat()
    proximas = sorted((f for f in db.festas if f.data >= hoje), key=lambda f: (f.data, f.inicio))
    mes = hoje[:7]
    do_mes = [f for f in db.festas if f.data.startswith(mes)]
    resumo = {
        "festas_mes": len(do_mes),
        "recebido": sum(p.valor for p in db.pagamentos),
        "a_receber": sum(f.total - db.pago(f) for f in db.festas),
    }
    return render_template("painel.html", proximas=proximas[:8], resumo=resumo)


# ---------- Agendamento
@app.route("/agendar", methods=["GET", "POST"])
@login_obrigatorio()
def agendar():
    form = request.form
    if request.method == "POST":
        if form.get("cliente_id") == "novo":
            cliente, erro = db.salvar_cliente(form["novo_nome"], form["novo_contato"], form["novo_documento"])
        else:
            cliente, erro = db.cliente(form["cliente_id"]), None
        if not erro:
            festa, erro = db.agendar(form["salao_id"], cliente.id, form["data"], form["inicio"],
                                     form.get("combo_id") or None, form.getlist("extras"),
                                     form.get("horas_extra", 0), form.get("obs", ""))
        if not erro:
            flash(f"Festa de {cliente.nome} agendada para {data_br(festa.data)} às {festa.inicio}.", "ok")
            return redirect(url_for("pagamentos", festa=festa.id))
        flash(erro, "erro")
    return render_template("agendar.html", form=form, hoje=date.today().isoformat(),
                           ocupados=db.horarios_ocupados(), duracao=DURACAO_BASE, hora_extra=VALOR_HORA_EXTRA)


# ---------- Clientes
@app.route("/clientes", methods=["GET", "POST"])
@login_obrigatorio()
def clientes():
    if request.method == "POST":
        f = request.form
        _, erro = db.salvar_cliente(f["nome"], f["contato"], f["documento"], f.get("id") or None)
        flash(erro or "Cliente salvo.", "erro" if erro else "ok")
        return redirect(url_for("clientes"))
    busca = request.args.get("q", "").lower()
    lista = [c for c in db.clientes if busca in c.nome.lower() or busca in c.documento]
    editar = db.cliente(request.args["editar"]) if request.args.get("editar") else None
    return render_template("clientes.html", clientes=lista, busca=busca, editar=editar)


# ---------- Pagamentos
@app.route("/pagamentos", methods=["GET", "POST"])
@login_obrigatorio()
def pagamentos():
    if request.method == "POST":
        try:
            valor = float(request.form["valor"].replace(".", "").replace(",", "."))
        except ValueError:
            valor = 0
        erro = db.registrar_pagamento(request.form["festa_id"], valor, request.form["tipo"])
        flash(erro or "Pagamento registrado.", "erro" if erro else "ok")
        return redirect(url_for("pagamentos", festa=request.form["festa_id"]))
    filtro = request.args.get("status", "")
    festas = sorted(db.festas, key=lambda f: f.data)
    if filtro:
        festas = [f for f in festas if db.status(f) == filtro]
    aberta = db.festa(request.args["festa"]) if request.args.get("festa") else None
    return render_template("pagamentos.html", festas=festas, filtro=filtro, aberta=aberta)


# ---------- Relatórios
@app.route("/relatorios")
@login_obrigatorio()
def relatorios():
    salao_id = request.args.get("salao", type=int)
    agenda = sorted((f for f in db.festas if not salao_id or f.salao_id == salao_id), key=lambda f: (f.data, f.inicio))
    historico = sorted(db.pagamentos, key=lambda p: p.data, reverse=True)
    return render_template("relatorios.html", agenda=agenda, salao_id=salao_id, historico=historico)


# ---------- Salões e combos (admin)
@app.route("/saloes", methods=["GET", "POST"])
@login_obrigatorio(admin=True)
def saloes():
    if request.method == "POST":
        f = request.form
        try:
            for s in db.saloes:
                s.capacidade = int(f[f"cap_{s.id}"])
                s.acrescimo = float(f[f"acr_{s.id}"])
            for c in db.combos:
                c.preco = float(f[f"combo_{c.id}"])
                c.descricao = f[f"desc_{c.id}"]
            for e in db.extras:
                e.preco = float(f[f"extra_{e.id}"])
        except ValueError:
            flash("Use apenas números nos campos de valor.", "erro")
        else:
            db.salvar()
            flash("Valores atualizados.", "ok")
        return redirect(url_for("saloes"))
    return render_template("saloes.html")


# ---------- Equipe (admin)
@app.route("/equipe", methods=["GET", "POST"])
@login_obrigatorio(admin=True)
def equipe():
    if request.method == "POST":
        f = request.form
        if f.get("remover"):
            if f["remover"] != usuario_atual().email:
                db.remover_funcionario(f["remover"])
                flash("Conta removida.", "ok")
        else:
            erro = db.criar_funcionario(f["nome"], f["email"], f["senha"], f["perfil"])
            flash(erro or "Conta criada.", "erro" if erro else "ok")
        return redirect(url_for("equipe"))
    return render_template("equipe.html")


if __name__ == "__main__":
    app.run(debug=True)
