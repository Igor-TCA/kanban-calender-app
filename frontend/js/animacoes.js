/**
 * Módulo de animações e efeitos visuais
 * Totalmente em PT-BR
 */

/**
 * Aplica efeito de sombra a um elemento
 */
function aplicarSombra(elemento, opcoes = {}) {
    const {
        raioDesfoque = 20,
        deslocamentoX = 0,
        deslocamentoY = 3,
        cor = 'rgba(0, 0, 0, 0.3)'
    } = opcoes;

    elemento.style.boxShadow = `${deslocamentoX}px ${deslocamentoY}px ${raioDesfoque}px ${cor}`;
}

/**
 * Animação de fade in (aparecer gradualmente)
 */
function fadeIn(elemento, duracao = DURACAO_FADE_IN) {
    elemento.style.opacity = '0';
    elemento.style.display = 'block';
    
    let inicio = null;
    
    function animar(timestamp) {
        if (!inicio) inicio = timestamp;
        const progresso = timestamp - inicio;
        const porcentagem = Math.min(progresso / duracao, 1);
        
        // Easing OutCubic
        const easing = 1 - Math.pow(1 - porcentagem, 3);
        elemento.style.opacity = easing.toString();
        
        if (porcentagem < 1) {
            requestAnimationFrame(animar);
        }
    }
    
    requestAnimationFrame(animar);
}

/**
 * Animação de fade out (desaparecer gradualmente)
 */
function fadeOut(elemento, duracao = DURACAO_FADE_OUT, callback = null) {
    let inicio = null;
    
    function animar(timestamp) {
        if (!inicio) inicio = timestamp;
        const progresso = timestamp - inicio;
        const porcentagem = Math.min(progresso / duracao, 1);
        
        // Easing InCubic
        const easing = Math.pow(porcentagem, 3);
        elemento.style.opacity = (1 - easing).toString();
        
        if (porcentagem < 1) {
            requestAnimationFrame(animar);
        } else {
            elemento.style.display = 'none';
            if (callback) callback();
        }
    }
    
    requestAnimationFrame(animar);
}

/**
 * Animação de slide in (deslizar para dentro)
 */
function slideIn(elemento, direcao = 'bottom', duracao = 300) {
    const traducoes = {
        top: { de: '-100%', para: '0' },
        bottom: { de: '100%', para: '0' },
        left: { de: '-100%', para: '0' },
        right: { de: '100%', para: '0' }
    };
    
    const eixo = (direcao === 'top' || direcao === 'bottom') ? 'Y' : 'X';
    const { de, para } = traducoes[direcao];
    
    elemento.style.transform = `translate${eixo}(${de})`;
    elemento.style.display = 'block';
    elemento.style.transition = `transform ${duracao}ms ease-out`;
    
    requestAnimationFrame(() => {
        elemento.style.transform = `translate${eixo}(${para})`;
    });
}

/**
 * Animação de scale (escala)
 */
function scaleIn(elemento, duracao = 200) {
    elemento.style.transform = 'scale(0.8)';
    elemento.style.opacity = '0';
    elemento.style.display = 'block';
    elemento.style.transition = `transform ${duracao}ms ease-out, opacity ${duracao}ms ease-out`;
    
    requestAnimationFrame(() => {
        elemento.style.transform = 'scale(1)';
        elemento.style.opacity = '1';
    });
}

/**
 * Efeito ripple ao clicar em um botão
 */
function adicionarEfeitoRipple(botao) {
    botao.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');
        
        const rect = this.getBoundingClientRect();
        const tamanho = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - tamanho / 2;
        const y = e.clientY - rect.top - tamanho / 2;
        
        ripple.style.width = ripple.style.height = `${tamanho}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), DURACAO_RIPPLE);
    });
}

/**
 * Exibe uma notificação toast temporária
 */
function mostrarToast(mensagem, duracao = DURACAO_TOAST_MEDIA, tipo = 'info') {
    const container = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = mensagem;
    
    container.appendChild(toast);
    
    // Disparar animação de entrada
    requestAnimationFrame(() => {
        toast.classList.add('toast-visible');
    });
    
    // Remover após a duração
    setTimeout(() => {
        toast.classList.remove('toast-visible');
        toast.classList.add('toast-hiding');
        
        setTimeout(() => {
            toast.remove();
        }, TEMPO_REMOCAO_TOAST);
    }, duracao);
}

/**
 * Inicializa efeitos ripple em todos os botões
 */
function inicializarEfeitosRipple() {
    document.querySelectorAll('.btn-primario, .btn-secundario').forEach(botao => {
        adicionarEfeitoRipple(botao);
    });
}

/**
 * Anima a entrada de um item de lista
 */
function animarEntradaItem(item, delay = 0) {
    item.style.opacity = '0';
    item.style.transform = 'translateX(-20px)';
    
    setTimeout(() => {
        item.style.transition = 'opacity 300ms ease-out, transform 300ms ease-out';
        item.style.opacity = '1';
        item.style.transform = 'translateX(0)';
    }, delay);
}

/**
 * Anima múltiplos itens em sequência
 */
function animarItensEmSequencia(itens, delayBase = DELAY_ENTRADA_ITEM) {
    itens.forEach((item, index) => {
        animarEntradaItem(item, index * delayBase);
    });
}

/**
 * Animação shake para indicar erro
 */
function shake(elemento) {
    elemento.classList.add('shake');
    setTimeout(() => elemento.classList.remove('shake'), TEMPO_ANIMACAO_SHAKE);
}

/**
 * Animação highlight para indicar atualização
 */
function highlight(elemento) {
    elemento.classList.add('highlight');
    setTimeout(() => elemento.classList.remove('highlight'), TEMPO_ANIMACAO_HIGHLIGHT);
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.Animacoes = {
        aplicarSombra,
        fadeIn,
        fadeOut,
        slideIn,
        scaleIn,
        adicionarEfeitoRipple,
        mostrarToast,
        inicializarEfeitosRipple,
        animarEntradaItem,
        animarItensEmSequencia,
        shake,
        highlight
    };
}
