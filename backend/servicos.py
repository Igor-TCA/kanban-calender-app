"""
Camada de serviço - abstrai lógica de negócio entre UI e persistência.
Suporta execução síncrona e assíncrona.
Atualizado com ServicoSincronizacao para integração Agenda-Kanban.
"""
import logging
from typing import List, Optional, Callable, Any
from datetime import datetime, date

from dominio import (
    TarefaDTO, AtividadeAgendaDTO, DiaDaSemana, StatusTarefa,
    Prioridade, Periodicidade, obter_dia_semana_atual, ExtratorMetadados
)
from persistencia import RepositorioTarefas, ErroRepositorio
from constantes import FORMATO_HORA

# Configurar logging
logger = logging.getLogger(__name__)


# =============================================================================
# EXCEÇÕES ESPECÍFICAS DE SERVIÇO
# =============================================================================

class ErroServico(Exception):
    """Exceção base para erros de serviço."""
    pass


class ErroValidacao(ErroServico):
    """Erro de validação de dados."""
    pass


# =============================================================================
# SERVIÇO DE TAREFAS
# =============================================================================


class ServicoTarefas:
    """
    Serviço para gerenciar operações de tarefas.
    Encapsula a lógica de negócio relacionada ao Kanban.
    """
    
    def __init__(self, repositorio: RepositorioTarefas):
        """
        Inicializa o serviço de tarefas.
        
        Args:
            repositorio: Instância do repositório de dados
        """
        self.repositorio = repositorio
    
    def criar_tarefa(
        self, 
        titulo: str, 
        dia: DiaDaSemana, 
        status: StatusTarefa = StatusTarefa.FAZER,
        prioridade: int = 3,
        origem: str = "manual",
        atividade_origem_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Cria uma nova tarefa.
        
        Args:
            titulo: Título da tarefa
            dia: Dia da semana (Enum)
            status: Status inicial da tarefa
            prioridade: Prioridade (0-3, menor = mais urgente)
            origem: "manual" ou "agenda"
            atividade_origem_id: ID da atividade de origem (se origem="agenda")
            
        Returns:
            ID da tarefa criada ou None em caso de erro
            
        Raises:
            ErroValidacao: Se o título for inválido
        """
        try:
            if not titulo or not titulo.strip():
                logger.warning("[ServicoTarefas] Tentativa de criar tarefa sem título")
                return None
            
            dto = TarefaDTO(
                id=None,
                titulo=titulo.strip(),
                dia=dia.value,
                status=status.value,
                prioridade=prioridade,
                origem=origem,
                atividade_origem_id=atividade_origem_id,
                data_criacao=date.today().isoformat()
            )
            
            id_tarefa = self.repositorio.adicionar(dto)
            logger.info(f"[ServicoTarefas] Tarefa '{titulo}' criada com ID {id_tarefa} (P{prioridade})")
            return id_tarefa
            
        except ErroRepositorio as erro:
            logger.error(f"[ServicoTarefas] Erro de repositório ao criar tarefa: {erro}")
            return None
        except Exception as erro:
            logger.error(f"[ServicoTarefas] Erro inesperado ao criar tarefa: {erro}")
            return None
    
    def mover_tarefa(
        self, 
        id_tarefa: int, 
        novo_dia: DiaDaSemana, 
        novo_status: StatusTarefa
    ) -> bool:
        """
        Move uma tarefa para novo dia e/ou status.
        
        Args:
            id_tarefa: ID da tarefa
            novo_dia: Novo dia da semana (Enum)
            novo_status: Novo status (Enum)
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self.repositorio.atualizar_status(
                id_tarefa, 
                novo_dia.value, 
                novo_status.value
            )
            logger.info(f"[ServicoTarefas] Tarefa {id_tarefa} movida para {novo_dia.value}/{novo_status.value}")
            return True
            
        except ErroRepositorio as erro:
            logger.error(f"[ServicoTarefas] Erro de repositório ao mover tarefa {id_tarefa}: {erro}")
            return False
        except Exception as erro:
            logger.error(f"[ServicoTarefas] Erro inesperado ao mover tarefa {id_tarefa}: {erro}")
            return False
    
    def deletar_tarefa(self, id_tarefa: int) -> bool:
        """
        Deleta uma tarefa.
        
        Args:
            id_tarefa: ID da tarefa
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self.repositorio.deletar(id_tarefa)
            logger.info(f"Tarefa {id_tarefa} deletada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar tarefa {id_tarefa}: {e}")
            return False
    
    def obter_tarefas_do_dia(self, dia: DiaDaSemana) -> List[TarefaDTO]:
        """
        Obtém todas as tarefas de um dia específico.
        
        Args:
            dia: Dia da semana (Enum)
            
        Returns:
            Lista de tarefas do dia
        """
        try:
            return self.repositorio.obter_por_dia(dia.value)
        except Exception as e:
            logger.error(f"Erro ao obter tarefas do dia {dia.value}: {e}")
            return []
    
    def obter_tarefas_do_dia_async(
        self, 
        dia: DiaDaSemana,
        callback_sucesso: Optional[Callable[[List[TarefaDTO]], None]] = None,
        callback_erro: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """
        Versão assíncrona de obter_tarefas_do_dia.
        
        Args:
            dia: Dia da semana (Enum)
            callback_sucesso: Função chamada com a lista de tarefas
            callback_erro: Função chamada em caso de erro
        """
        from workers import executar_async
        executar_async(
            self.obter_tarefas_do_dia,
            callback_sucesso,
            callback_erro,
            dia
        )


class ServicoHorarios:
    """Serviço para gerenciar horários e agenda."""
    
    def __init__(self, repositorio: RepositorioTarefas):
        self.repositorio = repositorio
    
    def obter_horarios_ordenados(self) -> List[str]:
        """
        Obtém lista de horários ordenados cronologicamente.
        
        Returns:
            Lista de strings de horários ordenados
        """
        try:
            horarios = self.repositorio.obter_horarios_definidos()
            return sorted(horarios, key=self._chave_ordenacao_horario)
        except Exception as e:
            logger.error(f"Erro ao obter horários: {e}")
            return []
    
    def obter_horarios_ordenados_async(
        self,
        callback_sucesso: Optional[Callable[[List[str]], None]] = None,
        callback_erro: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """
        Versão assíncrona de obter_horarios_ordenados.
        
        Args:
            callback_sucesso: Função chamada com a lista de horários
            callback_erro: Função chamada em caso de erro
        """
        from workers import executar_async
        executar_async(
            self.obter_horarios_ordenados,
            callback_sucesso,
            callback_erro
        )
    
    @staticmethod
    def _chave_ordenacao_horario(horario_str: str) -> datetime:
        """Função auxiliar para ordenação segura de horários."""
        try:
            parte_hora = horario_str.split(' ')[0].strip()
            return datetime.strptime(parte_hora, FORMATO_HORA)
        except ValueError:
            logger.warning(f"Horário inválido para ordenação: {horario_str}")
            return datetime.max
    
    def adicionar_horario(self, horario: str) -> bool:
        """
        Adiciona um novo horário à grade.
        
        Args:
            horario: String do horário (formato HH:MM)
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if not self._validar_formato_horario(horario):
                logger.warning(f"Formato de horário inválido: {horario}")
                return False
            
            self.repositorio.adicionar_horario_definido(horario)
            logger.info(f"Horário {horario} adicionado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar horário {horario}: {e}")
            return False
    
    def remover_horario(self, horario: str) -> bool:
        """
        Remove um horário e todos os dados associados.
        
        Args:
            horario: String do horário a remover
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self.repositorio.remover_horario_definido(horario)
            logger.info(f"Horário {horario} removido")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover horário {horario}: {e}")
            return False
    
    def salvar_atividade(self, horario: str, dia_indice: int, atividade: str) -> bool:
        """
        Salva uma atividade em um horário específico.
        
        Args:
            horario: String do horário
            dia_indice: Índice do dia (0-4)
            atividade: Texto da atividade
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self.repositorio.salvar_celula_horario(horario, dia_indice, atividade)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar atividade: {e}")
            return False
    
    def obter_dados_grade(self) -> dict:
        """
        Obtém todos os dados da grade de horários em formato estruturado.
        
        Returns:
            Dicionário com chave (horario, dia_indice) -> atividade
        """
        try:
            dados = self.repositorio.carregar_dados_horarios()
            return {(d[0], d[1]): d[2] for d in dados}
        except Exception as e:
            logger.error(f"Erro ao carregar dados da grade: {e}")
            return {}
    
    def obter_dados_grade_async(
        self,
        callback_sucesso: Optional[Callable[[dict], None]] = None,
        callback_erro: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """
        Versão assíncrona de obter_dados_grade.
        
        Args:
            callback_sucesso: Função chamada com o dicionário de dados
            callback_erro: Função chamada em caso de erro
        """
        from workers import executar_async
        executar_async(
            self.obter_dados_grade,
            callback_sucesso,
            callback_erro
        )
    
    @staticmethod
    def _validar_formato_horario(horario: str) -> bool:
        """Valida se o horário está no formato HH:MM."""
        try:
            datetime.strptime(horario, FORMATO_HORA)
            return True
        except ValueError:
            return False


class ServicoAgenda:
    """Serviço para gerenciar atividades da agenda semanal."""
    
    def __init__(self, repositorio: RepositorioTarefas):
        self.repositorio = repositorio
    
    def criar_atividade(
        self, 
        titulo: str, 
        dia_semana: DiaDaSemana,
        horario: str,
        prioridade: int = 3,
        periodicidade: str = "semanal"
    ) -> Optional[int]:
        """
        Cria uma nova atividade na agenda.
        
        Args:
            titulo: Título da atividade
            dia_semana: Dia da semana
            horario: Horário no formato HH:MM
            prioridade: Prioridade (0-3)
            periodicidade: Tipo de recorrência
            
        Returns:
            ID da atividade criada ou None em caso de erro
        """
        try:
            if not titulo or not titulo.strip():
                logger.warning("Tentativa de criar atividade sem título")
                return None
            
            dto = AtividadeAgendaDTO(
                id=None,
                titulo=titulo.strip(),
                dia_semana=dia_semana.value,
                horario=horario,
                prioridade=prioridade,
                periodicidade=periodicidade,
                ativa=True,
                ultima_geracao=None
            )
            
            id_atividade = self.repositorio.adicionar_atividade_agenda(dto)
            logger.info(f"Atividade '{titulo}' criada com ID {id_atividade}")
            return id_atividade
            
        except Exception as e:
            logger.error(f"Erro ao criar atividade: {e}")
            return None
    
    def atualizar_atividade(self, atividade: AtividadeAgendaDTO) -> bool:
        """Atualiza uma atividade existente."""
        try:
            self.repositorio.atualizar_atividade_agenda(atividade)
            logger.info(f"Atividade {atividade.id} atualizada")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar atividade: {e}")
            return False
    
    def deletar_atividade(self, atividade_id: int) -> bool:
        """Deleta uma atividade da agenda."""
        try:
            self.repositorio.deletar_atividade_agenda(atividade_id)
            logger.info(f"Atividade {atividade_id} deletada")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar atividade: {e}")
            return False
    
    def obter_todas_atividades(self) -> List[AtividadeAgendaDTO]:
        """Obtém todas as atividades da agenda."""
        try:
            return self.repositorio.obter_todas_atividades_agenda()
        except Exception as e:
            logger.error(f"Erro ao obter atividades: {e}")
            return []
    
    def obter_atividades_do_dia(self, dia_semana: DiaDaSemana) -> List[AtividadeAgendaDTO]:
        """Obtém atividades de um dia específico."""
        try:
            return self.repositorio.obter_atividades_por_dia(dia_semana.value)
        except Exception as e:
            logger.error(f"Erro ao obter atividades do dia: {e}")
            return []


class ServicoSincronizacao:
    """
    Serviço de sincronização Agenda → Kanban.
    Sincroniza atividades das células da grade para o quadro Kanban baseado no dia atual.
    """
    
    def __init__(self, repositorio: RepositorioTarefas, servico_tarefas: ServicoTarefas):
        self.repositorio = repositorio
        self.servico_tarefas = servico_tarefas
    
    def sincronizar_agenda_para_kanban(self) -> dict:
        """
        Sincroniza atividades da grade da agenda do dia atual para o Kanban.
        Usa as células preenchidas na tabela de horários.
        
        Returns:
            Dicionário com estatísticas da sincronização:
            - 'criadas': número de tarefas criadas
            - 'ignoradas': número de tarefas já existentes
            - 'erros': lista de erros encontrados
        """
        resultado = {
            'criadas': 0,
            'ignoradas': 0,
            'erros': []
        }
        
        try:
            dia_atual = obter_dia_semana_atual()
            if dia_atual is None:
                logger.info("Hoje é fim de semana - sincronização ignorada")
                return resultado
            
            # Obter índice do dia atual (0=Segunda, 1=Terça, etc.)
            indice_dia = self._obter_indice_dia(dia_atual)
            if indice_dia is None:
                return resultado
            
            data_hoje = date.today().isoformat()
            
            # Obter todas as células da grade de horários
            dados_grade = self.repositorio.carregar_dados_horarios()
            
            # Filtrar apenas as atividades do dia atual
            atividades_hoje = [
                (horario, atividade) 
                for horario, coluna, atividade in dados_grade 
                if coluna == indice_dia and atividade and atividade.strip()
            ]
            
            logger.info(f"Sincronizando {len(atividades_hoje)} atividades para {dia_atual.value}")
            
            for horario, atividade in atividades_hoje:
                try:
                    # Verificar se já existe tarefa com mesmo título hoje
                    if self._tarefa_ja_existe_hoje(dia_atual, horario, atividade, data_hoje):
                        resultado['ignoradas'] += 1
                        continue
                    
                    # Extrair prioridade do texto (formato [P0], [P1], etc)
                    prioridade = self._extrair_prioridade(atividade)
                    
                    # Criar nova tarefa no Kanban
                    titulo = f"[{horario}] {atividade}"
                    id_tarefa = self.servico_tarefas.criar_tarefa(
                        titulo=titulo,
                        dia=dia_atual,
                        status=StatusTarefa.FAZER,
                        prioridade=prioridade,
                        origem="agenda",
                        atividade_origem_id=None
                    )
                    
                    if id_tarefa:
                        resultado['criadas'] += 1
                        logger.info(f"Tarefa criada: {titulo} (ID: {id_tarefa}, P{prioridade})")
                    else:
                        resultado['erros'].append(f"Falha ao criar tarefa: {atividade}")
                        
                except Exception as e:
                    erro_msg = f"Erro ao processar atividade '{atividade}': {e}"
                    logger.error(erro_msg)
                    resultado['erros'].append(erro_msg)
            
            logger.info(f"Sincronização concluída: {resultado['criadas']} criadas, "
                       f"{resultado['ignoradas']} ignoradas, {len(resultado['erros'])} erros")
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            resultado['erros'].append(str(e))
        
        return resultado
    
    def _obter_indice_dia(self, dia: DiaDaSemana) -> Optional[int]:
        """Retorna o índice da coluna para o dia da semana."""
        mapeamento = {
            DiaDaSemana.SEGUNDA: 0,
            DiaDaSemana.TERCA: 1,
            DiaDaSemana.QUARTA: 2,
            DiaDaSemana.QUINTA: 3,
            DiaDaSemana.SEXTA: 4
        }
        return mapeamento.get(dia)
    
    def _extrair_prioridade(self, texto: str) -> int:
        """
        Extrai a prioridade do texto da atividade.
        Procura por [P0], [P1], [P2], [P3] no texto.
        
        Returns:
            0-3 representando a prioridade, 3 como padrão
        """
        return ExtratorMetadados.extrair_prioridade(texto)
    
    def _tarefa_ja_existe_hoje(self, dia: DiaDaSemana, horario: str, atividade: str, data_hoje: str) -> bool:
        """
        Verifica se já existe uma tarefa com o mesmo título (horário + atividade) hoje.
        """
        try:
            tarefas_do_dia = self.repositorio.obter_por_dia(dia.value)
            titulo_esperado = f"[{horario}] {atividade}"
            
            for tarefa in tarefas_do_dia:
                # Verificar se tarefa tem mesmo título e foi criada hoje
                if tarefa.titulo == titulo_esperado:
                    if hasattr(tarefa, 'data_criacao') and tarefa.data_criacao == data_hoje:
                        return True
                    # Se não tem data_criacao mas tem mesmo título, considerar duplicata
                    if tarefa.origem == "agenda":
                        return True
            return False
        except Exception as e:
            logger.warning(f"Erro ao verificar duplicatas: {e}")
            return False
    
    def sincronizar_async(
        self,
        callback_sucesso: Optional[Callable[[dict], None]] = None,
        callback_erro: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """
        Versão assíncrona da sincronização.
        
        Args:
            callback_sucesso: Função chamada com resultado da sincronização
            callback_erro: Função chamada em caso de erro
        """
        from workers import executar_async
        executar_async(
            self.sincronizar_agenda_para_kanban,
            callback_sucesso,
            callback_erro
        )