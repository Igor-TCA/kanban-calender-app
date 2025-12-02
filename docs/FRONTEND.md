# Calendário Kanban - Frontend JavaScript

## Descrição

Este é o front-end da aplicação Calendário Kanban, refatorado de PyQt6 para JavaScript puro (Vanilla JS).

## Estrutura do Projeto

```
frontend/
├── index.html          # Página principal
├── css/
│   ├── estilos.css     # Estilos principais e layout
│   ├── temas.css       # Tema claro e escuro
│   ├── componentes.css # Estilos de componentes (botões, modais, inputs)
│   └── animacoes.css   # Animações e transições CSS
└── js/
    ├── constantes.js   # Constantes e configurações
    ├── dominio.js      # Classes de domínio (Tarefa, AtividadeAgenda, etc.)
    ├── persistencia.js # Camada de persistência (localStorage)
    ├── servicos.js     # Camada de serviços (lógica de negócio)
    ├── animacoes.js    # Funções de animação JavaScript
    ├── componentes.js  # Componentes de UI reutilizáveis
    └── main.js         # Inicialização e lógica principal
```

## Funcionalidades

### Quadro Kanban
- ✅ Visualização de tarefas por dia da semana (Segunda a Sexta)
- ✅ Status: Fazer, Fazendo, Feito
- ✅ Drag and drop entre colunas e status
- ✅ Cores por prioridade (P0-P3)
- ✅ Menu de contexto para excluir tarefas
- ✅ Indicação visual de tarefas concluídas (strikethrough)

### Agenda Semanal
- ✅ Grade de horários editável
- ✅ Navegação entre semanas (anterior/próxima/hoje)
- ✅ Inclusão de atividades com prioridade e periodicidade
- ✅ Edição e exclusão de atividades
- ✅ Menu de contexto para células e linhas
- ✅ Suporte a atividades diárias (replicadas automaticamente)

### Calendário Mensal
- ✅ Visualização mensal das atividades
- ✅ Cores indicando a maior prioridade do dia
- ✅ Lista de atividades ao clicar em uma data
- ✅ Navegação entre meses

### Sincronização
- ✅ Sincronização de atividades da agenda para o Kanban
- ✅ Detecção de atividades já sincronizadas
- ✅ Suporte a periodicidade (única, diária, semanal, quinzenal, mensal)

### Temas
- ✅ Tema escuro (padrão)
- ✅ Tema claro
- ✅ Persistência da preferência de tema

## Como Executar

### Opção 1: Abrir diretamente no navegador
Abra o arquivo `index.html` em qualquer navegador moderno.

### Opção 2: Usar servidor local
```bash
# Com Python
python -m http.server 8000

# Com Node.js (npx serve)
npx serve frontend

# Com VS Code Live Server
# Instale a extensão Live Server e clique em "Go Live"
```

## Armazenamento de Dados

Os dados são armazenados no **localStorage** do navegador:
- `kanban_tarefas` - Lista de tarefas do Kanban
- `kanban_horarios` - Lista de horários da grade
- `kanban_agenda` - Atividades da agenda
- `kanban_tema_escuro` - Preferência de tema

## Compatibilidade

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Diferenças em Relação à Versão PyQt6

| Aspecto | PyQt6 | JavaScript |
|---------|-------|------------|
| Plataforma | Desktop (Windows/Mac/Linux) | Web (Browser) |
| Persistência | SQLite | localStorage |
| Instalação | Requer Python + PyQt6 | Nenhuma |
| Distribuição | Executável/Script | HTML estático |

## Backup

O backup dos arquivos originais do front-end PyQt6 está em:
```
BACKUP_FRONTEND_PYQT6/
├── main.py
├── componentes_ui.py
├── estilos.py
├── animacoes.py
├── constantes.py
└── temas/
    ├── claro.qss
    └── escuro.qss
```

## Licença

Mesmo projeto, nova interface.
