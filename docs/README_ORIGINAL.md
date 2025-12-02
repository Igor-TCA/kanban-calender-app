# Calendário Kanban

> Sistema de gerenciamento de tarefas com quadro Kanban semanal e grade de horários integrada.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/PyQt6-6.0+-green.svg" alt="PyQt6">
  <img src="https://img.shields.io/badge/SQLite-3-orange.svg" alt="SQLite">
  <img src="https://img.shields.io/badge/Code%20Quality-A+-brightgreen.svg" alt="Code Quality">
</p>

---

## Sobre o Projeto

**Calendário Kanban** é uma aplicação desktop desenvolvida em Python com PyQt6 para gerenciar tarefas semanais usando metodologia Kanban integrada a uma grade de horários. Ideal para profissionais que precisam organizar atividades por dia da semana e visualizar sua agenda de forma clara e eficiente.

### Principais Funcionalidades

- **Quadro Kanban Semanal** - 5 colunas (Segunda a Sexta) com 3 status (Fazer, Fazendo, Feito)
- **Grade de Horários** - Agenda visual com linhas customizáveis de horários
- **Temas Claro/Escuro** - Alternância rápida entre modos visuais
- **Drag & Drop** - Arraste tarefas entre status e dias facilmente
- **Persistência Automática** - Dados salvos em SQLite local
- **Animações Suaves** - Fade-in, sombras e efeitos visuais
- **Notificações Toast** - Feedback visual de ações

---

## Arquitetura do Sistema

### Visão Geral

O projeto segue **arquitetura em camadas** com separação clara de responsabilidades:

```
┌─────────────────────────────────┐
│   UI (Apresentação)             │  ← componentes_ui.py, main.py
├─────────────────────────────────┤
│   Serviços (Lógica de Negócio) │  ← servicos.py
├─────────────────────────────────┤
│   Persistência (Repositórios)  │  ← persistencia.py
├─────────────────────────────────┤
│   Dados (SQLite)                │  ← calendario_kanban.db
└─────────────────────────────────┘
      │
      └─→ Domínio (Transversal)    → dominio.py, constantes.py
```

### Fluxos Principais

**Adicionar Tarefa:**
```
Botão → DialogoTarefa → ServicoTarefas → RepositorioTarefas → BD
```

**Drag & Drop:**
```
Arrastar Item → Sinal tarefa_movida → ServicoTarefas.mover_tarefa() → BD → Atualizar UI
```

**Editar Grade de Horários:**
```
Editar Célula → cellChanged Signal → ServicoHorarios → RepositorioTarefas → BD (agenda)
```

### Padrões de Projeto Implementados

- **Repository Pattern** - `RepositorioTarefas` abstrai acesso ao banco
- **Service Layer** - `ServicoTarefas` e `ServicoHorarios` encapsulam lógica de negócio
- **Template Method** - `DialogoBase` define estrutura para diálogos
- **Observer** - Sinais PyQt6 (`tarefa_movida`, `solicitacao_atualizacao`)
- **Strategy** - `GerenciadorEstilo` permite trocar temas dinamicamente
- **Context Manager** - `obter_conexao_bd()` gerencia conexões SQLite
- **DTO** - `TarefaDTO` transfere dados entre camadas
---

## Estrutura do Projeto

```
calendario-kanban/
│
├── main.py                 # Ponto de entrada da aplicação
├── constantes.py           # Configurações e constantes centralizadas
├── servicos.py             # Camada de serviço (lógica de negócio)
├── dominio.py              # Entidades e enums do domínio
├── persistencia.py         # Acesso ao banco de dados
├── componentes_ui.py       # Componentes visuais (widgets customizados)
├── animacoes.py            # Efeitos visuais e animações
├── estilos.py              # Gerenciador de temas
│
├── temas/
│   ├── claro.qss           # Stylesheet do tema claro
│   └── escuro.qss          # Stylesheet do tema escuro
│
├── calendario_kanban.db    # Banco de dados SQLite (gerado automaticamente)
│

```

### Princípios SOLID

O código aplica os 5 princípios SOLID:

- **S**ingle Responsibility - Cada classe tem responsabilidade única
- **O**pen/Closed - Aberto para extensão, fechado para modificação
- **L**iskov Substitution - Subclasses substituíveis
- **I**nterface Segregation - Interfaces específicas por contexto
- **D**ependency Inversion - Dependências de abstrações, não implementações

- `typing` - Type hints
- `logging` - Sistema de logs
- `pathlib` - Manipulação de caminhos
- `contextlib` - Context managers

---

## Padrões de Projeto

O código implementa diversos padrões de design para garantir qualidade e manutenibilidade:

- **Repository Pattern** - Abstração de acesso a dados
- **Service Layer Pattern** - Lógica de negócio isolada
- **Template Method Pattern** - `DialogoBase` para diálogos
- **Observer Pattern** - Sinais PyQt6 para comunicação
- **Strategy Pattern** - Temas intercambiáveis
- **Context Manager Pattern** - Gerenciamento de conexões
- **DTO Pattern** - Transferência de dados entre camadas

---

## Banco de Dados

O projeto utiliza **SQLite** com 3 tabelas principais:

### Tabela: `tarefas`
Armazena todas as tarefas do quadro Kanban.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER PRIMARY KEY | Identificador único |
| `titulo` | TEXT | Descrição da tarefa |
| `dia` | TEXT | Dia da semana |
| `status` | TEXT | Fazer/Fazendo/Feito |
| `horario` | TEXT | Horário opcional |


### Tabela: `definicoes_horario`
Define as linhas de horários disponíveis.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `rotulo_horario` | TEXT PRIMARY KEY | Horário (HH:MM) |


### Tabela: `agenda`
Armazena atividades na grade de horários.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `rotulo_horario` | TEXT | Referência ao horário |
| `coluna` | INTEGER | Índice do dia (0-4) |
| `atividade` | TEXT | Descrição da atividade |

---

## Autor

- **[Igor-TCA](https://github.com/Igor-TCA)**



---

<p align="center">
  <sub>Study Project - Calendário Kanban © 2025</sub>
</p>
