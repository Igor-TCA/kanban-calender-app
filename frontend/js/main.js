/**
 * Módulo principal da aplicação Kanban.
 * Controla a inicialização e orquestração dos componentes.
 * Totalmente em PT-BR.
 */

// =============================================================================
// ESTADO DA APLICAÇÃO
// =============================================================================

/**
 * Estado global da aplicação.
 * Centraliza dados compartilhados entre componentes.
 */
const AppState = {
    temaEscuro: true,
    semanaOffset: 0,
    colunas: [],
    tabelaAgenda: null,
    calendarioMensal: null
};

// =============================================================================
// INICIALIZAÇÃO
// =============================================================================

/**
 * Inicialização da aplicação quando DOM estiver pronto
 */
document.addEventListener('DOMContentLoaded', () => {
    debugLog('Aplicação Kanban iniciando...');
    
    inicializarAplicacao();
    
    debugLog('Aplicação Kanban iniciada com sucesso');
});

/**
 * Inicializa todos os componentes da aplicação
 */
function inicializarAplicacao() {
    // Carregar tema salvo
    AppState.temaEscuro = repositorio.obterTemaEscuro();
    aplicarTema();
    
    // Inicializar componentes de UI
    ModalManager.inicializar();
    MenuContexto.inicializar();
    Animacoes.inicializarEfeitosRipple();
    
    // Configurar interface
    configurarAbas();
    configurarBarraFerramentas();
    configurarModalTarefa();
    configurarModalHorario();
    configurarAgenda();
    configurarCalendarioMensal();
    
    // Renderizar Kanban
    renderizarQuadroKanban();
    
    // Animação de entrada
    setTimeout(() => {
        Animacoes.fadeIn(document.body);
    }, ATRASO_FADE_IN);
}

// =============================================================================
// CONFIGURAÇÃO DE ABAS
// =============================================================================

/**
 * Configuração das abas
 */
function configurarAbas() {
    const abas = document.querySelectorAll('.aba');
    
    abas.forEach(aba => {
        aba.addEventListener('click', () => {
            // Remover ativo de todas as abas
            abas.forEach(a => a.classList.remove('ativa'));
            document.querySelectorAll('.conteudo-aba').forEach(c => c.classList.remove('ativo'));
            
            // Ativar aba clicada
            aba.classList.add('ativa');
            const abaId = `aba-${aba.dataset.aba}`;
            document.getElementById(abaId).classList.add('ativo');
            
            // Recarregar dados se necessário
            if (aba.dataset.aba === 'agenda') {
                AppState.tabelaAgenda.carregar();
            }
        });
    });
}

/**
 * Configuração da barra de ferramentas principal
 */
function configurarBarraFerramentas() {
    // Botão Nova Tarefa
    document.getElementById('btn-nova-tarefa').addEventListener('click', () => {
        document.getElementById('input-titulo-tarefa').value = '';
        document.getElementById('select-dia-tarefa').selectedIndex = 0;
        ModalManager.abrirModal('modal-tarefa');
    });
    
    // Botão Atualizar
    document.getElementById('btn-atualizar').addEventListener('click', atualizarTudo);
    
    // Botão Tema
    document.getElementById('btn-tema').addEventListener('click', alternarTema);
}

/**
 * Configuração do modal de nova tarefa
 */
function configurarModalTarefa() {
    document.getElementById('btn-salvar-tarefa').addEventListener('click', () => {
        const titulo = document.getElementById('input-titulo-tarefa').value.trim();
        const dia = document.getElementById('select-dia-tarefa').value;
        
        if (!titulo) {
            Animacoes.shake(document.getElementById('input-titulo-tarefa'));
            Animacoes.mostrarToast(MSG_TITULO_OBRIGATORIO, DURACAO_TOAST_CURTA, 'erro');
            return;
        }
        
        const id = servicoTarefas.criarTarefa({
            titulo,
            dia,
            status: STATUS_TAREFA.FAZER
        });
        
        if (id) {
            atualizarTudo();
            Animacoes.mostrarToast(`Tarefa '${titulo}' adicionada!`);
            ModalManager.fecharModal('modal-tarefa');
        } else {
            Animacoes.mostrarToast('Erro ao criar tarefa', DURACAO_TOAST_CURTA, 'erro');
        }
    });
    
    // Enter para salvar
    document.getElementById('input-titulo-tarefa').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('btn-salvar-tarefa').click();
        }
    });
}

/**
 * Configuração do modal de horário
 */
function configurarModalHorario() {
    const inputHora = document.getElementById('input-hora');
    const inputMinuto = document.getElementById('input-minuto');
    
    inputHora.addEventListener('input', atualizarPreviaHorario);
    inputMinuto.addEventListener('input', atualizarPreviaHorario);
    
    document.getElementById('btn-salvar-horario').addEventListener('click', () => {
        const horario = obterHorarioDoModal();
        
        if (servicoHorarios.adicionarHorario(horario)) {
            AppState.tabelaAgenda.carregar();
            Animacoes.mostrarToast(`Horário ${horario} adicionado`);
        } else {
            Animacoes.mostrarToast('Horário já existe', DURACAO_TOAST_CURTA, 'aviso');
        }
        
        ModalManager.fecharModal('modal-horario');
    });
}

/**
 * Configuração da aba de agenda
 */
function configurarAgenda() {
    // Criar tabela de agenda
    AppState.tabelaAgenda = new TabelaAgenda(
        document.getElementById('tabela-horarios'),
        servicoHorarios,
        AppState.semanaOffset
    );
    
    // Botão incluir atividade
    document.getElementById('btn-incluir-atividade').addEventListener('click', () => {
        abrirModalAtividade({
            modo: 'incluir',
            onSalvar: (dados) => {
                const indiceColuna = DIAS_SEMANA.indexOf(dados.dia);
                
                // Verificar se horário existe
                const horarios = servicoHorarios.obterHorariosOrdenados();
                if (!horarios.includes(dados.horario)) {
                    servicoHorarios.adicionarHorario(dados.horario);
                }
                
                const texto = ExtratorMetadados.formatarAtividade({
                    titulo: dados.titulo,
                    prioridade: dados.prioridade,
                    periodicidade: dados.periodicidade
                });
                
                servicoHorarios.salvarAtividade(dados.horario, indiceColuna, texto);
                AppState.tabelaAgenda.carregar();
                Animacoes.mostrarToast('Atividade adicionada');
            }
        });
    });
    
    // Botão adicionar horário
    document.getElementById('btn-adicionar-horario').addEventListener('click', () => {
        document.getElementById('input-hora').value = '9';
        document.getElementById('input-minuto').value = '0';
        atualizarPreviaHorario();
        ModalManager.abrirModal('modal-horario');
    });
    
    // Botão sincronizar
    document.getElementById('btn-sincronizar-kanban').addEventListener('click', sincronizarAgendaKanban);
    
    // Navegação de semanas
    document.getElementById('btn-semana-anterior').addEventListener('click', () => {
        AppState.semanaOffset--;
        AppState.tabelaAgenda.semanaOffset = AppState.semanaOffset;
        atualizarNavegacaoSemana();
    });
    
    document.getElementById('btn-proxima-semana').addEventListener('click', () => {
        AppState.semanaOffset++;
        AppState.tabelaAgenda.semanaOffset = AppState.semanaOffset;
        atualizarNavegacaoSemana();
    });
    
    document.getElementById('btn-hoje').addEventListener('click', () => {
        AppState.semanaOffset = 0;
        AppState.tabelaAgenda.semanaOffset = 0;
        atualizarNavegacaoSemana();
    });
    
    // Atualizar label inicial
    atualizarLabelSemana();
    
    // Carregar dados iniciais
    AppState.tabelaAgenda.carregar();
}

/**
 * Configuração do calendário mensal
 */
function configurarCalendarioMensal() {
    AppState.calendarioMensal = new CalendarioMensal(
        document.getElementById('calendario-grid'),
        servicoHorarios
    );
    
    document.getElementById('btn-calendario-mensal').addEventListener('click', () => {
        AppState.calendarioMensal.renderizar();
        ModalManager.abrirModal('modal-calendario');
    });
    
    document.getElementById('btn-mes-anterior').addEventListener('click', () => {
        AppState.calendarioMensal.mesAnterior();
    });
    
    document.getElementById('btn-proximo-mes').addEventListener('click', () => {
        AppState.calendarioMensal.proximoMes();
    });
}

/**
 * Renderiza o quadro Kanban
 */
function renderizarQuadroKanban() {
    const quadro = document.getElementById('quadro-kanban');
    quadro.innerHTML = '';
    AppState.colunas = [];
    
    DIAS_SEMANA.forEach(dia => {
        const container = document.createElement('div');
        quadro.appendChild(container);
        
        const coluna = new ColunaKanban(dia, container, servicoTarefas, atualizarTudo);
        AppState.colunas.push(coluna);
    });
    
    // Atualizar todas as colunas
    atualizarQuadroKanban();
}

/**
 * Atualiza o quadro Kanban
 */
function atualizarQuadroKanban() {
    AppState.colunas.forEach(coluna => coluna.atualizar());
}

/**
 * Atualiza tudo
 */
function atualizarTudo() {
    atualizarQuadroKanban();
    if (AppState.tabelaAgenda) {
        AppState.tabelaAgenda.carregar();
    }
    debugLog('Interface atualizada');
}

/**
 * Alterna entre tema claro e escuro
 */
function alternarTema() {
    AppState.temaEscuro = !AppState.temaEscuro;
    repositorio.salvarTema(AppState.temaEscuro);
    aplicarTema();
    
    const temaNome = AppState.temaEscuro ? 'Modo Escuro' : 'Modo Claro';
    Animacoes.mostrarToast(`${temaNome} ativado`);
}

/**
 * Aplica o tema atual
 */
function aplicarTema() {
    const body = document.body;
    const btnTema = document.getElementById('btn-tema');
    const iconeTema = document.getElementById('icone-tema');
    const textoTema = document.getElementById('texto-tema');
    
    if (AppState.temaEscuro) {
        body.classList.remove('tema-claro');
        body.classList.add('tema-escuro');
        iconeTema.src = 'icons/sun.svg';
        textoTema.textContent = 'Modo Claro';
    } else {
        body.classList.remove('tema-escuro');
        body.classList.add('tema-claro');
        iconeTema.src = 'icons/moon.svg';
        textoTema.textContent = 'Modo Escuro';
    }
}

/**
 * Atualiza navegação de semanas
 */
function atualizarNavegacaoSemana() {
    atualizarLabelSemana();
    AppState.tabelaAgenda.carregar();
}

/**
 * Atualiza label da semana
 */
function atualizarLabelSemana() {
    const datas = UtilsDatas.obterDatasSemana(AppState.semanaOffset);
    const inicio = UtilsDatas.formatarDataCurta(datas[0]);
    const fim = UtilsDatas.formatarDataCompleta(datas[4]);
    
    let texto;
    if (AppState.semanaOffset === 0) {
        texto = `Semana Atual: ${inicio} - ${fim}`;
    } else if (AppState.semanaOffset > 0) {
        texto = `+${AppState.semanaOffset} semana(s): ${inicio} - ${fim}`;
    } else {
        texto = `${AppState.semanaOffset} semana(s): ${inicio} - ${fim}`;
    }
    
    document.getElementById('label-semana').textContent = texto;
}

/**
 * Sincroniza agenda com Kanban
 */
function sincronizarAgendaKanban() {
    const resultado = servicoSincronizacao.sincronizar();
    const diaAtual = UtilsDatas.obterDiaSemanaAtual();
    const nomeDia = diaAtual || 'hoje';
    
    if (resultado.criadas > 0) {
        Animacoes.mostrarToast(`${resultado.criadas} tarefa(s) de ${nomeDia} sincronizada(s)!`);
        atualizarTudo();
    } else if (resultado.ignoradas > 0) {
        Animacoes.mostrarToast(`Tarefas de ${nomeDia} já sincronizadas`, DURACAO_TOAST_CURTA);
    } else if (resultado.erros.length > 0) {
        Animacoes.mostrarToast(`Erro na sincronização: ${resultado.erros[0]}`, DURACAO_TOAST_MEDIA, 'erro');
    } else if (!diaAtual) {
        Animacoes.mostrarToast('Fim de semana - sem atividades', DURACAO_TOAST_CURTA);
    } else {
        Animacoes.mostrarToast(`Nenhuma atividade em ${nomeDia}`, DURACAO_TOAST_CURTA);
    }
    
    debugLog(`Sincronização: ${resultado.criadas} criadas, ${resultado.ignoradas} ignoradas`);
}

// Exportar funções globais
if (typeof window !== 'undefined') {
    window.atualizarTudo = atualizarTudo;
    window.alternarTema = alternarTema;
    window.sincronizarAgendaKanban = sincronizarAgendaKanban;
    window.AppState = AppState;
}
