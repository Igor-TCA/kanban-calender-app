"""
Módulo de workers para execução assíncrona de tarefas.
Implementa multithreading para evitar travamentos na UI.
"""
import logging
from typing import Callable, Any, Optional
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool

from constantes import MAX_THREADS_POOL

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Sinais para comunicação entre worker e thread principal."""
    
    finalizado = pyqtSignal(object)  # Emitido com o resultado
    erro = pyqtSignal(Exception)     # Emitido com a exceção
    progresso = pyqtSignal(int)      # Emitido com percentual de progresso


class TarefaWorker(QRunnable):
    """Worker genérico para executar tarefas em background."""
    
    def __init__(self, funcao: Callable, *args, **kwargs):
        """
        Inicializa o worker.
        
        Args:
            funcao: Função a ser executada em background
            *args: Argumentos posicionais da função
            **kwargs: Argumentos nomeados da função
        """
        super().__init__()
        self.funcao = funcao
        self.args = args
        self.kwargs = kwargs
        self.sinais = WorkerSignals()
        # Não usar auto-delete para garantir que sinais não sejam deletados
        self.setAutoDelete(False)
    
    @pyqtSlot()
    def run(self) -> None:
        """Executa a tarefa e emite sinais apropriados."""
        try:
            logger.debug(f"Iniciando execução de {self.funcao.__name__}")
            resultado = self.funcao(*self.args, **self.kwargs)
            self.sinais.finalizado.emit(resultado)
            logger.debug(f"Execução de {self.funcao.__name__} concluída")
        except Exception as e:
            logger.error(f"Erro em {self.funcao.__name__}: {e}")
            self.sinais.erro.emit(e)


class GerenciadorThreads:
    """Gerenciador central de threads da aplicação."""
    
    _instancia: Optional['GerenciadorThreads'] = None
    
    def __new__(cls):
        """Implementa Singleton pattern."""
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia
    
    def __init__(self):
        """Inicializa o pool de threads."""
        if not hasattr(self, '_inicializado'):
            self.pool = QThreadPool.globalInstance()
            self.pool.setMaxThreadCount(MAX_THREADS_POOL)
            self._inicializado = True
            self._workers_ativos = []  # Manter referência aos workers
            logger.info(f"GerenciadorThreads inicializado com {self.pool.maxThreadCount()} threads")
    
    def executar_async(
        self,
        funcao: Callable,
        callback_sucesso: Optional[Callable[[Any], None]] = None,
        callback_erro: Optional[Callable[[Exception], None]] = None,
        *args,
        **kwargs
    ) -> None:
        """
        Executa uma função de forma assíncrona.
        
        Args:
            funcao: Função a ser executada
            callback_sucesso: Função chamada com o resultado em caso de sucesso
            callback_erro: Função chamada com a exceção em caso de erro
            *args: Argumentos para a função
            **kwargs: Argumentos nomeados para a função
        """
        worker = TarefaWorker(funcao, *args, **kwargs)
        
        if callback_sucesso:
            worker.sinais.finalizado.connect(callback_sucesso)
        
        if callback_erro:
            worker.sinais.erro.connect(callback_erro)
        
        # Limpar workers finalizados para evitar acúmulo de memória
        def limpar_worker():
            if worker in self._workers_ativos:
                self._workers_ativos.remove(worker)
        
        worker.sinais.finalizado.connect(limpar_worker)
        worker.sinais.erro.connect(limpar_worker)
        
        # Manter referência ao worker enquanto executa
        self._workers_ativos.append(worker)
        
        self.pool.start(worker)
        logger.debug(f"Worker para {funcao.__name__} adicionado ao pool")
    
    def threads_ativas(self) -> int:
        """Retorna o número de threads ativas."""
        return self.pool.activeThreadCount()
    
    def aguardar_conclusao(self, timeout_ms: int = -1) -> bool:
        """
        Aguarda a conclusão de todas as tarefas.
        
        Args:
            timeout_ms: Timeout em milissegundos (-1 para infinito)
            
        Returns:
            True se todas as tarefas foram concluídas, False se timeout
        """
        return self.pool.waitForDone(timeout_ms)


# Função helper para uso simplificado
def executar_async(
    funcao: Callable,
    callback_sucesso: Optional[Callable[[Any], None]] = None,
    callback_erro: Optional[Callable[[Exception], None]] = None,
    *args,
    **kwargs
) -> None:
    """
    Atalho para executar função de forma assíncrona.
    
    Args:
        funcao: Função a ser executada
        callback_sucesso: Callback para sucesso
        callback_erro: Callback para erro
        *args: Argumentos da função
        **kwargs: Argumentos nomeados da função
    """
    gerenciador = GerenciadorThreads()
    gerenciador.executar_async(funcao, callback_sucesso, callback_erro, *args, **kwargs)
