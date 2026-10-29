"""Modelos do EmojiFestas (POO). Dados em memória + arquivo JSON, só para demonstração."""
import json
from dataclasses import dataclass, asdict
from pathlib import Path

from werkzeug.security import generate_password_hash, check_password_hash

ARQUIVO = Path(__file__).parent / "dados.json"


@dataclass
class Funcionario:
    nome: str
    email: str
    senha_hash: str
    perfil: str = "atendente"  # "admin" (proprietária) ou "atendente"

    @property
    def is_admin(self) -> bool:
        return self.perfil == "admin"

    @property
    def perfil_nome(self) -> str:
        return "Proprietária" if self.is_admin else "Atendente"

    def confere_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)


@dataclass
class Salao:
    nome: str
    capacidade: int
    acrescimo: float


@dataclass
class Cliente:
    nome: str
    contato: str
    documento: str


@dataclass
class Festa:
    data: str
    salao: Salao
    cliente: Cliente
    pacote: str
    situacao: str  # Quitado, Pendente, Sinal pago


class RepositorioFuncionarios:
    def __init__(self):
        self._itens: dict[str, Funcionario] = {}
        if ARQUIVO.exists():
            for d in json.loads(ARQUIVO.read_text(encoding="utf-8")):
                self._itens[d["email"]] = Funcionario(**d)
        else:
            self.criar("Marta Oliveira", "dona@emojifestas.com", "admin123", "admin")
            self.criar("Ana Souza", "ana@emojifestas.com", "1234", "atendente")

    def _salvar(self):
        ARQUIVO.write_text(json.dumps([asdict(f) for f in self._itens.values()], ensure_ascii=False, indent=2), encoding="utf-8")

    def todos(self) -> list[Funcionario]:
        return list(self._itens.values())

    def buscar(self, email: str) -> Funcionario | None:
        return self._itens.get((email or "").strip().lower())

    def autenticar(self, email: str, senha: str) -> Funcionario | None:
        f = self.buscar(email)
        return f if f and f.confere_senha(senha) else None

    def criar(self, nome: str, email: str, senha: str, perfil: str) -> str | None:
        email = email.strip().lower()
        if email in self._itens:
            return "Já existe uma conta com esse e-mail."
        if len(senha) < 4:
            return "A senha precisa ter pelo menos 4 caracteres."
        self._itens[email] = Funcionario(nome.strip(), email, generate_password_hash(senha), perfil)
        self._salvar()

    def remover(self, email: str):
        self._itens.pop(email, None)
        self._salvar()


# Dados fictícios para o painel
SALOES = [Salao("Arco-Íris", 60, 0), Salao("Estrela", 100, 300), Salao("Confete", 150, 600)]
FESTAS = [
    Festa("sáb 08/11", SALOES[0], Cliente("Juliana P.", "", ""), "Combo Festa", "Quitado"),
    Festa("dom 09/11", SALOES[1], Cliente("Rafael M.", "", ""), "Personalizado", "Pendente"),
    Festa("sáb 15/11", SALOES[2], Cliente("Carla T.", "", ""), "Combo Mega", "Sinal pago"),
]
