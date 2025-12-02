"""
Constantes centralizadas do projeto - todas em PT-BR.
"""

# =============================================================================
# APLICAÇÃO
# =============================================================================
NOME_APLICATIVO = "Calendário Kanban"
NOME_ORGANIZACAO = "DevBroCorp"
NOME_APLICACAO = "GerenciadorProV2"
ARQUIVO_BANCO_DADOS = "calendario_kanban.db"

# =============================================================================
# DIMENSÕES DA JANELA
# =============================================================================
LARGURA_JANELA = 1280
ALTURA_JANELA = 720

# =============================================================================
# ANIMAÇÕES (milissegundos)
# =============================================================================
DURACAO_FADE_IN = 400
ATRASO_FADE_IN = 50
DURACAO_FADE_OUT = 200
DURACAO_RIPPLE = 400
DURACAO_ANIMACAO_HOVER = 150

# =============================================================================
# SOMBRAS
# =============================================================================
RAIO_DESFOQUE_SOMBRA = 15
DESLOCAMENTO_Y_SOMBRA = 2
COR_SOMBRA = (0, 0, 0, 60)
DESFOQUE_SOMBRA_DIALOGO = 25
DESLOCAMENTO_Y_SOMBRA_DIALOGO = 5
COR_SOMBRA_DIALOGO = (0, 0, 0, 150)

# =============================================================================
# DIÁLOGOS
# =============================================================================
ATRASO_FADE_DIALOGO = 10
DURACAO_FADE_DIALOGO = 250
LARGURA_DIALOGO_TAREFA = 480
ALTURA_DIALOGO_TAREFA = 320
LARGURA_DIALOGO_HORARIO = 380
ALTURA_DIALOGO_HORARIO = 280

# =============================================================================
# TOAST (NOTIFICAÇÕES)
# =============================================================================
DESLOCAMENTO_X_TOAST = 20
DESLOCAMENTO_Y_TOAST = 80
DURACAO_TOAST_CURTA = 1500
DURACAO_TOAST_MEDIA = 2000

# Estilos do Toast
ESTILO_TOAST = """
    QLabel {
        background: rgba(0, 0, 0, 200);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
    }
"""

# =============================================================================
# HORÁRIOS
# =============================================================================
HORARIO_INICIO_PADRAO = 7
HORARIO_FIM_PADRAO = 23
HORARIO_INICIAL_SPINBOX = 9
MINUTO_INICIAL_SPINBOX = 0
FORMATO_HORA = "%H:%M"

# =============================================================================
# THREADING
# =============================================================================
MAX_THREADS_POOL = 4

# =============================================================================
# INTERFACE DO USUÁRIO
# =============================================================================
ALTURA_MINIMA_LISTA = 120
ATRASO_SOMBRA_COLUNA = 100
LARGURA_MINIMA_SPINBOX = 80
ALTURA_MINIMA_SPINBOX = 30

# =============================================================================
# FONTE
# =============================================================================
FAMILIA_FONTE = "Segoe UI"
TAMANHO_FONTE = 9

# =============================================================================
# ESTILOS CSS/QSS
# =============================================================================
ESTILO_BOTAO_ADICIONAR_HORARIO = """
    QPushButton { 
        background-color: #6c5ce7; 
        color: white; 
        border-radius: 4px; 
        padding: 6px; 
        font-weight: bold; 
    }
    QPushButton:hover { 
        background-color: #a29bfe; 
    }
"""

ESTILO_LABEL_PREVIA_HORARIO = """
    QLabel {
        background: #6c5ce7;
        color: #ffffff;
        padding: 25px; 
        border-radius: 10px; 
        font-weight: bold; 
        font-size: 36px;
        letter-spacing: 4px;
        qproperty-alignment: AlignCenter;
    }
"""

ESTILO_SPINBOX = """
    QSpinBox {
        font-size: 13px;
        font-weight: bold;
        padding: 5px;
        border: 2px solid #6c5ce7;
        border-radius: 6px;
        min-width: 70px;
        min-height: 28px;
        background-color: rgba(30,30,30,0.85);
        color: #dfe6e9;
    }
    QSpinBox:focus {
        border: 2px solid #a29bfe;
        background-color: rgba(40,40,40,0.9);
    }
    QSpinBox::up-button, QSpinBox::down-button {
        width: 18px;
        background-color: #6c5ce7;
        border: none;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #a29bfe;
    }
    QSpinBox::up-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid white;
    }
    QSpinBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid white;
    }
"""

ESTILO_TITULO_DIALOGO = "font-size: 16px; font-weight: bold; padding: 10px;"

ESTILO_ROTULO_STATUS = "font-weight: bold; margin-top: 10px;"

# =============================================================================
# ESTILOS DE DIÁLOGOS
# =============================================================================
ESTILO_DIALOGO_TITULO = """
    QLabel {
        font-size: 16px;
        font-weight: bold;
        color: #6c5ce7;
        padding-bottom: 5px;
    }
"""

ESTILO_DIALOGO_LABEL_INPUT = """
    QLabel {
        font-size: 14px;
        font-weight: bold;
        padding-right: 5px;
        color: #dfe6e9;
    }
"""

ESTILO_DIALOGO_BOX_PREVIA = """
    QLabel {
        font-size: 18px;
        font-weight: bold;
        color: #dfe6e9;
        border: 2px solid #6c5ce7;
        border-radius: 6px;
        background-color: rgba(30,30,30,0.85);
        padding: 10px;
        min-height: 20px;
    }
"""

# =============================================================================
# CORES DE PRIORIDADE
# =============================================================================
CORES_PRIORIDADE_VIBRANTE = {
    0: "#e74c3c",  # P0 - vermelho
    1: "#f39c12",  # P1 - laranja
    2: "#3498db",  # P2 - azul
    3: "#27ae60",  # P3 - verde
}

CORES_PRIORIDADE_SUAVE = {
    0: "#f8d7da",  # P0 - vermelho suave
    1: "#fff3cd",  # P1 - amarelo suave
    2: "#d1ecf1",  # P2 - azul claro suave
    3: "#d4edda",  # P3 - verde suave
}

NOMES_PRIORIDADE = {
    0: "Crítica",
    1: "Alta",
    2: "Média",
    3: "Baixa",
}

DESCRICOES_PRIORIDADE = {
    0: "P0 - Crítica",
    1: "P1 - Alta",
    2: "P2 - Média",
    3: "P3 - Baixa",
}

# =============================================================================
# PERIODICIDADE
# =============================================================================
NOMES_PERIODICIDADE = {
    "unica": "Única",
    "diaria": "Diária",
    "semanal": "Semanal",
    "quinzenal": "Quinzenal",
    "mensal": "Mensal",
}

LISTA_PERIODICIDADES = [
    ("unica", "Única vez"),
    ("diaria", "Diária"),
    ("semanal", "Semanal"),
    ("quinzenal", "Quinzenal"),
    ("mensal", "Mensal"),
]

INDICE_PERIODICIDADE = {
    "unica": 0,
    "diaria": 1,
    "semanal": 2,
    "quinzenal": 3,
    "mensal": 4,
}

# =============================================================================
# MENSAGENS DO SISTEMA
# =============================================================================
MSG_TITULO_OBRIGATORIO = "O título é obrigatório."
MSG_ERRO_ATUALIZAR_HORARIO = "Não foi possível atualizar o horário."
MSG_ERRO_EDITAR_HORARIO = "Erro ao editar horário."
MSG_ERRO_REMOVER_HORARIO = "Erro ao remover horário."
MSG_CONFIRMAR_EXCLUSAO_HORARIO = "Tem certeza que deseja remover o horário {horario}?\nTodos os dados dessa linha serão perdidos."
MSG_CONFIRMAR_DELETAR_TAREFA = "Deletar tarefa?"
MSG_NENHUMA_ATIVIDADE = "Nenhuma atividade agendada"
MSG_FIM_DE_SEMANA = "Fim de semana"
MSG_TAREFA_ADICIONADA = "Tarefa '{titulo}' adicionada!"
MSG_ERRO_CRIAR_TAREFA = "Erro ao criar tarefa"
MSG_TEMA_ATIVADO = "{tema} ativado"
MSG_SINCRONIZACAO_SUCESSO = "{quantidade} tarefa(s) de {dia} sincronizada(s)!"
MSG_TAREFAS_JA_SINCRONIZADAS = "Tarefas de {dia} já sincronizadas"
MSG_ERRO_SINCRONIZACAO = "Erro na sincronização: {erro}"
MSG_SEM_ATIVIDADES_FIM_SEMANA = "Fim de semana - sem atividades"
MSG_NENHUMA_ATIVIDADE_DIA = "Nenhuma atividade em {dia}"

# =============================================================================
# TOOLTIPS
# =============================================================================
TOOLTIP_TAREFA_AGENDA = "Tarefa gerada automaticamente da Agenda\nPrioridade: P{prioridade}"
TOOLTIP_TAREFA_MANUAL = "Prioridade: P{prioridade}"
TOOLTIP_ATIVIDADE = "Prioridade: P{prioridade} - {nome_prioridade}\nPeriodicidade: {periodicidade}\nCriado em: {data}"
TOOLTIP_SINCRONIZAR = "Sincroniza as atividades do dia atual para o quadro Kanban"

