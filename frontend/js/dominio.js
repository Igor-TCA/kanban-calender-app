/**
 * Módulo de domínio - define entidades e classes do sistema.
 * Totalmente em PT-BR.
 */

/**
 * Classe para representar uma Tarefa do Kanban
 */
class Tarefa {
    constructor({
        id = null,
        titulo = "",
        dia = "Segunda-Feira",
        status = STATUS_TAREFA.FAZER,
        horario = "",
        prioridade = PRIORIDADE_PADRAO,
        origem = "manual",
        atividadeOrigemId = null,
        dataCriacao = null
    } = {}) {
        this.id = id || gerarIdUnico();
        this.titulo = titulo;
        this.dia = dia;
        this.status = status;
        this.horario = horario;
        this.prioridade = prioridade;
        this.origem = origem;
        this.atividadeOrigemId = atividadeOrigemId;
        this.dataCriacao = dataCriacao || new Date().toISOString().split('T')[0];
    }

    static fromJSON(json) {
        return new Tarefa(json);
    }

    toJSON() {
        return {
            id: this.id,
            titulo: this.titulo,
            dia: this.dia,
            status: this.status,
            horario: this.horario,
            prioridade: this.prioridade,
            origem: this.origem,
            atividadeOrigemId: this.atividadeOrigemId,
            dataCriacao: this.dataCriacao
        };
    }
}

/**
 * Classe para representar uma Atividade da Agenda Semanal
 */
class AtividadeAgenda {
    constructor({
        id = null,
        titulo = "",
        diaSemana = "Segunda-Feira",
        horario = "09:00",
        prioridade = PRIORIDADE_PADRAO,
        periodicidade = "semanal",
        ativa = true,
        ultimaGeracao = null,
        dataCriacao = null
    } = {}) {
        this.id = id || gerarIdUnico();
        this.titulo = titulo;
        this.diaSemana = diaSemana;
        this.horario = horario;
        this.prioridade = prioridade;
        this.periodicidade = periodicidade;
        this.ativa = ativa;
        this.ultimaGeracao = ultimaGeracao;
        this.dataCriacao = dataCriacao || new Date().toISOString().split('T')[0];
    }

    static fromJSON(json) {
        return new AtividadeAgenda(json);
    }

    toJSON() {
        return {
            id: this.id,
            titulo: this.titulo,
            diaSemana: this.diaSemana,
            horario: this.horario,
            prioridade: this.prioridade,
            periodicidade: this.periodicidade,
            ativa: this.ativa,
            ultimaGeracao: this.ultimaGeracao,
            dataCriacao: this.dataCriacao
        };
    }
}

/**
 * Classe para representar metadados de uma atividade
 */
class MetadadosAtividade {
    constructor({
        titulo = "",
        prioridade = PRIORIDADE_PADRAO,
        periodicidade = "semanal",
        dataCriacao = null
    } = {}) {
        this.titulo = titulo;
        this.prioridade = prioridade;
        this.periodicidade = periodicidade;
        this.dataCriacao = dataCriacao;
    }
}

/**
 * Utilitário para extrair e formatar metadados de atividades
 */
const ExtratorMetadados = {
    /**
     * Extrai metadados de um texto formatado
     * Formato esperado: "titulo [P{n}] [{periodicidade}] [criado:{data}]"
     */
    extrairMetadados(texto) {
        if (!texto || typeof texto !== 'string') {
            return new MetadadosAtividade();
        }

        let titulo = texto;
        let prioridade = 3;
        let periodicidade = "semanal";
        let dataCriacao = null;

        // Extrair prioridade [P0-P3]
        const regexPrioridade = /\[P([0-3])\]/i;
        const matchPrioridade = texto.match(regexPrioridade);
        if (matchPrioridade) {
            prioridade = parseInt(matchPrioridade[1]);
            titulo = titulo.replace(regexPrioridade, '');
        }

        // Extrair periodicidade
        const regexPeriodicidade = /\[(unica|diaria|semanal|quinzenal|mensal)\]/i;
        const matchPeriodicidade = texto.match(regexPeriodicidade);
        if (matchPeriodicidade) {
            periodicidade = matchPeriodicidade[1].toLowerCase();
            titulo = titulo.replace(regexPeriodicidade, '');
        }

        // Extrair data de criação
        const regexData = /\[criado:(\d{4}-\d{2}-\d{2})\]/;
        const matchData = texto.match(regexData);
        if (matchData) {
            dataCriacao = matchData[1];
            titulo = titulo.replace(regexData, '');
        }

        // Limpar título
        titulo = titulo.trim();

        return new MetadadosAtividade({ titulo, prioridade, periodicidade, dataCriacao });
    },

    /**
     * Formata uma atividade com metadados
     */
    formatarAtividade({ titulo, prioridade = 3, periodicidade = "semanal", dataCriacao = null }) {
        const partes = [titulo];
        partes.push(`[P${prioridade}]`);
        partes.push(`[${periodicidade}]`);
        
        if (dataCriacao) {
            partes.push(`[criado:${dataCriacao}]`);
        } else {
            partes.push(`[criado:${new Date().toISOString().split('T')[0]}]`);
        }

        return partes.join(' ');
    },

    /**
     * Extrai apenas o título limpo (sem metadados)
     */
    extrairTituloLimpo(texto) {
        return this.extrairMetadados(texto).titulo;
    },

    /**
     * Verifica se uma atividade é válida para uma determinada data
     */
    atividadeValidaParaData(data, periodicidade, dataCriacao) {
        if (!dataCriacao) return true;
        
        const dataObj = typeof data === 'string' ? new Date(data) : data;
        const dataCriacaoObj = new Date(dataCriacao);
        
        // Se a data é anterior à criação, não é válida
        if (dataObj < dataCriacaoObj) return false;

        switch (periodicidade) {
            case "unica":
                // Única vez só aparece na data de criação
                return dataObj.toISOString().split('T')[0] === dataCriacao;
            case "diaria":
                return true;
            case "semanal":
                return true; // Aparece toda semana no mesmo dia
            case "quinzenal":
                const diffDias = Math.floor((dataObj - dataCriacaoObj) / (1000 * 60 * 60 * 24));
                return diffDias % DIAS_QUINZENAL < DIAS_SEMANA_PERIODICIDADE;
            case "mensal":
                return dataObj.getDate() === dataCriacaoObj.getDate();
            default:
                return true;
        }
    }
};

/**
 * Utilitários de data
 */
const UtilsDatas = {
    /**
     * Obtém a data de hoje no formato ISO (YYYY-MM-DD)
     * @returns {string} Data formatada
     */
    obterDataHoje() {
        return new Date().toISOString().split('T')[0];
    },

    /**
     * Obtém o dia da semana atual como string
     */
    obterDiaSemanaAtual() {
        const hoje = new Date();
        const diaSemana = hoje.getDay();
        
        // 0 = Domingo, 6 = Sábado
        if (diaSemana === 0 || diaSemana === 6) {
            return null; // Fim de semana
        }
        
        return DIAS_SEMANA[diaSemana - 1];
    },

    /**
     * Obtém as datas de segunda a sexta de uma semana
     */
    obterDatasSemana(offsetSemanas = 0) {
        const hoje = new Date();
        const diasDesdeSegunda = (hoje.getDay() + 6) % 7;
        const segunda = new Date(hoje);
        segunda.setDate(hoje.getDate() - diasDesdeSegunda + (offsetSemanas * 7));
        
        const datas = [];
        for (let i = 0; i < 5; i++) {
            const data = new Date(segunda);
            data.setDate(segunda.getDate() + i);
            datas.push(data);
        }
        
        return datas;
    },

    /**
     * Formata uma data como DD/MM
     */
    formatarDataCurta(data) {
        const dia = String(data.getDate()).padStart(2, '0');
        const mes = String(data.getMonth() + 1).padStart(2, '0');
        return `${dia}/${mes}`;
    },

    /**
     * Formata uma data como DD/MM/YYYY
     */
    formatarDataCompleta(data) {
        const dia = String(data.getDate()).padStart(2, '0');
        const mes = String(data.getMonth() + 1).padStart(2, '0');
        const ano = data.getFullYear();
        return `${dia}/${mes}/${ano}`;
    },

    /**
     * Obtém o índice do dia da semana (0-4 para seg-sex)
     */
    obterIndiceDia(diaSemana) {
        return DIAS_SEMANA.indexOf(diaSemana);
    },

    /**
     * Verifica se uma data é hoje
     */
    ehHoje(data) {
        const hoje = new Date();
        return data.toDateString() === hoje.toDateString();
    },

    /**
     * Verifica se é fim de semana
     */
    ehFimDeSemana(data) {
        const dia = data.getDay();
        return dia === 0 || dia === 6;
    },

    /**
     * Obtém o nome do mês
     */
    obterNomeMes(mesIndex) {
        const meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ];
        return meses[mesIndex];
    }
};

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.Tarefa = Tarefa;
    window.AtividadeAgenda = AtividadeAgenda;
    window.MetadadosAtividade = MetadadosAtividade;
    window.ExtratorMetadados = ExtratorMetadados;
    window.UtilsDatas = UtilsDatas;
}
