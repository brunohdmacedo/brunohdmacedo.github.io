window.addEventListener("DOMContentLoaded", () => {
    // 1. Desativa a tela de loading após o carregamento completo
    setTimeout(() => {
        const loader = document.getElementById("loading-screen");
        if (loader) {
            loader.style.transition = "opacity 0.5s ease";
            loader.style.opacity = "0";
            setTimeout(() => loader.style.display = "none", 500);
        }
    }, 800);

    // 2. Sistema Avançado de Parallax Suave nas Imagens dos Agentes (CT e TR)
    const ctAgent = document.querySelector(".ct-agent");
    const trAgent = document.querySelector(".tr-agent");

    window.addEventListener("scroll", () => {
        let scrollValue = window.scrollY;
        
        if (window.innerWidth > 900) { // Executa apenas em telas maiores para poupar desempenho móvel
            if (ctAgent) {
                ctAgent.style.transform = `translateY(${scrollValue * 0.12}px) scale(${1 + scrollValue * 0.0001})`;
            }
            if (trAgent) {
                trAgent.style.transform = `translateY(${scrollValue * 0.12}px) scale(${1 + scrollValue * 0.0001})`;
            }
        }
    });
});

/**
 * Função Dinâmica de Cópia de Cupom com Retorno Visual ao Usuário
 * @param {string} cupomNome - Nome do Cupom a ser copiado ('BHS' ou 'BHSKING')
 * @param {HTMLElement} botaoElemento - O botão clicado
 */
function copiarCupom(cupomNome, botaoElemento) {
    navigator.clipboard.writeText(cupomNome).then(() => {
        // Guarda o HTML interno original para restaurar depois
        const originalHTML = botaoElemento.innerHTML;
        
        // Altera para feedback de sucesso
        botaoElemento.innerHTML = `<span class="btn-text">COPIADO COM SUCESSO!</span> <i class="fa-solid fa-check"></i>`;
        botaoElemento.style.filter = "brightness(1.3)";
        
        // Restaura após 2 segundos
        setTimeout(() => {
            botaoElemento.innerHTML = originalHTML;
            botaoElemento.style.filter = "none";
        }, 2000);
    }).catch(err => {
        console.error("Erro ao copiar código: ", err);
        alert(`Código: ${cupomNome}`);
    });
}

// SIMULAÇÃO DE VERIFICAÇÃO DE STATUS DE LIVE (API TWITCH/KICK)
// Em produção, você pode substituir isso por um fetch real da API da Twitch.
function checarStatusLive() {
    const popup = document.getElementById("live-popup-stream");
    if (!popup) return;

    // Simulação: Vamos definir como 'true' para demonstrar ele funcionando na tela.
    const estaOnline = true; 

    if (estaOnline) {
        // Remove a classe que esconde o popup após 3 segundos da página aberta (efeito elegante)
        setTimeout(() => {
            popup.classList.remove("hidden-popup");
        }, 3000);
    } else {
        popup.classList.add("hidden-popup");
    }
}

// Função executada ao clicar no botão 'X' do Pop-up
function fecharPopUpLive() {
    const popup = document.getElementById("live-popup-stream");
    if (popup) {
        popup.classList.add("hidden-popup");
    }
}

// 1. Controle da Tela de Carregamento (Loading Screen) com Fallback de Segurança
window.addEventListener("load", () => {
    const loader = document.getElementById("loading-screen");
    if (loader) {
        loader.style.transition = "opacity 0.5s ease";
        loader.style.opacity = "0";
        setTimeout(() => {
            loader.style.display = "none";
        }, 500);
    }
});

// 2. Sistema de Parallax Suave nos Agentes Laterais (Apenas em telas desktop)
window.addEventListener("scroll", () => {
    const scrollValue = window.scrollY;
    const ctAgent = document.querySelector(".ct-agent");
    const trAgent = document.querySelector(".tr-agent");

    if (window.innerWidth > 900) {
        if (ctAgent) {
            ctAgent.style.transform = `translateY(${scrollValue * 0.12}px) scale(${1 + scrollValue * 0.0001})`;
        }
        if (trAgent) {
            trAgent.style.transform = `translateY(${scrollValue * 0.12}px) scale(${1 + scrollValue * 0.0001})`;
        }
    }
});

// 3. Verificação Automatizada do Status da Live (Aparece o Pop-up se Online)
function checarStatusLive() {
    const popup = document.getElementById("live-popup-stream");
    if (!popup) return;

    // Define se a live está ativa (true = aparece na tela)
    const estaOnline = true; 

    if (estaOnline) {
        setTimeout(() => {
            popup.classList.remove("hidden-popup");
        }, 2000); // Surge elegantemente após 2 segundos
    } else {
        popup.classList.add("hidden-popup");
    }
}

// 4. Fechamento manual do Pop-up pelo botão 'X'
function fecharPopUpLive() {
    const popup = document.getElementById("live-popup-stream");
    if (popup) {
        popup.classList.add("hidden-popup");
    }
}

// 5. Sistema Dinâmico de Cópia de Cupons
function copiarCupom(cupomNome, botaoElemento) {
    navigator.clipboard.writeText(cupomNome).then(() => {
        const originalHTML = botaoElemento.innerHTML;
        botaoElemento.innerHTML = `<span class="btn-text">COPIADO!</span> <i class="fa-solid fa-check"></i>`;
        botaoElemento.style.filter = "brightness(1.3)";
        
        setTimeout(() => {
            botaoElemento.innerHTML = originalHTML;
            botaoElemento.style.filter = "none";
        }, 2000);
    }).catch(err => {
        console.error("Erro ao copiar: ", err);
    });
}

// Inicia as checagens periféricas assim que a estrutura do DOM estiver pronta
window.addEventListener("DOMContentLoaded", checarStatusLive);

// ========================================= //
/* LÓGICA DO CARROSSEL DE SORTEIOS PASSADOS  */
// ========================================= //
let indiceCarrosselAtual = 0;
let carrosselIntervalo;

function moverCarrosselAutomatico() {
    const track = document.getElementById("carouselTrack");
    if (!track) return;
    
    const itens = track.querySelectorAll(".carousel-item");
    if (itens.length === 0) return;

    indiceCarrosselAtual++;
    if (indiceCarrosselAtual >= itens.length) {
        indiceCarrosselAtual = 0;
    }
    
    atualizarPosicaoCarrossel(track);
}

function moveCarrossel(direcao) {
    const track = document.getElementById("carouselTrack");
    if (!track) return;
    
    const itens = track.querySelectorAll(".carousel-item");
    if (itens.length === 0) return;

    // Cancela o timer automático antigo para reiniciar o tempo quando o usuário clica manual
    clearInterval(carrosselIntervalo);

    indiceCarrosselAtual += direcao;
    
    if (indiceCarrosselAtual >= itens.length) {
        indiceCarrosselAtual = 0;
    }
    if (indiceCarrosselAtual < 0) {
        indiceCarrosselAtual = itens.length - 1;
    }

    atualizarPosicaoCarrossel(track);
    
    // Reinicia o loop automático
    iniciarLoopCarrossel();
}

function atualizarPosicaoCarrossel(track) {
    const deslocamento = indiceCarrosselAtual * -100;
    track.style.transform = `translateX(${deslocamento}%)`;
}

function iniciarLoopCarrossel() {
    carrosselIntervalo = setInterval(moverCarrosselAutomatico, 4000); // Muda de skin a cada 4 segundos
}

// Inicializa o movimento assim que o DOM carregar
window.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("carouselTrack")) {
        iniciarLoopCarrossel();
    }
});

// Função Dinâmica Universal para Cópia de Cupons com Feedback Visual
function copiarCupom(cupomNome, botaoElemento) {
    if (!botaoElemento) return;
    
    navigator.clipboard.writeText(cupomNome).then(() => {
        const spanText = botaoElemento.querySelector(".btn-text");
        const originalHTML = spanText ? spanText.innerText : botaoElemento.innerHTML;
        
        if (spanText) {
            spanText.innerText = "COPIADO!";
        } else {
            botaoElemento.innerText = "COPIADO!";
        }
        
        botaoElemento.style.filter = "brightness(1.4)";
        
        setTimeout(() => {
            if (spanText) {
                spanText.innerText = originalHTML;
            } else {
                botaoElemento.innerHTML = originalHTML;
            }
            botaoElemento.style.filter = "none";
        }, 2000);
    }).catch(err => {
        console.error("Erro ao copiar código: ", err);
    });
}