#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo
"""Gera o tutorial em PDF de cada idioma a partir das páginas tutorial.<idioma>.html (pandoc + XeLaTeX).

    python3 tools/tutorial_pdf.py          # brumare-tutorial.<idioma>.pdf para cada tradução
O PDF em português continua vindo do LaTeX próprio (brumare-tutorial.tex).
"""
import glob, os, re, subprocess, sys, tempfile, shutil
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPA = {
    "pt": ("Guia completo do BrUMaRe", "Bandas, DOS, PDOS, densidade de carga, defeitos e termodinâmica a partir de cálculos CASTEP, VASP, SIESTA, Quantum ESPRESSO e ORCA", "Versão", "Sumário", "portuguese"),
    "en": ("Complete guide to BrUMaRe", "Bands, DOS, PDOS, charge density, defects and thermodynamics from CASTEP, VASP, SIESTA, Quantum ESPRESSO and ORCA calculations", "Version", "Contents", "english"),
    "es": ("Guía completa de BrUMaRe", "Bandas, DOS, PDOS, densidad de carga, defectos y termodinámica a partir de cálculos de CASTEP, VASP, SIESTA, Quantum ESPRESSO y ORCA", "Versión", "Índice", "spanish"),
    "fr": ("Guide complet de BrUMaRe", "Bandes, DOS, PDOS, densité de charge, défauts et thermodynamique à partir de calculs CASTEP, VASP, SIESTA, Quantum ESPRESSO et ORCA", "Version", "Table des matières", "french"),
    "it": ("Guida completa a BrUMaRe", "Bande, DOS, PDOS, densità di carica, difetti e termodinamica da calcoli CASTEP, VASP, SIESTA, Quantum ESPRESSO e ORCA", "Versione", "Indice", "italian"),
    "la": ("Institutio integra BrUMaRe", "Fasciae, DOS, PDOS, densitas oneris, vitia et thermodynamica ex computationibus CASTEP, VASP, SIESTA, Quantum ESPRESSO et ORCA", "Versio", "Index", "latin"),
}
ACK = {"pt": "Agradecimento a \\textbf{Benedet, R. O.} --- sem ela, isso nunca teria acontecido.",
       "en": "Acknowledgment to \\textbf{Benedet, R. O.} --- without her, this would never have happened.",
       "es": "Agradecimiento a \\textbf{Benedet, R. O.} --- sin ella, esto nunca habría sucedido.",
       "fr": "Remerciements à \\textbf{Benedet, R. O.} --- sans elle, cela ne serait jamais arrivé.",
       "it": "Ringraziamento a \\textbf{Benedet, R. O.} --- senza di lei, tutto questo non sarebbe mai accaduto.",
       "la": "Gratiae \\textbf{Benedet, R. O.} --- sine ea, hoc numquam accidisset."}


def versao():
    return re.search(r'^VERSAO = "([^"]+)"', open(os.path.join(RAIZ, "brumare.py"), encoding="utf-8").read(), re.M).group(1)


def gerar(lang):
    html = open(os.path.join(RAIZ, "tutorial.html" if lang == "pt" else f"tutorial.{lang}.html"), encoding="utf-8").read()
    art = re.search(r'<article class="prose">(.*?)</article>', html, re.S).group(1)
    def _fig(m):                                         # figura simples (sem flutuar): funciona dentro de listas e blocos
        img = re.search(r'<img[^>]*src="([^"]+)"', m.group(0)); cap = re.search(r"<figcaption>(.*?)</figcaption>", m.group(0), re.S)
        return (f'<p><img src="{img.group(1)}" style="width:100%"></p>' if img else "") + (f"<p><em>{cap.group(1)}</em></p>" if cap else "")
    art = re.sub(r"<figure>.*?</figure>", _fig, art, flags=re.S)
    art = re.sub(r'<button class="copy"[^>]*>.*?</button>', "", art)
    art = re.sub(r"\\\[(.*?)\\\]", lambda m: f'<span class="math display">\\[{m.group(1)}\\]</span>', art, flags=re.S)
    art = re.sub(r"\\\((.*?)\\\)", lambda m: f'<span class="math inline">\\({m.group(1)}\\)</span>', art, flags=re.S)
    art = re.sub(r'<p class="callout">(.*?)</p>', r"<blockquote><p>\1</p></blockquote>", art, flags=re.S)   # cada destaque, aberto e fechado
    tit, sub, ver, sumario, babel = CAPA[lang]
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "img"))
    for pasta in (os.path.join(RAIZ, "img"), os.path.join(RAIZ, "docs", "manual", "img"), os.path.join(RAIZ, "docs", "img")):
        for x in glob.glob(os.path.join(pasta, "*.png")):
            shutil.copy(x, os.path.join(tmp, "img"))
    open(os.path.join(tmp, "t.html"), "w", encoding="utf-8").write(f"<html><body>{art}</body></html>")
    pre = open(os.path.join(RAIZ, "docs", "manual", "preambulo.tex"), encoding="utf-8").read()
    pre = re.sub(r"\\renewcommand\{\\maketitle\}\{.*", "", pre, flags=re.S)        # capa própria abaixo
    pre = pre.replace("{\\titulofonte\\small Manual do autor}", "{\\titulofonte\\small " + tit + "}")
    pre = pre.replace("\\fancyhead[R]{\\small\\color{gray}BrUMaRe e brunohdmacedo.tech}", "\\fancyhead[R]{\\small\\color{gray}brunohdmacedo.tech/brumare}")
    pre = pre.replace("Path=./fonts/", "Path=" + os.path.join(RAIZ, "docs", "manual", "fonts") + "/")
    capa = ("\\renewcommand{\\maketitle}{\\begin{titlepage}\\centering\\vspace*{2.4cm}"
            "\\includegraphics[width=0.6\\linewidth]{" + os.path.join(RAIZ, "docs", "img", "brumare-logo-claro.png") + "}\\par\\vspace{1.4cm}"
            "{\\titulofonte\\fontsize{28}{34}\\selectfont " + tit + "\\par}\\vspace{0.4cm}"
            "{\\large\\color{ciano} Brillouin-zone Utilities for Materials Research\\par}\\vspace{0.3cm}"
            "{\\normalsize " + sub + "\\par}\\vspace{2cm}{\\large Bruno Henrique Dourado Macedo\\footnote{" + ACK[lang] + "}\\par}\\vspace{0.2cm}"
            "{\\small PPGFISA, UNILA · Foz do Iguaçu\\par}\\vspace{0.2cm}{\\small\\url{https://brunohdmacedo.tech/brumare/} · ORCID 0000-0002-8152-0950\\par}"
            "\\vfill\\begin{minipage}{0.82\\linewidth}\\centering\\small\\itshape «Scientia, bonum commune generis humani, ab hominibus nata est ut universam naturam describeret: quod ab omnibus creatur, omnibus reddendum est. Docere est liberare; discere ius est, non privilegium. Ab unoquoque secundum facultates suas, unicuique secundum necessitates suas --- sic et scientia.»\\\\[4pt]\\upshape\\color{ciano}--- Bruno Macedo\\end{minipage}\\par"
            "\\vspace{0.8cm}{\\small\\color{gray} " + ver + " " + versao() + " · GPL-3.0-or-later\\par}\\end{titlepage}}\n")
    open(os.path.join(tmp, "pre.tex"), "w", encoding="utf-8").write(pre + capa)
    tex = os.path.join(tmp, "brumare-tutorial.tex" if lang == "pt" else f"brumare-tutorial.{lang}.tex")
    subprocess.run(["pandoc", "t.html", "-f", "html", "-s", "-o", tex, "--toc", "--toc-depth=1", "--include-in-header=pre.tex",
                    "-V", "fontfamily=fontspec", "-V", f"lang={'pt-BR' if lang == 'pt' else lang}", "-V", "documentclass=article", "-V", "fontsize=10pt",
                    "-V", "colorlinks=true", "-V", "linkcolor=ciano", "-V", "urlcolor=ciano", "-V", f"toc-title={sumario}",
                    "-M", f"title={tit}", "--resource-path", RAIZ], cwd=tmp, check=True)
    t = open(tex, encoding="utf-8").read()
    t = t.replace("\\begin{longtable}[]{@{}lll@{}}", "\\begin{longtable}[]{@{}p{0.28\\linewidth}p{0.33\\linewidth}p{0.33\\linewidth}@{}}")
    open(tex, "w", encoding="utf-8").write(t)
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", os.path.basename(tex)], cwd=tmp, capture_output=True, text=True)
    log = open(tex[:-4] + ".log", encoding="utf-8", errors="replace").read()
    pdf = tex[:-4] + ".pdf"
    erros = [l for l in log.splitlines() if l.startswith("!")]
    if erros or not os.path.exists(pdf):
        print("TEMP:", tmp)
        sys.exit(f"ERRO ao gerar {lang}: " + "\n".join(l for l in log.splitlines() if l.startswith("!"))[:600])
    shutil.copy(pdf, RAIZ)                                   # uma cópia só, na raiz (as páginas a usam)
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    print(f"  brumare-tutorial{'' if lang == 'pt' else '.' + lang}.pdf: {n} páginas, {log.count('Overfull \\\\hbox')} linhas estouradas, {len([l for l in log.splitlines() if l.startswith('!')])} erros")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    langs = sys.argv[1:] or ["pt"] + sorted(os.path.basename(f)[9:-5] for f in glob.glob(os.path.join(RAIZ, "tutorial.*.html")))
    for l in langs:
        gerar(l)
