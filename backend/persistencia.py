"""
Módulo de persistência - gerencia acesso ao banco de dados SQLite.
Traduzido para PT-BR com melhor tratamento de erros.
Atualizado para suportar prioridades, periodicidade e integração Agenda-Kanban.
"""
import sqlite3
import logging
from typing import Optional, List, Tuple
from contextlib import contextmanager
from datetime import date

from dominio import TarefaDTO, AtividadeAgendaDTO
from constantes import HORARIO_INICIO_PADRAO, HORARIO_FIM_PADRAO

logger = logging.getLogger(__name__)


# =============================================================================
# EXCEÇÕES ESPECÍFICAS
# =============================================================================

class ErroRepositorio(Exception):
    """Exceção base para erros do repositório."""
    pass


class ErroConexaoBancoDados(ErroRepositorio):
    """Erro ao conectar com o banco de dados."""
    pass


class ErroOperacaoBancoDados(ErroRepositorio):
    """Erro ao executar operação no banco de dados."""
    pass


# =============================================================================
# CONSULTAS SQL
# =============================================================================


class ConsultasSQL:
    """Centraliza todas as queries SQL do sistema."""
    
    # Tabela de tarefas (Kanban) - ATUALIZADA com novos campos
    CRIAR_TABELA_TAREFAS = '''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            dia TEXT NOT NULL,
            status TEXT NOT NULL,
            horario TEXT,
            prioridade INTEGER DEFAULT 3,
            origem TEXT DEFAULT 'manual',
            atividade_origem_id INTEGER,
            data_criacao TEXT
        )
    '''
    
    # Tabela de definições de horário (grade horária)
    CRIAR_TABELA_DEFINICOES_HORARIO = '''
        CREATE TABLE IF NOT EXISTS definicoes_horario (
            rotulo_horario TEXT PRIMARY KEY
        )
    '''
    
    # Tabela de agenda (células da grade) - mantida para compatibilidade
    CRIAR_TABELA_AGENDA = '''
        CREATE TABLE IF NOT EXISTS agenda (
            rotulo_horario TEXT,
            coluna INTEGER,
            atividade TEXT,
            PRIMARY KEY (rotulo_horario, coluna)
        )
    '''
    
    # NOVA: Tabela de atividades da agenda (templates recorrentes)
    CRIAR_TABELA_ATIVIDADES_AGENDA = '''
        CREATE TABLE IF NOT EXISTS atividades_agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            dia_semana TEXT NOT NULL,
            horario TEXT NOT NULL,
            prioridade INTEGER DEFAULT 3,
            periodicidade TEXT DEFAULT 'semanal',
            ativa INTEGER DEFAULT 1,
            ultima_geracao TEXT
        )
    '''
    
    # Queries de tarefas - ATUALIZADAS
    INSERIR_TAREFA = """
        INSERT INTO tarefas (titulo, dia, status, horario, prioridade, origem, atividade_origem_id, data_criacao) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    ATUALIZAR_TAREFA = "UPDATE tarefas SET dia = ?, status = ? WHERE id = ?"
    DELETAR_TAREFA = "DELETE FROM tarefas WHERE id = ?"
    SELECIONAR_TAREFAS_POR_DIA = "SELECT * FROM tarefas WHERE dia = ? ORDER BY prioridade ASC"
    SELECIONAR_TODAS_TAREFAS = "SELECT * FROM tarefas ORDER BY prioridade ASC"
    
    # Query para verificar duplicatas de tarefas da agenda
    VERIFICAR_TAREFA_AGENDA_EXISTE = """
        SELECT COUNT(*) FROM tarefas 
        WHERE atividade_origem_id = ? AND data_criacao = ?
    """
    
    # Queries de definições de horário
    SELECIONAR_DEFINICOES_HORARIO = "SELECT rotulo_horario FROM definicoes_horario"
    CONTAR_DEFINICOES_HORARIO = "SELECT count(*) FROM definicoes_horario"
    INSERIR_DEFINICAO_HORARIO = "INSERT OR IGNORE INTO definicoes_horario (rotulo_horario) VALUES (?)"
    DELETAR_DEFINICAO_HORARIO = "DELETE FROM definicoes_horario WHERE rotulo_horario = ?"
    
    # Queries de agenda (células)
    INSERIR_OU_SUBSTITUIR_AGENDA = "INSERT OR REPLACE INTO agenda (rotulo_horario, coluna, atividade) VALUES (?, ?, ?)"
    SELECIONAR_TODAS_AGENDAS = "SELECT rotulo_horario, coluna, atividade FROM agenda"
    DELETAR_AGENDA_POR_HORARIO = "DELETE FROM agenda WHERE rotulo_horario = ?"
    
    # NOVAS: Queries de atividades da agenda
    INSERIR_ATIVIDADE_AGENDA = """
        INSERT INTO atividades_agenda (titulo, dia_semana, horario, prioridade, periodicidade, ativa, ultima_geracao)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    ATUALIZAR_ATIVIDADE_AGENDA = """
        UPDATE atividades_agenda 
        SET titulo = ?, dia_semana = ?, horario = ?, prioridade = ?, periodicidade = ?, ativa = ?
        WHERE id = ?
    """
    ATUALIZAR_ULTIMA_GERACAO = "UPDATE atividades_agenda SET ultima_geracao = ? WHERE id = ?"
    DELETAR_ATIVIDADE_AGENDA = "DELETE FROM atividades_agenda WHERE id = ?"
    SELECIONAR_ATIVIDADES_POR_DIA = """
        SELECT * FROM atividades_agenda WHERE dia_semana = ? AND ativa = 1
    """
    SELECIONAR_TODAS_ATIVIDADES_AGENDA = "SELECT * FROM atividades_agenda ORDER BY horario ASC"
    SELECIONAR_ATIVIDADES_ATIVAS = "SELECT * FROM atividades_agenda WHERE ativa = 1"


@contextmanager
def obter_conexao_bd(caminho_bd: str):
    """
    Context manager para conexões com banco de dados.
    
    Args:
        caminho_bd: Caminho para o arquivo do banco de dados
        
    Yields:
        Conexão SQLite configurada
        
    Raises:
        ErroConexaoBancoDados: Se não for possível conectar
        ErroOperacaoBancoDados: Se ocorrer erro durante operação
    """
    conexao = None
    try:
        conexao = sqlite3.connect(caminho_bd)
        conexao.row_factory = sqlite3.Row
        yield conexao
        conexao.commit()
    except sqlite3.OperationalError as erro:
        logger.error(f"Erro de operação no banco de dados: {erro}")
        if conexao:
            conexao.rollback()
        raise ErroConexaoBancoDados(f"Não foi possível conectar ao banco: {erro}") from erro
    except sqlite3.Error as erro:
        logger.error(f"Erro no banco de dados: {erro}")
        if conexao:
            conexao.rollback()
        raise ErroOperacaoBancoDados(f"Erro ao executar operação: {erro}") from erro
    finally:
        if conexao:
            conexao.close()


# =============================================================================
# REPOSITÓRIO PRINCIPAL
# =============================================================================


class RepositorioTarefas:
    """Repositório para gerenciar tarefas e horários no banco de dados."""
    
    def __init__(self, caminho_bd: str):
        self.caminho_bd = caminho_bd
        self._inicializar_tabelas()
        self._migrar_banco_se_necessario()

    def _inicializar_tabelas(self) -> None:
        """Inicializa as tabelas do banco de dados."""
        try:
            with obter_conexao_bd(self.caminho_bd) as conexao:
                conexao.execute(ConsultasSQL.CRIAR_TABELA_TAREFAS)
                conexao.execute(ConsultasSQL.CRIAR_TABELA_DEFINICOES_HORARIO)
                conexao.execute(ConsultasSQL.CRIAR_TABELA_AGENDA)
                conexao.execute(ConsultasSQL.CRIAR_TABELA_ATIVIDADES_AGENDA)
                self._popular_horarios_padrao(conexao)
            logger.info("Tabelas inicializadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar tabelas: {e}")
            raise
    
    def _migrar_banco_se_necessario(self) -> None:
        """Adiciona novas colunas se não existirem (migração)."""
        try:
            with obter_conexao_bd(self.caminho_bd) as conexao:
                # Verificar e adicionar colunas novas na tabela tarefas
                cursor = conexao.execute("PRAGMA table_info(tarefas)")
                colunas_existentes = {row['name'] for row in cursor.fetchall()}
                
                novas_colunas = [
                    ("prioridade", "INTEGER DEFAULT 3"),
                    ("origem", "TEXT DEFAULT 'manual'"),
                    ("atividade_origem_id", "INTEGER"),
                    ("data_criacao", "TEXT"),
                ]
                
                for nome_coluna, tipo in novas_colunas:
                    if nome_coluna not in colunas_existentes:
                        conexao.execute(f"ALTER TABLE tarefas ADD COLUMN {nome_coluna} {tipo}")
                        logger.info(f"Coluna '{nome_coluna}' adicionada à tabela tarefas")
                        
        except Exception as e:
            logger.error(f"Erro na migração do banco: {e}")
    
    def _popular_horarios_padrao(self, conexao: sqlite3.Connection) -> None:
        """Popula horários padrão se a tabela estiver vazia."""
        cursor = conexao.execute(ConsultasSQL.CONTAR_DEFINICOES_HORARIO)
        if cursor.fetchone()[0] == 0:
            horarios_padrao = [
                (f"{h:02d}:00",) 
                for h in range(HORARIO_INICIO_PADRAO, HORARIO_FIM_PADRAO)
            ]
            conexao.executemany(ConsultasSQL.INSERIR_DEFINICAO_HORARIO, horarios_padrao)
            logger.info(f"Populados {len(horarios_padrao)} horários padrão")
    
    def _converter_row_para_dto(self, row: sqlite3.Row) -> TarefaDTO:
        """Converte uma row do banco para TarefaDTO."""
        return TarefaDTO(
            id=row['id'],
            titulo=row['titulo'],
            dia=row['dia'],
            status=row['status'],
            horario=row['horario'] or "",
            prioridade=row['prioridade'] if 'prioridade' in row.keys() else 3,
            origem=row['origem'] if 'origem' in row.keys() else "manual",
            atividade_origem_id=row['atividade_origem_id'] if 'atividade_origem_id' in row.keys() else None,
            data_criacao=row['data_criacao'] if 'data_criacao' in row.keys() else None
        )
    
    def _converter_row_para_atividade_dto(self, row: sqlite3.Row) -> AtividadeAgendaDTO:
        """Converte uma row do banco para AtividadeAgendaDTO."""
        return AtividadeAgendaDTO(
            id=row['id'],
            titulo=row['titulo'],
            dia_semana=row['dia_semana'],
            horario=row['horario'],
            prioridade=row['prioridade'],
            periodicidade=row['periodicidade'],
            ativa=bool(row['ativa']),
            ultima_geracao=row['ultima_geracao']
        )

    # =========================================================================
    # MÉTODOS DE TAREFAS (KANBAN)
    # =========================================================================
    
    def adicionar(self, tarefa: TarefaDTO) -> int:
        """
        Adiciona uma nova tarefa ao banco.
        
        Args:
            tarefa: DTO da tarefa a adicionar
            
        Returns:
            ID da tarefa criada
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(
                ConsultasSQL.INSERIR_TAREFA,
                (tarefa.titulo, tarefa.dia, tarefa.status, tarefa.horario,
                 tarefa.prioridade, tarefa.origem, tarefa.atividade_origem_id,
                 tarefa.data_criacao or date.today().isoformat())
            )
            return cursor.lastrowid

    def atualizar_status(self, id_tarefa: int, novo_dia: str, novo_status: str) -> None:
        """
        Atualiza dia e status de uma tarefa.
        
        Args:
            id_tarefa: ID da tarefa
            novo_dia: Novo dia da semana
            novo_status: Novo status da tarefa
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(
                ConsultasSQL.ATUALIZAR_TAREFA, 
                (novo_dia, novo_status, id_tarefa)
            )

    def deletar(self, id_tarefa: int) -> None:
        """
        Deleta uma tarefa.
        
        Args:
            id_tarefa: ID da tarefa a deletar
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(ConsultasSQL.DELETAR_TAREFA, (id_tarefa,))

    def obter_por_dia(self, dia: str) -> List[TarefaDTO]:
        """
        Obtém todas as tarefas de um dia específico, ordenadas por prioridade.
        
        Args:
            dia: Nome do dia da semana
            
        Returns:
            Lista de tarefas do dia
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(ConsultasSQL.SELECIONAR_TAREFAS_POR_DIA, (dia,))
            return [self._converter_row_para_dto(row) for row in cursor.fetchall()]
    
    def verificar_tarefa_agenda_existe(self, atividade_id: int, data: str) -> bool:
        """
        Verifica se uma tarefa da agenda já foi criada para a data especificada.
        
        Args:
            atividade_id: ID da atividade na agenda
            data: Data no formato ISO
            
        Returns:
            True se já existe, False caso contrário
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(
                ConsultasSQL.VERIFICAR_TAREFA_AGENDA_EXISTE,
                (atividade_id, data)
            )
            return cursor.fetchone()[0] > 0

    # =========================================================================
    # MÉTODOS DE HORÁRIOS (GRADE HORÁRIA)
    # =========================================================================
    
    def obter_horarios_definidos(self) -> List[str]:
        """
        Retorna a lista de horários disponíveis.
        
        Returns:
            Lista de strings de horários
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(ConsultasSQL.SELECIONAR_DEFINICOES_HORARIO)
            return [row['rotulo_horario'] for row in cursor.fetchall()]

    def adicionar_horario_definido(self, novo_horario: str) -> None:
        """
        Adiciona um novo horário à lista.
        
        Args:
            novo_horario: String do horário (formato HH:MM)
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(ConsultasSQL.INSERIR_DEFINICAO_HORARIO, (novo_horario,))

    def remover_horario_definido(self, horario: str) -> None:
        """
        Remove um horário e todas as atividades associadas.
        
        Args:
            horario: String do horário a remover
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(ConsultasSQL.DELETAR_DEFINICAO_HORARIO, (horario,))
            conexao.execute(ConsultasSQL.DELETAR_AGENDA_POR_HORARIO, (horario,))

    def salvar_celula_horario(self, rotulo_horario: str, coluna: int, atividade: str) -> None:
        """
        Salva o conteúdo de uma célula da agenda.
        
        Args:
            rotulo_horario: String do horário
            coluna: Índice da coluna (dia)
            atividade: Texto da atividade
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(
                ConsultasSQL.INSERIR_OU_SUBSTITUIR_AGENDA,
                (rotulo_horario, coluna, atividade)
            )

    def carregar_dados_horarios(self) -> List[Tuple[str, int, str]]:
        """
        Carrega todos os dados da agenda.
        
        Returns:
            Lista de tuplas (horario, coluna, atividade)
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(ConsultasSQL.SELECIONAR_TODAS_AGENDAS)
            return [
                (row['rotulo_horario'], row['coluna'], row['atividade']) 
                for row in cursor.fetchall()
            ]

    # =========================================================================
    # MÉTODOS DE ATIVIDADES DA AGENDA (TEMPLATES RECORRENTES)
    # =========================================================================
    
    def adicionar_atividade_agenda(self, atividade: AtividadeAgendaDTO) -> int:
        """
        Adiciona uma nova atividade à agenda semanal.
        
        Args:
            atividade: DTO da atividade
            
        Returns:
            ID da atividade criada
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(
                ConsultasSQL.INSERIR_ATIVIDADE_AGENDA,
                (atividade.titulo, atividade.dia_semana, atividade.horario,
                 atividade.prioridade, atividade.periodicidade, 
                 1 if atividade.ativa else 0, atividade.ultima_geracao)
            )
            return cursor.lastrowid
    
    def atualizar_atividade_agenda(self, atividade: AtividadeAgendaDTO) -> None:
        """
        Atualiza uma atividade existente na agenda.
        
        Args:
            atividade: DTO da atividade com dados atualizados
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(
                ConsultasSQL.ATUALIZAR_ATIVIDADE_AGENDA,
                (atividade.titulo, atividade.dia_semana, atividade.horario,
                 atividade.prioridade, atividade.periodicidade,
                 1 if atividade.ativa else 0, atividade.id)
            )
    
    def atualizar_ultima_geracao(self, atividade_id: int, data: str) -> None:
        """
        Atualiza a data da última geração de uma atividade.
        
        Args:
            atividade_id: ID da atividade
            data: Data no formato ISO
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(
                ConsultasSQL.ATUALIZAR_ULTIMA_GERACAO,
                (data, atividade_id)
            )
    
    def deletar_atividade_agenda(self, atividade_id: int) -> None:
        """
        Deleta uma atividade da agenda.
        
        Args:
            atividade_id: ID da atividade a deletar
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            conexao.execute(ConsultasSQL.DELETAR_ATIVIDADE_AGENDA, (atividade_id,))
    
    def obter_atividades_por_dia(self, dia_semana: str) -> List[AtividadeAgendaDTO]:
        """
        Obtém atividades ativas de um dia específico.
        
        Args:
            dia_semana: Nome do dia da semana
            
        Returns:
            Lista de atividades do dia
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(
                ConsultasSQL.SELECIONAR_ATIVIDADES_POR_DIA,
                (dia_semana,)
            )
            return [self._converter_row_para_atividade_dto(row) for row in cursor.fetchall()]
    
    def obter_todas_atividades_agenda(self) -> List[AtividadeAgendaDTO]:
        """
        Obtém todas as atividades da agenda.
        
        Returns:
            Lista de todas as atividades
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(ConsultasSQL.SELECIONAR_TODAS_ATIVIDADES_AGENDA)
            return [self._converter_row_para_atividade_dto(row) for row in cursor.fetchall()]
    
    def obter_atividades_ativas(self) -> List[AtividadeAgendaDTO]:
        """
        Obtém todas as atividades ativas.
        
        Returns:
            Lista de atividades ativas
        """
        with obter_conexao_bd(self.caminho_bd) as conexao:
            cursor = conexao.execute(ConsultasSQL.SELECIONAR_ATIVIDADES_ATIVAS)
            return [self._converter_row_para_atividade_dto(row) for row in cursor.fetchall()]
