/**
 * Constantes centralizadas do projeto - todas em PT-BR.
 * Este módulo centraliza todos os valores fixos do sistema.
 */

// =============================================================================
// APLICAÇÃO
// =============================================================================
const NOME_APLICATIVO = "Calendário Kanban";
const NOME_ORGANIZACAO = "DevBroCorp";

// =============================================================================
// TEMPO E DELAYS (milissegundos)
// =============================================================================
const TEMPO_REMOCAO_TOAST = 300;
const TEMPO_ANIMACAO_SHAKE = 500;
const TEMPO_ANIMACAO_HIGHLIGHT = 1000;
const DELAY_ENTRADA_ITEM = 50;
const DURACAO_TRANSICAO_PADRAO = 300;

// =============================================================================
// PERIODICIDADE EM DIAS
// =============================================================================
const DIAS_QUINZENAL = 14;
const DIAS_SEMANA_PERIODICIDADE = 7;

// =============================================================================
// VALORES PADRÃO
// =============================================================================
const PRIORIDADE_PADRAO = 3;
const TOTAL_DIAS_SEMANA = 5;
const DEBUG_MODE = false;  // Mudar para true durante desenvolvimento

// =============================================================================
// DIMENSÕES DA JANELA
// =============================================================================
const LARGURA_JANELA = 1280;
const ALTURA_JANELA = 720;

// =============================================================================
// ANIMAÇÕES (milissegundos)
// =============================================================================
const DURACAO_FADE_IN = 400;
const ATRASO_FADE_IN = 50;
const DURACAO_FADE_OUT = 200;
const DURACAO_RIPPLE = 400;
const DURACAO_ANIMACAO_HOVER = 150;

// =============================================================================
// TOAST (NOTIFICAÇÕES)
// =============================================================================
const DURACAO_TOAST_CURTA = 1500;
const DURACAO_TOAST_MEDIA = 2000;

// =============================================================================
// HORÁRIOS
// =============================================================================
const HORARIO_INICIO_PADRAO = 7;
const HORARIO_FIM_PADRAO = 23;
const HORARIO_INICIAL_SPINBOX = 9;
const MINUTO_INICIAL_SPINBOX = 0;

// =============================================================================
// DIAS DA SEMANA
// =============================================================================
const DIAS_SEMANA = [
    "Segunda-Feira",
    "Terça-Feira",
    "Quarta-Feira",
    "Quinta-Feira",
    "Sexta-Feira"
];

const DIAS_SEMANA_CURTO = [
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta"
];

// =============================================================================
// STATUS DE TAREFAS
// =============================================================================
const STATUS_TAREFA = {
    FAZER: "Fazer",
    FAZENDO: "Fazendo",
    FEITO: "Feito"
};

const STATUS_LISTA = [STATUS_TAREFA.FAZER, STATUS_TAREFA.FAZENDO, STATUS_TAREFA.FEITO];

// =============================================================================
// CORES DE PRIORIDADE
// =============================================================================
const CORES_PRIORIDADE_VIBRANTE = {
    0: "#e74c3c",  // P0 - vermelho
    1: "#f39c12",  // P1 - laranja
    2: "#3498db",  // P2 - azul
    3: "#27ae60",  // P3 - verde
};

const CORES_PRIORIDADE_SUAVE = {
    0: "#f8d7da",  // P0 - vermelho suave
    1: "#fff3cd",  // P1 - amarelo suave
    2: "#d1ecf1",  // P2 - azul claro suave
    3: "#d4edda",  // P3 - verde suave
};

const NOMES_PRIORIDADE = {
    0: "Crítica",
    1: "Alta",
    2: "Média",
    3: "Baixa",
};

const DESCRICOES_PRIORIDADE = {
    0: "P0 - Crítica",
    1: "P1 - Alta",
    2: "P2 - Média",
    3: "P3 - Baixa",
};

// =============================================================================
// PERIODICIDADE
// =============================================================================
const NOMES_PERIODICIDADE = {
    "unica": "Única",
    "diaria": "Diária",
    "semanal": "Semanal",
    "quinzenal": "Quinzenal",
    "mensal": "Mensal",
};

const LISTA_PERIODICIDADES = [
    { codigo: "unica", descricao: "Única vez" },
    { codigo: "diaria", descricao: "Diária" },
    { codigo: "semanal", descricao: "Semanal" },
    { codigo: "quinzenal", descricao: "Quinzenal" },
    { codigo: "mensal", descricao: "Mensal" },
];

// =============================================================================
// MENSAGENS DO SISTEMA
// =============================================================================
const MSG_TITULO_OBRIGATORIO = "O título é obrigatório.";
const MSG_ERRO_ATUALIZAR_HORARIO = "Não foi possível atualizar o horário.";
const MSG_ERRO_EDITAR_HORARIO = "Erro ao editar horário.";
const MSG_ERRO_REMOVER_HORARIO = "Erro ao remover horário.";
const MSG_CONFIRMAR_EXCLUSAO_HORARIO = "Tem certeza que deseja remover o horário {horario}?\nTodos os dados dessa linha serão perdidos.";
const MSG_CONFIRMAR_DELETAR_TAREFA = "Deletar tarefa?";
const MSG_NENHUMA_ATIVIDADE = "Nenhuma atividade agendada";
const MSG_FIM_DE_SEMANA = "Fim de semana";
const MSG_TAREFA_ADICIONADA = "Tarefa '{titulo}' adicionada!";
const MSG_ERRO_CRIAR_TAREFA = "Erro ao criar tarefa";
const MSG_TEMA_ATIVADO = "{tema} ativado";
const MSG_SINCRONIZACAO_SUCESSO = "{quantidade} tarefa(s) de {dia} sincronizada(s)!";
const MSG_TAREFAS_JA_SINCRONIZADAS = "Tarefas de {dia} já sincronizadas";
const MSG_ERRO_SINCRONIZACAO = "Erro na sincronização: {erro}";
const MSG_SEM_ATIVIDADES_FIM_SEMANA = "Fim de semana - sem atividades";
const MSG_NENHUMA_ATIVIDADE_DIA = "Nenhuma atividade em {dia}";

// =============================================================================
// TOOLTIPS
// =============================================================================
const TOOLTIP_TAREFA_AGENDA = "Tarefa gerada automaticamente da Agenda\nPrioridade: P{prioridade}";
const TOOLTIP_TAREFA_MANUAL = "Prioridade: P{prioridade}";
const TOOLTIP_ATIVIDADE = "Prioridade: P{prioridade} - {nome_prioridade}\nPeriodicidade: {periodicidade}\nCriado em: {data}";
const TOOLTIP_SINCRONIZAR = "Sincroniza as atividades do dia atual para o quadro Kanban";

// =============================================================================
// CHAVES LOCALSTORAGE
// =============================================================================
const STORAGE_KEYS = {
    TAREFAS: "kanban_tarefas",
    HORARIOS: "kanban_horarios",
    AGENDA: "kanban_agenda",
    TEMA: "kanban_tema_escuro",
    CONFIGURACOES: "kanban_configuracoes"
};

// =============================================================================
// EXPORTAÇÃO - Todas as constantes disponíveis globalmente
// =============================================================================
if (typeof window !== 'undefined') {
    window.Constantes = {
        // Aplicação
        NOME_APLICATIVO,
        NOME_ORGANIZACAO,
        
        // Tempos e delays
        TEMPO_REMOCAO_TOAST,
        TEMPO_ANIMACAO_SHAKE,
        TEMPO_ANIMACAO_HIGHLIGHT,
        DELAY_ENTRADA_ITEM,
        DURACAO_TRANSICAO_PADRAO,
        DURACAO_TOAST_CURTA,
        DURACAO_TOAST_MEDIA,
        DURACAO_FADE_IN,
        DURACAO_FADE_OUT,
        DURACAO_RIPPLE,
        
        // Periodicidade
        DIAS_QUINZENAL,
        DIAS_SEMANA_PERIODICIDADE,
        
        // Dias e Status
        DIAS_SEMANA,
        DIAS_SEMANA_CURTO,
        STATUS_TAREFA,
        STATUS_LISTA,
        TOTAL_DIAS_SEMANA,
        
        // Prioridades
        PRIORIDADE_PADRAO,
        CORES_PRIORIDADE_VIBRANTE,
        CORES_PRIORIDADE_SUAVE,
        NOMES_PRIORIDADE,
        DESCRICOES_PRIORIDADE,
        
        // Periodicidade
        NOMES_PERIODICIDADE,
        LISTA_PERIODICIDADES,
        
        // Armazenamento
        STORAGE_KEYS,
        
        // Mensagens
        MSG_TITULO_OBRIGATORIO,
        MSG_CONFIRMAR_DELETAR_TAREFA,
        MSG_CONFIRMAR_EXCLUSAO_HORARIO,
        MSG_NENHUMA_ATIVIDADE,
        MSG_FIM_DE_SEMANA,
        MSG_SEM_ATIVIDADES_FIM_SEMANA
    };
}
