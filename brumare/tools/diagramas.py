#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gera os diagramas do BrUMaRe (16:9) em PDF vetorial, SVG e PNG (claro e escuro).
    python3 tools/diagramas.py  ->  docs/diagramas/"""
import os, subprocess
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, "docs", "diagramas")
FONTES = os.path.join(RAIZ, "vendor", "fonts")

CSS = """
@font-face{font-family:SG;src:url('file://%(f)s/SpaceGrotesk.ttf')}
@font-face{font-family:JB;src:url('file://%(f)s/JetBrainsMono.ttf')}
:root{--bg:#F6FAF9;--card:#FFFFFF;--fg:#0C1614;--mut:#55706A;--line:#D3E2DE;--acc:#0A8F78;--acc2:#4FE3C1;--amb:#C77D00;--amb2:#F5B544;--vio:#6B5BD6;--red:#D94850;--blu:#2F6FD1}
body.dark{--bg:#070C0B;--card:#0F1A18;--fg:#E8F1EF;--mut:#8FA6A0;--line:#1E302C;--acc:#4FE3C1;--acc2:#0A8F78;--amb:#F5B544;--amb2:#C77D00;--vio:#9B8CF8;--red:#F06A72;--blu:#6EA0F2}
*{box-sizing:border-box;margin:0;padding:0}
body{width:1600px;height:900px;background:var(--bg);color:var(--fg);font-family:SG,'DejaVu Sans',sans-serif;position:relative;overflow:hidden}
.h{position:absolute;left:56px;top:40px;right:56px;display:flex;justify-content:space-between;align-items:flex-end}
.h h1{font-size:40px;font-weight:700;letter-spacing:-.5px}.h h1 span{color:var(--acc)}
.h p{font-family:JB,monospace;font-size:15px;color:var(--mut)}
.marca{font-family:SG;font-weight:700;font-size:22px}.marca i{font-style:normal;color:var(--amb2)}
.sub{position:absolute;left:56px;top:96px;font-size:18px;color:var(--mut)}
.c{position:absolute;background:var(--card);border:1.5px solid var(--line);border-radius:16px;padding:14px 16px;box-shadow:0 2px 10px rgba(0,0,0,.04)}
.c h3{font-size:18px;margin-bottom:6px;display:flex;align-items:center;gap:8px}.c h3 b{display:inline-block;width:10px;height:10px;border-radius:3px;background:var(--acc)}
.c p,.c li{font-size:14px;line-height:1.35;color:var(--mut)}.c ul{list-style:none}.c li:before{content:'› ';color:var(--acc)}
.c code,.k{font-family:JB,monospace;font-size:12.5px;color:var(--fg);background:color-mix(in srgb,var(--acc2) 18%,transparent);padding:1px 5px;border-radius:5px}
.acc{border-color:var(--acc);border-width:2px}.amb{border-color:var(--amb2);border-width:2px}.vio{border-color:var(--vio);border-width:2px}
.pill{display:inline-block;font-family:JB,monospace;font-size:12px;border:1px solid var(--line);border-radius:999px;padding:2px 8px;margin:2px 3px 2px 0;color:var(--fg)}
.num{position:absolute;width:44px;height:44px;border-radius:50%;background:var(--acc);color:var(--bg);font-weight:700;font-size:22px;display:flex;align-items:center;justify-content:center}
svg.ar{position:absolute;left:0;top:0;width:1600px;height:900px;pointer-events:none}
.rod{position:absolute;left:56px;right:56px;bottom:26px;display:flex;justify-content:space-between;font-family:JB,monospace;font-size:13px;color:var(--mut)}
.faixa{position:absolute;border-radius:14px;background:color-mix(in srgb,var(--acc2) 14%,var(--card));border:1.5px dashed var(--acc);display:flex;align-items:center;justify-content:center;font-size:17px;gap:10px}
"""

SETA = '<marker id="m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--acc)"/></marker>'


def pagina(titulo, sub, corpo, setas=""):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS.replace('%(f)s', FONTES)}</style></head><body>"
            f"<div class='h'><h1>{titulo}</h1><div class='marca'>BrUMa<i>Re</i></div></div><div class='sub'>{sub}</div>{corpo}"
            f"<svg class='ar' viewBox='0 0 1600 900'><defs>{SETA}</defs>{setas}</svg>"
            "<div class='rod'><span>BrUMaRe 1.3.0 · Brillouin-zone Utilities for Materials Research · GPL-3.0</span><span>brunohdmacedo.tech/brumare</span></div></body></html>")


def c(x, y, w, h, tit, txt="", cls="", cor=None):
    b = f"<b style='background:{cor}'></b>" if cor else "<b></b>"
    return f"<div class='c {cls}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px'><h3>{b}{tit}</h3>{txt}</div>"


def ul(*it):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in it) + "</ul>"


def seta(x1, y1, x2, y2, curva=0):
    if curva:
        mx = (x1 + x2) / 2
        return f"<path d='M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}' fill='none' stroke='var(--acc)' stroke-width='2.2' marker-end='url(#m)'/>"
    return f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='var(--acc)' stroke-width='2.2' marker-end='url(#m)'/>"


D = {}
# 1 · Arquitetura ------------------------------------------------------------------------------------
ent = [("CASTEP", ".bands · .pdos_bin · .castep · .cell · .den_fmt"), ("VASP", "vasprun.xml · KPOINTS · CHGCAR"), ("SIESTA", ".bands · .EIG · .PDOS · .RHO · .out"),
       ("Quantum ESPRESSO", "data-file-schema.xml · pasta .save"), ("ORCA", "saída .out (moléculas)"), ("Estruturas", "CIF · POSCAR · .cell · XSF · QE · XYZ · COD · biblioteca (51)")]
corpo = "".join(c(56, 150 + i * 98, 330, 86, t, f"<p>{d}</p>") for i, (t, d) in enumerate(ent))
corpo += c(470, 300, 300, 150, "Leitores e unidades", "<p>Cada formato é convertido para o mesmo modelo:<br><span class='k'>Ha · Å · e/Å³</span><br>E<sub>F</sub> sempre o do programa</p>", "acc")
corpo += c(470, 480, 300, 130, "Modelo de dados comum", "<p>bandas · projeções · estrutura · densidade · energias · simetria</p>", "acc")
grupos = [("Estrutura eletrônica", "bandas · DOS/PDOS · gap · m* · correção do gap"), ("Defeitos e termodinâmica", "distorção · E<sub>f</sub> · ΔH · T<sub>d</sub>"),
          ("Densidade e cargas", "3D/2D · Voronoi · Bader · Δρ"), ("Zona de Brillouin e simetria", "grupo espacial · 14 redes · caminho k"), ("Comparação", "vários cálculos e programas")]
corpo += "".join(c(850, 150 + i * 98, 330, 86, t, f"<p>{d}</p>", "vio" if i == 3 else "") for i, (t, d) in enumerate(grupos))
sai = [("Figuras", "PNG · JPG · JXL · WEBP · SVG"), ("Dados", ".dat (Origin) · CHGCAR · XSF · JSON"), ("Entradas DFT", "KPOINTS · .cell · QE · SIESTA"), ("Relatórios", ".txt de análise, defeito, comparação"), ("Citação", ".bib com o que foi usado")]
corpo += "".join(c(1260, 150 + i * 98, 284, 86, t, f"<p>{d}</p>", "amb" if i == 4 else "", "var(--amb2)" if i == 4 else None) for i, (t, d) in enumerate(sai))
corpo += "<div class='faixa' style='left:56px;top:760px;width:1488px;height:76px'><b>Três interfaces, mesmos resultados:</b> Página web (sem instalação) · Aplicativo de computador e Windows .exe (offline) · Linha de comando Python (cluster)</div>"
setas = "".join(seta(386, 193 + i * 98, 470, 375, 1) for i in range(6)) + seta(620, 450, 620, 480)
setas += "".join(seta(770, 545, 850, 193 + i * 98, 1) for i in range(5)) + "".join(seta(1180, 193 + i * 98, 1260, 193 + i * 98) for i in range(5))
D["1_arquitetura"] = pagina("Arquitetura do <span>sistema</span>", "Cinco programas de estrutura eletrônica, um modelo de dados, todas as análises e saídas prontas para publicação", corpo, setas)

# 2 · Fluxo de trabalho --------------------------------------------------------------------------------
passos = [("Calcule", "Rode o cálculo DFT no seu programa", ["CASTEP, VASP, SIESTA, QE ou ORCA", "Dica: <code>PDOS_CALCULATE_WEIGHTS</code>, <code>LORBIT = 11</code>", "Caminho k pronto na aba Zona de Brillouin"]),
          ("Carregue", "Abra os arquivos ou a pasta", ["Arraste para a página ou o aplicativo", "<code>brumare seed</code> no cluster", "Nada é enviado a servidores"]),
          ("Analise", "Escolha as abas", ["Bandas, DOS, PDOS, análise", "Defeito, densidade, Δρ, Bader", "Zona de Brillouin e simetria"]),
          ("Exporte", "Figuras e dados prontos", ["PNG, JPG, JXL, WEBP, SVG", ".dat para Origin · CHGCAR para VESTA", "Entradas para os programas DFT"]),
          ("Cite e publique", "Reprodutível e com crédito", ["<code>.bib</code> automático com o que foi usado", "Relatórios em texto", "Tutorial e teoria em 6 idiomas"])]
corpo = ""
for i, (t, s, it) in enumerate(passos):
    x = 56 + i * 302
    corpo += f"<div class='num' style='left:{x + 115}px;top:170px'>{i + 1}</div>"
    corpo += c(x, 240, 280, 300, t, f"<p style='font-size:17px;color:var(--fg);margin-bottom:12px'>{s}</p><div style='font-size:15.5px'>" + ul(*it) + "</div>", "acc" if i in (0, 4) else "")
corpo += "<div class='faixa' style='left:56px;top:600px;width:1488px;height:76px'><span>O nível de Fermi é sempre o que o programa escreveu · energias originais com linha traço-ponto em E<sub>F</sub> por padrão</span></div>"
setas = "".join(seta(336 + i * 302, 192, 371 + i * 302, 192) for i in range(4))
D["2_fluxo"] = pagina("Fluxo de <span>trabalho</span>", "Do cálculo de primeiros princípios à figura e à citação no artigo, em cinco passos", corpo, setas)

# 3 · Mapa de funções ------------------------------------------------------------------------------------
corpo = "<div class='c acc' style='left:640px;top:390px;width:320px;height:120px;text-align:center;display:flex;flex-direction:column;justify-content:center'><div class='marca' style='font-size:40px'>BrUMa<i>Re</i></div><p>todas as análises</p></div>"
ramos = [(56, 140, "Estrutura eletrônica", ["bandas com spin ↑↓", "DOS e PDOS em 5 níveis", "bandas projetadas", "gap por contagem de elétrons", "massa efetiva", "correção do gap (tesoura, PBE→G₀W₀)"]),
         (590, 130, "Zona de Brillouin e simetria", ["grupo espacial e Wyckoff (moyo/spglib)", "células primitiva e convencional", "14 redes de Bravais · caminho k", "malhas Monkhorst–Pack"]),
         (1124, 140, "Defeitos e termodinâmica", ["vacância, substitucional, intersticial", "Baur, ⟨λ⟩, σ², ECoN", "campo de deslocamentos", "E<sub>f</sub>, ΔH, ΔΔH, T<sub>d</sub>, capacidade de H"]),
         (56, 560, "Densidade e cargas", ["3D, cortes (hkl), perfis", "densidade de spin", "Voronoi e Bader refinado", "Δρ, dipolo, transferência de carga", "exportação para VESTA"]),
         (590, 580, "Comparação", ["vários cálculos e programas", "tabela, DOS sobrepostas", "bandas lado a lado"]),
         (1124, 560, "Saídas e citação", ["5 formatos de figura", ".dat, CHGCAR, XSF, JSON", "entradas DFT prontas", ".bib automático", "6 idiomas"])]
for x, y, t, it in ramos:
    corpo += c(x, y, 420, 30 + 26 * len(it) + 24, t, ul(*it), "vio" if "Brillouin" in t else "")
setas = seta(640, 420, 476, 260, 1) + seta(800, 390, 800, 300) + seta(960, 420, 1124, 260, 1) + seta(640, 480, 476, 640, 1) + seta(800, 510, 800, 580) + seta(960, 480, 1124, 640, 1)
D["3_funcoes"] = pagina("Mapa de <span>funções</span>", "O que o BrUMaRe calcula, para qualquer material e para os cinco programas", corpo, setas)

# 4 · Plataformas -----------------------------------------------------------------------------------------
pl = [("Página web", "Navegador", ["sem instalação, qualquer sistema", "os arquivos nunca saem do computador", "JavaScript + Plotly + WebAssembly (simetria, JPEG XL)", "6 idiomas, responsiva (celular a 4K)"], "brunohdmacedo.tech/brumare"),
      ("Aplicativo", "Linux · macOS · Windows", ["a mesma interface da página", "funciona sem internet", "janela nativa (pywebview)", "bibliotecas e fontes incluídas"], "brumare-gui"),
      ("Windows (.exe)", "Instalador", ["BrUMaRe-Setup.exe com atalhos", "gerado automaticamente (GitHub Actions)", "PyInstaller + Inno Setup", "inclui linha de comando e aplicativo"], "BrUMaRe-Setup-1.3.0.exe"),
      ("Python / cluster", "Linha de comando", ["um arquivo, só numpy e matplotlib", "scripts SLURM e PBS de exemplo", "figuras, .dat, relatórios, .bib", "simetria (moyopy) e JXL opcionais"], "pip install brumare")]
corpo = ""
for i, (t, s, it, cmd) in enumerate(pl):
    x = 56 + i * 377
    corpo += c(x, 150, 357, 330, t, f"<p style='font-size:15px;color:var(--fg)'>{s}</p><div style='height:8px'></div>" + ul(*it) + f"<div style='position:absolute;bottom:16px;left:16px'><span class='k'>{cmd}</span></div>", "acc" if i in (0, 3) else "")
corpo += c(56, 520, 700, 170, "Código compartilhado", "<p><span class='k'>index.html</span> → site, aplicativo e .exe (mesma interface)<br><span class='k'>brumare.py</span> → linha de comando e cluster<br>As duas implementações seguem a mesma especificação e são comparadas nos mesmos arquivos.</p>", "vio")
corpo += c(800, 520, 744, 170, "Exemplos na linha de comando", "<p><span class='k'>brumare mgh2_Fe -e Mg,H,Fe</span> análise completa<br><span class='k'>brumare --estrutura Bi2Se3.cif</span> simetria e caminho k<br><span class='k'>brumare pasta_vasp/ --format png,jxl,svg</span> vários formatos</p>")
D["4_plataformas"] = pagina("Plataformas: <span>web, aplicativo, .exe e Python</span>", "Quatro formas de usar, o mesmo núcleo de análises e os mesmos números (paridade testada)", corpo)

# 5 · Zona de Brillouin -------------------------------------------------------------------------------------
et = [("Estrutura", "CIF, POSCAR, .cell, XSF, QE, XYZ<br>cálculo carregado · COD<br>biblioteca com 51 materiais"),
      ("Simetria", "moyo, sucessor do spglib<br>grupo espacial (1–230), Hall, Pearson<br>Wyckoff e simetria de sítio"),
      ("Célula primitiva", "padronizada pelo moyo<br>exportável: POSCAR, .cell, QE, CIF<br>convencional também"),
      ("Rede recíproca", "b<sub>i</sub> = 2π a<sub>j</sub>×a<sub>k</sub>/V<br>redução LLL da base<br>V<sub>ZB</sub> = (2π)³/V"),
      ("Wigner–Seitz", "planos de Bragg k·G = |G|²/2<br>vértices, arestas e faces<br>volume conferido com (2π)³/V"),
      ("Tipo de rede", "14 redes de Bravais<br>25 casos de Setyawan–Curtarolo<br>tolerância de simetria"),
      ("Pontos padronizados", "Setyawan–Curtarolo (2010)<br>alinhados à base padronizada<br>todos na superfície da zona"),
      ("Caminho e malha", "pontos por Å⁻¹ em cada segmento<br>malha Monkhorst–Pack<br>coordenadas fracionárias")]
corpo = ""
for i, (t, d) in enumerate(et):
    col, lin = i % 4, i // 4
    x = 56 + col * 377; y = 160 + lin * 230
    corpo += c(x, y, 330, 170, f"{i + 1} · {t}", f"<p>{d}</p>", "vio" if i in (1, 6) else ("acc" if i == 4 else ""))
corpo += "<div class='faixa' style='left:56px;top:640px;width:1488px;height:110px;flex-direction:column;gap:4px'><b>Saídas prontas para copiar ou baixar</b><span><span class='pill'>CASTEP SPECTRAL_KPOINT_PATH</span><span class='pill'>VASP KPOINTS</span><span class='pill'>QE K_POINTS crystal_b</span><span class='pill'>SIESTA BandLines</span><span class='pill'>JSON</span><span class='pill'>POSCAR · .cell · QE · CIF</span></span></div>"
setas = "".join(seta(386 + i * 377, 245, 433 + i * 377, 245) for i in range(3)) + seta(1386, 330, 1386, 360) + seta(1386, 360, 221, 360, 0).replace("x2='221'", "x2='221'")
setas = "".join(seta(386 + i * 377, 245, 433 + i * 377, 245) for i in range(3)) + "<path d='M1312,330 L1312,355 L221,355 L221,390' fill='none' stroke='var(--acc)' stroke-width='2.2' marker-end='url(#m)'/>" + "".join(seta(386 + i * 377, 475, 433 + i * 377, 475) for i in range(3)) + seta(1312, 560, 1312, 640)
D["5_zona_brillouin"] = pagina("Zona de Brillouin e <span>simetria</span>", "Da estrutura cristalina às entradas de bandas dos programas DFT", corpo, setas)

# 6 · Validação ------------------------------------------------------------------------------------------
corpo = "<div class='c acc' style='left:640px;top:380px;width:320px;height:140px;text-align:center;display:flex;flex-direction:column;justify-content:center'><div class='marca' style='font-size:36px'>BrUMa<i>Re</i></div><p>resultados verificáveis</p></div>"
vs = [(56, 150, "Saídas reais", ["5 programas de DFT", "22 estruturas de teste", "51 materiais da biblioteca"]),
      (1124, 150, "Ferramentas de referência", ["pymatgen · sumo · sisl · cclib · pybader", "concordância até 10⁻⁴ eV", "Bader: 0,0008 e/átomo"]),
      (56, 580, "80 testes automatizados", ["pytest, integração contínua", "Python 3.9 e 3.12", "regressão do CASTEP"]),
      (1124, 580, "Paridade página × Python", ["mesmos gaps e massas", "mesmos grupos espaciais", "pontos k idênticos (14 redes)"]),
      (590, 150, "Achados de método", ["gap por contagem de elétrons", "massa com termo linear", "F₃ do MCLC1 corrigido"])]
for x, y, t, it in vs:
    corpo += c(x, y, 420, 140, t, "<div style='font-size:15.5px'>" + ul(*it) + "</div>", "vio" if "Achados" in t else "")
setas = seta(476, 235, 640, 420, 1) + seta(1124, 235, 960, 420, 1) + seta(476, 665, 640, 490, 1) + seta(1124, 665, 960, 490, 1) + seta(800, 320, 800, 380)
D["6_validacao"] = pagina("Validação e <span>qualidade</span>", "Como os resultados do BrUMaRe são conferidos", corpo, setas)


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, html in D.items():
            fn = os.path.join(OUT, nome + ".html"); open(fn, "w", encoding="utf-8").write(html)
            for tema in ("claro", "escuro"):
                pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=2)
                pg.goto("file://" + fn); pg.evaluate(f"document.body.classList.toggle('dark', {'true' if tema == 'escuro' else 'false'})"); pg.wait_for_timeout(500)
                pg.screenshot(path=os.path.join(OUT, f"{nome}_{tema}.png"))
                if tema == "claro":
                    pg.pdf(path=os.path.join(OUT, nome + ".pdf"), width="1600px", height="900px", print_background=True)
                pg.close()
            subprocess.run(["pdftocairo", "-svg", os.path.join(OUT, nome + ".pdf"), os.path.join(OUT, nome + ".svg")], check=False)
            os.remove(fn)
        b.close()
    subprocess.run(["pdfunite"] + [os.path.join(OUT, n + ".pdf") for n in D] + [os.path.join(OUT, "BrUMaRe-diagramas.pdf")], check=False)
    print(f"{len(D)} diagramas -> {OUT}")


if __name__ == "__main__":
    main()
