/**
 * RENATA OLMEDO BENEDET - PORTFOLIO INTERATIVO
 * Simulações Físicas, Internacionalização (i18n) e Efeitos Dinâmicos
 */

// Dicionário Multilíngue (PT / EN)
const i18n = {
  pt: {
    brand_sub: "FÍSICA MÉDICA • P&D",
    nav_about: "Sobre",
    nav_sim: "Simulador CS-XSI",
    nav_pillars: "Especialidades",
    nav_pubs: "Publicações",
    nav_timeline: "Trajetória",
    hero_badge: "Mestranda em Física Aplicada • Bolsista CAPES",
    hero_sub: "Engenharia Física aplicada à Física Médica, Instrumentação de Raios X e Prototipagem 3D.",
    hero_desc: "Pesquisadora especializada no design, simulação e fabricação aditiva de fendas cônicas para espectrometria e espalhamento de raios X (CS-XSI), visando a detecção e diferenciação não invasiva de microcalcificações de oxalato de cálcio em tecidos biológicos.",
    stat_articles: "Artigos em Periódicos",
    stat_confs: "Trabalhos em Anais",
    stat_pres: "Apresentações",
    stat_hours: "Horas de Extensão",
    btn_sim: "Testar Simulador de Feixe",
    btn_pubs: "Ver Publicações",
    badge_geo: "Geometria Óptica Cônica Ativa",
    badge_desc: "Detecção Não Invasiva de Oxalato de Cálcio",
    sim_tag: "Ambiente Interativo de Pesquisa",
    sim_title: "Simulador de Fenda Cônica (CS-XSI)",
    sim_lead: "Explore interativamente como os parâmetros ópticos, a energia do feixe de raios X e o tipo de material influenciam a dispersão e a relação sinal-ruído (SNR) no plano do detector.",
    sim_params: "Parâmetros do Feixe & Fenda",
    sim_mat: "Material do Fantoma:",
    sim_energy: "Energia do Feixe (E):",
    sim_slit: "Abertura da Fenda Cônica (W):",
    sim_angle: "Ângulo de Espalhamento (2θ):",
    sim_snr: "SNR Estimado:",
    sim_q: "Vetor de Espalhamento (q):",
    sim_contrast: "Contraste Diferencial:",
    sim_detector: "Padrão 2D no Detector Circular (Difração Debye-Scherrer)",
    leg_scatter: "Pico de Espalhamento Coerente",
    leg_back: "Fundo Compton (Incoerente)",
    leg_collim: "Anel de Fenda 3D",
    pillars_tag: "Competências Científicas",
    pillars_title: "Especialidades & Áreas de Atuação",
    pillars_lead: "Abordagem integrada combinando formulação teórica de óptica radiológica, engenharia de prototipagem rápida e caracterização biocristalográfica.",
    pil_1_t: "Física Médica & Espalhamento de Raios X",
    pil_1_d: "Desenvolvimento de técnicas analíticas de espalhamento de raios X (X-ray scattering) aplicadas à diferenciação precoce e não invasiva de microcalcificações associadas a lesões neoplásicas de mama.",
    pil_2_t: "Prototipagem por Impressão 3D",
    pil_2_d: "Modelagem computacional e manufatura aditiva de alta precisão para colimadores cônicos, suportes de fantomas e fendas ópticas dedicadas a montagens experimentais com feixes colimados.",
    pil_3_t: "Cristalografia & Difração",
    pil_3_d: "Investigação de perfis de difração de oxalato de cálcio mono e di-hidratado. Formação em microscopia crioeletrônica de partícula única (Cryo-EM) pela Associação Brasileira de Cristalografia (ABCR).",
    pil_4_t: "Extensão & Eletroquímica Aplicada",
    pil_4_d: "Coordenação e execução de projetos de divulgação científica e extensão educacional em escolas públicas, além de gestão estudantil ativa junto ao Centro Acadêmico de Engenharia Física (CAENFIS).",
    pub_tag: "Produção Intelectual",
    pub_title: "Artigos & Comunicações Científicas",
    pub_lead: "Filtragem interativa por categoria, com exportação de citação em ABNT e BibTeX com um clique.",
    pub_search_ph: "Buscar por título, coautor ou periódico...",
    flt_all: "Todas (8)",
    flt_jour: "Periódicos (3)",
    flt_conf: "Congressos & Anais (5)",
    traj_tag: "Formação & Marcos",
    traj_title: "Trajetória Acadêmica",
    traj_msc_title: "Mestrado em Física Aplicada",
    traj_msc_desc: "Pesquisa voltada à instrumentação com raios X, modelagem óptica de colimadores e identificação não invasiva de biominerais em tecidos mamários. Financiado pela bolsa de mestrado CAPES.",
    traj_adv: "Orientador:",
    traj_bsc_title: "Graduação em Engenharia Física",
    traj_cert_title: "Formação Complementar",
    cont_tag: "Conexão Acadêmica",
    cont_title: "Pronta para Novos Desafios em P&D",
    cont_desc: "Aberta a contatos de grupos de pesquisa, programas de doutorado e instituições de diagnóstico e instrumentação médica.",
    btn_email: "Enviar E-mail Acadêmico"
  },
  en: {
    brand_sub: "MEDICAL PHYSICS • R&D",
    nav_about: "About",
    nav_sim: "CS-XSI Simulator",
    nav_pillars: "Expertise",
    nav_pubs: "Publications",
    nav_timeline: "Trajectory",
    hero_badge: "M.Sc. Candidate in Applied Physics • CAPES Fellow",
    hero_sub: "Physical Engineering bridging Medical Physics, X-Ray Instrumentation, and 3D Prototyping.",
    hero_desc: "Researcher focused on numerical modeling, design, and 3D printing of conical slits for X-ray scattering imaging (CS-XSI), targeting non-invasive breast microcalcification diagnostics.",
    stat_articles: "Journal Articles",
    stat_confs: "Conference Papers",
    stat_pres: "Oral Presentations",
    stat_hours: "Outreach Hours",
    btn_sim: "Run Beam Simulator",
    btn_pubs: "View Research",
    badge_geo: "Active Conical Geometry",
    badge_desc: "Non-invasive Calcium Oxalate Profiling",
    sim_tag: "Interactive Physics Workbench",
    sim_title: "Conical Slit Beam Simulator (CS-XSI)",
    sim_lead: "Interactively explore how optical collimation geometry, X-ray beam energy, and phantom materials affect diffraction rings and Signal-to-Noise Ratio (SNR).",
    sim_params: "Beam & Slit Parameters",
    sim_mat: "Phantom Target:",
    sim_energy: "Photon Energy (E):",
    sim_slit: "Conical Slit Width (W):",
    sim_angle: "Scattering Angle (2θ):",
    sim_snr: "Estimated SNR:",
    sim_q: "Momentum Transfer (q):",
    sim_contrast: "Differential Contrast:",
    sim_detector: "2D Circular Detector Array (Debye-Scherrer Diffraction)",
    leg_scatter: "Coherent Bragg Peak",
    leg_back: "Incoherent Compton Halo",
    leg_collim: "3D Slit Acceptance",
    pillars_tag: "Core Scientific Pillars",
    pillars_title: "Specialization & Research Focus",
    pillars_lead: "Integrated approach combining radiation optics, rapid additive prototyping, and biocrystallographic analysis.",
    pil_1_t: "Medical Physics & X-Ray Scattering",
    pil_1_d: "Pioneering conical slit scattering imaging (CS-XSI) to non-invasively classify benign vs. malignant calcium deposits in soft tissues.",
    pil_2_t: "3D Printing & Additive Manufacturing",
    pil_2_d: "High-precision CAD modeling and slicing for custom collimators, tissue phantom holders, and beamline optical components.",
    pil_3_t: "Biocrystallography & Diffraction",
    pil_3_d: "X-ray powder diffraction analysis of bio-salts. Specialized training in single particle Cryo-EM by the Brazilian Crystallographic Association (ABCR).",
    pil_4_t: "Academic Outreach & Electrochemistry",
    pil_4_d: "Directing STEM outreach programs in secondary schools and leading departmental student governance on the CAENFIS board.",
    pub_tag: "Scholarly Record",
    pub_title: "Publications & Conference Proceedings",
    pub_lead: "Real-time search and filter with one-click ABNT and BibTeX citation export.",
    pub_search_ph: "Search by title, co-author, or journal...",
    flt_all: "All (8)",
    flt_jour: "Journals (3)",
    flt_conf: "Proceedings (5)",
    traj_tag: "Academic Pathway",
    traj_title: "Education & Research Milestones",
    traj_msc_title: "M.Sc. in Applied Physics",
    traj_msc_desc: "Investigation of novel conical slit scatter geometries and breast tissue phantom characterization. Supported by a CAPES fellowship.",
    traj_adv: "Advisor:",
    traj_bsc_title: "B.Sc. in Physical Engineering",
    traj_cert_title: "Complementary Training",
    cont_tag: "Get in Touch",
    cont_title: "Open for Ph.D. & Collaborative Research",
    cont_desc: "Eager to connect with doctoral supervisors, medical physics labs, and synchrotron instrumentation facilities worldwide.",
    btn_email: "Send Inquiries"
  }
};

document.addEventListener('DOMContentLoaded', () => {
  initLanguageSwitcher();
  initAnimatedCounters();
  initHologramTilt();
  initBackgroundCanvas();
  initSimulatorWorkbench();
  initPublicationSearchAndFilter();
  initCitationCopy();
});

// 1. Alternador de Idiomas
function initLanguageSwitcher() {
  const ptBtn = document.getElementById('langPt');
  const enBtn = document.getElementById('langEn');

  function setLanguage(lang) {
    if (lang === 'en') {
      enBtn.classList.add('active');
      ptBtn.classList.remove('active');
    } else {
      ptBtn.classList.add('active');
      enBtn.classList.remove('active');
    }

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (i18n[lang][key]) el.innerHTML = i18n[lang][key];
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (i18n[lang][key]) el.placeholder = i18n[lang][key];
    });
  }

  ptBtn.addEventListener('click', () => setLanguage('pt'));
  enBtn.addEventListener('click', () => setLanguage('en'));
}

// 2. Contadores Animados de Métricas
function initAnimatedCounters() {
  const statElements = document.querySelectorAll('.stat-num');
  let hasAnimated = false;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !hasAnimated) {
        hasAnimated = true;
        statElements.forEach(el => {
          const target = parseInt(el.getAttribute('data-target'));
          let count = 0;
          const speed = Math.max(15, Math.floor(1200 / target));
          const timer = setInterval(() => {
            count += Math.ceil(target / 40);
            if (count >= target) {
              el.innerText = target;
              clearInterval(timer);
            } else {
              el.innerText = count;
            }
          }, speed);
        });
      }
    });
  }, { threshold: 0.3 });

  const statsContainer = document.querySelector('.stats-row');
  if (statsContainer) observer.observe(statsContainer);
}

// 3. Efeito Giroscópico / Tilt no Card do Emblema
function initHologramTilt() {
  const card = document.getElementById('tiltCard');
  if (!card) return;

  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;

    const rotX = (y / (rect.height / 2)) * -12;
    const rotY = (x / (rect.width / 2)) * 12;

    card.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'rotateX(0deg) rotateY(0deg)';
  });
}

// 4. Fundo Dinâmico de Partículas de Raios X (Canvas)
function initBackgroundCanvas() {
  const canvas = document.getElementById('xrayCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  // Partículas simulando fótons e anéis de espalhamento
  const photons = [];
  const count = Math.min(60, Math.floor(width / 22));

  for (let i = 0; i < count; i++) {
    photons.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.7,
      vy: (Math.random() - 0.5) * 0.7,
      radius: Math.random() * 2 + 1,
      color: Math.random() > 0.5 ? '#f472b6' : '#c084fc',
      opacity: Math.random() * 0.6 + 0.2
    });
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);

    // Desenha ondas concêntricas difusas simulando anéis de difração suaves
    ctx.save();
    ctx.strokeStyle = 'rgba(216, 180, 254, 0.04)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(width * 0.75, height * 0.45, 180, 0, Math.PI * 2);
    ctx.arc(width * 0.75, height * 0.45, 290, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Atualiza e desenha fótons
    photons.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.save();
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.opacity;
      ctx.shadowBlur = 8;
      ctx.shadowColor = p.color;
      ctx.fill();
      ctx.restore();
    });

    requestAnimationFrame(animate);
  }

  animate();
}

// 5. Simulador Físico de Bancada (CS-XSI Detector)
function initSimulatorWorkbench() {
  const dCanvas = document.getElementById('detectorCanvas');
  if (!dCanvas) return;
  const dCtx = dCanvas.getContext('2d');

  const phantomSel = document.getElementById('phantomSelect');
  const energyRange = document.getElementById('energyRange');
  const slitRange = document.getElementById('slitRange');
  const angleRange = document.getElementById('angleRange');

  const energyVal = document.getElementById('energyVal');
  const slitVal = document.getElementById('slitVal');
  const angleVal = document.getElementById('angleVal');
  const snrDisplay = document.getElementById('snrDisplay');
  const qDisplay = document.getElementById('qDisplay');
  const contrastDisplay = document.getElementById('contrastDisplay');

  // Materiais e fatores de espalhamento
  const materials = {
    caox: { name: 'Oxalato de Cálcio', braggPeak: 8.4, baseSNR: 18.2, contrast: 'Excelente (Forte)', color: '#f472b6' },
    ha: { name: 'Hidroxiapatita', braggPeak: 10.6, baseSNR: 15.5, contrast: 'Alto (Diferenciado)', color: '#fb7185' },
    glandular: { name: 'Tecido Glandular', braggPeak: 6.2, baseSNR: 9.8, contrast: 'Médio / Difuso', color: '#c084fc' },
    adipose: { name: 'Tecido Adiposo', braggPeak: 5.1, baseSNR: 7.4, contrast: 'Baixo / Fundo', color: '#a855f7' }
  };

  function updateSimulation() {
    const matKey = phantomSel.value;
    const mat = materials[matKey];
    const energy = parseFloat(energyRange.value);
    const slit = parseFloat(slitRange.value);
    const angle = parseFloat(angleRange.value);

    energyVal.innerText = `${energy.toFixed(1)} keV`;
    slitVal.innerText = `${slit.toFixed(1)} mm`;
    angleVal.innerText = `${angle.toFixed(1)}°`;

    // Cálculo do Momento de Transferência q = (4 * pi / lambda) * sin(theta)
    // lambda (Å) ~ 12.398 / E(keV)
    const lambda = 12.398 / energy;
    const thetaRad = (angle / 2) * (Math.PI / 180);
    const q = (4 * Math.PI / lambda) * Math.sin(thetaRad);
    qDisplay.innerText = `${q.toFixed(2)} Å⁻¹`;

    // Cálculo dinâmico da relação Sinal-Ruído (SNR)
    const angleDiff = Math.abs(angle - mat.braggPeak);
    const peakFactor = Math.exp(-Math.pow(angleDiff / 1.6, 2));
    const slitFactor = Math.sin(Math.min(Math.PI / 2, slit / 1.5));
    const energyOptimum = 1 - Math.abs(energy - 22.5) / 25;
    const currentSNR = Math.max(2.0, (mat.baseSNR * peakFactor * slitFactor * energyOptimum)).toFixed(1);

    snrDisplay.innerText = `${currentSNR} dB`;
    contrastDisplay.innerText = mat.contrast;

    // Renderizar padrão circular no Detector
    drawDetectorPattern(angle, slit, mat, peakFactor);
  }

  function drawDetectorPattern(angle, slit, mat, peakFactor) {
    const w = dCanvas.width;
    const h = dCanvas.height;
    const cx = w / 2;
    const cy = h / 2;

    dCtx.clearRect(0, 0, w, h);

    // Fundo do Detector
    const bgGrad = dCtx.createRadialGradient(cx, cy, 10, cx, cy, w / 2);
    bgGrad.addColorStop(0, '#0c0717');
    bgGrad.addColorStop(0.7, '#07040f');
    bgGrad.addColorStop(1, '#020105');
    dCtx.fillStyle = bgGrad;
    dCtx.fillRect(0, 0, w, h);

    // Grade de Mira Polar
    dCtx.strokeStyle = 'rgba(216, 180, 254, 0.12)';
    dCtx.lineWidth = 1;
    [40, 80, 120, 160, 200].forEach(r => {
      dCtx.beginPath();
      dCtx.arc(cx, cy, r, 0, Math.PI * 2);
      dCtx.stroke();
    });

    // Fundo de Espalhamento Compton (Incoerente e contínuo)
    const comptonGrad = dCtx.createRadialGradient(cx, cy, 30, cx, cy, 190);
    comptonGrad.addColorStop(0, 'rgba(139, 92, 246, 0.25)');
    comptonGrad.addColorStop(0.5, 'rgba(139, 92, 246, 0.08)');
    comptonGrad.addColorStop(1, 'rgba(139, 92, 246, 0)');
    dCtx.fillStyle = comptonGrad;
    dCtx.beginPath();
    dCtx.arc(cx, cy, 190, 0, Math.PI * 2);
    dCtx.fill();

    // Anel de Projeção da Fenda Cônica 3D (W)
    const slitRadius = 70 + (slit * 26);
    dCtx.strokeStyle = 'rgba(251, 191, 36, 0.35)';
    dCtx.lineWidth = Math.max(2, slit * 2.5);
    dCtx.beginPath();
    dCtx.arc(cx, cy, slitRadius, 0, Math.PI * 2);
    dCtx.stroke();

    // Anel de Difração Coerente de Bragg (Pico de Debye-Scherrer)
    const braggRadius = (angle / 16) * 190;
    const intensity = Math.max(0.2, peakFactor);

    dCtx.save();
    dCtx.strokeStyle = mat.color;
    dCtx.lineWidth = Math.max(2, 6 * intensity);
    dCtx.shadowBlur = 18 * intensity;
    dCtx.shadowColor = mat.color;
    dCtx.globalAlpha = Math.min(1, 0.4 + intensity * 0.6);

    dCtx.beginPath();
    dCtx.arc(cx, cy, braggRadius, 0, Math.PI * 2);
    dCtx.stroke();
    dCtx.restore();

    // Ponto Central do Feixe Primário Atenuado (Beamstop)
    dCtx.fillStyle = '#060309';
    dCtx.strokeStyle = '#f472b6';
    dCtx.lineWidth = 2;
    dCtx.beginPath();
    dCtx.arc(cx, cy, 14, 0, Math.PI * 2);
    dCtx.fill();
    dCtx.stroke();
  }

  phantomSel.addEventListener('change', updateSimulation);
  energyRange.addEventListener('input', updateSimulation);
  slitRange.addEventListener('input', updateSimulation);
  angleRange.addEventListener('input', updateSimulation);

  updateSimulation();
}

// 6. Busca e Filtragem de Publicações em Tempo Real
function initPublicationSearchAndFilter() {
  const searchInput = document.getElementById('pubSearch');
  const filterBtns = document.querySelectorAll('.pill-btn');
  const pubCards = document.querySelectorAll('.pub-card');

  function filterContent() {
    const term = (searchInput?.value || '').toLowerCase().trim();
    const activeFilter = document.querySelector('.pill-btn.active')?.getAttribute('data-filter') || 'all';

    pubCards.forEach(card => {
      const cardCat = card.getAttribute('data-cat');
      const text = card.innerText.toLowerCase();

      const matchesCat = (activeFilter === 'all' || cardCat === activeFilter);
      const matchesSearch = text.includes(term);

      if (matchesCat && matchesSearch) {
        card.style.display = 'block';
        card.style.opacity = '1';
      } else {
        card.style.display = 'none';
        card.style.opacity = '0';
      }
    });
  }

  if (searchInput) searchInput.addEventListener('input', filterContent);

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterContent();
    });
  });
}

// 7. Copiador de Citações com Feedback Toast
function initCitationCopy() {
  const toast = document.getElementById('toast');

  function showToast(msg) {
    if (!toast) return;
    toast.innerText = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }

  document.querySelectorAll('.copy-abnt').forEach(btn => {
    btn.addEventListener('click', () => {
      const cite = btn.getAttribute('data-cite');
      navigator.clipboard.writeText(cite).then(() => {
        showToast('Citação ABNT copiada para a área de transferência!');
      });
    });
  });

  document.querySelectorAll('.copy-bib').forEach(btn => {
    btn.addEventListener('click', () => {
      const bib = btn.getAttribute('data-bib');
      navigator.clipboard.writeText(bib).then(() => {
        showToast('Código BibTeX copiado com sucesso!');
      });
    });
  });
}
