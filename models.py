"""Modelos do EmojiFestas (POO). Persistência simples em JSON, só para demonstração."""
import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash, check_password_hash

ARQUIVO = Path(__file__).parent / "dados.json"
DURACAO_BASE = 4      # horas incluídas em toda festa
VALOR_HORA_EXTRA = 200.0


@dataclass
class Funcionario:
    nome: str
    email: str
    senha_hash: str
    perfil: str = "atendente"  # "admin" (proprietária) ou "atendente"

    @property
    def is_admin(self):
        return self.perfil == "admin"

    @property
    def perfil_nome(self):
        return "Proprietária" if self.is_admin else "Atendente"

    def confere_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


@dataclass
class Salao:
    id: int
    nome: str
    capacidade: int
    acrescimo: float


@dataclass
class Combo:
    id: int
    nome: str
    preco: float
    descricao: str = ""


@dataclass
class Extra:
    id: int
    nome: str
    preco: float


@dataclass
class Cliente:
    id: int
    nome: str
    contato: str
    documento: str


@dataclass
class Pagamento:
    id: int
    festa_id: int
    valor: float
    data: str
    tipo: str  # Sinal, Parcela, Quitação


@dataclass
class Festa:
    id: int
    salao_id: int
    cliente_id: int
    data: str          # AAAA-MM-DD
    inicio: str        # HH:MM
    combo_id: int | None
    extras: list[int] = field(default_factory=list)
    horas_extra: int = 0
    total: float = 0
    obs: str = ""

    @property
    def duracao(self):
        return DURACAO_BASE + self.horas_extra

    def intervalo(self):
        ini = datetime.fromisoformat(f"{self.data}T{self.inicio}")
        return ini, ini + timedelta(hours=self.duracao)

    def conflita_com(self, outra: "Festa"):
        if self.salao_id != outra.salao_id or self.id == outra.id:
            return False
        a1, a2 = self.intervalo()
        b1, b2 = outra.intervalo()
        return a1 < b2 and b1 < a2


class Banco:
    """Guarda todas as entidades e as regras de negócio que cruzam mais de uma delas."""

    TIPOS = {"funcionarios": Funcionario, "saloes": Salao, "combos": Combo, "extras": Extra,
             "clientes": Cliente, "festas": Festa, "pagamentos": Pagamento}

    def __init__(self):
        if ARQUIVO.exists():
            dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
            for nome, cls in self.TIPOS.items():
                setattr(self, nome, [cls(**d) for d in dados.get(nome, [])])
        else:
            self._dados_iniciais()
            self.salvar()

    def salvar(self):
        dados = {nome: [asdict(o) for o in getattr(self, nome)] for nome in self.TIPOS}
        ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _proximo_id(lista):
        return max((o.id for o in lista), default=0) + 1

    @staticmethod
    def _por_id(lista, id_):
        return next((o for o in lista if o.id == int(id_)), None)

    # ---- Funcionários
    def funcionario(self, email):
        email = (email or "").strip().lower()
        return next((f for f in self.funcionarios if f.email == email), None)

    def autenticar(self, email, senha):
        f = self.funcionario(email)
        return f if f and f.confere_senha(senha) else None

    def criar_funcionario(self, nome, email, senha, perfil):
        email = email.strip().lower()
        if self.funcionario(email):
            return "Já existe uma conta com esse e-mail."
        if len(senha) < 4:
            return "A senha precisa ter pelo menos 4 caracteres."
        self.funcionarios.append(Funcionario(nome.strip(), email, generate_password_hash(senha), perfil))
        self.salvar()

    def remover_funcionario(self, email):
        self.funcionarios = [f for f in self.funcionarios if f.email != email]
        self.salvar()

    # ---- Buscas
    def salao(self, id_): return self._por_id(self.saloes, id_)
    def combo(self, id_): return self._por_id(self.combos, id_) if id_ else None
    def extra(self, id_): return self._por_id(self.extras, id_)
    def cliente(self, id_): return self._por_id(self.clientes, id_)
    def festa(self, id_): return self._por_id(self.festas, id_)

    # ---- Clientes
    def salvar_cliente(self, nome, contato, documento, id_=None):
        if not nome.strip() or not contato.strip():
            return None, "Nome e contato são obrigatórios."
        if id_:
            c = self.cliente(id_)
            c.nome, c.contato, c.documento = nome.strip(), contato.strip(), documento.strip()
        else:
            c = Cliente(self._proximo_id(self.clientes), nome.strip(), contato.strip(), documento.strip())
            self.clientes.append(c)
        self.salvar()
        return c, None

    # ---- Orçamento e agendamento
    def calcular_total(self, salao_id, combo_id, extras, horas_extra):
        total = self.salao(salao_id).acrescimo + horas_extra * VALOR_HORA_EXTRA
        total += self.combo(combo_id).preco if combo_id else 0
        total += sum(self.extra(e).preco for e in extras)
        return total

    def agendar(self, salao_id, cliente_id, data_, inicio, combo_id, extras, horas_extra, obs=""):
        if not combo_id and not extras:
            return None, "Escolha um combo ou monte um pacote com pelo menos um item."
        festa = Festa(self._proximo_id(self.festas), int(salao_id), int(cliente_id), data_, inicio,
                      int(combo_id) if combo_id else None, [int(e) for e in extras], int(horas_extra), 0, obs)
        if festa.data < date.today().isoformat():
            return None, "Não é possível agendar em uma data que já passou."
        choque = next((f for f in self.festas if festa.conflita_com(f)), None)
        if choque:
            ini, fim = choque.intervalo()
            return None, (f"O salão {self.salao(salao_id).nome} já está reservado nesse dia, "
                          f"das {ini:%H:%M} às {fim:%H:%M}.")
        festa.total = self.calcular_total(salao_id, festa.combo_id, festa.extras, festa.horas_extra)
        self.festas.append(festa)
        self.salvar()
        return festa, None

    def horarios_ocupados(self):
        """{salao_id: {data: ["14:00–18:00", ...]}} para o calendário do agendamento."""
        mapa = {}
        for f in self.festas:
            ini, fim = f.intervalo()
            mapa.setdefault(f.salao_id, {}).setdefault(f.data, []).append(f"{ini:%H:%M}–{fim:%H:%M}")
        return mapa

    # ---- Pagamentos
    def pagamentos_da(self, festa_id):
        return [p for p in self.pagamentos if p.festa_id == festa_id]

    def pago(self, festa):
        return sum(p.valor for p in self.pagamentos_da(festa.id))

    def status(self, festa):
        pago = self.pago(festa)
        if pago >= festa.total:
            return "Quitado"
        return "Pago" if pago > 0 else "Pendente"

    def registrar_pagamento(self, festa_id, valor, tipo):
        festa = self.festa(festa_id)
        saldo = festa.total - self.pago(festa)
        if valor <= 0:
            return "Informe um valor maior que zero."
        if valor > saldo + 0.001:
            return f"O valor passa do saldo devedor (R$ {saldo:,.2f}).".replace(",", "X").replace(".", ",").replace("X", ".")
        if abs(valor - saldo) < 0.001:
            tipo = "Quitação"
        self.pagamentos.append(Pagamento(self._proximo_id(self.pagamentos), festa.id, valor, date.today().isoformat(), tipo))
        self.salvar()

    # ---- Dados de exemplo
    def _dados_iniciais(self):
        h = lambda s: generate_password_hash(s)
        self.funcionarios = [Funcionario("Marta Oliveira", "dona@emojifestas.com", h("admin123"), "admin"),
                             Funcionario("Ana Souza", "ana@emojifestas.com", h("1234"))]
        self.saloes = [Salao(1, "Arco-Íris", 60, 0), Salao(2, "Estrela", 100, 300), Salao(3, "Confete", 150, 600)]
        self.combos = [Combo(1, "Básico", 1500, "Decoração simples, salgados e refrigerante"),
                       Combo(2, "Festa", 2500, "Decoração temática, buffet completo e bolo"),
                       Combo(3, "Mega", 3800, "Tudo do Festa + brinquedos e animador")]
        self.extras = [Extra(1, "Salgados", 350), Extra(2, "Bebidas", 250), Extra(3, "Pula-pula", 400),
                       Extra(4, "Bolo", 300), Extra(5, "Animador", 450)]
        self.clientes = [Cliente(1, "Juliana Prado", "(11) 98888-1111", "123.456.789-00"),
                         Cliente(2, "Rafael Mendes", "(11) 97777-2222", "987.654.321-00"),
                         Cliente(3, "Carla Teixeira", "(11) 96666-3333", "111.222.333-44")]
        self.festas, self.pagamentos = [], []
        d = lambda n: (date.today() + timedelta(days=n)).isoformat()
        for args, pagos in [((1, 1, d(3), "14:00", 2, [], 0), [2500]),
                            ((2, 2, d(4), "15:00", None, [1, 2, 3], 1), []),
                            ((3, 3, d(10), "13:00", 3, [5], 2), [1500])]:
            festa = Festa(self._proximo_id(self.festas), *args)
            festa.total = self.calcular_total(festa.salao_id, festa.combo_id, festa.extras, festa.horas_extra)
            self.festas.append(festa)
            for v in pagos:
                self.pagamentos.append(Pagamento(self._proximo_id(self.pagamentos), festa.id, v,
                                                 date.today().isoformat(), "Sinal" if v < festa.total else "Quitação"))
