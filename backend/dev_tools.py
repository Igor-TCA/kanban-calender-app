"""
Ferramentas de desenvolvimento para edição de UI em tempo real.
Execute: python dev_tools.py
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QPushButton, QLabel, QSpinBox, QColorDialog,
    QSlider, QGroupBox, QFormLayout, QLineEdit, QComboBox, QSplitter,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QFileSystemWatcher
from PyQt6.QtGui import QFont, QColor

# Importar componentes do projeto
from componentes_ui import DialogoHorario, DialogoTarefa, BotaoEstilizado
from constantes import *


class EditorEstilosTempoReal(QMainWindow):
    """Editor de estilos com preview em tempo real."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Dev Tools - Editor de UI em Tempo Real")
        self.resize(1400, 800)
        
        # Widget de preview atual
        self.preview_widget = None
        
        self._configurar_interface()
        self._carregar_estilos_atuais()
        
    def _configurar_interface(self):
        """Configura a interface do editor."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout_principal = QHBoxLayout(central)
        
        # Splitter para redimensionar painéis
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout_principal.addWidget(splitter)
        
        # Painel esquerdo - Controles
        painel_controles = self._criar_painel_controles()
        splitter.addWidget(painel_controles)
        
        # Painel direito - Preview
        painel_preview = self._criar_painel_preview()
        splitter.addWidget(painel_preview)
        
        # Proporção inicial 40/60
        splitter.setSizes([500, 900])
        
    def _criar_painel_controles(self) -> QWidget:
        """Cria o painel de controles."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Seletor de componente
        grupo_componente = QGroupBox("Componente para Preview")
        layout_comp = QHBoxLayout(grupo_componente)
        
        self.combo_componente = QComboBox()
        self.combo_componente.addItems([
            "DialogoHorario",
            "DialogoTarefa",
            "BotaoEstilizado"
        ])
        self.combo_componente.currentTextChanged.connect(self._atualizar_preview)
        layout_comp.addWidget(self.combo_componente)
        
        btn_atualizar = QPushButton("Atualizar Preview")
        btn_atualizar.clicked.connect(self._atualizar_preview)
        layout_comp.addWidget(btn_atualizar)
        
        layout.addWidget(grupo_componente)
        
        # Abas de edição
        abas = QTabWidget()
        
        # Aba 1 - Dimensões
        aba_dimensoes = self._criar_aba_dimensoes()
        abas.addTab(aba_dimensoes, "📐 Dimensões")
        
        # Aba 2 - Cores
        aba_cores = self._criar_aba_cores()
        abas.addTab(aba_cores, "🎨 Cores")
        
        # Aba 3 - Editor CSS/QSS
        aba_css = self._criar_aba_css()
        abas.addTab(aba_css, "📝 Editor QSS")
        
        # Aba 4 - Constantes
        aba_constantes = self._criar_aba_constantes()
        abas.addTab(aba_constantes, "⚙️ Constantes")
        
        layout.addWidget(abas)
        
        return widget
    
    def _criar_aba_dimensoes(self) -> QWidget:
        """Cria aba de edição de dimensões."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Largura do diálogo
        self.spin_largura = QSpinBox()
        self.spin_largura.setRange(200, 1000)
        self.spin_largura.setValue(LARGURA_DIALOGO_HORARIO)
        self.spin_largura.valueChanged.connect(self._aplicar_dimensoes)
        layout.addRow("Largura Diálogo:", self.spin_largura)
        
        # Altura do diálogo
        self.spin_altura = QSpinBox()
        self.spin_altura.setRange(200, 800)
        self.spin_altura.setValue(ALTURA_DIALOGO_HORARIO)
        self.spin_altura.valueChanged.connect(self._aplicar_dimensoes)
        layout.addRow("Altura Diálogo:", self.spin_altura)
        
        # Tamanho da fonte
        self.spin_fonte = QSpinBox()
        self.spin_fonte.setRange(8, 36)
        self.spin_fonte.setValue(16)
        self.spin_fonte.valueChanged.connect(self._aplicar_dimensoes)
        layout.addRow("Tamanho Fonte:", self.spin_fonte)
        
        # Padding
        self.spin_padding = QSpinBox()
        self.spin_padding.setRange(0, 50)
        self.spin_padding.setValue(10)
        self.spin_padding.valueChanged.connect(self._aplicar_dimensoes)
        layout.addRow("Padding:", self.spin_padding)
        
        # Border radius
        self.spin_border_radius = QSpinBox()
        self.spin_border_radius.setRange(0, 30)
        self.spin_border_radius.setValue(8)
        self.spin_border_radius.valueChanged.connect(self._aplicar_dimensoes)
        layout.addRow("Border Radius:", self.spin_border_radius)
        
        # Spacing
        self.spin_spacing = QSpinBox()
        self.spin_spacing.setRange(0, 50)
        self.spin_spacing.setValue(15)
        self.spin_spacing.valueChanged.connect(self._aplicar_dimensoes)
        layout.addRow("Spacing:", self.spin_spacing)
        
        return widget
    
    def _criar_aba_cores(self) -> QWidget:
        """Cria aba de edição de cores."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Cores principais
        self.cores = {
            "Cor Primária": "#6c5ce7",
            "Cor Secundária": "#a29bfe",
            "Cor de Fundo": "#ffffff",
            "Cor do Texto": "#2d3436",
            "Cor da Borda": "#6c5ce7",
            "Cor de Destaque": "#dfe6e9"
        }
        
        self.botoes_cores = {}
        
        for nome, cor in self.cores.items():
            grupo = QHBoxLayout()
            
            label = QLabel(nome + ":")
            label.setMinimumWidth(120)
            grupo.addWidget(label)
            
            btn = QPushButton(cor)
            btn.setStyleSheet(f"background-color: {cor}; color: {'white' if self._cor_escura(cor) else 'black'}; padding: 8px;")
            btn.clicked.connect(lambda checked, n=nome: self._escolher_cor(n))
            self.botoes_cores[nome] = btn
            grupo.addWidget(btn)
            
            layout.addLayout(grupo)
        
        layout.addStretch()
        
        btn_aplicar = QPushButton("✨ Aplicar Cores ao Preview")
        btn_aplicar.clicked.connect(self._aplicar_cores)
        layout.addWidget(btn_aplicar)
        
        return widget
    
    def _criar_aba_css(self) -> QWidget:
        """Cria aba de editor CSS/QSS."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Edite o QSS e clique em Aplicar para ver as mudanças:")
        layout.addWidget(label)
        
        self.editor_css = QTextEdit()
        self.editor_css.setFont(QFont("Consolas", 11))
        self.editor_css.setPlaceholderText("/* Escreva seu QSS aqui */")
        layout.addWidget(self.editor_css)
        
        btn_layout = QHBoxLayout()
        
        btn_aplicar = QPushButton("▶️ Aplicar QSS")
        btn_aplicar.clicked.connect(self._aplicar_css_personalizado)
        btn_layout.addWidget(btn_aplicar)
        
        btn_resetar = QPushButton("Resetar")
        btn_resetar.clicked.connect(self._resetar_css)
        btn_layout.addWidget(btn_resetar)
        
        btn_copiar = QPushButton("📋 Copiar para Clipboard")
        btn_copiar.clicked.connect(self._copiar_css)
        btn_layout.addWidget(btn_copiar)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def _criar_aba_constantes(self) -> QWidget:
        """Cria aba para visualizar e editar constantes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        conteudo = QWidget()
        form_layout = QFormLayout(conteudo)
        
        # Mostrar constantes relevantes do projeto
        constantes_ui = [
            ("LARGURA_DIALOGO_HORARIO", LARGURA_DIALOGO_HORARIO),
            ("ALTURA_DIALOGO_HORARIO", ALTURA_DIALOGO_HORARIO),
            ("LARGURA_DIALOGO_TAREFA", LARGURA_DIALOGO_TAREFA),
            ("ALTURA_DIALOGO_TAREFA", ALTURA_DIALOGO_TAREFA),
            ("DURACAO_FADE_IN", DURACAO_FADE_IN),
            ("DURACAO_RIPPLE", DURACAO_RIPPLE),
            ("RAIO_DESFOQUE_SOMBRA", RAIO_DESFOQUE_SOMBRA),
        ]
        
        self.campos_constantes = {}
        
        for nome, valor in constantes_ui:
            spin = QSpinBox()
            spin.setRange(0, 2000)
            spin.setValue(valor)
            self.campos_constantes[nome] = spin
            form_layout.addRow(nome + ":", spin)
        
        scroll.setWidget(conteudo)
        layout.addWidget(scroll)
        
        btn_gerar = QPushButton("📄 Gerar Código Python")
        btn_gerar.clicked.connect(self._gerar_codigo_constantes)
        layout.addWidget(btn_gerar)
        
        return widget
    
    def _criar_painel_preview(self) -> QWidget:
        """Cria o painel de preview."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("📱 Preview em Tempo Real")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Seletor de tema
        tema_layout = QHBoxLayout()
        tema_layout.addWidget(QLabel("Tema:"))
        
        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Escuro", "Claro"])
        self.combo_tema.currentTextChanged.connect(self._mudar_tema_preview)
        tema_layout.addWidget(self.combo_tema)
        tema_layout.addStretch()
        
        layout.addLayout(tema_layout)
        
        # Área de preview
        self.area_preview = QFrame()
        self.area_preview.setFrameStyle(QFrame.Shape.StyledPanel)
        self.area_preview.setStyleSheet("background-color: #2d3436; border-radius: 10px;")
        self.layout_preview = QVBoxLayout(self.area_preview)
        self.layout_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.area_preview, 1)
        
        # Info
        self.label_info = QLabel("Selecione um componente e clique em Atualizar")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_info)
        
        return widget
    
    def _atualizar_preview(self):
        """Atualiza o preview do componente selecionado."""
        # Limpar preview anterior
        if self.preview_widget:
            self.preview_widget.setParent(None)
            self.preview_widget.deleteLater()
            self.preview_widget = None
        
        componente = self.combo_componente.currentText()
        
        try:
            if componente == "DialogoHorario":
                # Criar instância sem executar como modal
                self.preview_widget = DialogoHorario()
                self.preview_widget.setWindowFlags(Qt.WindowType.Widget)
            elif componente == "DialogoTarefa":
                self.preview_widget = DialogoTarefa()
                self.preview_widget.setWindowFlags(Qt.WindowType.Widget)
            elif componente == "BotaoEstilizado":
                container = QWidget()
                layout = QVBoxLayout(container)
                btn = BotaoEstilizado("Botão Estilizado")
                btn.setStyleSheet(ESTILO_BOTAO_ADICIONAR_HORARIO)
                layout.addWidget(btn)
                self.preview_widget = container
            
            if self.preview_widget:
                self.layout_preview.addWidget(self.preview_widget)
                self.label_info.setText(f"✅ Preview: {componente}")
                
        except Exception as e:
            self.label_info.setText(f"❌ Erro: {str(e)}")
    
    def _aplicar_dimensoes(self):
        """Aplica as dimensões ao preview."""
        if self.preview_widget and hasattr(self.preview_widget, 'setFixedSize'):
            self.preview_widget.setFixedSize(
                self.spin_largura.value(),
                self.spin_altura.value()
            )
    
    def _escolher_cor(self, nome_cor: str):
        """Abre diálogo para escolher cor."""
        cor_atual = QColor(self.cores[nome_cor])
        cor = QColorDialog.getColor(cor_atual, self, f"Escolher {nome_cor}")
        
        if cor.isValid():
            hex_cor = cor.name()
            self.cores[nome_cor] = hex_cor
            btn = self.botoes_cores[nome_cor]
            btn.setText(hex_cor)
            btn.setStyleSheet(f"background-color: {hex_cor}; color: {'white' if self._cor_escura(hex_cor) else 'black'}; padding: 8px;")
    
    def _cor_escura(self, hex_cor: str) -> bool:
        """Verifica se uma cor é escura."""
        hex_cor = hex_cor.lstrip('#')
        r, g, b = int(hex_cor[0:2], 16), int(hex_cor[2:4], 16), int(hex_cor[4:6], 16)
        luminosidade = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminosidade < 0.5
    
    def _aplicar_cores(self):
        """Aplica as cores ao preview."""
        css = f"""
            QDialog, QWidget {{
                background-color: {self.cores['Cor de Fundo']};
                color: {self.cores['Cor do Texto']};
            }}
            QPushButton {{
                background-color: {self.cores['Cor Primária']};
                color: white;
                border-radius: {self.spin_border_radius.value()}px;
                padding: {self.spin_padding.value()}px;
            }}
            QPushButton:hover {{
                background-color: {self.cores['Cor Secundária']};
            }}
            QSpinBox {{
                border: 2px solid {self.cores['Cor da Borda']};
                border-radius: {self.spin_border_radius.value()}px;
                padding: {self.spin_padding.value()}px;
                background-color: {self.cores['Cor de Fundo']};
                color: {self.cores['Cor do Texto']};
            }}
            QLabel {{
                color: {self.cores['Cor do Texto']};
            }}
        """
        
        if self.preview_widget:
            self.preview_widget.setStyleSheet(css)
        
        self.editor_css.setPlainText(css)
    
    def _aplicar_css_personalizado(self):
        """Aplica CSS personalizado do editor."""
        css = self.editor_css.toPlainText()
        if self.preview_widget:
            self.preview_widget.setStyleSheet(css)
    
    def _resetar_css(self):
        """Reseta o CSS para o padrão."""
        self.editor_css.clear()
        self._atualizar_preview()
    
    def _copiar_css(self):
        """Copia o CSS para o clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.editor_css.toPlainText())
        self.label_info.setText("📋 CSS copiado para o clipboard!")
    
    def _mudar_tema_preview(self, tema: str):
        """Muda o tema do preview."""
        if tema == "Escuro":
            self.area_preview.setStyleSheet("background-color: #2d3436; border-radius: 10px;")
        else:
            self.area_preview.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
    
    def _carregar_estilos_atuais(self):
        """Carrega os estilos atuais no editor."""
        css_inicial = f"""/* Estilos do DialogoHorario */
{ESTILO_DIALOGO_TITULO}

{ESTILO_DIALOGO_LABEL_INPUT}

{ESTILO_DIALOGO_BOX_PREVIA}

{ESTILO_SPINBOX}

{ESTILO_BOTAO_ADICIONAR_HORARIO}
"""
        self.editor_css.setPlainText(css_inicial)
    
    def _gerar_codigo_constantes(self):
        """Gera código Python com as constantes editadas."""
        codigo = "# Constantes geradas pelo Dev Tools\n\n"
        
        for nome, spin in self.campos_constantes.items():
            codigo += f"{nome} = {spin.value()}\n"
        
        self.editor_css.setPlainText(codigo)
        self.label_info.setText("📄 Código Python gerado! Copie do editor QSS.")


class HotReloadWatcher(QMainWindow):
    """
    Ferramenta alternativa: Observa mudanças em arquivos .qss e recarrega automaticamente.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 Hot Reload - QSS Watcher")
        self.resize(800, 600)
        
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self._arquivo_modificado)
        
        self._configurar_interface()
        self._adicionar_arquivos_observados()
    
    def _configurar_interface(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        label = QLabel("👁️ Observando mudanças em arquivos...")
        label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(label)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log)
        
        self.preview = DialogoHorario()
        self.preview.setWindowFlags(Qt.WindowType.Widget)
        layout.addWidget(self.preview)
    
    def _adicionar_arquivos_observados(self):
        arquivos = [
            "constantes.py",
            "temas/claro.qss",
            "temas/escuro.qss"
        ]
        
        for arq in arquivos:
            path = Path(__file__).parent / arq
            if path.exists():
                self.watcher.addPath(str(path))
                self._log(f"👁️ Observando: {arq}")
    
    def _arquivo_modificado(self, path: str):
        self._log(f"Arquivo modificado: {Path(path).name}")
        
        # Recarregar módulo de constantes
        if "constantes" in path:
            import importlib
            import constantes
            importlib.reload(constantes)
            self._log("✅ Constantes recarregadas!")
        
        # Recarregar preview
        QTimer.singleShot(100, self._recarregar_preview)
    
    def _recarregar_preview(self):
        # Recriar o preview com novos estilos
        self.preview.setParent(None)
        self.preview.deleteLater()
        self.preview = DialogoHorario()
        self.preview.setWindowFlags(Qt.WindowType.Widget)
        self.centralWidget().layout().addWidget(self.preview)
        self._log("✅ Preview atualizado!")
    
    def _log(self, msg: str):
        from datetime import datetime
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def main():
    """Inicia o editor de UI em tempo real."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Escolher ferramenta
    print("\n🎨 Dev Tools - Escolha uma opção:")
    print("1. Editor de UI em Tempo Real (padrão)")
    print("2. Hot Reload Watcher (observa arquivos)")
    
    escolha = input("\nOpção (1/2): ").strip() or "1"
    
    if escolha == "2":
        janela = HotReloadWatcher()
    else:
        janela = EditorEstilosTempoReal()
    
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
