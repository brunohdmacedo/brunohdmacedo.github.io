#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo
# BrUMaRe: Brillouin-zone Utilities for Materials Research - https://github.com/brunohdmacedo/brumare
"""Monta brumare_app/web/: a cópia OFFLINE do site usada pelo aplicativo de computador.

    python3 tools/montar_app.py

Copia index.html, tutorial.html, figuras, logo, PDFs e citações, e troca os endereços
de CDN (Plotly, JSZip, Google Fonts) pelos arquivos de vendor/. Rode sempre que mudar
o index.html ou o tutorial (o workflow do Windows e o tools/versao.py já fazem isso).
"""
import os
import re
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(RAIZ, "brumare_app", "web")
FONTES = """<style>
@font-face{font-family:'Space Grotesk';src:url('vendor/fonts/SpaceGrotesk.ttf') format('truetype');font-weight:300 700;font-display:swap}
@font-face{font-family:'JetBrains Mono';src:url('vendor/fonts/JetBrainsMono.ttf') format('truetype');font-weight:100 800;font-display:swap}
</style>"""


def offline(html):
    """Troca CDNs por arquivos locais; o resto do site fica igual."""
    n0 = len(html)
    html = re.sub(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/plotly\.js/[^"]+"></script>', '<script src="vendor/plotly.min.js"></script>', html)
    html = re.sub(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/jszip/[^"]+"></script>', '<script src="vendor/jszip.min.js"></script>', html)
    html = re.sub(r'<script async src="https://cdnjs\.cloudflare\.com/ajax/libs/mathjax/[^"]+"></script>', '<script async src="vendor/mathjax/tex-chtml.js"></script>', html)
    html = re.sub(r"<script>if\(!window\.Plotly\).*?</script>\n?", "", html, flags=re.S)       # reserva de CDN: desnecessária offline
    html = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\n?', "", html)
    html = re.sub(r'<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">', FONTES, html)
    html = html.replace("<html lang=\"pt-BR\"", "<html lang=\"pt-BR\" data-app=\"desktop\"", 1)
    return html, n0


def main():
    if os.path.isdir(WEB):
        shutil.rmtree(WEB)
    os.makedirs(WEB)
    import glob
    for nome in ["index.html", "tutorial.html"] + sorted(os.path.basename(x) for x in glob.glob(os.path.join(RAIZ, "tutorial.*.html"))):
        html = open(os.path.join(RAIZ, nome), encoding="utf-8").read()
        html, _ = offline(html)
        if re.search(r"cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|fonts\.googleapis\.com/css2", html):
            sys.exit(f"ERRO: ainda há CDN em {nome}")
        open(os.path.join(WEB, nome), "w", encoding="utf-8").write(html)
    for d in ("img", "assets", "vendor"):
        shutil.copytree(os.path.join(RAIZ, d), os.path.join(WEB, d))
    for f in ("brumare-tutorial.pdf", "brumare.bib", "CITATION.cff", os.path.join("docs", "teoria", "teoria-brumare.pdf")):
        p = os.path.join(RAIZ, f)
        if os.path.isfile(p):
            shutil.copy(p, WEB)
    for p in glob.glob(os.path.join(RAIZ, "brumare-tutorial.*.pdf")):
        shutil.copy(p, WEB)
    tam = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(WEB) for f in fs)
    print(f"brumare_app/web montado: {sum(len(fs) for _, _, fs in os.walk(WEB))} arquivos, {tam / 1e6:.1f} MB (offline)")


if __name__ == "__main__":
    main()
