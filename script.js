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

/**
 * Bruno Macedo — Computational Physics & Quantum Mechanics
 * Sistema de Internacionalização (i18n PT / EN), Simulações Quânticas e Terminal
 */

// =========================================================================
// DICIONÁRIO DE TRADUÇÃO (PORTUGUÊS & ENGLISH)
// =========================================================================
const translations = {
  pt: {
    nav_about: "Sobre",
    nav_lab: "Lab Quântico",
    nav_research: "Pesquisa & DFT",
    nav_sim: "Simulador Bandas",
    nav_timeline: "Trajetória",
    nav_media: "Mídia",
    nav_terminal: "Cluster",
    nav_theme: "Tema",
    nav_cta: "Fale comigo",
    
    hero_eyebrow: "Física Computacional · LIMCCA & Eletroquímica · UNILA",
    hero_title: "Modelando a matéria pela <em>Mecânica Quântica</em> e primeiros princípios.",
    hero_desc: "Pesquisador em Física Computacional e Materiais Sustentáveis. Combino cálculos de Teoria do Funcional da Densidade (DFT), computação em clusters e algoritmos preditivos para resolver a equação de muitos corpos e simular o armazenamento quântico de hidrogênio no MgH₂.",
    role_1: "Mestrando em Física Aplicada",
    role_2: "Engenharia Física",
    role_3: "Cálculos DFT & HPC",
    role_4: "Modelagem Quântica · LIMCCA",
    role_5: "Eletroquímica UNILA",
    hero_btn_lab: "Simular Função de Onda",
    hero_btn_term: "Abrir Terminal Quântico",

    about_title: "Fundamentos & Linha Científica",
    about_subtitle: "A física do estado sólido desvendada através de simulações numéricas intensivas e computação quântica de materiais.",
    about_p1: "Meu nome é <strong>Bruno Macedo</strong>, mestrando no Programa de Pós-Graduação em Física Aplicada e Engenheiro Físico graduado pela <strong>Universidade Federal da Integração Latino-Americana (UNILA)</strong>. Minha pesquisa concentra-se na física do estado sólido computacional, termodinâmica quântica e machine learning aplicado às ciências da matéria.",
    about_p2: "Atuo ativamente como pesquisador no <strong>Laboratório Interdisciplinar de Modelagem e Computação Científica Aplicada (LIMCCA)</strong> e no <strong>Grupo Interdisciplinar de Eletroquímica da UNILA</strong>. Minha trajetória engloba projetos de <strong>P&D na UNIOESTE</strong> e investigação por primeiros princípios no grupo <strong>GANEL</strong>, desenvolvendo modelos mecanísticos de aprisionamento de hidrogênio no hidreto de magnésio (MgH₂).",
    about_p3: "Detenho certificação avançada em <em>Density Functional Theory</em> pela renomada École Polytechnique (França) e em <em>Machine Learning Foundations</em> pela University of Washington (EUA), construindo rotinas de simulação atomística em Python, Fortran e ambientes paralelos em supercomputadores.",
    fact_1: "horas em simulação & treinamento avançado",
    fact_2: "menções honrosas acadêmicas",
    fact_3: "grupos & labs (LIMCCA, Eletroquímica, GANEL, LACA)",

    lab_title: "Laboratório Quântico Interativo",
    lab_desc: "Explore as soluções da Equação de Schrödinger para um poço de potencial infinito. Altere o número quântico principal n e observe a probabilidade |ψ(x)|².",
    lab_control_lbl: "Estado Quântico (Nível de Energia n):",
    lab_energy: "Energia Relativa",
    lab_nodes: "Nós na Função",
    lab_leg_psi: "Função de Onda ψₙ(x)",
    lab_leg_prob: "Densidade de Probabilidade |ψₙ(x)|²",

    res_title: "Linhas de Pesquisa Computacional",
    res_subtitle: "Aplicações da mecânica quântica e inteligência artificial na fronteira dos materiais e da energia.",
    res_f_all: "Todos os Projetos",
    res_f_dft: "DFT & Hidrogênio",
    res_f_limcca: "LIMCCA & Eletroquímica",
    res_f_ml: "Machine Learning",
    rcard1_title: "Armazenamento de Hidrogênio via DFT",
    rcard1_desc: "Cálculos por primeiros princípios sobre células unitárias do hidreto de magnésio dopado com metais de transição. Análise de relaxação atômica, densidade de estados e energia de formação para viabilizar desidretação a baixas temperaturas.",
    rcard_read: "Acessar Artigo / TCC →",
    rcard2_title: "Modelagem no LIMCCA & Interfaces Eletroquímicas",
    rcard2_desc: "Modelagem numérica atomística e de transporte iônico no LIMCCA em convergência com o Grupo de Eletroquímica da UNILA, estudando cinética reacional e estabilidade em interfaces ativas.",
    rcard_contact: "Ver Colaborações →",
    rcard3_title: "Classificação Espectroscópica & Séries Temporais",
    rcard3_desc: "Redes neurais e algoritmos ensemble aplicados sobre dados espectrais de difração de raios-X / Raman (banco RRUFF) e triagem de exoplanetas a partir de curvas de luz astronômicas do Kepler.",
    rcard_view: "Ver Resultados →",

    sim_title: "Simulador de Estrutura Eletrônica & Bandgap",
    sim_subtitle: "Veja como o gap de energia quântico define as propriedades condutoras dos materiais que investigamos.",
    sim_b1: "Isolante Quântico (MgH₂ Puro)",
    sim_b2: "Semicondutor (MgH₂ Dopado)",
    sim_b3: "Condutor Metálico (Banda Cruzada)",

    tl_title: "Trajetória Acadêmica & P&D",
    tl_subtitle: "Caminho evolutivo da base em Engenharia Física à pesquisa avançada em pós-graduação e projetos aplicados.",
    tl_cur_year: "Atual",
    tl_tag_msc: "Mestrado & Modelagem",
    tl_msc_title: "Mestrado em Física Aplicada — LIMCCA & Grupo de Eletroquímica",
    tl_msc_desc: "Pesquisador de pós-graduação no LIMCCA e membro do Grupo Interdisciplinar de Eletroquímica da UNILA. Modelagem computacional por primeiros princípios de nanomateriais e eletroquímica de superfícies para transição energética.",
    tl_tag_pd: "P&D & Graduação",
    tl_2025_title: "Projeto de P&D na UNIOESTE e Conclusão do TCC",
    tl_2025_desc: "Atuação em projeto de Pesquisa e Desenvolvimento (P&D) na UNIOESTE integrando hardware de sensoriamento, automação e análise de dados. Defesa da tese de graduação em dopagem de hidreto de magnésio por DFT e Menção Honrosa na SIEPE 2025.",
    tl_tag_mh: "Menção Honrosa",
    tl_2024_title: "Início no Grupo GANEL — Pesquisa em Hidrogênio",
    tl_2024_desc: "Ingresso no grupo de pesquisa GANEL, liderando cálculos mecânico-quânticos em clusters de supercomputação dedicados à dinâmica atômica de difusão de hidrogênio em redes metálicas.",
    tl_tag_ext: "Prêmio de Extensão",
    tl_2023_title: "Melhor Projeto de Extensão & Univ. of Washington",
    tl_2023_desc: "Laureado com o troféu de Melhor Projeto de Extensão da UNILA e certificação em Machine Learning Foundations pela University of Washington (EUA).",
    tl_2022_title: "Especialização em DFT (École Polytechnique) & SIEPE",
    tl_2022_desc: "Certificação intensiva em Teoria do Funcional da Densidade pela prestigiada École Polytechnique (França) e Menção Honrosa em mostra de ensino e pesquisa científica.",
    tl_2020_laca_title: "Atuação em IA no Laboratório LACA",
    tl_2020_laca_desc: "Quatro anos como integrante do LACA/UNILA, trabalhando na modelagem computacional de dados observacionais espaciais da NASA para identificação de trânsitos exoplanetários.",
    tl_2020_entry_title: "Ingresso em Engenharia Física — UNILA",
    tl_2020_entry_desc: "Início da formação acadêmica em Foz do Iguaçu, iniciando na física do estado sólido, métodos numéricos, equações diferenciais parciais e instrumentação.",

    media_title: "Vídeos & Instagram",
    media_subtitle: "Divulgação científica, rotinas laboratoriais e física computacional no @brunohdmacedo.",
    yt_sec_title: "Vídeos no YouTube",
    yt_link: "Canal @brunohdmacedo →",
    yt_tag_1: "Física Quântica",
    yt_title_1: "Como Construir Células Unitárias e Calcular DFT",
    yt_desc_1: "Métodos práticos de simulação da mecânica quântica em redes cristalinas periódicas.",
    yt_tag_2: "Séries Temporais",
    yt_title_2: "Classificando Exoplanetas com Dados do Kepler",
    yt_desc_2: "Processamento e redução de ruído em dados espaciais com Python científico.",
    yt_tag_3: "Computação Científica",
    yt_title_3: "Automação e Scripts para Simulação de Materiais",
    yt_desc_3: "Construção de rotinas para convergência de energia e extração de autovalores.",
    ig_link: "Ver Feed Completo →",
    ig_c1: "Cálculos quânticos no cluster e convergência SCF para MgH₂. 🔬⚡",
    ig_c2: "Desenvolvimento de rotinas em Python para pós-processamento de bandas. 💻",
    ig_c3: "Apresentação dos projetos do LIMCCA e Eletroquímica na SIEPE. 🎓",
    ig_c4: "Modelos supervisionados em dados do telescópio Kepler. 🌌",

    term_title: "Terminal de Simulação Científica",
    term_subtitle: "Ambiente simulando um nó de processamento de alto desempenho (HPC). Digite os comandos para rodar rotinas quânticas.",
    term_welcome_1: "Cluster LIMCCA/UNILA (x86_64, 64 nós de cálculo, OpenMPI + DFT)",
    term_welcome_2: "Digite <span class=\"term-cmd\">ajuda</span> ou <span class=\"term-cmd\">help</span> para listar os comandos quânticos disponíveis.",
    term_ph: "Ex: rodar-dft, calcular-gap, status",

    contact_title: "Colaborações Científicas",
    contact_desc: "Disponível para cooperações em simulações por primeiros princípios, projetos interdisciplinares no LIMCCA, Grupo de Eletroquímica da UNILA e desenvolvimento de modelos numéricos avançados.",
    contact_copy: "Copiar e-mail científico",
    contact_k_email: "E-mail",
    contact_k_loc: "Localização",
    gh_sub: "Repositórios Quânticos",
    footer_rights: "Mestrando em Física Aplicada · Engenheiro Físico (UNILA).",
    back_top: "Voltar ao topo ↑"
  },
  en: {
    nav_about: "About",
    nav_lab: "Quantum Lab",
    nav_research: "Research & DFT",
    nav_sim: "Band Simulator",
    nav_timeline: "Timeline",
    nav_media: "Media",
    nav_terminal: "Cluster",
    nav_theme: "Theme",
    nav_cta: "Contact me",

    hero_eyebrow: "Computational Physics · LIMCCA & Electrochemistry · UNILA",
    hero_title: "Modelling matter through <em>Quantum Mechanics</em> and first-principles.",
    hero_desc: "Researcher in Computational Physics and Sustainable Materials. Combining Density Functional Theory (DFT) calculations, cluster computing and predictive algorithms to solve the many-body problem and model quantum hydrogen storage in MgH₂.",
    role_1: "MSc Candidate in Applied Physics",
    role_2: "Physical Engineering",
    role_3: "DFT & HPC Calculations",
    role_4: "Quantum Modelling · LIMCCA",
    role_5: "Electrochemistry UNILA",
    hero_btn_lab: "Simulate Wavefunction",
    hero_btn_term: "Open Quantum Terminal",

    about_title: "Fundamentals & Scientific Line",
    about_subtitle: "Solid-state physics unveiled through high-throughput numerical simulations and quantum materials computing.",
    about_p1: "My name is <strong>Bruno Macedo</strong>, an MSc researcher in Applied Physics and Physical Engineer graduated from <strong>Federal University for Latin American Integration (UNILA)</strong>. My research focuses on computational solid-state physics, quantum thermodynamics and machine learning applied to materials science.",
    about_p2: "I actively conduct research at the <strong>Interdisciplinary Laboratory of Applied Mathematical and Computational Modeling (LIMCCA)</strong> and the <strong>Interdisciplinary Electrochemistry Group at UNILA</strong>. My background includes <strong>R&D projects at UNIOESTE</strong> and first-principles simulations in the <strong>GANEL</strong> group, focusing on hydrogen uptake in magnesium hydride (MgH₂).",
    about_p3: "I hold advanced training in <em>Density Functional Theory</em> from École Polytechnique (France) and <em>Machine Learning Foundations</em> from the University of Washington (USA), developing atomistic modeling pipelines in Python, Fortran, and parallel HPC clusters.",
    fact_1: "hours of advanced simulation & training",
    fact_2: "academic honorable mentions",
    fact_3: "research groups & labs (LIMCCA, Electrochemistry, GANEL, LACA)",

    lab_title: "Interactive Quantum Laboratory",
    lab_desc: "Explore solutions to Schrödinger's Equation for an infinite potential well. Change the principal quantum number n and observe the probability density |ψ(x)|².",
    lab_control_lbl: "Quantum State (Energy Level n):",
    lab_energy: "Relative Energy",
    lab_nodes: "Wavefunction Nodes",
    lab_leg_psi: "Wavefunction ψₙ(x)",
    lab_leg_prob: "Probability Density |ψₙ(x)|²",

    res_title: "Computational Research Lines",
    res_subtitle: "Applications of quantum mechanics and artificial intelligence at the frontier of materials and sustainable energy.",
    res_f_all: "All Projects",
    res_f_dft: "DFT & Hydrogen",
    res_f_limcca: "LIMCCA & Electrochemistry",
    res_f_ml: "Machine Learning",
    rcard1_title: "Hydrogen Storage via DFT",
    rcard1_desc: "First-principles calculations on magnesium hydride supercells with transition metal doping. Assessing atomic relaxation, electronic density of states, and formation energies to optimize low-temperature desorption.",
    rcard_read: "Read Paper / Thesis →",
    rcard2_title: "LIMCCA Modeling & Electrochemical Interfaces",
    rcard2_desc: "Atomistic and ionic transport numerical modeling at LIMCCA joint with UNILA's Electrochemistry Group, probing reaction kinetics and stability in active interfaces.",
    rcard_contact: "Collaborations →",
    rcard3_title: "Spectroscopic Classification & Time Series",
    rcard3_desc: "Deep neural networks and ensemble learning applied to RRUFF Raman/XRD spectra, along with transit classification on NASA's Kepler space telescope light curves.",
    rcard_view: "View Results →",

    sim_title: "Electronic Band Structure & Bandgap Simulator",
    sim_subtitle: "Observe how quantum energy gaps govern the electrical transport properties of the materials we simulate.",
    sim_b1: "Quantum Insulator (Pure MgH₂)",
    sim_b2: "Semiconductor (Doped MgH₂)",
    sim_b3: "Metallic Conductor (Band Crossing)",

    tl_title: "Academic & R&D Trajectory",
    tl_subtitle: "Bottom-up chronological path: from Physical Engineering fundamentals to advanced graduate research and applied R&D.",
    tl_cur_year: "Present",
    tl_tag_msc: "Graduate & Modelling",
    tl_msc_title: "MSc in Applied Physics — LIMCCA & Electrochemistry Group",
    tl_msc_desc: "Graduate researcher at LIMCCA and member of UNILA's Interdisciplinary Electrochemistry Group. First-principles quantum simulations of nanomaterials and surface electrochemistry for clean energy.",
    tl_tag_pd: "R&D & Engineering",
    tl_2025_title: "R&D Project at UNIOESTE & Capstone Thesis Defense",
    tl_2025_desc: "Research & Development project at UNIOESTE integrating sensing, automation and scientific analysis. Defended Physical Engineering capstone thesis on transition metal doped MgH₂ via DFT, earning an Honorable Mention at SIEPE 2025.",
    tl_tag_mh: "Honorable Mention",
    tl_2024_title: "Joined GANEL Research Group — Hydrogen Studies",
    tl_2024_desc: "Started working with the GANEL research group, running supercomputing cluster DFT calculations on hydrogen atom migration dynamics in metallic lattices.",
    tl_tag_ext: "Best Extension Award",
    tl_2023_title: "Best Extension Project Award & Univ. of Washington",
    tl_2023_desc: "Awarded Best Extension Project of the year at UNILA and completed Machine Learning Foundations certification from the University of Washington (USA).",
    tl_2022_title: "DFT Specialization (École Polytechnique) & SIEPE",
    tl_2022_desc: "Completed advanced Density Functional Theory program by École Polytechnique (France) and received Academic Honorable Mention at SIEPE research symposium.",
    tl_2020_laca_title: "AI Research at LACA Laboratory",
    tl_2020_laca_desc: "Four years conducting machine learning research on NASA astrophysical light curves to automate exoplanet detection.",
    tl_2020_entry_title: "Started Physical Engineering — UNILA",
    tl_2020_entry_desc: "Began undergraduate degree in Foz do Iguaçu, building strong foundations in quantum mechanics, solid-state physics, numerical methods and scientific computing.",

    media_title: "Videos & Instagram",
    media_subtitle: "Science communication, laboratory insights, and computational physics at @brunohdmacedo.",
    yt_sec_title: "YouTube Channel",
    yt_link: "Channel @brunohdmacedo →",
    yt_tag_1: "Quantum Physics",
    yt_title_1: "Building Unit Cells & Running DFT Calculations",
    yt_desc_1: "Hands-on quantum mechanical modeling in periodic crystal lattices.",
    yt_tag_2: "Time Series",
    yt_title_2: "Classifying Exoplanets with Kepler Telescope Data",
    yt_desc_2: "Signal processing and machine learning pipelines in scientific Python.",
    yt_tag_3: "Scientific Computing",
    yt_title_3: "Automating High-Throughput Materials Simulation",
    yt_desc_3: "Writing clean automation scripts for SCF energy convergence and eigenvalues.",
    ig_link: "View Full Feed →",
    ig_c1: "Cluster quantum simulations and SCF convergence routines for MgH₂. 🔬⚡",
    ig_c2: "Developing scientific Python scripts for automated band structure post-processing. 💻",
    ig_c3: "Presenting LIMCCA and Electrochemistry research projects at SIEPE. 🎓",
    ig_c4: "Supervised ML pipelines applied to Kepler astronomical data. 🌌",

    term_title: "Scientific Simulation Terminal",
    term_subtitle: "Simulated High-Performance Computing (HPC) node. Type commands to run quantum tasks.",
    term_welcome_1: "LIMCCA/UNILA Cluster Node (x86_64, 64 compute nodes, OpenMPI + DFT)",
    term_welcome_2: "Type <span class=\"term-cmd\">help</span> or <span class=\"term-cmd\">ajuda</span> to list available quantum simulation commands.",
    term_ph: "E.g.: run-dft, calc-gap, status, help",

    contact_title: "Scientific Collaborations",
    contact_desc: "Available for first-principles research partnerships, multidisciplinary modeling at LIMCCA, UNILA's Electrochemistry Group and advanced R&D projects.",
    contact_copy: "Copy scientific email",
    contact_k_email: "Email",
    contact_k_loc: "Location",
    gh_sub: "Quantum Repositories",
    footer_rights: "MSc Candidate in Applied Physics · Physical Engineer (UNILA).",
    back_top: "Back to top ↑"
  }
};

// =========================================================================
// MOTOR DE IDIOMA DINÂMICO
// =========================================================================
let currentLang = localStorage.getItem('bm-lang') || 'pt';

function updateLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('bm-lang', lang);
  document.documentElement.setAttribute('lang', lang === 'pt' ? 'pt-BR' : 'en');

  // Traduz todos os elementos com data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang] && translations[lang][key]) {
      el.innerHTML = translations[lang][key];
    }
  });

  // Atualiza botões de idioma
  const flag = lang === 'pt' ? '🇺🇸' : '🇧🇷';
  const text = lang === 'pt' ? 'EN' : 'PT';
  const flagEl = document.getElementById('langFlag');
  const textEl = document.getElementById('langText');
  if (flagEl) flagEl.textContent = flag;
  if (textEl) textEl.textContent = text;

  const flagMobile = document.getElementById('langFlagMobile');
  const textMobile = document.getElementById('langTextMobile');
  if (flagMobile) flagMobile.textContent = flag;
  if (textMobile) textMobile.textContent = lang === 'pt' ? 'English' : 'Português';

  // Atualiza placeholder do terminal
  const termIn = document.getElementById('termInput');
  if (termIn) {
    termIn.placeholder = lang === 'pt' ? 'Ex: rodar-dft, calcular-gap, status' : 'E.g.: run-dft, calc-gap, status';
  }

  // Atualiza nota do simulador de bandas
  if (typeof updateBandText === 'function') updateBandText();
}

// Alternadores de clique
const langToggle = document.getElementById('langToggle');
if (langToggle) {
  langToggle.addEventListener('click', () => {
    updateLanguage(currentLang === 'pt' ? 'en' : 'pt');
  });
}
const langToggleMobile = document.getElementById('langToggleMobile');
if (langToggleMobile) {
  langToggleMobile.addEventListener('click', () => {
    updateLanguage(currentLang === 'pt' ? 'en' : 'pt');
  });
}

// =========================================================================
// DEMAIS SCRIPTS (SIMULAÇÕES, TILT, SCROLL, TERMINAL)
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
  // Inicializa idioma guardado
  updateLanguage(currentLang);

  // Ano no rodapé
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Barra de progresso
  const progressBar = document.getElementById('scrollProgress');
  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (window.scrollY / totalHeight) * 100;
    if (progressBar) progressBar.style.width = `${progress}%`;
  }, { passive: true });

  // Menu móvel
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

  // Tema Claro/Escuro
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

  // Scroll Reveal
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

  // Contadores animados
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

  // Filtro de pesquisas
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

  // Copiar e-mail
  const emailBtn = document.getElementById('emailCopyBtn');
  const toast = document.getElementById('toast');
  if (emailBtn) {
    emailBtn.addEventListener('click', () => {
      const email = 'brunohdmacedo@gmail.com';
      navigator.clipboard.writeText(email).then(() => {
        if (toast) {
          toast.textContent = currentLang === 'pt' ? 'E-mail copiado com sucesso!' : 'Email copied to clipboard!';
          toast.classList.add('show');
          setTimeout(() => toast.classList.remove('show'), 2600);
        }
      });
    });
  }

  // Efeito Tilt 3D
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
  // SIMULAÇÃO HERO: ONDAS QUÂNTICAS
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
          const k = 0.015 + l * 0.003;
          const omega = 0.03 + l * 0.008;
          let psi = Math.sin(k * x - omega * t) * Math.cos(0.004 * x + omega * 0.5 * t);
          
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
  // LAB QUÂNTICO: POÇO 1D
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

    ctx.strokeStyle = '#64748B';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(padding, 20); ctx.lineTo(padding, h - 20);
    ctx.moveTo(w - padding, 20); ctx.lineTo(w - padding, h - 20);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padding, baseline); ctx.lineTo(w - padding, baseline);
    ctx.stroke();
    ctx.setLineDash([]);

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

    ctx.beginPath();
    ctx.strokeStyle = '#FBBF24';
    ctx.fillStyle = 'rgba(251, 191, 36, 0.18)';
    ctx.lineWidth = 2;

    ctx.moveTo(padding, baseline);
    for (let i = 0; i <= L; i++) {
      const x = padding + i;
      const val = Math.sin((currentN * Math.PI * i) / L);
      const prob = val * val;
      const y = baseline - prob * (amplitude * 0.95);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(w - padding, baseline);
    ctx.stroke();
    ctx.fill();

    ctx.fillStyle = '#94A3B8';
    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.fillText('x = 0 (V = ∞)', padding - 20, h - 6);
    ctx.fillText('x = L (V = ∞)', w - padding - 40, h - 6);
  }
  drawWell();

  // =========================================================================
  // SIMULADOR DE BANDAS
  // =========================================================================
  const bandCanvas = document.getElementById('bandCanvas');
  const bandBtns = document.querySelectorAll('.band-btn');
  const bandExplanation = document.getElementById('bandExplanation');

  const bandConfigs = {
    insulator: {
      gap: 90,
      name_pt: 'MgH₂ Puro (Isolante)',
      text_pt: 'Amplo bandgap (~5.6 eV). Os elétrons da banda de valência não cruzam para a condução sob condições brandas, resultando em baixa cinética de dessorção.',
      name_en: 'Pure MgH₂ (Insulator)',
      text_en: 'Wide bandgap (~5.6 eV). Valence electrons cannot cross into the conduction band under mild conditions, causing sluggish desorption kinetics.'
    },
    semiconductor: {
      gap: 38,
      name_pt: 'MgH₂ Dopado com Fe/Ni (Semicondutor)',
      text_pt: 'A inserção de impurezas metálicas cria estados intermediários no gap, diminuindo a barreira energética e acelerando a termodinâmica do hidrogênio.',
      name_en: 'Fe/Ni-Doped MgH₂ (Semiconductor)',
      text_en: 'Transition metal dopants introduce intermediate in-gap states, lowering reaction energy barriers and facilitating hydrogen storage thermodynamics.'
    },
    metal: {
      gap: -15,
      name_pt: 'Cruzamento Metálico (Condutor)',
      text_pt: 'Sobreposição das bandas de valência e condução através do nível de Fermi (EF), viabilizando máxima transferência eletrônica superficial.',
      name_en: 'Metallic Crossing (Conductor)',
      text_en: 'Valence and conduction bands overlap across the Fermi level (EF), providing continuous electron transport and enhanced interfacial exchange.'
    }
  };

  let currentBandMode = 'insulator';

  window.updateBandText = function() {
    if (!bandExplanation) return;
    const cfg = bandConfigs[currentBandMode];
    const name = currentLang === 'pt' ? cfg.name_pt : cfg.name_en;
    const text = currentLang === 'pt' ? cfg.text_pt : cfg.text_en;
    bandExplanation.innerHTML = `<strong>${name}:</strong> ${text}`;
  };

  bandBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      bandBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentBandMode = btn.getAttribute('data-type');
      updateBandText();
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

    ctx.strokeStyle = '#E5A93C';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(60, efY); ctx.lineTo(w - 60, efY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#E5A93C';
    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.fillText(currentLang === 'pt' ? 'Nível de Fermi (EF)' : 'Fermi Level (EF)', w - 190, efY - 8);

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

    ctx.fillStyle = '#94A3B8';
    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.fillText('Γ (0,0,0)', 60, h - 14);
    ctx.fillText('X (0.5, 0, 0.5)', w / 2 - 40, h - 14);
    ctx.fillText('L (0.5, 0.5, 0.5)', w - 160, h - 14);
  }
  renderBandDiagram();

  // =========================================================================
  // TERMINAL HPC BILÍNGUE
  // =========================================================================
  const termInput = document.getElementById('termInput');
  const termOutput = document.getElementById('termOutput');

  const cmdDatabase = {
    pt: {
      'ajuda': 'Comandos: <strong>rodar-dft</strong>, <strong>calcular-gap</strong>, <strong>mgh2</strong>, <strong>limcca</strong>, <strong>clear</strong>, <strong>sobre</strong>',
      'help': 'Comandos: <strong>rodar-dft</strong>, <strong>calcular-gap</strong>, <strong>mgh2</strong>, <strong>limcca</strong>, <strong>clear</strong>, <strong>sobre</strong>',
      'sobre': 'Pesquisador: Bruno H. D. Macedo | Mestrando em Física Aplicada (UNILA) | Especialista em DFT e Ciência de Materiais.',
      'limcca': 'LIMCCA: Laboratório Interdisciplinar de Modelagem e Computação Científica Aplicada — UNILA.',
      'mgh2': 'Estrutura: Hidreto de Magnésio (P4_2/mnm, Rutilo). Parâmetros a=4.501 Å, c=3.010 Å. Capacidade gravimétrica: 7.6 wt% H2.',
      'calcular-gap': 'Autovalores Kohn-Sham: Bandgap direto = 5.61 eV (PBE). Estado: Isolante largo.',
      'calc-gap': 'Autovalores Kohn-Sham: Bandgap direto = 5.61 eV (PBE). Estado: Isolante largo.',
      'rodar-dft': '[JOB 4092] Rodando DFT (CASTEP/Quantum ESPRESSO)...<br>&gt; Otimização geométrica: CONVERGIDA (4 iterações SCF)<br>&gt; Energia Total = -1428.39201 Ry<br>&gt; Simulação concluída com sucesso!'
    },
    en: {
      'help': 'Commands: <strong>run-dft</strong>, <strong>calc-gap</strong>, <strong>mgh2</strong>, <strong>limcca</strong>, <strong>clear</strong>, <strong>about</strong>',
      'ajuda': 'Commands: <strong>run-dft</strong>, <strong>calc-gap</strong>, <strong>mgh2</strong>, <strong>limcca</strong>, <strong>clear</strong>, <strong>about</strong>',
      'about': 'Researcher: Bruno H. D. Macedo | MSc in Applied Physics (UNILA) | DFT & Materials Science Specialist.',
      'limcca': 'LIMCCA: Interdisciplinary Laboratory of Applied Mathematical and Computational Modeling — UNILA.',
      'mgh2': 'Structure: Magnesium Hydride (P4_2/mnm, Rutile). Lattice params a=4.501 Å, c=3.010 Å. Theoretical gravimetric capacity: 7.6 wt% H2.',
      'calc-gap': 'Kohn-Sham eigenvalues: Direct bandgap = 5.61 eV (PBE). State: Wide-gap insulator.',
      'run-dft': '[JOB 4092] Running DFT (CASTEP/Quantum ESPRESSO)...<br>&gt; Geometry optimization: CONVERGED (4 SCF cycles)<br>&gt; Total Energy = -1428.39201 Ry<br>&gt; Simulation completed successfully!'
    }
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

        const dict = cmdDatabase[currentLang] || cmdDatabase['pt'];
        const resp = dict[val] || (currentLang === 'pt' ? `Comando não reconhecido: "${val}". Digite <strong>ajuda</strong>.` : `Command not recognized: "${val}". Type <strong>help</strong>.`);

        const respRow = document.createElement('p');
        respRow.className = 'term-out';
        respRow.innerHTML = resp;
        termOutput.appendChild(respRow);

        termOutput.scrollTop = termOutput.scrollHeight;
      }
    });
  }
});
