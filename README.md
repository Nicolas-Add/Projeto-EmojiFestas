# 🎈 EmojiFestas

> **Sistema Integrado de Gestão e Agendamento para Salões de Festas**

O **EmojiFestas** é uma aplicação desenvolvida para centralizar a gestão administrativa e operacional de 3 salões de festas. O sistema substitui o controle manual por planilhas, oferecendo agendamento seguro, gestão de combos personalizados e acompanhamento financeiro em tempo real.

---

## 👥 Dados da Equipe

| Nome do Integrante |
| :--- |
| **Nicolas Addevico** |
| **Eduardo Andina** |
| **Eduardo Tulini** |
| **Henry Medeiros** |
| **Vitor Amora** |
| **Henrique Vaz** |

---

## 🎯 Contextualização & Dores do Cliente

### **Público-Alvo**
* **Usuários Diretos:** Proprietária do empreendimento e funcionários responsáveis pela gestão e atendimento.
* **Locais de Uso:** Recepção dos 3 salões de festas e no ambiente administrativo no escritório (computador de mesa).

### **Problemas Encontrados (Dores)**
Atualmente, o controle dos 3 salões é feito por planilhas descentralizadas, gerando gargalos operacionais:
* ⚠️ **Risco de sobreposição de datas:** Falta de validação automática para reservas.
* 📊 **Descentralização:** Ausência de um sistema único para gerenciar pagamentos, combos e agendas.
* ⏳ **Lentidão no atendimento:** Dificuldade em calcular orçamentos personalizados e opções de pacotes em tempo real.

---

## 📋 Requisitos da Aplicação

### 🛠️ Requisitos Funcionais (RF)

1. **Controle de Acesso (Login):** Autenticação segura por usuário e senha, com controle de acesso baseado em perfis (*Administrador/Proprietária* e *Atendente/Funcionário*).
2. **Gestão de Salões e Combos:** 
   * Cadastro e manutenção dos 3 salões de festas.
   * Seleção entre 3 combos pré-definidos ou personalização de pacotes (adicionando comidas, bebidas, brinquedos, etc.).
   * Cálculo de horas adicionais mediante cobrança extra.
3. **Gestão de Clientes:** Cadastro, edição e consulta dos contratantes (nome, contato, documento) vinculados aos agendamentos.
4. **Agendamento de Eventos:** Marcação de festas com validação automática de disponibilidade por data, horário e salão, prevenindo choque de agenda.
5. **Sistema de Pagamentos:** Registro e controle financeiro de entradas (sinal), parcelamento, quitação e histórico financeiro por cliente.
6. **Relatórios e Consultas:** Visualização rápida e organizada da agenda por salão e histórico financeiro completo das festas.

### ⚙️ Requisitos Não Funcionais (RNF)

1. **Estabilidade:** Execução fluida e sem travamentos durante consultas de disponibilidade e processamento de cálculos orçamentários.
2. **Usabilidade:** Interface intuitiva, limpa e responsiva para agilizar o atendimento diário no balcão e no escritório.
3. **Consistência de Dados:** Arquitetura orientada a objetos (**POO**) garantindo a integridade dos modelos e relacionamentos (`Salao`, `Festa`, `Funcionario`, `Pagamento`, `Cliente`).

---

## 🖥️ Telas da Aplicação (Interface)

* **🔐 Tela de Login e Autenticação:** Acesso restrito via credenciais com redirecionamento baseado na permissão do usuário (*Funcionário* ou *Administrador*).
* **📅 Tela de Agendamento e Seleção de Combos:** Fluxo guiado em etapas para inserção dos dados do cliente, escolha de data no calendário, seleção de combo base/opcionais e cálculo em tempo real do orçamento.
* **💳 Tela de Gestão de Pagamentos e Contratos:** Painel financeiro em tabela exibindo o status dos eventos (*Quitado*, *Pago*, *Pendente*) e permitindo registrar a baixa de novos pagamentos.

---

## ▶️ Como rodar

```bash
pip install -r requirements.txt
python app.py
```

Acesse http://127.0.0.1:5000. Contas de teste: `dona@emojifestas.com` / `admin123` (Proprietária) e `ana@emojifestas.com` / `1234` (Atendente).
