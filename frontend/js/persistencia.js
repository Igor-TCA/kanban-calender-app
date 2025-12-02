/**
 * Módulo de persistência - gerencia armazenamento local (localStorage)
 * Simula o comportamento do banco de dados SQLite
 */

// =============================================================================
// UTILITÁRIOS
// =============================================================================

/**
 * Gera um ID único para entidades
 * @returns {string} ID único baseado em timestamp + random
 */
function gerarIdUnico() {
    const timestamp = Date.now().toString(36);
    const aleatorio = Math.random().toString(36).substring(2, 11);
    return timestamp + aleatorio;
}

// =============================================================================
// ARMAZENAMENTO SEGURO
// =============================================================================

/**
 * Wrapper seguro para localStorage com tratamento de erros.
 * Encapsula operações de leitura, escrita e remoção com try-catch.
 */
const StorageSeguro = {
    get(chave) {
        try {
            return localStorage.getItem(chave);
        } catch (e) {
            console.error(`Erro ao ler localStorage [${chave}]:`, e);
            return null;
        }
    },
    
    set(chave, valor) {
        try {
            localStorage.setItem(chave, valor);
            return true;
        } catch (e) {
            console.error(`Erro ao salvar localStorage [${chave}]:`, e);
            return false;
        }
    },
    
    remove(chave) {
        try {
            localStorage.removeItem(chave);
            return true;
        } catch (e) {
            console.error(`Erro ao remover localStorage [${chave}]:`, e);
            return false;
        }
    }
};

// =============================================================================
// REPOSITÓRIO PRINCIPAL
// =============================================================================

/**
 * Classe Repositório - gerencia todas as operações de persistência.
 * Fornece métodos para tarefas, horários, agenda e configurações.
 */
class Repositorio {
    constructor() {
        this._inicializarDados();
    }

    /**
     * Inicializa dados padrão se não existirem no storage
     * @private
     */
    _inicializarDados() {
        // Inicializar tarefas se não existir
        if (!StorageSeguro.get(STORAGE_KEYS.TAREFAS)) {
            StorageSeguro.set(STORAGE_KEYS.TAREFAS, JSON.stringify([]));
        }

        // Inicializar horários se não existir
        if (!StorageSeguro.get(STORAGE_KEYS.HORARIOS)) {
            // Horários padrão
            const horariosPadrao = [];
            for (let h = HORARIO_INICIO_PADRAO; h <= HORARIO_FIM_PADRAO; h++) {
                horariosPadrao.push(`${String(h).padStart(2, '0')}:00`);
            }
            StorageSeguro.set(STORAGE_KEYS.HORARIOS, JSON.stringify(horariosPadrao));
        }

        // Inicializar agenda se não existir
        if (!StorageSeguro.get(STORAGE_KEYS.AGENDA)) {
            StorageSeguro.set(STORAGE_KEYS.AGENDA, JSON.stringify({}));
        }
    }

    // =========================================================================
    // TAREFAS
    // =========================================================================

    /**
     * Obtém todas as tarefas
     */
    obterTodasTarefas() {
        const dados = StorageSeguro.get(STORAGE_KEYS.TAREFAS);
        const tarefasJSON = JSON.parse(dados || '[]');
        return tarefasJSON.map(t => Tarefa.fromJSON(t));
    }

    /**
     * Obtém tarefas de um dia específico
     */
    obterTarefasPorDia(dia) {
        return this.obterTodasTarefas()
            .filter(t => t.dia === dia)
            .sort((a, b) => a.prioridade - b.prioridade);
    }

    /**
     * Adiciona uma nova tarefa
     */
    adicionarTarefa(tarefa) {
        const tarefas = this.obterTodasTarefas();
        tarefas.push(tarefa);
        this._salvarTarefas(tarefas);
        return tarefa.id;
    }

    /**
     * Atualiza uma tarefa existente
     */
    atualizarTarefa(id, novosDados) {
        const tarefas = this.obterTodasTarefas();
        const indice = tarefas.findIndex(t => t.id === id);
        
        if (indice !== -1) {
            tarefas[indice] = { ...tarefas[indice], ...novosDados };
            this._salvarTarefas(tarefas);
            return true;
        }
        return false;
    }

    /**
     * Move uma tarefa para novo dia/status
     */
    moverTarefa(id, novoDia, novoStatus) {
        return this.atualizarTarefa(id, { dia: novoDia, status: novoStatus });
    }

    /**
     * Deleta uma tarefa
     */
    deletarTarefa(id) {
        const tarefas = this.obterTodasTarefas();
        const tarefasFiltradas = tarefas.filter(t => t.id !== id);
        this._salvarTarefas(tarefasFiltradas);
        return true;
    }

    /**
     * Verifica se uma tarefa da agenda já existe
     */
    verificarTarefaAgendaExiste(atividadeOrigemId, dataCriacao) {
        const tarefas = this.obterTodasTarefas();
        return tarefas.some(t => 
            t.atividadeOrigemId === atividadeOrigemId && 
            t.dataCriacao === dataCriacao
        );
    }

    _salvarTarefas(tarefas) {
        StorageSeguro.set(STORAGE_KEYS.TAREFAS, JSON.stringify(tarefas.map(t => t.toJSON ? t.toJSON() : t)));
    }

    // =========================================================================
    // HORÁRIOS (Grade Horária)
    // =========================================================================

    /**
     * Obtém todos os horários ordenados
     */
    obterHorariosOrdenados() {
        const dados = StorageSeguro.get(STORAGE_KEYS.HORARIOS);
        const horarios = JSON.parse(dados || '[]');
        return horarios.sort((a, b) => a.localeCompare(b));
    }

    /**
     * Adiciona um novo horário
     */
    adicionarHorario(horario) {
        const horarios = this.obterHorariosOrdenados();
        if (!horarios.includes(horario)) {
            horarios.push(horario);
            StorageSeguro.set(STORAGE_KEYS.HORARIOS, JSON.stringify(horarios));
            return true;
        }
        return false;
    }

    /**
     * Remove um horário e suas atividades
     */
    removerHorario(horario) {
        let horarios = this.obterHorariosOrdenados();
        horarios = horarios.filter(h => h !== horario);
        StorageSeguro.set(STORAGE_KEYS.HORARIOS, JSON.stringify(horarios));
        
        // Remover atividades desse horário
        const agenda = this.obterDadosGrade();
        const novaAgenda = {};
        for (const chave in agenda) {
            if (!chave.startsWith(horario + '|')) {
                novaAgenda[chave] = agenda[chave];
            }
        }
        StorageSeguro.set(STORAGE_KEYS.AGENDA, JSON.stringify(novaAgenda));
        
        return true;
    }

    // =========================================================================
    // AGENDA (Células da Grade)
    // =========================================================================

    /**
     * Obtém todos os dados da grade
     * Retorna: { "HH:MM|coluna": "texto da atividade" }
     */
    obterDadosGrade() {
        const dados = StorageSeguro.get(STORAGE_KEYS.AGENDA);
        return JSON.parse(dados || '{}');
    }

    /**
     * Salva uma atividade em uma célula específica
     */
    salvarAtividade(horario, coluna, texto) {
        const agenda = this.obterDadosGrade();
        const chave = `${horario}|${coluna}`;
        
        if (texto && texto.trim()) {
            agenda[chave] = texto;
        } else {
            delete agenda[chave];
        }
        
        StorageSeguro.set(STORAGE_KEYS.AGENDA, JSON.stringify(agenda));
        return true;
    }

    /**
     * Obtém atividade de uma célula específica
     */
    obterAtividade(horario, coluna) {
        const agenda = this.obterDadosGrade();
        return agenda[`${horario}|${coluna}`] || "";
    }

    /**
     * Obtém todas as atividades de um dia da semana (por índice 0-4)
     */
    obterAtividadesPorDia(indiceDia) {
        const agenda = this.obterDadosGrade();
        const atividades = [];
        
        for (const chave in agenda) {
            const [horario, coluna] = chave.split('|');
            if (parseInt(coluna) === indiceDia && agenda[chave]) {
                const metadados = ExtratorMetadados.extrairMetadados(agenda[chave]);
                atividades.push({
                    horario,
                    textoCompleto: agenda[chave],
                    ...metadados
                });
            }
        }
        
        return atividades.sort((a, b) => a.horario.localeCompare(b.horario));
    }

    // =========================================================================
    // TEMA
    // =========================================================================

    obterTemaEscuro() {
        return StorageSeguro.get(STORAGE_KEYS.TEMA) === 'true';
    }

    salvarTema(escuro) {
        StorageSeguro.set(STORAGE_KEYS.TEMA, escuro.toString());
    }

    // =========================================================================
    // EXPORTAR / IMPORTAR
    // =========================================================================

    exportarDados() {
        return {
            tarefas: this.obterTodasTarefas().map(t => t.toJSON()),
            horarios: this.obterHorariosOrdenados(),
            agenda: this.obterDadosGrade(),
            exportadoEm: new Date().toISOString()
        };
    }

    importarDados(dados) {
        if (dados.tarefas) {
            StorageSeguro.set(STORAGE_KEYS.TAREFAS, JSON.stringify(dados.tarefas));
        }
        if (dados.horarios) {
            StorageSeguro.set(STORAGE_KEYS.HORARIOS, JSON.stringify(dados.horarios));
        }
        if (dados.agenda) {
            StorageSeguro.set(STORAGE_KEYS.AGENDA, JSON.stringify(dados.agenda));
        }
        return true;
    }

    limparTudo() {
        StorageSeguro.remove(STORAGE_KEYS.TAREFAS);
        StorageSeguro.remove(STORAGE_KEYS.HORARIOS);
        StorageSeguro.remove(STORAGE_KEYS.AGENDA);
        this._inicializarDados();
    }
}

// Instância global do repositório
const repositorio = new Repositorio();

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.gerarIdUnico = gerarIdUnico;
    window.StorageSeguro = StorageSeguro;
    window.Repositorio = Repositorio;
    window.repositorio = repositorio;
}
