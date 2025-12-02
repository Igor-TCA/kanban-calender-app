/**
 * Módulo de componentes de interface do usuário.
 * Contém componentes reutilizáveis para a aplicação Kanban.
 */

// =============================================================================
// GERENCIADOR DE MODAIS
// =============================================================================

/**
 * Gerenciador de Modais - controla abertura, fechamento e foco de modais.
 */
const ModalManager = {
    abrirModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.add('ativo');
            document.body.classList.add('modal-aberto');
            
            // Focus no primeiro input
            const primeiroInput = modal.querySelector('input, select');
            if (primeiroInput) {
                setTimeout(() => primeiroInput.focus(), 100);
            }
        }
    },

    fecharModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove('ativo');
            document.body.classList.remove('modal-aberto');
        }
    },

    fecharTodosModais() {
        document.querySelectorAll('.modal-overlay.ativo').forEach(modal => {
            modal.classList.remove('ativo');
        });
        document.body.classList.remove('modal-aberto');
    },

    inicializar() {
        // Fechar modal ao clicar no overlay
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.classList.remove('ativo');
                    document.body.classList.remove('modal-aberto');
                }
            });
        });

        // Fechar modal ao clicar em botão de fechar
        document.querySelectorAll('[data-fechar]').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal-overlay');
                if (modal) {
                    modal.classList.remove('ativo');
                    document.body.classList.remove('modal-aberto');
                }
            });
        });

        // Fechar modal com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.fecharTodosModais();
            }
        });
    }
};

// =============================================================================
// MENU DE CONTEXTO
// =============================================================================

/**
 * Gerenciador de Menu de Contexto - exibe menus flutuantes ao clicar com botão direito.
 */
const MenuContexto = {
    menu: null,

    inicializar() {
        this.menu = document.getElementById('menu-contexto');
        
        // Fechar menu ao clicar fora
        document.addEventListener('click', () => this.fechar());
        
        // Fechar menu com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.fechar();
        });
    },

    mostrar(x, y, itens) {
        if (!this.menu) return;

        const lista = this.menu.querySelector('.menu-lista');
        lista.innerHTML = '';

        itens.forEach(item => {
            if (item.separador) {
                const separador = document.createElement('li');
                separador.className = 'menu-separador';
                lista.appendChild(separador);
            } else {
                const li = document.createElement('li');
                li.className = 'menu-item';
                li.textContent = item.texto;
                li.addEventListener('click', (e) => {
                    e.stopPropagation();
                    item.acao();
                    this.fechar();
                });
                lista.appendChild(li);
            }
        });

        // Posicionar menu
        this.menu.style.left = `${x}px`;
        this.menu.style.top = `${y}px`;
        this.menu.classList.add('visivel');

        // Ajustar posição se sair da tela
        requestAnimationFrame(() => {
            const rect = this.menu.getBoundingClientRect();
            if (rect.right > window.innerWidth) {
                this.menu.style.left = `${x - rect.width}px`;
            }
            if (rect.bottom > window.innerHeight) {
                this.menu.style.top = `${y - rect.height}px`;
            }
        });
    },

    fechar() {
        if (this.menu) {
            this.menu.classList.remove('visivel');
        }
    }
};

// =============================================================================
// COLUNA KANBAN
// =============================================================================

/**
 * Componente de Coluna Kanban - representa um dia da semana no quadro.
 * Contém listas para cada status (Fazer, Fazendo, Feito).
 */
class ColunaKanban {
    constructor(dia, container, servicoTarefas, onDadosAlterados) {
        this.dia = dia;
        this.container = container;
        this.servicoTarefas = servicoTarefas;
        this.onDadosAlterados = onDadosAlterados;
        this.listas = {};
        
        this.renderizar();
    }

    renderizar() {
        this.container.innerHTML = '';
        this.container.className = 'coluna-dia';
        
        // Cabeçalho
        const cabecalho = document.createElement('div');
        cabecalho.className = 'cabecalho-dia';
        cabecalho.textContent = this.dia;
        this.container.appendChild(cabecalho);
        
        // Seções de status
        STATUS_LISTA.forEach(status => {
            this.criarSecaoStatus(status);
        });

        // Aplicar sombra
        Animacoes.aplicarSombra(this.container, {
            raioDesfoque: 15,
            deslocamentoY: 2,
            cor: 'rgba(0, 0, 0, 0.15)'
        });
    }

    criarSecaoStatus(status) {
        const secao = document.createElement('div');
        secao.className = 'secao-status';

        const rotulo = document.createElement('div');
        rotulo.className = 'rotulo-status';
        rotulo.textContent = status;
        secao.appendChild(rotulo);

        const lista = document.createElement('ul');
        lista.className = 'lista-tarefas';
        lista.dataset.dia = this.dia;
        lista.dataset.status = status;
        
        // Configurar drag and drop
        this.configurarDropZone(lista);
        
        secao.appendChild(lista);
        this.listas[status] = lista;
        this.container.appendChild(secao);
    }

    configurarDropZone(lista) {
        lista.addEventListener('dragover', (e) => {
            e.preventDefault();
            lista.classList.add('drag-over');
        });

        lista.addEventListener('dragleave', () => {
            lista.classList.remove('drag-over');
        });

        lista.addEventListener('drop', (e) => {
            e.preventDefault();
            lista.classList.remove('drag-over');
            
            const idTarefa = e.dataTransfer.getData('text/plain');
            const novoDia = lista.dataset.dia;
            const novoStatus = lista.dataset.status;
            
            if (idTarefa) {
                this.servicoTarefas.moverTarefa(idTarefa, novoDia, novoStatus);
                this.onDadosAlterados();
            }
        });
    }

    atualizar() {
        const tarefas = this.servicoTarefas.obterTarefasDoDia(this.dia);
        
        // Limpar listas
        Object.values(this.listas).forEach(lista => lista.innerHTML = '');
        
        // Preencher listas
        tarefas.forEach(tarefa => {
            if (this.listas[tarefa.status]) {
                const item = this.criarItemTarefa(tarefa);
                this.listas[tarefa.status].appendChild(item);
            }
        });

        // Animar entrada
        Object.values(this.listas).forEach(lista => {
            Animacoes.animarItensEmSequencia(Array.from(lista.children));
        });
    }

    criarItemTarefa(tarefa) {
        const item = document.createElement('li');
        item.className = 'item-tarefa';
        item.draggable = true;
        item.dataset.id = tarefa.id;
        
        // Cor de prioridade
        const corFundo = CORES_PRIORIDADE_VIBRANTE[tarefa.prioridade] || CORES_PRIORIDADE_VIBRANTE[3];
        item.style.backgroundColor = corFundo;
        item.style.color = '#ffffff';
        
        // Título
        let titulo = ExtratorMetadados.extrairTituloLimpo(tarefa.titulo);
        if (tarefa.status === STATUS_TAREFA.FEITO) {
            titulo = this.aplicarStrikethrough(titulo);
            item.classList.add('tarefa-feita');
        }
        item.textContent = titulo;
        
        // Tooltip
        const tooltipTexto = tarefa.origem === 'agenda' 
            ? `Tarefa gerada da Agenda\nPrioridade: P${tarefa.prioridade}`
            : `Prioridade: P${tarefa.prioridade}`;
        item.title = tooltipTexto;
        
        // Drag events
        item.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', tarefa.id);
            item.classList.add('dragging');
        });

        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
        });
        
        // Menu de contexto
        item.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            MenuContexto.mostrar(e.clientX, e.clientY, [
                {
                    texto: 'Excluir',
                    acao: () => this.confirmarExclusao(tarefa.id)
                }
            ]);
        });

        return item;
    }

    aplicarStrikethrough(texto) {
        return texto.split('').map(c => c + '\u0336').join('');
    }

    confirmarExclusao(id) {
        confirmarAcao(MSG_CONFIRMAR_DELETAR_TAREFA, () => {
            this.servicoTarefas.deletarTarefa(id);
            this.onDadosAlterados();
            Animacoes.mostrarToast('Tarefa excluída');
        });
    }
}

// =============================================================================
// TABELA DE AGENDA
// =============================================================================

/**
 * Componente de Tabela de Agenda - exibe grade de horários semanal.
 * Permite visualizar e editar atividades por horário e dia.
 */
class TabelaAgenda {
    constructor(container, servicoHorarios, semanaOffset = 0) {
        this.container = container;
        this.servicoHorarios = servicoHorarios;
        this.semanaOffset = semanaOffset;
        this.horariosAtuais = [];
    }

    atualizarHeaders() {
        const headerRow = document.getElementById('header-dias');
        if (!headerRow) return;

        // Manter primeira célula (Horário)
        const primeiraCell = headerRow.firstElementChild;
        headerRow.innerHTML = '';
        headerRow.appendChild(primeiraCell);

        const datas = UtilsDatas.obterDatasSemana(this.semanaOffset);
        const hoje = new Date();

        DIAS_SEMANA_CURTO.forEach((dia, i) => {
            const th = document.createElement('th');
            const data = datas[i];
            const dataStr = UtilsDatas.formatarDataCurta(data);
            
            if (UtilsDatas.ehHoje(data)) {
                th.innerHTML = `<strong>&gt;&gt; ${dia} &lt;&lt;</strong><br>${dataStr}`;
                th.classList.add('dia-atual');
            } else {
                th.innerHTML = `${dia}<br>${dataStr}`;
            }
            
            headerRow.appendChild(th);
        });
    }

    carregar() {
        const tbody = document.getElementById('corpo-tabela');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        const horarios = this.servicoHorarios.obterHorariosOrdenados();
        this.horariosAtuais = horarios;
        const dadosGrade = this.servicoHorarios.obterDadosGrade();
        const datas = UtilsDatas.obterDatasSemana(this.semanaOffset);

        horarios.forEach(horario => {
            const tr = document.createElement('tr');
            
            // Célula do horário (header vertical)
            const thHorario = document.createElement('th');
            thHorario.className = 'celula-horario';
            thHorario.textContent = horario;
            thHorario.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.mostrarMenuHorario(e, horario);
            });
            tr.appendChild(thHorario);

            // Células dos dias
            for (let coluna = 0; coluna < TOTAL_DIAS_SEMANA; coluna++) {
                const td = this.criarCelulaDia(horario, coluna, dadosGrade, datas);
                tr.appendChild(td);
            }

            tbody.appendChild(tr);
        });

        this.atualizarHeaders();
    }

    /**
     * Busca atividade diária aplicável para a célula
     * @private
     */
    _buscarAtividadeDiaria(horario, coluna, dadosGrade, datas) {
        for (const chave in dadosGrade) {
            const [h, c] = chave.split('|');
            if (h === horario && dadosGrade[chave]) {
                const meta = ExtratorMetadados.extrairMetadados(dadosGrade[chave]);
                if (meta.periodicidade === 'diaria') {
                    const dataCriacao = meta.dataCriacao ? new Date(meta.dataCriacao) : null;
                    if (!dataCriacao || datas[coluna] >= dataCriacao) {
                        return dadosGrade[chave];
                    }
                }
            }
        }
        return '';
    }

    /**
     * Aplica estilos e conteúdo à célula baseado nos metadados
     * @private
     */
    _aplicarConteudoCelula(td, textoCompleto) {
        const metadados = ExtratorMetadados.extrairMetadados(textoCompleto);
        td.textContent = metadados.titulo;
        td.dataset.textoCompleto = textoCompleto;
        
        // Cor de fundo baseada na prioridade
        const corFundo = CORES_PRIORIDADE_SUAVE[metadados.prioridade];
        if (corFundo) {
            td.style.backgroundColor = corFundo;
            td.style.color = '#1a1a2e';
        }

        // Tooltip
        const nomePrioridade = NOMES_PRIORIDADE[metadados.prioridade] || 'N/A';
        const nomePeriodicidade = NOMES_PERIODICIDADE[metadados.periodicidade] || metadados.periodicidade;
        td.title = `Prioridade: P${metadados.prioridade} - ${nomePrioridade}\nPeriodicidade: ${nomePeriodicidade}\nCriado em: ${metadados.dataCriacao || ''}`;
    }

    /**
     * Configura eventos da célula
     * @private
     */
    _configurarEventosCelula(td, horario, coluna, textoCompleto) {
        // Menu de contexto
        td.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.mostrarMenuCelula(e, horario, coluna, textoCompleto);
        });

        // Duplo clique para editar
        td.addEventListener('dblclick', () => {
            if (textoCompleto) {
                this.editarAtividade(horario, coluna, textoCompleto);
            } else {
                this.incluirAtividadeCelula(horario, coluna);
            }
        });
    }

    /**
     * Cria uma célula de dia na tabela de agenda
     */
    criarCelulaDia(horario, coluna, dadosGrade, datas) {
        const td = document.createElement('td');
        td.className = 'celula-atividade';
        td.dataset.horario = horario;
        td.dataset.coluna = coluna;

        const chave = `${horario}|${coluna}`;
        let textoCompleto = dadosGrade[chave] || '';

        // Verificar atividades diárias se não há atividade específica
        if (!textoCompleto) {
            textoCompleto = this._buscarAtividadeDiaria(horario, coluna, dadosGrade, datas);
        }

        // Aplicar conteúdo se houver
        if (textoCompleto) {
            this._aplicarConteudoCelula(td, textoCompleto);
        }

        // Configurar eventos
        this._configurarEventosCelula(td, horario, coluna, textoCompleto);

        return td;
    }

    mostrarMenuHorario(e, horario) {
        MenuContexto.mostrar(e.clientX, e.clientY, [
            {
                texto: `Editar Horário '${horario}'`,
                acao: () => this.editarHorario(horario)
            },
            { separador: true },
            {
                texto: `Excluir Linha '${horario}'`,
                acao: () => this.excluirHorario(horario)
            }
        ]);
    }

    mostrarMenuCelula(e, horario, coluna, textoAtual) {
        const dia = DIAS_SEMANA[coluna];
        const itens = [];

        if (textoAtual) {
            itens.push({
                texto: 'Editar atividade',
                acao: () => this.editarAtividade(horario, coluna, textoAtual)
            });
            itens.push({ separador: true });
        }

        itens.push({
            texto: `Incluir atividade em ${horario}`,
            acao: () => this.incluirAtividadeCelula(horario, coluna)
        });

        if (textoAtual) {
            itens.push({
                texto: 'Limpar célula',
                acao: () => this.limparCelula(horario, coluna)
            });
        }

        MenuContexto.mostrar(e.clientX, e.clientY, itens);
    }

    editarHorario(horarioAntigo) {
        // Preencher modal com valores atuais
        const [hora, minuto] = horarioAntigo.split(':');
        document.getElementById('input-hora').value = hora;
        document.getElementById('input-minuto').value = minuto;
        atualizarPreviaHorario();

        // Abrir modal
        ModalManager.abrirModal('modal-horario');

        // Configurar callback de salvar (temporário)
        const btnSalvar = document.getElementById('btn-salvar-horario');
        const novoHandler = () => {
            const novoHorario = obterHorarioDoModal();
            if (novoHorario && novoHorario !== horarioAntigo) {
                this.servicoHorarios.removerHorario(horarioAntigo);
                this.servicoHorarios.adicionarHorario(novoHorario);
                this.carregar();
                Animacoes.mostrarToast(`Horário atualizado para ${novoHorario}`);
            }
            ModalManager.fecharModal('modal-horario');
            btnSalvar.removeEventListener('click', novoHandler);
        };
        
        btnSalvar.addEventListener('click', novoHandler, { once: true });
    }

    excluirHorario(horario) {
        confirmarAcao(
            `Tem certeza que deseja remover o horário ${horario}?\nTodos os dados dessa linha serão perdidos.`,
            () => {
                this.servicoHorarios.removerHorario(horario);
                this.carregar();
                Animacoes.mostrarToast('Horário removido');
            }
        );
    }

    editarAtividade(horario, coluna, textoCompleto) {
        const metadados = ExtratorMetadados.extrairMetadados(textoCompleto);
        const dia = DIAS_SEMANA[coluna];
        
        abrirModalAtividade({
            modo: 'editar',
            titulo: metadados.titulo,
            dia,
            horario,
            prioridade: metadados.prioridade,
            periodicidade: metadados.periodicidade,
            dataCriacao: metadados.dataCriacao,
            onSalvar: (dados) => {
                const novoTexto = ExtratorMetadados.formatarAtividade({
                    titulo: dados.titulo,
                    prioridade: dados.prioridade,
                    periodicidade: dados.periodicidade,
                    dataCriacao: metadados.dataCriacao // Manter data original
                });

                // Se mudou de posição, limpar antiga
                const novoIndice = DIAS_SEMANA.indexOf(dados.dia);
                if (dados.horario !== horario || novoIndice !== coluna) {
                    this.servicoHorarios.salvarAtividade(horario, coluna, '');
                    
                    // Verificar se novo horário existe
                    const horarios = this.servicoHorarios.obterHorariosOrdenados();
                    if (!horarios.includes(dados.horario)) {
                        this.servicoHorarios.adicionarHorario(dados.horario);
                    }
                }

                this.servicoHorarios.salvarAtividade(dados.horario, novoIndice, novoTexto);
                this.carregar();
                Animacoes.mostrarToast('Atividade atualizada');
            }
        });
    }

    incluirAtividadeCelula(horario, coluna) {
        const dia = DIAS_SEMANA[coluna];
        
        abrirModalAtividade({
            modo: 'incluir',
            dia,
            horario,
            onSalvar: (dados) => {
                const novoTexto = ExtratorMetadados.formatarAtividade({
                    titulo: dados.titulo,
                    prioridade: dados.prioridade,
                    periodicidade: dados.periodicidade
                });

                this.servicoHorarios.salvarAtividade(horario, coluna, novoTexto);
                this.carregar();
                Animacoes.mostrarToast('Atividade adicionada');
            }
        });
    }

    limparCelula(horario, coluna) {
        this.servicoHorarios.salvarAtividade(horario, coluna, '');
        this.carregar();
        Animacoes.mostrarToast('Célula limpa');
    }
}

/**
 * Componente de Calendário Mensal
 */
class CalendarioMensal {
    constructor(container, servicoHorarios) {
        this.container = container;
        this.servicoHorarios = servicoHorarios;
        this.mesAtual = new Date().getMonth();
        this.anoAtual = new Date().getFullYear();
        this.atividadesPorDia = {};
    }

    carregarAtividades() {
        this.atividadesPorDia = {};
        const dadosGrade = this.servicoHorarios.obterDadosGrade();

        for (const chave in dadosGrade) {
            const [horario, coluna] = chave.split('|');
            const texto = dadosGrade[chave];
            
            if (texto && texto.trim()) {
                const colunaNum = parseInt(coluna);
                if (!this.atividadesPorDia[colunaNum]) {
                    this.atividadesPorDia[colunaNum] = [];
                }
                
                const metadados = ExtratorMetadados.extrairMetadados(texto);
                this.atividadesPorDia[colunaNum].push({ horario, ...metadados });
            }
        }

        // Ordenar por horário
        for (const coluna in this.atividadesPorDia) {
            this.atividadesPorDia[coluna].sort((a, b) => a.horario.localeCompare(b.horario));
        }
    }

    renderizar() {
        this.carregarAtividades();
        this.atualizarLabel();
        this.renderizarGrid();
    }

    atualizarLabel() {
        const label = document.getElementById('label-mes');
        if (label) {
            label.textContent = `${UtilsDatas.obterNomeMes(this.mesAtual)} ${this.anoAtual}`;
        }
    }

    renderizarGrid() {
        const grid = document.getElementById('calendario-grid');
        if (!grid) return;

        grid.innerHTML = '';

        // Dias da semana
        const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
        diasSemana.forEach(dia => {
            const cell = document.createElement('div');
            cell.className = 'calendario-dia-semana';
            cell.textContent = dia;
            grid.appendChild(cell);
        });

        // Primeiro dia do mês
        const primeiroDia = new Date(this.anoAtual, this.mesAtual, 1);
        const ultimoDia = new Date(this.anoAtual, this.mesAtual + 1, 0);
        
        // Dias em branco antes do primeiro dia
        for (let i = 0; i < primeiroDia.getDay(); i++) {
            const cell = document.createElement('div');
            cell.className = 'calendario-dia vazio';
            grid.appendChild(cell);
        }

        // Dias do mês
        for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
            const cell = this.criarCelulaDia(dia);
            grid.appendChild(cell);
        }
    }

    criarCelulaDia(dia) {
        const cell = document.createElement('div');
        cell.className = 'calendario-dia';
        cell.textContent = dia;

        const data = new Date(this.anoAtual, this.mesAtual, dia);
        const diaSemana = data.getDay();
        const hoje = new Date();

        // Marcar hoje
        if (data.toDateString() === hoje.toDateString()) {
            cell.classList.add('hoje');
        }

        // Marcar fim de semana
        if (diaSemana === 0 || diaSemana === 6) {
            cell.classList.add('fim-de-semana');
        } else {
            // Verificar atividades para este dia
            const indiceDia = diaSemana - 1; // 0-4 para seg-sex
            const prioridades = this.obterPrioridadesDoDia(data, indiceDia);
            
            if (prioridades.length > 0) {
                const maiorPrioridade = Math.min(...prioridades);
                const cor = CORES_PRIORIDADE_VIBRANTE[maiorPrioridade];
                cell.style.backgroundColor = cor;
                cell.style.color = '#ffffff';
                cell.style.fontWeight = 'bold';
            }
        }

        // Click para ver atividades
        cell.addEventListener('click', () => {
            this.mostrarAtividadesDoDia(data, diaSemana);
        });

        return cell;
    }

    obterPrioridadesDoDia(data, indiceDia) {
        const prioridades = [];

        for (const coluna in this.atividadesPorDia) {
            const atividades = this.atividadesPorDia[coluna];
            
            for (const atividade of atividades) {
                if (atividade.periodicidade === 'diaria') {
                    if (ExtratorMetadados.atividadeValidaParaData(data, 'diaria', atividade.dataCriacao)) {
                        prioridades.push(atividade.prioridade);
                    }
                } else if (parseInt(coluna) === indiceDia) {
                    if (ExtratorMetadados.atividadeValidaParaData(data, atividade.periodicidade, atividade.dataCriacao)) {
                        prioridades.push(atividade.prioridade);
                    }
                }
            }
        }

        return prioridades;
    }

    mostrarAtividadesDoDia(data, diaSemana) {
        const label = document.getElementById('label-data-selecionada');
        const lista = document.getElementById('lista-atividades-dia');
        
        if (!label || !lista) return;

        lista.innerHTML = '';

        if (diaSemana === 0 || diaSemana === 6) {
            label.textContent = `${UtilsDatas.formatarDataCompleta(data)} (Fim de semana)`;
            return;
        }

        const indiceDia = diaSemana - 1;
        const nomeDia = DIAS_SEMANA[indiceDia];
        label.textContent = `${UtilsDatas.formatarDataCompleta(data)} - ${nomeDia}`;

        // Coletar atividades válidas
        const atividadesValidas = [];

        for (const coluna in this.atividadesPorDia) {
            const atividades = this.atividadesPorDia[coluna];
            
            for (const atividade of atividades) {
                if (atividade.periodicidade === 'diaria') {
                    if (ExtratorMetadados.atividadeValidaParaData(data, 'diaria', atividade.dataCriacao)) {
                        atividadesValidas.push(atividade);
                    }
                } else if (parseInt(coluna) === indiceDia) {
                    if (ExtratorMetadados.atividadeValidaParaData(data, atividade.periodicidade, atividade.dataCriacao)) {
                        atividadesValidas.push(atividade);
                    }
                }
            }
        }

        // Ordenar e exibir
        atividadesValidas.sort((a, b) => a.horario.localeCompare(b.horario));

        if (atividadesValidas.length === 0) {
            const li = document.createElement('li');
            li.textContent = MSG_NENHUMA_ATIVIDADE;
            li.className = 'sem-atividades';
            lista.appendChild(li);
        } else {
            atividadesValidas.forEach(ativ => {
                const li = document.createElement('li');
                li.textContent = `${ativ.horario} - ${ativ.titulo}`;
                li.style.color = CORES_PRIORIDADE_VIBRANTE[ativ.prioridade];
                lista.appendChild(li);
            });
        }
    }

    mesAnterior() {
        this.mesAtual--;
        if (this.mesAtual < 0) {
            this.mesAtual = 11;
            this.anoAtual--;
        }
        this.renderizar();
    }

    proximoMes() {
        this.mesAtual++;
        if (this.mesAtual > 11) {
            this.mesAtual = 0;
            this.anoAtual++;
        }
        this.renderizar();
    }
}

// Funções auxiliares
function obterHorarioDoModal() {
    const hora = document.getElementById('input-hora').value.padStart(2, '0');
    const minuto = document.getElementById('input-minuto').value.padStart(2, '0');
    return `${hora}:${minuto}`;
}

function atualizarPreviaHorario() {
    const hora = document.getElementById('input-hora').value.padStart(2, '0');
    const minuto = document.getElementById('input-minuto').value.padStart(2, '0');
    const previa = document.getElementById('previa-horario');
    if (previa) {
        previa.textContent = `${hora}:${minuto} horas`;
    }
}

function abrirModalAtividade(opcoes) {
    const {
        modo = 'incluir',
        titulo = '',
        dia = DIAS_SEMANA[0],
        horario = '09:00',
        prioridade = 3,
        periodicidade = 'semanal',
        dataCriacao = null,
        onSalvar
    } = opcoes;

    // Configurar título do modal
    document.getElementById('titulo-modal-atividade').textContent = 
        modo === 'editar' ? 'Editar Atividade' : 'Nova Atividade';

    // Preencher campos
    document.getElementById('input-titulo-atividade').value = titulo;
    document.getElementById('select-dia-atividade').value = dia;
    
    const [hora, minuto] = horario.split(':');
    document.getElementById('input-hora-atividade').value = hora;
    document.getElementById('input-minuto-atividade').value = minuto;
    
    document.getElementById('select-prioridade').value = prioridade;
    document.getElementById('select-periodicidade').value = periodicidade;

    // Abrir modal
    ModalManager.abrirModal('modal-atividade');

    // Configurar callback de salvar
    const btnSalvar = document.getElementById('btn-salvar-atividade');
    const handler = () => {
        const novoTitulo = document.getElementById('input-titulo-atividade').value.trim();
        
        if (!novoTitulo) {
            Animacoes.shake(document.getElementById('input-titulo-atividade'));
            Animacoes.mostrarToast(MSG_TITULO_OBRIGATORIO, DURACAO_TOAST_CURTA, 'erro');
            return;
        }

        const horaAtiv = document.getElementById('input-hora-atividade').value.padStart(2, '0');
        const minutoAtiv = document.getElementById('input-minuto-atividade').value.padStart(2, '0');

        onSalvar({
            titulo: novoTitulo,
            dia: document.getElementById('select-dia-atividade').value,
            horario: `${horaAtiv}:${minutoAtiv}`,
            prioridade: parseInt(document.getElementById('select-prioridade').value),
            periodicidade: document.getElementById('select-periodicidade').value
        });

        ModalManager.fecharModal('modal-atividade');
        btnSalvar.removeEventListener('click', handler);
    };

    btnSalvar.addEventListener('click', handler, { once: true });
}

function confirmarAcao(mensagem, onConfirmar) {
    document.getElementById('texto-confirmacao').textContent = mensagem;
    ModalManager.abrirModal('modal-confirmar');

    const btnSim = document.getElementById('btn-confirmar-sim');
    const btnNao = document.getElementById('btn-confirmar-nao');

    const limpar = () => {
        ModalManager.fecharModal('modal-confirmar');
        btnSim.removeEventListener('click', handleSim);
        btnNao.removeEventListener('click', handleNao);
    };

    const handleSim = () => {
        limpar();
        onConfirmar();
    };

    const handleNao = () => {
        limpar();
    };

    btnSim.addEventListener('click', handleSim, { once: true });
    btnNao.addEventListener('click', handleNao, { once: true });
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.ModalManager = ModalManager;
    window.MenuContexto = MenuContexto;
    window.ColunaKanban = ColunaKanban;
    window.TabelaAgenda = TabelaAgenda;
    window.CalendarioMensal = CalendarioMensal;
    window.atualizarPreviaHorario = atualizarPreviaHorario;
    window.obterHorarioDoModal = obterHorarioDoModal;
    window.abrirModalAtividade = abrirModalAtividade;
    window.confirmarAcao = confirmarAcao;
}
