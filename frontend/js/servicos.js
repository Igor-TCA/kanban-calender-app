/**
 * Camada de serviço - abstrai lógica de negócio entre UI e persistência.
 * Este módulo contém os serviços principais da aplicação.
 */

// =============================================================================
// UTILITÁRIOS DE DEBUG
// =============================================================================

/**
 * Log condicional para debug.
 * Só exibe mensagens quando DEBUG_MODE está ativo.
 * @param {...any} args - Argumentos para logar
 */
function debugLog(...args) {
    if (typeof DEBUG_MODE !== 'undefined' && DEBUG_MODE) {
        console.log('[DEBUG]', ...args);
    }
}

// =============================================================================
// SERVIÇO DE TAREFAS
// =============================================================================

/**
 * Serviço para gerenciar operações de tarefas.
 * Encapsula a lógica de negócio relacionada a tarefas do Kanban.
 */
class ServicoTarefas {
    /**
     * @param {Repositorio} repositorio - Instância do repositório
     */
    constructor(repositorio) {
        this.repositorio = repositorio;
    }

    /**
     * Cria uma nova tarefa
     * @param {Object} dados - Dados da tarefa
     * @returns {string|null} ID da tarefa criada ou null em caso de erro
     */
    criarTarefa({ titulo, dia, status = STATUS_TAREFA.FAZER, prioridade = PRIORIDADE_PADRAO, origem = "manual", atividadeOrigemId = null }) {
        if (!titulo || !titulo.trim()) {
            console.warn("[ServicoTarefas] Tentativa de criar tarefa sem título");
            return null;
        }

        const tarefa = new Tarefa({
            titulo: titulo.trim(),
            dia,
            status,
            prioridade,
            origem,
            atividadeOrigemId,
            dataCriacao: UtilsDatas.obterDataHoje()
        });

        const id = this.repositorio.adicionarTarefa(tarefa);
        debugLog(`Tarefa '${titulo}' criada com ID ${id} (prioridade P${prioridade})`);
        return id;
    }

    /**
     * Move uma tarefa para novo dia e/ou status
     * @param {string} id - ID da tarefa
     * @param {string} novoDia - Novo dia da semana
     * @param {string} novoStatus - Novo status
     * @returns {boolean} True se sucesso
     */
    moverTarefa(id, novoDia, novoStatus) {
        try {
            this.repositorio.moverTarefa(id, novoDia, novoStatus);
            debugLog(`Tarefa ${id} movida para ${novoDia}/${novoStatus}`);
            return true;
        } catch (erro) {
            console.error(`[ServicoTarefas] Erro ao mover tarefa ${id}:`, erro);
            return false;
        }
    }

    /**
     * Deleta uma tarefa
     * @param {string} id - ID da tarefa
     * @returns {boolean} True se sucesso
     */
    deletarTarefa(id) {
        try {
            this.repositorio.deletarTarefa(id);
            debugLog(`Tarefa ${id} deletada`);
            return true;
        } catch (erro) {
            console.error(`[ServicoTarefas] Erro ao deletar tarefa ${id}:`, erro);
            return false;
        }
    }

    /**
     * Obtém todas as tarefas de um dia específico
     * @param {string} dia - Nome do dia
     * @returns {Tarefa[]} Lista de tarefas
     */
    obterTarefasDoDia(dia) {
        try {
            return this.repositorio.obterTarefasPorDia(dia);
        } catch (erro) {
            console.error(`[ServicoTarefas] Erro ao obter tarefas do dia ${dia}:`, erro);
            return [];
        }
    }

    /**
     * Obtém todas as tarefas
     * @returns {Tarefa[]} Lista de todas as tarefas
     */
    obterTodasTarefas() {
        return this.repositorio.obterTodasTarefas();
    }
}

// =============================================================================
// SERVIÇO DE HORÁRIOS
// =============================================================================

/**
 * Serviço para gerenciar operações de horários/agenda.
 * Encapsula a lógica de negócio relacionada à grade de horários.
 */
class ServicoHorarios {
    /**
     * @param {Repositorio} repositorio - Instância do repositório
     */
    constructor(repositorio) {
        this.repositorio = repositorio;
    }

    /**
     * Obtém todos os horários ordenados cronologicamente
     * @returns {string[]} Lista de horários ordenados
     */
    obterHorariosOrdenados() {
        return this.repositorio.obterHorariosOrdenados();
    }

    /**
     * Adiciona um novo horário à grade
     * @param {string} horario - Horário no formato HH:MM
     * @returns {boolean} True se adicionado com sucesso
     */
    adicionarHorario(horario) {
        return this.repositorio.adicionarHorario(horario);
    }

    /**
     * Remove um horário e suas atividades
     * @param {string} horario - Horário a remover
     * @returns {boolean} True se removido com sucesso
     */
    removerHorario(horario) {
        return this.repositorio.removerHorario(horario);
    }

    /**
     * Obtém todos os dados da grade de horários
     * @returns {Object} Dados da grade
     */
    obterDadosGrade() {
        return this.repositorio.obterDadosGrade();
    }

    /**
     * Salva uma atividade em uma célula específica
     * @param {string} horario - Horário da célula
     * @param {number} coluna - Índice da coluna (dia)
     * @param {string} texto - Texto da atividade
     * @returns {boolean} True se salvo com sucesso
     */
    salvarAtividade(horario, coluna, texto) {
        return this.repositorio.salvarAtividade(horario, coluna, texto);
    }

    /**
     * Obtém atividades de um dia específico
     * @param {number} indiceDia - Índice do dia (0-4)
     * @returns {Object[]} Lista de atividades
     */
    obterAtividadesPorDia(indiceDia) {
        return this.repositorio.obterAtividadesPorDia(indiceDia);
    }
}

// =============================================================================
// SERVIÇO DE SINCRONIZAÇÃO
// =============================================================================

/**
 * Serviço para sincronização entre Agenda e Kanban.
 * Converte atividades da agenda em tarefas do quadro Kanban.
 */
class ServicoSincronizacao {
    /**
     * @param {Repositorio} repositorio - Instância do repositório
     * @param {ServicoTarefas} servicoTarefas - Serviço de tarefas
     */
    constructor(repositorio, servicoTarefas) {
        this.repositorio = repositorio;
        this.servicoTarefas = servicoTarefas;
    }

    /**
     * Sincroniza atividades do dia atual para o Kanban
     * @returns {Object} Resultado com estatísticas da sincronização
     */
    sincronizar() {
        const diaAtual = UtilsDatas.obterDiaSemanaAtual();
        
        if (!diaAtual) {
            return {
                criadas: 0,
                ignoradas: 0,
                erros: [],
                mensagem: MSG_SEM_ATIVIDADES_FIM_SEMANA
            };
        }

        const indiceDia = UtilsDatas.obterIndiceDia(diaAtual);
        const atividades = this.repositorio.obterAtividadesPorDia(indiceDia);
        
        const resultado = {
            criadas: 0,
            ignoradas: 0,
            erros: []
        };

        const hoje = UtilsDatas.obterDataHoje();

        for (const atividade of atividades) {
            try {
                // Verificar se a atividade é válida para hoje
                if (!ExtratorMetadados.atividadeValidaParaData(hoje, atividade.periodicidade, atividade.dataCriacao)) {
                    continue;
                }

                // Verificar se já existe uma tarefa para esta atividade hoje
                // Usamos o horário + título como identificador único
                const identificador = `${atividade.horario}_${atividade.titulo}`;
                const jaExiste = this.repositorio.obterTodasTarefas().some(tarefa => 
                    tarefa.origem === 'agenda' && 
                    tarefa.dataCriacao === hoje &&
                    tarefa.titulo === atividade.titulo
                );

                if (jaExiste) {
                    resultado.ignoradas++;
                    continue;
                }

                // Criar tarefa
                const id = this.servicoTarefas.criarTarefa({
                    titulo: atividade.titulo,
                    dia: diaAtual,
                    status: STATUS_TAREFA.FAZER,
                    prioridade: atividade.prioridade,
                    origem: 'agenda',
                    atividadeOrigemId: identificador
                });

                if (id) {
                    resultado.criadas++;
                } else {
                    resultado.erros.push(`Erro ao criar tarefa: ${atividade.titulo}`);
                }
            } catch (erro) {
                resultado.erros.push(erro.message);
            }
        }

        return resultado;
    }
}

// =============================================================================
// INSTÂNCIAS E EXPORTAÇÕES
// =============================================================================

// Instâncias globais dos serviços (injetando dependências)
const servicoTarefas = new ServicoTarefas(repositorio);
const servicoHorarios = new ServicoHorarios(repositorio);
const servicoSincronizacao = new ServicoSincronizacao(repositorio, servicoTarefas);

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.debugLog = debugLog;
    window.ServicoTarefas = ServicoTarefas;
    window.ServicoHorarios = ServicoHorarios;
    window.ServicoSincronizacao = ServicoSincronizacao;
    window.servicoTarefas = servicoTarefas;
    window.servicoHorarios = servicoHorarios;
    window.servicoSincronizacao = servicoSincronizacao;
}
