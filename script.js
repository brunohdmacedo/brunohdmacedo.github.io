/**
 * Bruno Macedo — Física Computacional & Mecânica Quântica
 * Simulações Quânticas Interativas, Terminal HPC, Estrutura de Bandas e Filtros
 */

document.addEventListener('DOMContentLoaded', () => {

  // 1. Atualizar ano
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // 2. Barra de leitura
  const progressBar = document.getElementById('scrollProgress');
  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (window.scrollY / totalHeight) * 100;
    if (progressBar) progressBar.style.width = `${progress}%`;
  }, { passive: true });

  // 3. Menu Mobile
  const header = document.getElementById('siteHeader');
  const burger = document.getElementById('burger');
  if (burger && header) {
    burger.addEventListener('click', () => {
      const isOpen = header.classList.toggle('open');
      burger.setAttribute('aria-expanded', isOpen);
    });
    document.querySelectorAll('#mobilemenu a').forEach(link => {
      link.addEventListener('click', () => {
        header.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // 4. Alternador de Tema Claro/Escuro
  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('bm-theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const target = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', target);
      localStorage.setItem('bm-theme', target);
    });
  }

  // 5. Scroll Reveal
  const reveals = document.querySelectorAll('.reveal, .reveal-tl');
  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    reveals.forEach(el => obs.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('in'));
  }

  // 6. Contadores
  const counters = document.querySelectorAll('.counter');
  let counted = false;
  if ('IntersectionObserver' in window && counters.length > 0) {
    const counterObs = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !counted) {
        counted = true;
        counters.forEach(counter => {
          const target = +counter.getAttribute('data-target');
          const suffix = counter.getAttribute('data-suffix') || '';
          let current = 0;
          const inc = target / 35;
          const update = () => {
            current += inc;
            if (current < target) {
              counter.textContent = Math.ceil(current) + suffix;
              requestAnimationFrame(update);
            } else {
              counter.textContent = target + suffix;
            }
          };
          update();
        });
      }
    }, { threshold: 0.4 });
    counterObs.observe(counters[0]);
  }

  // 7. Filtro de Pesquisas
  const filterBtns = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.rcard');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      cards.forEach(card => {
        const cat = card.getAttribute('data-category');
        if (filter === 'all' || cat === filter) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  // 8. Copiar E-mail com Toast
  const emailBtn = document.getElementById('emailCopyBtn');
  const toast = document.getElementById('toast');
  if (emailBtn) {
    emailBtn.addEventListener('click', () => {
      const email = 'brunohdmacedo@gmail.com';
      navigator.clipboard.writeText(email).then(() => {
        if (toast) {
          toast.textContent = 'E-mail copiado com sucesso!';
          toast.classList.add('show');
          setTimeout(() => toast.classList.remove('show'), 2600);
        }
      });
    });
  }

  // 9. Tilt 3D
  document.querySelectorAll('[data-tilt]').forEach(el => {
    el.addEventListener('mousemove', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      el.style.transform = `perspective(500px) rotateX(${-y / 6}deg) rotateY(${x / 6}deg) scale(1.05)`;
    });
    el.addEventListener('mouseleave', () => {
      el.style.transform = 'perspective(500px) rotateX(0deg) rotateY(0deg) scale(1)';
    });
  });

  // =========================================================================
  // 10. SIMULAÇÃO HERO: ONDAS QUÂNTICAS & PACOTE DE ONDAS SCHRÖDINGER
  // =========================================================================
  const qCanvas = document.getElementById('quantumWaveCanvas');
  if (qCanvas) {
    const ctx = qCanvas.getContext('2d');
    let width, height;
    let t = 0;
    let mouse = { x: -1000, y: -1000 };

    window.addEventListener('mousemove', (e) => {
      const rect = qCanvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });

    function resize() {
      width = qCanvas.width = qCanvas.parentElement.offsetWidth;
      height = qCanvas.height = qCanvas.parentElement.offsetHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    function drawWave() {
      ctx.clearRect(0, 0, width, height);
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      
      const numLines = 6;
      for (let l = 0; l < numLines; l++) {
        ctx.beginPath();
        const baseOffsetY = height * (0.35 + l * 0.1);
        ctx.strokeStyle = isDark 
          ? `rgba(94, 234, 212, ${0.08 + l * 0.03})` 
          : `rgba(30, 80, 73, ${0.08 + l * 0.03})`;
        ctx.lineWidth = 1.6;

        for (let x = 0; x <= width; x += 6) {
          // Equação de onda periódica modulada por pacote gaussiano
          const k = 0.015 + l * 0.003;
          const omega = 0.03 + l * 0.008;
          
          let psi = Math.sin(k * x - omega * t) * Math.cos(0.004 * x + omega * 0.5 * t);
          
          // Efeito de perturbação do potencial pelo cursor (efeito túnel/dispersão)
          const distMouse = Math.hypot(x - mouse.x, baseOffsetY - mouse.y);
          if (distMouse < 180) {
            const perturbation = (180 - distMouse) / 180;
            psi += Math.sin(distMouse * 0.1 - t * 0.1) * perturbation * 1.5;
          }

          const y = baseOffsetY + psi * (28 + l * 6);
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }

      t += 1;
      requestAnimationFrame(drawWave);
    }
    drawWave();
  }

  // =========================================================================
  // 11. LABORATÓRIO QUÂNTICO: POÇO DE POTENCIAL 1D
  // =========================================================================
  const wellCanvas = document.getElementById('wellCanvas');
  const qButtons = document.querySelectorAll('.btn-q');
  const energyValue = document.getElementById('energyValue');
  const nodesCount = document.getElementById('nodesCount');

  let currentN = 1;

  qButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      qButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentN = +btn.getAttribute('data-n');
      if (energyValue) energyValue.textContent = `${(currentN * currentN).toFixed(2)} E₁`;
      if (nodesCount) nodesCount.textContent = `${currentN - 1}`;
      drawWell();
    });
  });

  function drawWell() {
    if (!wellCanvas) return;
    const ctx = wellCanvas.getContext('2d');
    const w = wellCanvas.width;
    const h = wellCanvas.height;
    ctx.clearRect(0, 0, w, h);

    const padding = 70;
    const L = w - 2 * padding;
    const baseline = h / 2;

    // Paredes do Poço de Potencial Infinito (V = ∞)
    ctx.strokeStyle = '#64748B';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(padding, 20);
    ctx.lineTo(padding, h - 20);
    ctx.moveTo(w - padding, 20);
    ctx.lineTo(w - padding, h - 20);
    ctx.stroke();

    // Linha de base de Energia Zero
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padding, baseline);
    ctx.lineTo(w - padding, baseline);
    ctx.stroke();
    ctx.setLineDash([]);

    // 1. Função de Onda psi_n(x) = sqrt(2/L) * sin(n*pi*x/L)
    ctx.beginPath();
    ctx.strokeStyle = '#5EEAD4';
    ctx.lineWidth = 2.4;
    const amplitude = 85;

    for (let i = 0; i <= L; i++) {
      const x = padding + i;
      const val = Math.sin((currentN * Math.PI * i) / L);
      const y = baseline - val * amplitude;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // 2. Densidade de Probabilidade |psi_n(x)|^2
    ctx.beginPath();
    ctx.strokeStyle = '#FBBF24';
    ctx.fillStyle = 'rgba(251, 191, 36, 0.18)';
    ctx.lineWidth = 2;

    ctx.moveTo(padding, baseline);
    for (let i = 0; i <= L; i++) {
      const x = padding + i;
      const val = Math.sin((currentN * Math.PI * i) / L);
      const prob = val * val; // |psi|^2
      const y = baseline - prob * (amplitude * 0.95);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(w - padding, baseline);
    ctx.stroke();
    ctx.fill();

    // Rótulos do Poço
    ctx.fillStyle = '#94A3B8';
    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.fillText('x = 0 (V = ∞)', padding - 20, h - 6);
    ctx.fillText('x = L (V = ∞)', w - padding - 40, h - 6);
  }
  drawWell();

  // =========================================================================
  // 12. SIMULADOR DE ESTRUTURA DE BANDAS E BANDGAP
  // =========================================================================
  const bandCanvas = document.getElementById('bandCanvas');
  const bandBtns = document.querySelectorAll('.band-btn');
  const bandExplanation = document.getElementById('bandExplanation');

  const bandConfigs = {
    insulator: {
      gap: 90,
      name: 'MgH₂ Puro (Isolante)',
      text: 'MgH₂ Puro: Amplo bandgap (~5.6 eV). Os elétrons da banda de valência não cruzam para a condução sob condições brandas, resultando em baixa reatividade inicial de dessorção.'
    },
    semiconductor: {
      gap: 38,
      name: 'MgH₂ Dopado com Fe/Ni (Semicondutor/Ativado)',
      text: 'MgH₂ Dopado: A inserção de impurezas metálicas cria estados eletrônicos intermediários no gap, diminuindo a barreira energética e acelerando a cinética de estocagem de hidrogênio.'
    },
    metal: {
      gap: -15,
      name: 'Cruzamento Metálico (Condutor)',
      text: 'Fase Condutora: Sobreposição das bandas de valência e condução através do nível de Fermi (EF), permitindo mobilidade eletrônica máxima e alta transferência de carga.'
    }
  };

  let currentBandMode = 'insulator';

  bandBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      bandBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentBandMode = btn.getAttribute('data-type');
      if (bandExplanation) bandExplanation.innerHTML = `<strong>${bandConfigs[currentBandMode].name}:</strong> ${bandConfigs[currentBandMode].text}`;
      renderBandDiagram();
    });
  });

  function renderBandDiagram() {
    if (!bandCanvas) return;
    const ctx = bandCanvas.getContext('2d');
    const w = bandCanvas.width;
    const h = bandCanvas.height;
    ctx.clearRect(0, 0, w, h);

    const cfg = bandConfigs[currentBandMode];
    const efY = h / 2;

    // Nível de Fermi (E_F)
    ctx.strokeStyle = '#E5A93C';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(60, efY);
    ctx.lineTo(w - 60, efY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#E5A93C';
    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.fillText('Nível de Fermi (EF)', w - 190, efY - 8);

    // Banda de Condução (Superior)
    ctx.beginPath();
    ctx.strokeStyle = '#6EE7B7';
    ctx.lineWidth = 2.4;
    const condY = efY - (cfg.gap / 2);
    for (let x = 60; x <= w - 60; x++) {
      const k = (x - 60) / (w - 120);
      const curve = Math.cos(k * Math.PI * 2) * -35;
      const y = condY + curve - 30;
      if (x === 60) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Banda de Valência (Inferior)
    ctx.beginPath();
    ctx.strokeStyle = '#38BDF8';
    ctx.lineWidth = 2.4;
    const valY = efY + (cfg.gap / 2);
    for (let x = 60; x <= w - 60; x++) {
      const k = (x - 60) / (w - 120);
      const curve = Math.cos(k * Math.PI * 2) * 35;
      const y = valY + curve + 30;
      if (x === 60) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Rótulos de simetria k (Γ - X - L)
    ctx.fillStyle = '#94A3B8';
    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.fillText('Γ (0,0,0)', 60, h - 14);
    ctx.fillText('X (0.5, 0, 0.5)', w / 2 - 40, h - 14);
    ctx.fillText('L (0.5, 0.5, 0.5)', w - 160, h - 14);
  }
  renderBandDiagram();

  // =========================================================================
  // 13. TERMINAL SHELL INTERATIVO DE SIMULAÇÃO (CLUSTER LIMCCA)
  // =========================================================================
  const termInput = document.getElementById('termInput');
  const termOutput = document.getElementById('termOutput');

  const cmdDatabase = {
    'ajuda': 'Comandos: <strong>rodar-dft</strong>, <strong>calcular-gap</strong>, <strong>mgh2</strong>, <strong>limcca</strong>, <strong>clear</strong>, <strong>sobre</strong>',
    'sobre': 'Pesquisador: Bruno H. D. Macedo | Mestrando em Física Aplicada (UNILA) | Especialista em DFT e Ciência de Materiais.',
    'limcca': 'LIMCCA: Laboratório Interdisciplinar de Modelagem e Computação Científica Aplicada — UNILA. Foco em simulações multifísicas e mecânica quântica.',
    'mgh2': 'Estrutura: Hidreto de Magnésio (P4_2/mnm, Rutilo). Parâmetros a=4.501 Å, c=3.010 Å. Capacidade teórica gravimétrica: 7.6 wt% H2.',
    'calcular-gap': 'Autovalores Kohn-Sham calculados: Bandgap direto = 5.61 eV (PBE). Estado: Isolante de gap largo.',
    'rodar-dft': '[JOB 4092] Iniciando cálculo DFT (CASTEP/Quantum ESPRESSO)...<br>&gt; Otimização de geometria: CONVERGIDA (4 iterações SCF)<br>&gt; Energia Total = -1428.39201 Ry<br>&gt; Forças atômicas residuais &lt; 0.001 eV/Å.<br>&gt; Simulação concluída com sucesso!'
  };

  if (termInput && termOutput) {
    termInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const val = termInput.value.trim().toLowerCase();
        termInput.value = '';
        if (!val) return;

        if (val === 'clear') {
          termOutput.innerHTML = '';
          return;
        }

        const userRow = document.createElement('p');
        userRow.className = 'term-line-info';
        userRow.innerHTML = `<span class="term-user">bruno@limcca:~$</span> <span class="term-cmd">${val}</span>`;
        termOutput.appendChild(userRow);

        const respRow = document.createElement('p');
        respRow.className = 'term-out';
        respRow.innerHTML = cmdDatabase[val] || `Comando não reconhecido: "${val}". Digite <strong>ajuda</strong>.`;
        termOutput.appendChild(respRow);

        termOutput.scrollTop = termOutput.scrollHeight;
      }
    });
  }

});