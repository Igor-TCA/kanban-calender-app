# Calendário Kanban

Aplicação de gerenciamento de tarefas com quadro Kanban e agenda semanal.

``Este aplicativo é um estudo de possibilidades.``

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Mac%20%7C%20Linux-yellow.svg)
![Study](https://img.shields.io/badge/study-projecto-orange.svg)


## Estrutura do Projeto

```
KANBAN_APP/
├── frontend/           # Interface web (HTML/CSS/JS)
│   ├── css/           # Estilos
│   ├── js/            # Lógica JavaScript
│   └── icons/         # Ícones SVG da interface
├── electron/          # Configuração do app desktop
│   └── main-electron.js
├── backend/           # Backend Python original (PyQt6)
│   ├── main.py
│   ├── componentes_ui.py
│   ├── dominio.py
│   ├── persistencia.py
│   ├── servicos.py
│   └── temas/
├── assets/            # Ícones do aplicativo
│   ├── icon.svg       # Ícone fonte
│   ├── icon.ico       # Windows
│   └── icon-*.png     # Vários tamanhos
├── docs/              # Documentação
│   ├── INSTALADOR.md  # Guia para criar instalador
│   ├── FRONTEND.md    # Documentação do frontend
│   └── README_ORIGINAL.md  # Doc original do PyQt6
└── backup/            # Backups do projeto
```

O instalador será gerado na pasta `dist/`.

## Funcionalidades

- **Quadro Kanban** - Organize tarefas por dia da semana
- **Agenda Semanal** - Visualize atividades em grade de horários
- **Calendário Mensal** - Navegue entre meses
- **Tema Claro/Escuro** - Alterne entre modos visuais
- **Persistência Local** - Dados salvos no navegador (localStorage)
- **App Desktop** - Empacotado com Electron

## Diagrama de Funcionalidades

```mermaid
flowchart TB
    subgraph APP["Calendário Kanban"]
        direction TB
        
        subgraph KANBAN["Quadro Kanban"]
            K1[("Colunas por<br/>Dia da Semana")]
            K2["Criar Tarefas"]
            K3["Mover Tarefas<br/>Drag & Drop"]
            K4["Editar Tarefas"]
            K5["Deletar Tarefas"]
            K6["Prioridades<br/>P1-P4"]
            K7["Status<br/>Fazer - Fazendo - Feito"]
        end
        
        subgraph AGENDA["Agenda Semanal"]
            A1["Grade de Horários"]
            A2["Adicionar Atividades"]
            A3["Periodicidade<br/>Semanal/Quinzenal"]
            A4["Ativar/Desativar<br/>Atividades"]
            A5["Gerar Tarefas<br/>Automáticas"]
        end
        
        subgraph CALENDARIO["Calendário"]
            C1["Navegação<br/>Mês a Mês"]
            C2["Destaque do<br/>Dia Atual"]
            C3["Visualização<br/>Mensal"]
        end
        
        subgraph UI["Interface"]
            U1["Tema Escuro"]
            U2["Tema Claro"]
            U3["Toasts/<br/>Notificações"]
            U4["Menu de<br/>Contexto"]
            U5["Modais"]
            U6["Animações CSS"]
        end
        
        subgraph DADOS["Persistência"]
            D1[("LocalStorage")]
            D2["Tarefas"]
            D3["Atividades"]
            D4["Horários"]
            D5["Configurações"]
        end
    end
    
    K1 --> K2
    K2 --> K3
    K3 --> K7
    K4 --> K6
    
    A1 --> A2
    A2 --> A3
    A3 --> A5
    A5 -.->|"Cria"| K2
    
    C1 --> C2
    
    U1 <--> U2
    
    D1 --> D2
    D1 --> D3
    D1 --> D4
    D1 --> D5
    
    KANBAN <--> DADOS
    AGENDA <--> DADOS
    UI --> APP
```

### Fluxo de Dados

```mermaid
sequenceDiagram
    participant U as Usuário
    participant C as Componentes
    participant S as Serviços
    participant R as Repositório
    participant L as LocalStorage

    U->>C: Criar Tarefa
    C->>S: ServicoTarefas.criarTarefa()
    S->>R: repositorio.adicionarTarefa()
    R->>L: localStorage.setItem()
    L-->>R: OK
    R-->>S: ID da tarefa
    S-->>C: Sucesso
    C->>C: Renderizar tarefa
    C-->>U: Toast de confirmação

    U->>C: Mover Tarefa (Drag & Drop)
    C->>S: ServicoTarefas.moverTarefa()
    S->>R: repositorio.moverTarefa()
    R->>L: Atualizar dados
    L-->>R: OK
    R-->>S: Sucesso
    S-->>C: Atualizado
    C->>C: Re-renderizar colunas
    C-->>U: Animação de transição
```

### Arquitetura de Camadas

```mermaid
graph LR
    subgraph Frontend["Frontend"]
        HTML["index.html"]
        CSS["CSS Modules"]
        JS["JavaScript"]
    end
    
    subgraph Camadas["Camadas JS"]
        MAIN["main.js<br/>Inicialização"]
        COMP["componentes.js<br/>UI Components"]
        SERV["servicos.js<br/>Lógica de Negócio"]
        DOM["dominio.js<br/>Entidades"]
        PERS["persistencia.js<br/>Repositório"]
        CONST["constantes.js<br/>Configurações"]
        ANIM["animacoes.js<br/>Efeitos Visuais"]
    end
    
    subgraph Desktop["Desktop"]
        ELECTRON["Electron"]
        WIN["Windows"]
        MAC["macOS"]
        LINUX["Linux"]
    end
    
    HTML --> MAIN
    CSS --> HTML
    MAIN --> COMP
    COMP --> SERV
    SERV --> DOM
    SERV --> PERS
    COMP --> ANIM
    MAIN --> CONST
    
    ELECTRON --> HTML
    ELECTRON --> WIN
    ELECTRON --> MAC
    ELECTRON --> LINUX
```

## Tecnologias

### Frontend Web
- HTML5, CSS3, JavaScript (Vanilla)
- LocalStorage para persistência
- Animações CSS

### Desktop
- Electron 28.x
- electron-builder para empacotamento

### Backend Original
- Python 3.x
- PyQt6
- SQLite

---
