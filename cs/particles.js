const canvas = document.getElementById("particles-canvas");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = canvas.parentElement.offsetHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

const particleArray = [];
const numberOfParticles = 120; // Quantidade balanceada para excelente performance

class EnergyParticle {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = Math.random() * canvas.width;
        // Começa sempre na parte inferior da seção hero
        this.y = canvas.height + Math.random() * 20; 
        this.size = Math.random() * 2.5 + 0.8;
        this.speedY = Math.random() * 2.2 + 0.6; // Velocidade de subida
        
        // Movimento lateral para simular chama/raio flutuante
        this.speedX = Math.random() * 1 - 0.5; 
        
        // Define a cor baseada no lado da tela (Lado esquerdo = Azul CT | Lado direito = Laranja TR)
        if (this.x < canvas.width / 2) {
            this.color = Math.random() > 0.2 ? "#00a2ff" : "#ffffff"; // Azul ou Faísca branca
            this.glowColor = "rgba(0, 162, 255, 0.6)";
        } else {
            this.color = Math.random() > 0.2 ? "#ff8c00" : "#ffeedd"; // Laranja ou Brilho térmico
            this.glowColor = "rgba(255, 140, 0, 0.6)";
        }
        
        this.opacity = Math.random() * 0.7 + 0.3;
        this.life = Math.random() * 200 + 100; // Tempo de vida da partícula
    }

    update() {
        this.y -= this.speedY;
        this.x += this.speedX;
        this.life--;

        // Pequena oscilação horizontal simulando calor
        this.speedX += (Math.random() * 0.4 - 0.2);
        
        // Restringe a oscilação lateral máxima
        if (this.speedX > 1.5) this.speedX = 1.5;
        if (this.speedX < -1.5) this.speedX = -1.5;

        // Se a partícula morrer ou sair do topo, reseta abaixo
        if (this.y < 0 || this.life <= 0) {
            this.reset();
        }
    }

    draw() {
        ctx.save();
        ctx.globalAlpha = this.opacity;
        ctx.shadowBlur = 8;
        ctx.shadowColor = this.glowColor;
        ctx.fillStyle = this.color;
        
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
}

// Inicializa o array de partículas
for (let i = 0; i < numberOfParticles; i++) {
    particleArray.push(new EnergyParticle());
}

// Loop de Animação em 60fps (Otimizado com RequestAnimationFrame)
function handleParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < particleArray.length; i++) {
        particleArray[i].update();
        particleArray[i].draw();
    }
    requestAnimationFrame(handleParticles);
}

handleParticles();

const canvas = document.getElementById("particles-canvas");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = canvas.parentElement.offsetHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

const particleArray = [];
const numberOfParticles = 100; // Densidade ideal para não causar lag visual

class BulletTracerParticle {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = Math.random() * canvas.width;
        // Metade das partículas surge debaixo, a outra metade surge das laterais simulando tiros cruzados
        this.y = Math.random() > 0.5 ? canvas.height + Math.random() * 50 : Math.random() * canvas.height;
        
        // Define se a partícula é um "Tiro Traçante Rapido" ou uma "Faísca de Impacto"
        this.isTracer = Math.random() > 0.6; 

        if (this.isTracer) {
            this.length = Math.random() * 40 + 20; // Comprimento da linha do tiro
            this.speedY = Math.random() * 8 + 6;   // Muito veloz
            this.speedX = Math.random() * 4 - 2;   // Direção diagonal angular
            this.size = Math.random() * 1.5 + 0.5; // Espessura do tiro
        } else {
            this.length = 0; // Ponto/Faísca circular normal
            this.speedY = Math.random() * 2 + 0.5;
            this.speedX = Math.random() * 1.5 - 0.75;
            this.size = Math.random() * 2 + 0.8;
        }

        // Divisão de Cores por território (Esquerda = Azul CT | Direita = Laranja TR)
        if (this.x < canvas.width / 2) {
            this.color = this.isTracer ? "#00c3ff" : "#0088ff";
            this.glowColor = "rgba(0, 162, 255, 0.8)";
        } else {
            this.color = this.isTracer ? "#ffaa00" : "#ff5500";
            this.glowColor = "rgba(255, 140, 0, 0.8)";
        }

        this.opacity = Math.random() * 0.6 + 0.4;
        this.life = Math.random() * 150 + 50;
    }

    update() {
        this.y -= this.speedY;
        this.x -= this.speedX; // Movimento contínuo no vetor do disparo
        this.life--;

        // Se sair da tela ou o tempo expirar, reinicia como um novo disparo
        if (this.y < -50 || this.x < -50 || this.x > canvas.width + 50 || this.life <= 0) {
            this.reset();
        }
    }

    draw() {
        ctx.save();
        ctx.globalAlpha = this.opacity;
        ctx.shadowBlur = this.isTracer ? 12 : 6;
        ctx.shadowColor = this.glowColor;
        ctx.fillStyle = this.color;
        ctx.strokeStyle = this.color;
        ctx.lineWidth = this.size;

        if (this.isTracer) {
            // Desenha a linha esticada representando o projétil traçante em movimento
            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            // O traço aponta na direção de onde ele veio baseado em sua velocidade
            ctx.lineTo(this.x + this.speedX * 2, this.y + this.speedY * 2);
            ctx.stroke();
        } else {
            // Desenha a faísca circular tradicional de fogo/energia
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }
}

// Alimentando o sistema
for (let i = 0; i < numberOfParticles; i++) {
    particleArray.push(new BulletTracerParticle());
}

// Loop contínuo otimizado em alta taxa de quadros
function animateEngine() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < particleArray.length; i++) {
        particleArray[i].update();
        particleArray[i].draw();
    }
    requestAnimationFrame(animateEngine);
}

animateEngine();