"""
Módulo de domínio - define entidades e enums do sistema.
Totalmente em PT-BR.
"""
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import date, timedelta


class StatusTarefa(Enum):
    """Representa os possíveis status de uma tarefa no quadro Kanban."""
    FAZER = "Fazer"
    FAZENDO = "Fazendo"
    FEITO = "Feito"


class DiaDaSemana(Enum):
    """Representa os dias úteis da semana."""
    SEGUNDA = "Segunda-Feira"
    TERCA = "Terça-Feira"
    QUARTA = "Quarta-Feira"
    QUINTA = "Quinta-Feira"
    SEXTA = "Sexta-Feira"


class Prioridade(Enum):
    """Níveis de prioridade das tarefas."""
    P0 = (0, "P0", "#e74c3c", "Crítica")      # Vermelho
    P1 = (1, "P1", "#e67e22", "Alta")         # Laranja
    P2 = (2, "P2", "#f1c40f", "Média")        # Amarelo
    P3 = (3, "P3", "#3498db", "Baixa")        # Azul
    
    def __init__(self, nivel: int, codigo: str, cor: str, descricao: str):
        self.nivel = nivel
        self.codigo = codigo
        self.cor = cor
        self.descricao = descricao
    
    @property
    def value(self) -> int:
        """Retorna o nível numérico como valor."""
        return self.nivel
    
    def obter_cor(self) -> str:
        """Retorna a cor hexadecimal da prioridade."""
        return self.cor
    
    @classmethod
    def from_nivel(cls, nivel: int) -> 'Prioridade':
        """Retorna a prioridade pelo nível numérico."""
        for p in cls:
            if p.nivel == nivel:
                return p
        return cls.P3  # Padrão


# =============================================================================
# CONSTANTES DE PERIODICIDADE
# =============================================================================

# Dias para cálculo de periodicidade
DIAS_SEMANAL = 7
DIAS_QUINZENAL = 14
DIAS_MENSAL = 30


class Periodicidade(Enum):
    """Frequência de repetição das atividades da agenda."""
    UNICA = ("unica", "Única vez", 0)
    DIARIA = ("diaria", "Diária", 1)
    SEMANAL = ("semanal", "Semanal", DIAS_SEMANAL)
    QUINZENAL = ("quinzenal", "Quinzenal", DIAS_QUINZENAL)
    MENSAL = ("mensal", "Mensal", DIAS_MENSAL)
    
    def __init__(self, codigo: str, descricao: str, dias: int):
        self.codigo = codigo
        self.descricao = descricao
        self.dias = dias
    
    @classmethod
    def from_codigo(cls, codigo: str) -> 'Periodicidade':
        """Retorna a periodicidade pelo código."""
        for periodicidade in cls:
            if periodicidade.codigo == codigo:
                return periodicidade
        return cls.SEMANAL  # Padrão


# =============================================================================
# OBJETOS DE TRANSFERÊNCIA DE DADOS (DTOs)
# =============================================================================

@dataclass
class TarefaDTO:
    """
    Objeto de transferência de dados para Tarefas do Kanban.
    
    Attributes:
        titulo: Título/descrição da tarefa
        dia: Dia da semana (usar valores de DiaDaSemana.value)
        status: Status da tarefa (usar valores de StatusTarefa.value)
        id: ID único da tarefa (None para novas tarefas)
        horario: Horário associado à tarefa (opcional)
        prioridade: Nível de prioridade (0-3)
        origem: "manual" ou "agenda"
        atividade_origem_id: ID da atividade na agenda (se origem="agenda")
        data_criacao: Data de criação da tarefa
    """
    titulo: str
    dia: str
    status: str
    id: Optional[int] = None
    horario: str = field(default="")
    prioridade: int = field(default=3)
    origem: str = field(default="manual")
    atividade_origem_id: Optional[int] = field(default=None)
    data_criacao: Optional[str] = field(default=None)


@dataclass
class AtividadeAgendaDTO:
    """
    Objeto de transferência de dados para Atividades da Agenda Semanal.
    Representa um template de atividade recorrente.
    
    Attributes:
        titulo: Título da atividade
        dia_semana: Dia da semana
        horario: Horário da atividade
        prioridade: Nível de prioridade (0-3)
        periodicidade: Código da periodicidade
        ativa: Se a atividade está ativa
        id: ID único
        ultima_geracao: Data da última geração no Kanban
    """
    titulo: str
    dia_semana: str
    horario: str
    prioridade: int = field(default=3)
    periodicidade: str = field(default="semanal")
    ativa: bool = field(default=True)
    id: Optional[int] = field(default=None)
    ultima_geracao: Optional[str] = field(default=None)


# =============================================================================
# FUNÇÕES CONVERSORAS
# =============================================================================
def converter_string_para_dia(dia_str: str) -> Optional[DiaDaSemana]:
    """Converte string para enum DiaDaSemana.
    
    Args:
        dia_str: Nome do dia da semana (ex: 'Segunda-Feira')
        
    Returns:
        DiaDaSemana correspondente ou None se não encontrado
    """
    for dia in DiaDaSemana:
        if dia.value == dia_str:
            return dia
    return None


def converter_string_para_status(status_str: str) -> Optional[StatusTarefa]:
    """Converte string para enum StatusTarefa.
    
    Args:
        status_str: Nome do status (ex: 'Fazer')
        
    Returns:
        StatusTarefa correspondente ou None se não encontrado
    """
    for status in StatusTarefa:
        if status.value == status_str:
            return status
    return None


def obter_dia_semana_atual() -> Optional[DiaDaSemana]:
    """Retorna o dia da semana atual como enum.
    
    Returns:
        DiaDaSemana correspondente ao dia atual ou None se for fim de semana
    """
    from datetime import datetime
    dia_numero = datetime.now().weekday()  # 0=Segunda, 6=Domingo
    
    mapa_dias = {
        0: DiaDaSemana.SEGUNDA,
        1: DiaDaSemana.TERCA,
        2: DiaDaSemana.QUARTA,
        3: DiaDaSemana.QUINTA,
        4: DiaDaSemana.SEXTA,
    }
    
    return mapa_dias.get(dia_numero)


# =============================================================================
# METADADOS DE ATIVIDADES
# =============================================================================
@dataclass
class MetadadosAtividade:
    """
    Representa os metadados extraídos de uma atividade formatada.
    Encapsula prioridade, periodicidade, data de criação e título.
    """
    titulo: str
    prioridade: int = 3
    periodicidade: str = "semanal"
    data_criacao: Optional[date] = None
    
    def para_texto_formatado(self) -> str:
        """Serializa os metadados para o formato de texto armazenado."""
        data_str = self.data_criacao.isoformat() if self.data_criacao else date.today().isoformat()
        return f"[P{self.prioridade}][{self.periodicidade}][{data_str}] {self.titulo}"
    
    @property
    def prioridade_enum(self) -> 'Prioridade':
        """Retorna a prioridade como enum."""
        return Prioridade.from_nivel(self.prioridade)
    
    @property
    def periodicidade_enum(self) -> 'Periodicidade':
        """Retorna a periodicidade como enum."""
        return Periodicidade.from_codigo(self.periodicidade)


class ExtratorMetadados:
    """
    Classe utilitária para extrair e manipular metadados de atividades.
    Centraliza toda a lógica de parsing de texto formatado.
    """
    
    # Padrões regex compilados para melhor performance
    _PADRAO_PRIORIDADE = re.compile(r'\[P([0-3])\]', re.IGNORECASE)
    _PADRAO_PERIODICIDADE = re.compile(r'\[(unica|diaria|semanal|quinzenal|mensal)\]', re.IGNORECASE)
    _PADRAO_DATA = re.compile(r'\[(\d{4}-\d{2}-\d{2})\]')
    _PADRAO_HORARIO = re.compile(r'^\s*\[(\d{2}:\d{2})\]\s*')
    _PADRAO_METADADOS = re.compile(r'^\s*(\[[^\]]+\]\s*)+')
    
    @classmethod
    def extrair_prioridade(cls, texto: str) -> int:
        """
        Extrai o nível de prioridade do texto.
        
        Args:
            texto: Texto com metadados no formato [P0], [P1], etc.
            
        Returns:
            Nível de prioridade (0-3), padrão 3 se não encontrado
        """
        if not texto:
            return 3
        
        correspondencia = cls._PADRAO_PRIORIDADE.search(texto)
        if correspondencia:
            return int(correspondencia.group(1))
        return 3
    
    @classmethod
    def extrair_periodicidade(cls, texto: str) -> str:
        """
        Extrai o código de periodicidade do texto.
        
        Args:
            texto: Texto com metadados no formato [semanal], [diaria], etc.
            
        Returns:
            Código da periodicidade, padrão "semanal" se não encontrado
        """
        if not texto:
            return "semanal"
        
        correspondencia = cls._PADRAO_PERIODICIDADE.search(texto)
        if correspondencia:
            return correspondencia.group(1).lower()
        return "semanal"
    
    @classmethod
    def extrair_data_criacao(cls, texto: str) -> Optional[date]:
        """
        Extrai a data de criação do texto.
        
        Args:
            texto: Texto com metadados no formato [YYYY-MM-DD]
            
        Returns:
            Data de criação ou None se não encontrada
        """
        if not texto:
            return None
        
        correspondencia = cls._PADRAO_DATA.search(texto)
        if correspondencia:
            try:
                return date.fromisoformat(correspondencia.group(1))
            except ValueError:
                pass
        return None
    
    @classmethod
    def extrair_horario(cls, texto: str) -> Optional[str]:
        """
        Extrai o horário do início do texto.
        
        Args:
            texto: Texto com horário no formato [HH:MM]
            
        Returns:
            Horário no formato HH:MM ou None se não encontrado
        """
        if not texto:
            return None
        
        correspondencia = cls._PADRAO_HORARIO.search(texto)
        if correspondencia:
            return correspondencia.group(1)
        return None
    
    @classmethod
    def extrair_titulo_limpo(cls, texto: str) -> str:
        """
        Remove todos os metadados e retorna apenas o título.
        
        Args:
            texto: Texto completo com metadados
            
        Returns:
            Título limpo sem metadados
        """
        if not texto:
            return ""
        
        # Remove prefixo de horário [HH:MM]
        texto_limpo = cls._PADRAO_HORARIO.sub('', texto)
        # Remove todos os metadados [...]
        texto_limpo = cls._PADRAO_METADADOS.sub('', texto_limpo)
        return texto_limpo.strip()
    
    @classmethod
    def extrair_metadados(cls, texto: str) -> MetadadosAtividade:
        """
        Extrai todos os metadados de uma vez.
        
        Args:
            texto: Texto completo com metadados
            
        Returns:
            Objeto MetadadosAtividade com todos os dados extraídos
        """
        return MetadadosAtividade(
            titulo=cls.extrair_titulo_limpo(texto),
            prioridade=cls.extrair_prioridade(texto),
            periodicidade=cls.extrair_periodicidade(texto),
            data_criacao=cls.extrair_data_criacao(texto)
        )
    
    @classmethod
    def formatar_atividade(
        cls,
        titulo: str,
        prioridade: int = 3,
        periodicidade: str = "semanal",
        data_criacao: Optional[date] = None
    ) -> str:
        """
        Formata uma atividade com seus metadados.
        
        Args:
            titulo: Título da atividade
            prioridade: Nível de prioridade (0-3)
            periodicidade: Código da periodicidade
            data_criacao: Data de criação (usa hoje se None)
            
        Returns:
            Texto formatado com metadados
        """
        data_str = (data_criacao or date.today()).isoformat()
        return f"[P{prioridade}][{periodicidade}][{data_str}] {titulo}"
    
    @classmethod
    def atividade_valida_para_data(
        cls,
        data_alvo: date,
        periodicidade: str,
        data_criacao: Optional[date] = None
    ) -> bool:
        """
        Verifica se uma atividade deve aparecer em uma data específica.
        
        Args:
            data_alvo: Data a verificar
            periodicidade: Código da periodicidade
            data_criacao: Data de criação da atividade
            
        Returns:
            True se a atividade é válida para a data
        """
        if data_criacao is None:
            data_criacao = date.today()
        
        # Nunca mostrar em datas anteriores à criação
        if data_alvo < data_criacao:
            return False
        
        # Calcular primeira ocorrência
        dias_ate_dia_semana = (data_alvo.weekday() - data_criacao.weekday()) % 7
        if dias_ate_dia_semana == 0 and data_criacao.weekday() == data_alvo.weekday():
            primeira_ocorrencia = data_criacao
        else:
            primeira_ocorrencia = data_criacao + timedelta(days=dias_ate_dia_semana)
        
        if periodicidade == "unica":
            return data_alvo == primeira_ocorrencia
        
        elif periodicidade == "diaria":
            return data_alvo >= data_criacao and data_alvo.weekday() < 5
        
        elif periodicidade == "semanal":
            return data_alvo >= primeira_ocorrencia
        
        elif periodicidade == "quinzenal":
            if data_alvo < primeira_ocorrencia:
                return False
            semanas_diff = (data_alvo - primeira_ocorrencia).days // 7
            return semanas_diff % 2 == 0
        
        elif periodicidade == "mensal":
            if data_alvo < primeira_ocorrencia:
                return False
            
            def semana_do_mes(d: date) -> int:
                primeiro_dia = date(d.year, d.month, 1)
                primeiro_mesmo_dia_semana = primeiro_dia + timedelta(
                    days=(d.weekday() - primeiro_dia.weekday()) % 7
                )
                return (d - primeiro_mesmo_dia_semana).days // 7
            
            return semana_do_mes(primeira_ocorrencia) == semana_do_mes(data_alvo)
        
        return False


