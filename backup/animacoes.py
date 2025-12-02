"""
Módulo de animações e efeitos visuais para PyQt6.
Totalmente em PT-BR com constantes extraídas.
"""
from typing import Optional, Callable
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QLabel
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QColor

from constantes import (
    DURACAO_FADE_IN, DURACAO_FADE_OUT, 
    DESLOCAMENTO_X_TOAST, DESLOCAMENTO_Y_TOAST,
    ESTILO_TOAST
)


def aplicar_sombra(
    widget: QWidget, 
    raio_desfoque: int = 20, 
    deslocamento_x: int = 0, 
    deslocamento_y: int = 3, 
    cor: tuple = (0, 0, 0, 120)
) -> None:
    """
    Aplica efeito de sombra a um widget.
    
    Args:
        widget: Widget alvo
        raio_desfoque: Raio do desfoque da sombra
        deslocamento_x: Deslocamento horizontal da sombra
        deslocamento_y: Deslocamento vertical da sombra
        cor: Tupla RGBA da cor da sombra
    """
    sombra = QGraphicsDropShadowEffect()
    sombra.setBlurRadius(raio_desfoque)
    sombra.setXOffset(deslocamento_x)
    sombra.setYOffset(deslocamento_y)
    sombra.setColor(QColor(*cor))
    widget.setGraphicsEffect(sombra)


def fade_in(widget: QWidget, duracao: int = DURACAO_FADE_IN) -> None:
    """
    Animação de fade in (aparecer gradualmente).
    
    Args:
        widget: Widget alvo
        duracao: Duração da animação em milissegundos
    """
    widget.setWindowOpacity(0.0)
    widget.show()
    
    animacao = QPropertyAnimation(widget, b"windowOpacity")
    animacao.setDuration(duracao)
    animacao.setStartValue(0.0)
    animacao.setEndValue(1.0)
    animacao.setEasingCurve(QEasingCurve.Type.OutCubic)
    animacao.start()
    
    # Mantém referência para evitar garbage collection
    widget._animacao_fade = animacao


def fade_out(
    widget: QWidget, 
    duracao: int = DURACAO_FADE_OUT, 
    callback: Optional[Callable] = None
) -> None:
    """
    Animação de fade out (desaparecer gradualmente).
    
    Args:
        widget: Widget alvo
        duracao: Duração da animação em milissegundos
        callback: Função a ser chamada ao final da animação
    """
    animacao = QPropertyAnimation(widget, b"windowOpacity")
    animacao.setDuration(duracao)
    animacao.setStartValue(1.0)
    animacao.setEndValue(0.0)
    animacao.setEasingCurve(QEasingCurve.Type.InCubic)
    
    if callback:
        animacao.finished.connect(callback)
    
    animacao.start()
    
    # Mantém referência para evitar garbage collection
    widget._animacao_fade = animacao


def mostrar_toast(
    pai: QWidget, 
    mensagem: str, 
    duracao_exibicao: int = 2000
) -> None:
    """
    Exibe uma notificação toast temporária.
    
    Args:
        pai: Widget pai
        mensagem: Texto da mensagem
        duracao_exibicao: Tempo de exibição em milissegundos
    """
    rotulo = QLabel(mensagem, pai)
    rotulo.setStyleSheet(ESTILO_TOAST)
    rotulo.adjustSize()
    rotulo.move(
        pai.width() - rotulo.width() - DESLOCAMENTO_X_TOAST,
        pai.height() - DESLOCAMENTO_Y_TOAST
    )
    
    fade_in(rotulo, DURACAO_FADE_OUT)
    
    def esconder():
        fade_out(rotulo, DURACAO_FADE_OUT, lambda: rotulo.deleteLater())
    
    QTimer.singleShot(duracao_exibicao, esconder)
