"""
Módulo de componentes de interface do usuário.
Refatorado para incluir layout horizontal de horários conforme especificação de design.
"""
import logging
from typing import Dict, Tuple, Optional, List
from datetime import date, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, 
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QLineEdit, QDialogButtonBox, QMessageBox, QSpinBox,
    QPushButton, QGridLayout, QFrame, QCalendarWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal, QTimer, QPoint, pyqtProperty, QPropertyAnimation, QEasingCurve, QDate
from PyQt6.QtGui import QDrag, QAction, QFont, QColor, QPainter, QPen, QTextCharFormat, QBrush

from dominio import (
    DiaDaSemana, StatusTarefa, Prioridade, Periodicidade,
    converter_string_para_dia, converter_string_para_status,
    ExtratorMetadados, MetadadosAtividade
)
from servicos import ServicoTarefas, ServicoHorarios
from animacoes import aplicar_sombra, fade_in
from constantes import (
    LARGURA_DIALOGO_TAREFA, ALTURA_DIALOGO_TAREFA, LARGURA_DIALOGO_HORARIO,
    ALTURA_DIALOGO_HORARIO, DESFOQUE_SOMBRA_DIALOGO, DESLOCAMENTO_Y_SOMBRA_DIALOGO,
    COR_SOMBRA_DIALOGO, ATRASO_FADE_DIALOGO, DURACAO_FADE_DIALOGO,
    HORARIO_INICIAL_SPINBOX, MINUTO_INICIAL_SPINBOX, LARGURA_MINIMA_SPINBOX,
    ALTURA_MINIMA_SPINBOX, ALTURA_MINIMA_LISTA, ESTILO_BOTAO_ADICIONAR_HORARIO,
    ESTILO_LABEL_PREVIA_HORARIO, ESTILO_SPINBOX, ESTILO_TITULO_DIALOGO,
    ESTILO_ROTULO_STATUS, DURACAO_RIPPLE,
    ESTILO_DIALOGO_TITULO, ESTILO_DIALOGO_LABEL_INPUT, ESTILO_DIALOGO_BOX_PREVIA,
    CORES_PRIORIDADE_VIBRANTE, CORES_PRIORIDADE_SUAVE, NOMES_PRIORIDADE,
    DESCRICOES_PRIORIDADE, NOMES_PERIODICIDADE, LISTA_PERIODICIDADES,
    INDICE_PERIODICIDADE,
    MSG_TITULO_OBRIGATORIO, MSG_ERRO_ATUALIZAR_HORARIO, MSG_ERRO_EDITAR_HORARIO,
    MSG_ERRO_REMOVER_HORARIO, MSG_CONFIRMAR_EXCLUSAO_HORARIO,
    MSG_CONFIRMAR_DELETAR_TAREFA, MSG_NENHUMA_ATIVIDADE, MSG_FIM_DE_SEMANA,
    TOOLTIP_TAREFA_AGENDA, TOOLTIP_TAREFA_MANUAL, TOOLTIP_ATIVIDADE,
    TOOLTIP_SINCRONIZAR
)

logger = logging.getLogger(__name__)


class BotaoEstilizado(QPushButton):
    """Botão com efeito ripple ao clicar."""
    
    def __init__(self, texto: str = "", pai: Optional[QWidget] = None):
        super().__init__(texto, pai)
        self._raio_ripple = 0
        self._posicao_clique = QPoint()
        self._animacao_ripple: Optional[QPropertyAnimation] = None
        
    @pyqtProperty(int)
    def raio_ripple(self) -> int:
        return self._raio_ripple
    
    @raio_ripple.setter
    def raio_ripple(self, valor: int) -> None:
        self._raio_ripple = valor
        self.update()
    
    def mousePressEvent(self, evento):
        """Inicia animação ripple ao clicar."""
        self._posicao_clique = evento.pos()
        raio_maximo = max(self.width(), self.height())
        
        self._animacao_ripple = QPropertyAnimation(self, b"raio_ripple")
        self._animacao_ripple.setDuration(DURACAO_RIPPLE)
        self._animacao_ripple.setStartValue(0)
        self._animacao_ripple.setEndValue(raio_maximo)
        self._animacao_ripple.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animacao_ripple.finished.connect(lambda: setattr(self, '_raio_ripple', 0))
        self._animacao_ripple.start()
        
        super().mousePressEvent(evento)
    
    def paintEvent(self, evento):
        """Desenha o efeito ripple."""
        super().paintEvent(evento)
        
        if self._raio_ripple > 0:
            pintor = QPainter(self)
            pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
            pintor.setBrush(QColor(255, 255, 255, 70))
            pintor.setPen(QPen(Qt.PenStyle.NoPen))
            pintor.drawEllipse(
                self._posicao_clique,
                self._raio_ripple,
                self._raio_ripple
            )


class DialogoBase(QDialog):
    """Classe base para diálogos com efeitos visuais padronizados."""
    
    def __init__(self, titulo: str, largura: int, altura: int, pai: Optional[QWidget] = None):
        super().__init__(pai)
        self.setWindowTitle(titulo)
        self.setFixedSize(largura, altura)
        self._aplicar_efeitos_visuais()
    
    def _aplicar_efeitos_visuais(self) -> None:
        """Aplica sombra e animação de fade in ao diálogo."""
        QTimer.singleShot(
            ATRASO_FADE_DIALOGO, 
            lambda: aplicar_sombra(
                self, 
                raio_desfoque=DESFOQUE_SOMBRA_DIALOGO,
                deslocamento_y=DESLOCAMENTO_Y_SOMBRA_DIALOGO,
                cor=COR_SOMBRA_DIALOGO
            )
        )
        QTimer.singleShot(
            ATRASO_FADE_DIALOGO + 10, 
            lambda: fade_in(self, DURACAO_FADE_DIALOGO)
        )


class DialogoTarefa(DialogoBase):
    """Diálogo para criar nova tarefa."""
    
    def __init__(self, pai: Optional[QWidget] = None):
        super().__init__("Nova Tarefa", LARGURA_DIALOGO_TAREFA, ALTURA_DIALOGO_TAREFA, pai)
        self._configurar_interface()
    
    def _configurar_interface(self) -> None:
        """Configura os elementos da interface."""
        layout = QVBoxLayout()

        self.entrada_titulo = QLineEdit()
        self.entrada_titulo.setPlaceholderText("Título da tarefa...")
        layout.addWidget(QLabel("Descrição:"))
        layout.addWidget(self.entrada_titulo)

        self.combo_dia = QComboBox()
        self.combo_dia.addItems([dia.value for dia in DiaDaSemana])
        layout.addWidget(QLabel("Dia:"))
        layout.addWidget(self.combo_dia)

        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        
        self.setLayout(layout)

    def obter_dados(self) -> Tuple[str, str]:
        """Retorna título e dia selecionados."""
        return self.entrada_titulo.text(), self.combo_dia.currentText()


class DialogoHorario(DialogoBase):
    """
    Diálogo para adicionar horários.
    Layout atualizado para formato horizontal com prévia em caixa.
    """
    
    def __init__(self, pai: Optional[QWidget] = None):
        # Utiliza as constantes, mas ajusta se necessário. Sugestão: 400x300 é ideal para esse layout.
        super().__init__("Adicionar Horário", LARGURA_DIALOGO_HORARIO, ALTURA_DIALOGO_HORARIO, pai)
        self._configurar_interface()
    
    def _configurar_interface(self) -> None:
        """Configura os elementos da interface seguindo o novo design."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # 1. Título e Separador
        titulo = QLabel("Configurar Horário")
        titulo.setStyleSheet(ESTILO_DIALOGO_TITULO)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(linha)
        
        layout.addSpacing(5)
        
        # 2. Grupo de Inputs (Horizontal)
        layout.addWidget(self._criar_grupo_inputs_horizontal())
        
        # 3. Prévia
        lbl_previa_titulo = QLabel("Prévia")
        lbl_previa_titulo.setStyleSheet("font-weight: bold; font-size: 12px; color: #a29bfe;")
        lbl_previa_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_previa_titulo)
        
        self.label_previa = QLabel("00:00 horas")
        self.label_previa.setStyleSheet(ESTILO_DIALOGO_BOX_PREVIA)
        self.label_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_previa)
        
        layout.addStretch()
        
        # 4. Botões
        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botoes.setCenterButtons(True)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        
        self.setLayout(layout)
        
        # Inicializa a prévia
        self._atualizar_previa()
    
    def _criar_grupo_inputs_horizontal(self) -> QWidget:
        """Cria o grupo de spinboxes alinhados horizontalmente."""
        container = QWidget()
        layout_h = QHBoxLayout(container)
        layout_h.setContentsMargins(0, 0, 0, 0)
        layout_h.setSpacing(10)
        
        # Hora
        lbl_hora = QLabel("Hora:")
        lbl_hora.setStyleSheet(ESTILO_DIALOGO_LABEL_INPUT)
        self.spin_hora = self._criar_spinbox(0, 23, "h", HORARIO_INICIAL_SPINBOX)
        
        # Minuto
        lbl_min = QLabel("Minuto:")
        lbl_min.setStyleSheet(ESTILO_DIALOGO_LABEL_INPUT)
        self.spin_minuto = self._criar_spinbox(0, 59, "min", MINUTO_INICIAL_SPINBOX)
        
        # Montagem com Stretch para centralizar o bloco
        layout_h.addStretch()
        layout_h.addWidget(lbl_hora)
        layout_h.addWidget(self.spin_hora)
        layout_h.addSpacing(15) # Espaço extra entre os pares
        layout_h.addWidget(lbl_min)
        layout_h.addWidget(self.spin_minuto)
        layout_h.addStretch()
        
        return container
    
    def _criar_spinbox(self, min_val: int, max_val: int, sufixo: str, inicial: int) -> QSpinBox:
        """Fábrica de spinboxes."""
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(inicial)
        spin.setSuffix(f" {sufixo}")
        spin.setMinimumWidth(LARGURA_MINIMA_SPINBOX)
        spin.setMinimumHeight(ALTURA_MINIMA_SPINBOX)
        spin.setStyleSheet(ESTILO_SPINBOX)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.valueChanged.connect(self._atualizar_previa)
        return spin
    
    def _atualizar_previa(self) -> None:
        """Atualiza a prévia do horário formatado."""
        if hasattr(self, 'spin_hora') and hasattr(self, 'spin_minuto') and hasattr(self, 'label_previa'):
            hora = self.spin_hora.value()
            minuto = self.spin_minuto.value()
            self.label_previa.setText(f"{hora:02d}:{minuto:02d} horas")

    def obter_horario(self) -> str:
        """Retorna o horário formatado (HH:MM)."""
        # Nota: O retorno remove a palavra 'horas' para manter compatibilidade com o backend que espera HH:MM
        hora = self.spin_hora.value()
        minuto = self.spin_minuto.value()
        return f"{hora:02d}:{minuto:02d}"


class DialogoAtividade(DialogoBase):
    """
    Diálogo para criar/editar atividades da agenda.
    Inclui campos para horário, título, dia, prioridade e periodicidade.
    """
    
    def __init__(self, dia_preenchido: str = None, horario_preenchido: str = None, pai: Optional[QWidget] = None):
        super().__init__("Incluir Atividade", 450, 520, pai)
        self.dia_preenchido = dia_preenchido
        self.horario_preenchido = horario_preenchido
        self._configurar_interface()
    
    def _configurar_interface(self) -> None:
        """Configura os elementos da interface."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Título
        titulo = QLabel("Nova Atividade")
        titulo.setStyleSheet(ESTILO_DIALOGO_TITULO)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(linha)
        
        # Título da atividade
        layout.addWidget(QLabel("Título:"))
        self.entrada_titulo = QLineEdit()
        self.entrada_titulo.setPlaceholderText("Descrição da atividade...")
        layout.addWidget(self.entrada_titulo)
        
        # Dia da semana
        layout.addWidget(QLabel("Dia da Semana:"))
        self.combo_dia = QComboBox()
        self.combo_dia.addItems([dia.value for dia in DiaDaSemana])
        if self.dia_preenchido:
            indice = self.combo_dia.findText(self.dia_preenchido)
            if indice >= 0:
                self.combo_dia.setCurrentIndex(indice)
        layout.addWidget(self.combo_dia)
        
        # Horário (spinboxes horizontais)
        layout.addWidget(QLabel("Horário:"))
        layout.addWidget(self._criar_grupo_horario())
        
        # Prioridade
        layout.addWidget(QLabel("Prioridade:"))
        self.combo_prioridade = QComboBox()
        for nivel, descricao in DESCRICOES_PRIORIDADE.items():
            self.combo_prioridade.addItem(descricao, nivel)
        self.combo_prioridade.setCurrentIndex(3)  # P3 como padrão
        layout.addWidget(self.combo_prioridade)
        
        # Periodicidade
        layout.addWidget(QLabel("Periodicidade:"))
        self.combo_periodicidade = QComboBox()
        for codigo, descricao in LISTA_PERIODICIDADES:
            self.combo_periodicidade.addItem(descricao, codigo)
        self.combo_periodicidade.setCurrentIndex(2)  # Semanal como padrão
        layout.addWidget(self.combo_periodicidade)
        
        layout.addStretch()
        
        # Botoes
        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        
        self.setLayout(layout)
    
    def _criar_grupo_horario(self) -> QWidget:
        """Cria grupo de spinboxes para horario."""
        container = QWidget()
        layout_h = QHBoxLayout(container)
        layout_h.setContentsMargins(0, 0, 0, 0)
        layout_h.setSpacing(10)
        
        self.spin_hora = QSpinBox()
        self.spin_hora.setRange(0, 23)
        self.spin_hora.setSuffix(" h")
        self.spin_hora.setMinimumWidth(90)
        self.spin_hora.setMinimumHeight(32)
        
        self.spin_minuto = QSpinBox()
        self.spin_minuto.setRange(0, 59)
        self.spin_minuto.setSuffix(" min")
        self.spin_minuto.setMinimumWidth(90)
        self.spin_minuto.setMinimumHeight(32)
        
        # Preencher horario se fornecido
        if self.horario_preenchido:
            try:
                hora, minuto = self.horario_preenchido.split(':')
                self.spin_hora.setValue(int(hora))
                self.spin_minuto.setValue(int(minuto))
            except (ValueError, AttributeError):
                self.spin_hora.setValue(9)
                self.spin_minuto.setValue(0)
        else:
            self.spin_hora.setValue(9)
            self.spin_minuto.setValue(0)
        
        layout_h.addWidget(self.spin_hora)
        layout_h.addWidget(QLabel(":"))
        layout_h.addWidget(self.spin_minuto)
        layout_h.addStretch()
        
        return container
    
    def obter_dados(self) -> Optional[dict]:
        """Retorna os dados preenchidos como dicionário."""
        titulo = self.entrada_titulo.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Aviso", MSG_TITULO_OBRIGATORIO)
            return None
        
        horario = f"{self.spin_hora.value():02d}:{self.spin_minuto.value():02d}"
        
        return {
            'titulo': titulo,
            'dia_semana': self.combo_dia.currentText(),
            'horario': horario,
            'prioridade': self.combo_prioridade.currentData(),
            'periodicidade': self.combo_periodicidade.currentData(),
        }


class ListaArrastavel(QListWidget):
    """Lista com suporte a arrastar e soltar tarefas."""
    
    tarefa_movida = pyqtSignal(int, str, str)
    tarefa_deletada = pyqtSignal(int)

    def __init__(self, dia: str, status: str, pai: Optional[QWidget] = None):
        super().__init__(pai)
        self.dia = dia
        self.status = status
        self._configurar_widget()

    def _configurar_widget(self) -> None:
        """Configura propriedades do widget."""
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setMinimumHeight(ALTURA_MINIMA_LISTA)

    def dragEnterEvent(self, evento):
        """Aceita evento de entrada de arrasto."""
        if evento.mimeData().hasText():
            evento.accept()
        else:
            evento.ignore()

    def dragMoveEvent(self, evento):
        """Aceita movimento de arrasto."""
        if evento.mimeData().hasText():
            evento.setDropAction(Qt.DropAction.MoveAction)
            evento.accept()
        else:
            evento.ignore()

    def dropEvent(self, evento):
        """Processa evento de soltar item."""
        if not evento.mimeData().hasText():
            evento.ignore()
            return
            
        try:
            dados = evento.mimeData().text().split('|')
            id_tarefa = int(dados[0])
            self.tarefa_movida.emit(id_tarefa, self.dia, self.status)
            evento.setDropAction(Qt.DropAction.MoveAction)
            evento.accept()
        except (ValueError, IndexError):
            evento.ignore()

    def startDrag(self, acoes_suportadas):
        """Inicia arrasto de item."""
        item = self.currentItem()
        if not item:
            return
            
        mime = QMimeData()
        id_tarefa = item.data(Qt.ItemDataRole.UserRole)
        mime.setText(f"{id_tarefa}|{item.text()}")
        arrasto = QDrag(self)
        arrasto.setMimeData(mime)
        arrasto.exec(acoes_suportadas)

    def contextMenuEvent(self, evento):
        """Exibe menu de contexto para deletar tarefa."""
        item = self.itemAt(evento.pos())
        if not item:
            return
            
        menu = QMenu(self)
        acao = QAction("Excluir", self)
        acao.triggered.connect(
            lambda: self.tarefa_deletada.emit(item.data(Qt.ItemDataRole.UserRole))
        )
        menu.addAction(acao)
        menu.exec(evento.globalPos())


class ColunaDia(QWidget):
    """Coluna representando um dia da semana no quadro Kanban."""
    
    # Sinal emitido quando dados são alterados e a interface precisa ser atualizada
    dados_alterados = pyqtSignal()
    
    def __init__(self, dia: DiaDaSemana, servico_tarefas: ServicoTarefas, pai: Optional[QWidget] = None):
        super().__init__(pai)
        self.dia = dia
        self.servico_tarefas = servico_tarefas
        self.listas: Dict[str, ListaArrastavel] = {}
        self._configurar_interface()

    def _configurar_interface(self) -> None:
        """Configura a interface da coluna."""
        layout = QVBoxLayout()
        
        cabecalho = self._criar_cabecalho()
        layout.addWidget(cabecalho)
        
        for status in StatusTarefa:
            self._adicionar_secao_status(layout, status)
        
        self.setLayout(layout)
    
    def _criar_cabecalho(self) -> QLabel:
        """Cria o cabeçalho da coluna."""
        cabecalho = QLabel(self.dia.value)
        cabecalho.setObjectName("HeaderDay")
        cabecalho.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return cabecalho
    
    def _adicionar_secao_status(self, layout: QVBoxLayout, status: StatusTarefa) -> None:
        """Adiciona uma seção de status à coluna."""
        rotulo = QLabel(status.value)
        rotulo.setStyleSheet(ESTILO_ROTULO_STATUS)
        layout.addWidget(rotulo)
        
        lista = ListaArrastavel(self.dia.value, status.value, self)
        lista.tarefa_movida.connect(self._tratar_movimento_tarefa)
        lista.tarefa_deletada.connect(self._tratar_delecao_tarefa)
        self.listas[status.value] = lista
        layout.addWidget(lista)

    def _tratar_movimento_tarefa(self, id_tarefa: int, novo_dia: str, novo_status: str) -> None:
        """Trata movimento de tarefa entre colunas/status."""
        dia_enum = converter_string_para_dia(novo_dia)
        status_enum = converter_string_para_status(novo_status)
        
        if dia_enum and status_enum:
            self.servico_tarefas.mover_tarefa(id_tarefa, dia_enum, status_enum)
            self.dados_alterados.emit()

    def _tratar_delecao_tarefa(self, id_tarefa: int) -> None:
        """Trata deleção de tarefa."""
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar", 
            MSG_CONFIRMAR_DELETAR_TAREFA,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacao == QMessageBox.StandardButton.Yes:
            self.servico_tarefas.deletar_tarefa(id_tarefa)
            self.dados_alterados.emit()

    def atualizar(self) -> None:
        """Atualiza a visualização da coluna de forma assíncrona."""
        self.servico_tarefas.obter_tarefas_do_dia_async(
            self.dia,
            callback_sucesso=self._aplicar_tarefas,
            callback_erro=self._tratar_erro_carregamento
        )
    
    def _aplicar_tarefas(self, tarefas: list) -> None:
        """Aplica as tarefas carregadas à interface com badges de prioridade."""
        for lista in self.listas.values():
            lista.clear()
        
        for tarefa in tarefas:
            if tarefa.status in self.listas:
                prioridade = tarefa.prioridade if hasattr(tarefa, 'prioridade') and tarefa.prioridade is not None else 3
                
                # Usar ExtratorMetadados para limpar o título
                titulo_limpo = ExtratorMetadados.extrair_titulo_limpo(tarefa.titulo)
                
                # Se tarefa está em "Feito", aplicar strikethrough no texto
                if tarefa.status == StatusTarefa.FEITO.value:
                    titulo_exibicao = self._aplicar_strikethrough(titulo_limpo)
                else:
                    titulo_exibicao = titulo_limpo
                
                item = QListWidgetItem(titulo_exibicao)
                item.setData(Qt.ItemDataRole.UserRole, tarefa.id)
                
                # Configurar fonte
                fonte = QFont()
                fonte.setBold(True)
                if tarefa.status == StatusTarefa.FEITO.value:
                    fonte.setStrikeOut(True)
                item.setFont(fonte)
                
                # Aplicar cor de fundo baseada na prioridade
                cor_fundo = CORES_PRIORIDADE_VIBRANTE.get(prioridade)
                if cor_fundo:
                    item.setBackground(QColor(cor_fundo))
                    item.setForeground(QColor("#ffffff"))
                
                # Indicar origem da tarefa (agenda vs manual)
                if hasattr(tarefa, 'origem') and tarefa.origem == "agenda":
                    item.setToolTip(TOOLTIP_TAREFA_AGENDA.format(prioridade=prioridade))
                else:
                    item.setToolTip(TOOLTIP_TAREFA_MANUAL.format(prioridade=prioridade))
                
                self.listas[tarefa.status].addItem(item)
    
    @staticmethod
    def _aplicar_strikethrough(texto: str) -> str:
        """Aplica caractere de strikethrough Unicode a cada caractere do texto."""
        return ''.join(c + '\u0336' for c in texto)
    
    def _tratar_erro_carregamento(self, erro: Exception) -> None:
        """Trata erros no carregamento de tarefas."""
        logger.error(f"Erro ao carregar tarefas para {self.dia.value}: {erro}")


class VisualizacaoHorarios(QWidget):
    """
    Widget para visualização e edição de horários semanais.
    Inclui navegação entre semanas, calendário mensal e inclusão de atividades.
    """
    
    sincronizacao_solicitada = pyqtSignal()
    
    def __init__(self, servico_horarios: ServicoHorarios, servico_sincronizacao=None):
        super().__init__()
        self.servico_horarios = servico_horarios
        self.servico_sincronizacao = servico_sincronizacao
        self.semana_offset = 0  # 0 = semana atual, -1 = semana passada, +1 = próxima
        self._configurar_interface()

    def _configurar_interface(self) -> None:
        """Configura a interface da visualizacao."""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Barra de ferramentas superior
        layout.addLayout(self._criar_barra_ferramentas())
        
        # Navegacao de semanas
        layout.addLayout(self._criar_navegacao_semanas())
        
        # Tabela de horarios
        self.tabela = self._criar_tabela()
        layout.addWidget(self.tabela)
        
        self.setLayout(layout)
    
    def _criar_barra_ferramentas(self) -> QHBoxLayout:
        """Cria a barra de ferramentas."""
        toolbar = QHBoxLayout()
        
        # Botao incluir atividade
        botao_incluir = BotaoEstilizado("Incluir Atividade")
        botao_incluir.setCursor(Qt.CursorShape.PointingHandCursor)
        botao_incluir.setStyleSheet(ESTILO_BOTAO_ADICIONAR_HORARIO)
        botao_incluir.clicked.connect(self._incluir_atividade)
        toolbar.addWidget(botao_incluir)
        
        # Botao adicionar linha de horario
        botao_horario = BotaoEstilizado("Adicionar Horario")
        botao_horario.setCursor(Qt.CursorShape.PointingHandCursor)
        botao_horario.clicked.connect(self._adicionar_linha_horario)
        toolbar.addWidget(botao_horario)
        
        # Botao sincronizar com Kanban
        botao_sincronizar = BotaoEstilizado("Sincronizar Kanban")
        botao_sincronizar.setCursor(Qt.CursorShape.PointingHandCursor)
        botao_sincronizar.setStyleSheet(ESTILO_BOTAO_ADICIONAR_HORARIO)
        botao_sincronizar.setToolTip("Sincroniza as atividades do dia atual para o quadro Kanban")
        botao_sincronizar.clicked.connect(self._solicitar_sincronizacao)
        toolbar.addWidget(botao_sincronizar)
        
        toolbar.addStretch()
        
        # Botao calendario mensal
        botao_calendario = BotaoEstilizado("Calendario Mensal")
        botao_calendario.setCursor(Qt.CursorShape.PointingHandCursor)
        botao_calendario.clicked.connect(self._abrir_calendario_mensal)
        toolbar.addWidget(botao_calendario)
        
        return toolbar
    
    def _criar_navegacao_semanas(self) -> QHBoxLayout:
        """Cria a barra de navegacao entre semanas."""
        nav = QHBoxLayout()
        
        # Botao semana anterior
        self.btn_anterior = BotaoEstilizado("<< Anterior")
        self.btn_anterior.clicked.connect(self._semana_anterior)
        nav.addWidget(self.btn_anterior)
        
        nav.addStretch()
        
        # Label da semana atual
        self.label_semana = QLabel()
        self.label_semana.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_semana.setStyleSheet("font-weight: bold; font-size: 14px;")
        nav.addWidget(self.label_semana)
        
        nav.addStretch()
        
        # Botao proxima semana
        self.btn_proxima = BotaoEstilizado("Proxima >>")
        self.btn_proxima.clicked.connect(self._proxima_semana)
        nav.addWidget(self.btn_proxima)
        
        # Botao voltar para hoje
        self.btn_hoje = BotaoEstilizado("Hoje")
        self.btn_hoje.clicked.connect(self._ir_para_hoje)
        nav.addWidget(self.btn_hoje)
        
        self._atualizar_label_semana()
        
        return nav
    
    def _obter_datas_semana(self) -> List[date]:
        """Retorna as datas de segunda a sexta da semana atual (com offset)."""
        hoje = date.today()
        # Encontrar a segunda-feira da semana
        dias_desde_segunda = hoje.weekday()
        segunda = hoje - timedelta(days=dias_desde_segunda)
        # Aplicar offset de semanas
        segunda = segunda + timedelta(weeks=self.semana_offset)
        # Retornar segunda a sexta
        return [segunda + timedelta(days=i) for i in range(5)]
    
    def _atualizar_label_semana(self) -> None:
        """Atualiza o label com informacoes da semana."""
        datas = self._obter_datas_semana()
        inicio = datas[0].strftime("%d/%m")
        fim = datas[4].strftime("%d/%m/%Y")
        
        if self.semana_offset == 0:
            self.label_semana.setText(f"Semana Atual: {inicio} - {fim}")
        elif self.semana_offset > 0:
            self.label_semana.setText(f"+{self.semana_offset} semana(s): {inicio} - {fim}")
        else:
            self.label_semana.setText(f"{self.semana_offset} semana(s): {inicio} - {fim}")
    
    def _criar_tabela(self) -> QTableWidget:
        """Cria e configura a tabela de horarios."""
        tabela = QTableWidget()
        tabela.setColumnCount(5)
        
        # Configurar headers com datas
        self._atualizar_headers_tabela(tabela)
        
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabela.cellChanged.connect(self._ao_salvar_celula)
        
        tabela.verticalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tabela.verticalHeader().customContextMenuRequested.connect(self._menu_contexto_header)
        
        # Menu de contexto para celulas
        tabela.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tabela.customContextMenuRequested.connect(self._menu_contexto_celula)
        
        return tabela
    
    def _atualizar_headers_tabela(self, tabela: QTableWidget = None) -> None:
        """Atualiza os headers da tabela com nome do dia e data."""
        if tabela is None:
            tabela = self.tabela
        
        datas = self._obter_datas_semana()
        hoje = date.today()
        
        headers = []
        for i, dia in enumerate(DiaDaSemana):
            data = datas[i]
            nome_dia = dia.value.split('-')[0]  # "Segunda" de "Segunda-Feira"
            data_str = data.strftime("%d/%m")
            
            # Marcar o dia atual
            if data == hoje:
                headers.append(f">> {nome_dia} <<\n{data_str}")
            else:
                headers.append(f"{nome_dia}\n{data_str}")
        
        tabela.setHorizontalHeaderLabels(headers)
    
    def _semana_anterior(self) -> None:
        """Navega para a semana anterior."""
        self.semana_offset -= 1
        self._atualizar_navegacao()
    
    def _proxima_semana(self) -> None:
        """Navega para a proxima semana."""
        self.semana_offset += 1
        self._atualizar_navegacao()
    
    def _ir_para_hoje(self) -> None:
        """Volta para a semana atual."""
        self.semana_offset = 0
        self._atualizar_navegacao()
    
    def _atualizar_navegacao(self) -> None:
        """Atualiza a interface apos mudanca de semana."""
        self._atualizar_label_semana()
        self._atualizar_headers_tabela()
        self.carregar_dados()
    
    def _incluir_atividade(self) -> None:
        """Abre diálogo para incluir nova atividade."""
        dialogo = DialogoAtividade(pai=self)
        if dialogo.exec():
            dados = dialogo.obter_dados()
            if dados:
                # Encontrar índice do dia
                indice_dia = None
                for i, dia in enumerate(DiaDaSemana):
                    if dia.value == dados['dia_semana']:
                        indice_dia = i
                        break
                
                if indice_dia is not None:
                    horario = dados['horario']
                    
                    # Verificar se horário existe, senão criar
                    horarios_existentes = self.servico_horarios.obter_horarios_ordenados()
                    if horario not in horarios_existentes:
                        self.servico_horarios.adicionar_horario(horario)
                    
                    # Usar ExtratorMetadados para formatar
                    texto_atividade = ExtratorMetadados.formatar_atividade(
                        titulo=dados['titulo'],
                        prioridade=dados['prioridade'],
                        periodicidade=dados['periodicidade']
                    )
                    
                    # Salvar na célula
                    self.servico_horarios.salvar_atividade(horario, indice_dia, texto_atividade)
                    self.carregar_dados()
    
    def _menu_contexto_celula(self, posicao: QPoint) -> None:
        """Menu de contexto ao clicar com botao direito em uma celula."""
        item = self.tabela.itemAt(posicao)
        if not item:
            return
        
        linha = item.row()
        coluna = item.column()
        
        if not hasattr(self, '_horarios_atuais') or linha >= len(self._horarios_atuais):
            return
        
        horario = self._horarios_atuais[linha]
        dia = list(DiaDaSemana)[coluna].value
        
        menu = QMenu(self)
        
        # Editar atividade existente
        if item.text():
            acao_editar = QAction(f"Editar atividade", self)
            acao_editar.triggered.connect(lambda: self._editar_atividade_celula(horario, dia, coluna, linha))
            menu.addAction(acao_editar)
            
            menu.addSeparator()
        
        # Adicionar atividade nesta celula
        acao_adicionar = QAction(f"Incluir atividade em {horario}", self)
        acao_adicionar.triggered.connect(lambda: self._incluir_atividade_celula(horario, dia, coluna))
        menu.addAction(acao_adicionar)
        
        # Limpar celula
        if item.text():
            acao_limpar = QAction("Limpar célula", self)
            acao_limpar.triggered.connect(lambda: self._limpar_celula(linha, coluna))
            menu.addAction(acao_limpar)
        
        menu.exec(self.tabela.viewport().mapToGlobal(posicao))
    
    def _incluir_atividade_celula(self, horario: str, dia: str, coluna: int) -> None:
        """Abre diálogo para incluir atividade em célula específica."""
        dialogo = DialogoAtividade(dia_preenchido=dia, horario_preenchido=horario, pai=self)
        if dialogo.exec():
            dados = dialogo.obter_dados()
            if dados:
                texto_atividade = ExtratorMetadados.formatar_atividade(
                    titulo=dados['titulo'],
                    prioridade=dados['prioridade'],
                    periodicidade=dados['periodicidade']
                )
                
                self.servico_horarios.salvar_atividade(horario, coluna, texto_atividade)
                self.carregar_dados()
    
    def _editar_atividade_celula(self, horario: str, dia: str, coluna: int, linha: int) -> None:
        """Abre diálogo para editar atividade existente."""
        item = self.tabela.item(linha, coluna)
        if not item or not item.text():
            return
        
        # Obter texto completo armazenado (com metadados)
        texto_completo = item.data(Qt.ItemDataRole.UserRole) or item.text()
        
        # Extrair todos os metadados de uma vez
        metadados = ExtratorMetadados.extrair_metadados(texto_completo)
        
        # Manter a data de criação original
        data_criacao_original = metadados.data_criacao or date.today()
        
        # Criar diálogo pré-preenchido
        dialogo = DialogoAtividade(dia_preenchido=dia, horario_preenchido=horario, pai=self)
        dialogo.setWindowTitle("Editar Atividade")
        dialogo.entrada_titulo.setText(metadados.titulo)
        dialogo.combo_prioridade.setCurrentIndex(metadados.prioridade)
        
        # Selecionar periodicidade atual
        indice_periodicidade = INDICE_PERIODICIDADE.get(metadados.periodicidade, 2)
        dialogo.combo_periodicidade.setCurrentIndex(indice_periodicidade)
        
        if dialogo.exec():
            dados = dialogo.obter_dados()
            if dados:
                # Formatar com a data de criação original mantida
                texto_atividade = ExtratorMetadados.formatar_atividade(
                    titulo=dados['titulo'],
                    prioridade=dados['prioridade'],
                    periodicidade=dados['periodicidade'],
                    data_criacao=data_criacao_original
                )
                
                # Salvar na mesma célula ou na nova posição se dia/horário mudaram
                novo_horario = dados['horario']
                novo_indice_dia = None
                for i, d in enumerate(DiaDaSemana):
                    if d.value == dados['dia_semana']:
                        novo_indice_dia = i
                        break
                
                # Se mudou de posição, limpar a antiga
                if novo_horario != horario or novo_indice_dia != coluna:
                    self.servico_horarios.salvar_atividade(horario, coluna, "")
                    
                    # Verificar se novo horário existe
                    horarios_existentes = self.servico_horarios.obter_horarios_ordenados()
                    if novo_horario not in horarios_existentes:
                        self.servico_horarios.adicionar_horario(novo_horario)
                
                self.servico_horarios.salvar_atividade(novo_horario, novo_indice_dia, texto_atividade)
                self.carregar_dados()
    
    def _limpar_celula(self, linha: int, coluna: int) -> None:
        """Limpa o conteúdo de uma célula."""
        if hasattr(self, '_horarios_atuais') and linha < len(self._horarios_atuais):
            horario = self._horarios_atuais[linha]
            self.servico_horarios.salvar_atividade(horario, coluna, "")
            self.carregar_dados()
    
    def _abrir_calendario_mensal(self) -> None:
        """Abre diálogo com calendário mensal mostrando atividades."""
        dialogo = DialogoCalendarioMensal(self.servico_horarios, self)
        dialogo.exec()
    
    def _solicitar_sincronizacao(self) -> None:
        """Emite sinal para solicitar sincronização com o Kanban."""
        self.sincronizacao_solicitada.emit()

    def carregar_dados(self) -> None:
        """Carrega todos os dados da tabela de forma assincrona."""
        self.tabela.blockSignals(True)
        self.tabela.clearContents()
        
        # Carregar horarios de forma assincrona
        self.servico_horarios.obter_horarios_ordenados_async(
            callback_sucesso=self._ao_carregar_horarios,
            callback_erro=self._tratar_erro_carregamento
        )
    
    def _ao_carregar_horarios(self, horarios_ordenados: list) -> None:
        """Callback apos carregar horarios."""
        self._configurar_linhas_tabela(horarios_ordenados)
        
        # Carregar dados da grade de forma assincrona
        self.servico_horarios.obter_dados_grade_async(
            callback_sucesso=lambda dados: self._ao_carregar_dados_grade(horarios_ordenados, dados),
            callback_erro=self._tratar_erro_carregamento
        )
    
    def _ao_carregar_dados_grade(self, horarios: list, dados: dict) -> None:
        """Callback apos carregar dados da grade."""
        self._preencher_tabela_com_dados(horarios, dados)
        self.tabela.blockSignals(False)
    
    def _configurar_linhas_tabela(self, horarios: list) -> None:
        """Configura o numero de linhas e rotulos."""
        self.tabela.setRowCount(len(horarios))
        self.tabela.setVerticalHeaderLabels(horarios)
        self._horarios_atuais = horarios
    
    def _preencher_tabela_com_dados(self, horarios: list, dados: dict) -> None:
        """Preenche a tabela com dados fornecidos, aplicando cores de prioridade."""
        import re
        from datetime import date
        
        # Primeiro, identificar atividades diárias para replicar em todas as colunas
        atividades_diarias = {}  # {(horario, coluna): texto_completo}
        for (horario, coluna), texto in dados.items():
            if texto:
                metadados = ExtratorMetadados.extrair_metadados(texto)
                if metadados.periodicidade == "diaria":
                    data_criacao = metadados.data_criacao or date.today()
                    
                    # Verificar se as datas da semana atual são >= data de criação
                    datas_semana = self._obter_datas_semana()
                    for idx, data_dia in enumerate(datas_semana):
                        if data_dia >= data_criacao:
                            chave = (horario, idx)
                            if chave not in atividades_diarias:
                                atividades_diarias[chave] = texto
        
        # Mesclar atividades diárias com os dados originais
        dados_completos = dict(dados)
        for chave, texto in atividades_diarias.items():
            if chave not in dados_completos or not dados_completos[chave]:
                dados_completos[chave] = texto
        
        for indice_linha, horario in enumerate(horarios):
            for indice_coluna in range(5):
                texto_completo = dados_completos.get((horario, indice_coluna), "")
                
                if texto_completo:
                    # Extrair metadados usando a classe centralizada
                    metadados = ExtratorMetadados.extrair_metadados(texto_completo)
                    item = QTableWidgetItem(metadados.titulo)
                    
                    # Criar tooltip com informações detalhadas
                    nome_prioridade = NOMES_PRIORIDADE.get(metadados.prioridade, "N/A")
                    nome_periodicidade = NOMES_PERIODICIDADE.get(metadados.periodicidade, metadados.periodicidade)
                    data_str = metadados.data_criacao.isoformat() if metadados.data_criacao else ""
                    
                    tooltip = TOOLTIP_ATIVIDADE.format(
                        prioridade=metadados.prioridade,
                        nome_prioridade=nome_prioridade,
                        periodicidade=nome_periodicidade,
                        data=data_str
                    )
                    item.setToolTip(tooltip)
                    
                    # Aplicar cor de fundo baseada na prioridade
                    cor_fundo = CORES_PRIORIDADE_SUAVE.get(metadados.prioridade)
                    if cor_fundo:
                        item.setBackground(QColor(cor_fundo))
                        item.setForeground(QColor("#1a1a2e"))
                else:
                    item = QTableWidgetItem("")
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Guardar texto completo como dado do item para salvar corretamente
                item.setData(Qt.ItemDataRole.UserRole, texto_completo)
                self.tabela.setItem(indice_linha, indice_coluna, item)
    
    def _tratar_erro_carregamento(self, erro: Exception) -> None:
        """Trata erros no carregamento de dados."""
        logger.error(f"Erro ao carregar dados de horários: {erro}")
        self.tabela.blockSignals(False)

    def _ao_salvar_celula(self, linha: int, coluna: int) -> None:
        """Salva alterações em uma célula."""
        item = self.tabela.item(linha, coluna)
        if item and hasattr(self, '_horarios_atuais'):
            horario = self._horarios_atuais[linha]
            # Se o texto foi editado manualmente, salvar o texto exibido
            # Se não, manter o texto completo original
            texto_original = item.data(Qt.ItemDataRole.UserRole)
            texto_exibido = item.text()
            
            # Se o texto exibido está vazio, limpar a célula
            if not texto_exibido.strip():
                self.servico_horarios.salvar_atividade(horario, coluna, "")
            elif texto_original:
                # Se tem texto original, manter (não foi editado pelo usuário)
                self.servico_horarios.salvar_atividade(horario, coluna, texto_original)
            else:
                # Texto novo digitado diretamente
                self.servico_horarios.salvar_atividade(horario, coluna, texto_exibido)

    def _adicionar_linha_horario(self) -> None:
        """Adiciona uma nova linha de horario."""
        dialogo = DialogoHorario(self)
        if dialogo.exec():
            horario = dialogo.obter_horario()
            if horario:
                self.servico_horarios.adicionar_horario(horario)
                self.carregar_dados()

    def _menu_contexto_header(self, posicao: QPoint) -> None:
        """Exibe menu de contexto para editar ou excluir linha."""
        indice_linha = self.tabela.verticalHeader().logicalIndexAt(posicao)
        if not hasattr(self, '_horarios_atuais') or indice_linha < 0 or indice_linha >= len(self._horarios_atuais):
            return
        
        horario = self._horarios_atuais[indice_linha]
        
        menu = QMenu(self)
        
        # Acao Editar
        acao_editar = QAction(f"Editar Horario '{horario}'", self)
        acao_editar.triggered.connect(lambda: self._editar_horario(indice_linha, horario))
        menu.addAction(acao_editar)
        
        menu.addSeparator()
        
        # Acao Excluir
        acao_excluir = QAction(f"Excluir Linha '{horario}'", self)
        acao_excluir.triggered.connect(lambda: self._excluir_linha(horario))
        menu.addAction(acao_excluir)
        
        menu.exec(self.tabela.verticalHeader().mapToGlobal(posicao))

    def _editar_horario(self, indice_linha: int, horario_antigo: str) -> None:
        """Edita um horário existente."""
        dialogo = DialogoHorario(self)
        
        # Pré-preencher com valores atuais
        try:
            hora, minuto = horario_antigo.split(':')
            dialogo.spin_hora.setValue(int(hora))
            dialogo.spin_minuto.setValue(int(minuto))
        except (ValueError, AttributeError):
            pass
        
        if dialogo.exec():
            horario_novo = dialogo.obter_horario()
            if horario_novo and horario_novo != horario_antigo:
                # Remover horário antigo e adicionar novo
                if self.servico_horarios.remover_horario(horario_antigo):
                    if self.servico_horarios.adicionar_horario(horario_novo):
                        self.carregar_dados()
                    else:
                        # Se falhar ao adicionar, restaurar o antigo
                        self.servico_horarios.adicionar_horario(horario_antigo)
                        QMessageBox.warning(self, "Aviso", MSG_ERRO_ATUALIZAR_HORARIO)
                else:
                    QMessageBox.critical(self, "Erro", MSG_ERRO_EDITAR_HORARIO)
    
    def _excluir_linha(self, horario: str) -> None:
        """Exclui uma linha de horário após confirmação."""
        confirmacao = QMessageBox.question(
            self, 
            "Excluir", 
            MSG_CONFIRMAR_EXCLUSAO_HORARIO.format(horario=horario),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmacao == QMessageBox.StandardButton.Yes:
            if self.servico_horarios.remover_horario(horario):
                self.carregar_dados()
            else:
                QMessageBox.critical(self, "Erro", MSG_ERRO_REMOVER_HORARIO)


class DialogoCalendarioMensal(QDialog):
    """Diálogo com calendário mensal mostrando atividades agendadas."""
    
    def __init__(self, servico_horarios: ServicoHorarios, pai: Optional[QWidget] = None):
        super().__init__(pai)
        self.servico_horarios = servico_horarios
        self.setWindowTitle("Calendário Mensal")
        self.setMinimumSize(700, 550)
        self._configurar_interface()
        self._carregar_atividades()
    
    def _configurar_interface(self) -> None:
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        
        # Calendário
        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.calendario.clicked.connect(self._ao_clicar_data)
        self.calendario.currentPageChanged.connect(self._ao_mudar_mes)
        layout.addWidget(self.calendario)
        
        # Legenda de prioridades
        layout.addWidget(self._criar_legenda())
        
        # Area de atividades do dia selecionado
        self.label_data = QLabel("Selecione uma data para ver as atividades")
        self.label_data.setStyleSheet("font-weight: bold; font-size: 13px; margin-top: 10px;")
        layout.addWidget(self.label_data)
        
        self.lista_atividades = QListWidget()
        self.lista_atividades.setMaximumHeight(150)
        layout.addWidget(self.lista_atividades)
        
        # Botao fechar
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        
        self.setLayout(layout)
    
    def _criar_legenda(self) -> QWidget:
        """Cria legenda das prioridades."""
        container = QWidget()
        layout_h = QHBoxLayout(container)
        layout_h.setContentsMargins(0, 5, 0, 5)
        
        layout_h.addWidget(QLabel("Legenda:"))
        
        for nivel, cor in CORES_PRIORIDADE_VIBRANTE.items():
            rotulo = QLabel(f"  P{nivel}")
            rotulo.setStyleSheet(f"color: {cor}; font-weight: bold;")
            layout_h.addWidget(rotulo)
        
        layout_h.addStretch()
        return container
    
    def _carregar_atividades(self) -> None:
        """Carrega as atividades e marca no calendário."""
        # {dia_semana_index: [(horario, metadados), ...]}
        self.atividades_por_dia = {}
        
        dados_grade = self.servico_horarios.obter_dados_grade()
        
        for (horario, coluna), texto in dados_grade.items():
            if texto and texto.strip():
                if coluna not in self.atividades_por_dia:
                    self.atividades_por_dia[coluna] = []
                
                metadados = ExtratorMetadados.extrair_metadados(texto)
                self.atividades_por_dia[coluna].append((horario, metadados))
        
        # Ordenar por horário
        for coluna in self.atividades_por_dia:
            self.atividades_por_dia[coluna].sort(key=lambda x: x[0])
        
        self._marcar_datas_calendario()
    
    def _marcar_datas_calendario(self) -> None:
        """Marca as datas que têm atividades no calendário com cor da maior prioridade."""
        mes_exibido = self.calendario.monthShown()
        ano_exibido = self.calendario.yearShown()
        
        # Marcar 3 meses: anterior, atual e próximo (para cobrir dias visíveis de meses adjacentes)
        for mes_offset in range(-1, 2):
            mes_total = mes_exibido + mes_offset
            if mes_total < 1:
                ano = ano_exibido - 1
                mes = 12 + mes_total
            elif mes_total > 12:
                ano = ano_exibido + 1
                mes = mes_total - 12
            else:
                ano = ano_exibido
                mes = mes_total
            
            # Para cada dia do mês
            for dia in range(1, 32):
                try:
                    data_atual = date(ano, mes, dia)
                    dia_semana = data_atual.weekday()
                    
                    # Verificar se é dia útil (0-4 = seg-sex)
                    if dia_semana < 5:
                        # Coletar todas as prioridades válidas para esta data
                        prioridades_do_dia = []
                        
                        # Para atividades diárias, verificar TODAS as colunas
                        # Para outras periodicidades, verificar apenas a coluna do dia da semana
                        for coluna, atividades in self.atividades_por_dia.items():
                            for horario, metadados in atividades:
                                if metadados.periodicidade == "diaria":
                                    # Atividade diária aparece em todos os dias úteis a partir da criação
                                    if ExtratorMetadados.atividade_valida_para_data(
                                        data_atual, metadados.periodicidade, metadados.data_criacao
                                    ):
                                        prioridades_do_dia.append(metadados.prioridade)
                                elif coluna == dia_semana:
                                    # Outras atividades só aparecem no dia da semana correspondente
                                    if ExtratorMetadados.atividade_valida_para_data(
                                        data_atual, metadados.periodicidade, metadados.data_criacao
                                    ):
                                        prioridades_do_dia.append(metadados.prioridade)
                        
                        if prioridades_do_dia:
                            # Usar a maior prioridade (menor número)
                            maior_prioridade = min(prioridades_do_dia)
                            cor_prioridade = CORES_PRIORIDADE_VIBRANTE.get(maior_prioridade, "#e8f4fd")
                            
                            formato_atividade = QTextCharFormat()
                            formato_atividade.setBackground(QBrush(QColor(cor_prioridade)))
                            formato_atividade.setForeground(QBrush(QColor("#ffffff")))
                            formato_atividade.setFontWeight(QFont.Weight.Bold)
                            
                            qdate = QDate(ano, mes, dia)
                            self.calendario.setDateTextFormat(qdate, formato_atividade)
                except ValueError:
                    break  # Dia inválido para o mês
    
    def _ao_mudar_mes(self, ano: int, mes: int) -> None:
        """Callback ao mudar de mês no calendário."""
        self._marcar_datas_calendario()
    
    def _ao_clicar_data(self, qdate: QDate) -> None:
        """Callback ao clicar em uma data."""
        data = date(qdate.year(), qdate.month(), qdate.day())
        dia_semana = data.weekday()
        
        self.lista_atividades.clear()
        
        if dia_semana >= 5:  # Fim de semana
            self.label_data.setText(f"{data.strftime('%d/%m/%Y')} ({MSG_FIM_DE_SEMANA})")
            return
        
        nome_dia = list(DiaDaSemana)[dia_semana].value
        self.label_data.setText(f"{data.strftime('%d/%m/%Y')} - {nome_dia}")
        
        # Coletar todas as atividades válidas para esta data
        atividades_validas = []
        
        for coluna, atividades in self.atividades_por_dia.items():
            for horario, metadados in atividades:
                if metadados.periodicidade == "diaria":
                    # Atividade diária aparece em todos os dias úteis
                    if ExtratorMetadados.atividade_valida_para_data(
                        data, metadados.periodicidade, metadados.data_criacao
                    ):
                        atividades_validas.append((horario, metadados))
                elif coluna == dia_semana:
                    # Outras atividades só aparecem no dia da semana correspondente
                    if ExtratorMetadados.atividade_valida_para_data(
                        data, metadados.periodicidade, metadados.data_criacao
                    ):
                        atividades_validas.append((horario, metadados))
        
        # Ordenar por horário
        atividades_validas.sort(key=lambda x: x[0])
        
        # Exibir atividades
        for horario, metadados in atividades_validas:
            item = QListWidgetItem(f"{horario} - {metadados.titulo}")
            cor = CORES_PRIORIDADE_VIBRANTE.get(metadados.prioridade)
            if cor:
                item.setForeground(QColor(cor))
            self.lista_atividades.addItem(item)
        
        if self.lista_atividades.count() == 0:
            self.lista_atividades.addItem(MSG_NENHUMA_ATIVIDADE)