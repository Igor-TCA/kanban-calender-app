"""
Módulo de estilos - gerencia temas visuais da aplicação.
Totalmente em PT-BR com melhor tratamento de erros.
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class GerenciadorEstilo:
    """Gerencia carregamento e aplicação de temas visuais."""
    
    _DIRETORIO_TEMAS = Path(__file__).parent / "temas"
    
    @staticmethod
    def _carregar_arquivo_tema(nome_arquivo: str) -> str:
        """
        Carrega o conteúdo de um arquivo de tema.
        
        Args:
            nome_arquivo: Nome do arquivo de tema (ex: "claro.qss")
            
        Returns:
            Conteúdo do arquivo de tema ou string vazia se não encontrado
        """
        caminho = GerenciadorEstilo._DIRETORIO_TEMAS / nome_arquivo
        try:
            conteudo = caminho.read_text(encoding='utf-8')
            logger.info(f"Tema '{nome_arquivo}' carregado com sucesso")
            return conteudo
        except FileNotFoundError:
            logger.warning(f"Arquivo de tema '{nome_arquivo}' não encontrado em {caminho}")
            return ""
        except Exception as e:
            logger.error(f"Erro ao carregar tema '{nome_arquivo}': {e}")
            return ""
    
    @staticmethod
    def obter_tema_claro() -> str:
        """Retorna o stylesheet do tema claro."""
        return GerenciadorEstilo._carregar_arquivo_tema("claro.qss")

    @staticmethod
    def obter_tema_escuro() -> str:
        """Retorna o stylesheet do tema escuro."""
        return GerenciadorEstilo._carregar_arquivo_tema("escuro.qss")
