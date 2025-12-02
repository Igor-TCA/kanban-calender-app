"""
Módulo principal da aplicação Kanban.
Totalmente em PT-BR com uso da camada de serviço.
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QTabWidget, QToolBar, QSizePolicy
from PyQt6.QtCore import QSettings, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont

from constantes import (
    NOME_APLICATIVO, ARQUIVO_BANCO_DADOS, LARGURA_JANELA, ALTURA_JANELA,
    ATRASO_FADE_IN, DURACAO_FADE_IN, ATRASO_SOMBRA_COLUNA,
    RAIO_DESFOQUE_SOMBRA, DESLOCAMENTO_Y_SOMBRA, COR_SOMBRA,
    DURACAO_TOAST_CURTA, DURACAO_TOAST_MEDIA, FAMILIA_FONTE, TAMANHO_FONTE,
    NOME_ORGANIZACAO, NOME_APLICACAO
)
from dominio import DiaDaSemana, StatusTarefa, converter_string_para_dia
from persistencia import RepositorioTarefas
from servicos import ServicoTarefas, ServicoHorarios, ServicoSincronizacao
from estilos import GerenciadorEstilo
from componentes_ui import ColunaDia, DialogoTarefa, VisualizacaoHorarios
from animacoes import aplicar_sombra, fade_in, mostrar_toast

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JanelaPrincipal(QMainWindow):
    """Janela principal da aplicação Kanban."""
    
    solicitacao_atualizacao = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._inicializar_servicos()
        self._inicializar_configuracoes()
        self._configurar_janela()
        self._configurar_interface()
        self._conectar_sinais()
        self._aplicar_animacao_inicial()
        
        logger.info("Aplicação iniciada com sucesso")

    def _inicializar_servicos(self) -> None:
        """Inicializa repositório e serviços."""
        self.repositorio = RepositorioTarefas(ARQUIVO_BANCO_DADOS)
        self.servico_tarefas = ServicoTarefas(self.repositorio)
        self.servico_horarios = ServicoHorarios(self.repositorio)
        self.servico_sincronizacao = ServicoSincronizacao(self.repositorio, self.servico_tarefas)

    def _inicializar_configuracoes(self) -> None:
        """Inicializa configurações da aplicação."""
        self.configuracoes = QSettings(NOME_ORGANIZACAO, NOME_APLICACAO)
        self.tema_escuro = self.configuracoes.value("modo_escuro", False, type=bool)
        logger.info(f"Tema carregado: {'Escuro' if self.tema_escuro else 'Claro'}")

    def _configurar_janela(self) -> None:
        """Configura propriedades básicas da janela."""
        self.setWindowTitle(NOME_APLICATIVO)
        self.resize(LARGURA_JANELA, ALTURA_JANELA)

    def _configurar_interface(self) -> None:
        """Configura a interface completa."""
        self._criar_barra_ferramentas()
        self._criar_abas()
        self.aplicar_tema()
    
    def _criar_barra_ferramentas(self) -> None:
        """Cria e configura a barra de ferramentas."""
        barra = QToolBar()
        barra.setMovable(False)
        self.addToolBar(barra)

        acao_adicionar = QAction("Nova Tarefa", self)
        acao_adicionar.triggered.connect(self._abrir_dialogo_adicionar)
        barra.addAction(acao_adicionar)

        acao_atualizar = QAction("Atualizar", self)
        acao_atualizar.triggered.connect(self.atualizar_tudo)
        barra.addAction(acao_atualizar)

        espacador = QWidget()
        espacador.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        barra.addWidget(espacador)

        self.acao_tema = QAction(self._obter_texto_botao_tema(), self)
        self.acao_tema.triggered.connect(self._alternar_tema)
        barra.addAction(self.acao_tema)
    
    def _criar_abas(self) -> None:
        """Cria as abas do aplicativo."""
        self.abas = QTabWidget()
        self.setCentralWidget(self.abas)

        self._criar_aba_kanban()
        self._criar_aba_horarios()
    
    def _criar_aba_kanban(self) -> None:
        """Cria a aba Kanban com colunas para cada dia."""
        self.widget_kanban = QWidget()
        layout_kanban = QHBoxLayout(self.widget_kanban)
        self.colunas = []
        
        for dia in DiaDaSemana:
            coluna = ColunaDia(dia, self.servico_tarefas)
            coluna.dados_alterados.connect(self.atualizar_tudo)
            layout_kanban.addWidget(coluna)
            self.colunas.append(coluna)
            
            QTimer.singleShot(
                ATRASO_SOMBRA_COLUNA,
                lambda c=coluna: aplicar_sombra(
                    c,
                    raio_desfoque=RAIO_DESFOQUE_SOMBRA,
                    deslocamento_y=DESLOCAMENTO_Y_SOMBRA,
                    cor=COR_SOMBRA
                )
            )
        
        self.abas.addTab(self.widget_kanban, "Kanban")
    
    def _criar_aba_horarios(self) -> None:
        """Cria a aba de visualização de horários."""
        self.visualizacao_horarios = VisualizacaoHorarios(
            self.servico_horarios, 
            self.servico_sincronizacao
        )
        self.visualizacao_horarios.sincronizacao_solicitada.connect(self._sincronizar_agenda)
        self.abas.addTab(self.visualizacao_horarios, "Agenda Semanal")

    def _conectar_sinais(self) -> None:
        """Conecta sinais e slots."""
        self.solicitacao_atualizacao.connect(self.atualizar_tudo)

    def _aplicar_animacao_inicial(self) -> None:
        """Aplica animação de fade in inicial."""
        QTimer.singleShot(ATRASO_FADE_IN, lambda: fade_in(self, DURACAO_FADE_IN))
        self.atualizar_tudo()

    def _abrir_dialogo_adicionar(self) -> None:
        """Abre diálogo para adicionar nova tarefa."""
        dialogo = DialogoTarefa(self)
        if dialogo.exec():
            titulo, dia_str = dialogo.obter_dados()
            if titulo and dia_str:
                dia_enum = converter_string_para_dia(dia_str)
                if dia_enum:
                    id_tarefa = self.servico_tarefas.criar_tarefa(
                        titulo, 
                        dia_enum, 
                        StatusTarefa.FAZER
                    )
                    if id_tarefa:
                        self.atualizar_tudo()
                        mostrar_toast(self, f"Tarefa '{titulo}' adicionada!", DURACAO_TOAST_MEDIA)
                        logger.info(f"Tarefa '{titulo}' criada com ID {id_tarefa}")
                    else:
                        mostrar_toast(self, "Erro ao criar tarefa", DURACAO_TOAST_CURTA)
                        logger.error("Falha ao criar tarefa")

    def atualizar_tudo(self) -> None:
        """Atualiza todas as visualizações."""
        for coluna in self.colunas:
            coluna.atualizar()
        self.visualizacao_horarios.carregar_dados()
        logger.debug("Interface atualizada")
    
    def _sincronizar_agenda(self) -> None:
        """Sincroniza atividades da agenda para o Kanban."""
        from dominio import obter_dia_semana_atual
        
        def callback_sucesso(resultado: dict):
            criadas = resultado.get('criadas', 0)
            ignoradas = resultado.get('ignoradas', 0)
            erros = resultado.get('erros', [])
            
            dia_atual = obter_dia_semana_atual()
            nome_dia = dia_atual.value if dia_atual else "hoje"
            
            if criadas > 0:
                mostrar_toast(self, f"{criadas} tarefa(s) de {nome_dia} sincronizada(s)!", DURACAO_TOAST_MEDIA)
                self.atualizar_tudo()
            elif ignoradas > 0:
                mostrar_toast(self, f"Tarefas de {nome_dia} já sincronizadas", DURACAO_TOAST_CURTA)
            elif erros:
                mostrar_toast(self, f"Erro na sincronização: {erros[0]}", DURACAO_TOAST_MEDIA)
            elif dia_atual is None:
                mostrar_toast(self, "Fim de semana - sem atividades", DURACAO_TOAST_CURTA)
            else:
                mostrar_toast(self, f"Nenhuma atividade em {nome_dia}", DURACAO_TOAST_CURTA)
            
            logger.info(f"Sincronização: {criadas} criadas, {ignoradas} ignoradas")
        
        def callback_erro(erro: Exception):
            mostrar_toast(self, f"Erro: {erro}", DURACAO_TOAST_MEDIA)
            logger.error(f"Erro na sincronização: {erro}")
        
        self.servico_sincronizacao.sincronizar_async(callback_sucesso, callback_erro)

    def _alternar_tema(self) -> None:
        """Alterna entre tema claro e escuro."""
        self.tema_escuro = not self.tema_escuro
        self.configuracoes.setValue("modo_escuro", self.tema_escuro)
        self.aplicar_tema()
        
        tema_nome = "Modo Escuro" if self.tema_escuro else "Modo Claro"
        mostrar_toast(self, f"{tema_nome} ativado", DURACAO_TOAST_CURTA)
        logger.info(f"Tema alternado para: {tema_nome}")

    def aplicar_tema(self) -> None:
        """Aplica o tema atual à aplicação."""
        aplicacao = QApplication.instance()
        if self.tema_escuro:
            aplicacao.setStyleSheet(GerenciadorEstilo.obter_tema_escuro())
        else:
            aplicacao.setStyleSheet(GerenciadorEstilo.obter_tema_claro())
        
        self.acao_tema.setText(self._obter_texto_botao_tema())
    
    def _obter_texto_botao_tema(self) -> str:
        """Retorna o texto apropriado para o botão de tema."""
        return "Modo Claro" if self.tema_escuro else "Modo Escuro"


def main():
    """Função principal da aplicação."""
    aplicacao = QApplication(sys.argv)
    aplicacao.setStyle("windows11")
    aplicacao.setFont(QFont(FAMILIA_FONTE, TAMANHO_FONTE))
    
    janela = JanelaPrincipal()
    janela.show()
    
    codigo_saida = aplicacao.exec()
    logger.info(f"Aplicação encerrada com código {codigo_saida}")
    sys.exit(codigo_saida)


if __name__ == "__main__":
    main()
