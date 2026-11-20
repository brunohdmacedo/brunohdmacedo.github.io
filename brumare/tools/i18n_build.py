#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo
"""Monta i18n/dict.js a partir dos .tsv (pt ¦ en ¦ es ¦ fr ¦ it ¦ la) e injeta o motor de idiomas
nas páginas (entre <!-- i18n:inicio --> e <!-- i18n:fim -->).

    python3 tools/i18n_build.py                 # monta e injeta em index.html e tutorial.html
    python3 tools/i18n_build.py --site ../brunohdmacedo.github.io   # também na página principal do site
"""
import glob, json, os, re, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = ["en", "es", "fr", "it", "la"]


def ler(f):
    out = []
    for n, linha in enumerate(open(f, encoding="utf-8"), 1):
        linha = linha.rstrip("\n")
        if not linha.strip() or linha.startswith("#"):
            continue
        c = [x.strip() for x in linha.split(" ¦ ")]
        if len(c) != 6:
            sys.exit(f"ERRO {os.path.basename(f)}:{n}: esperadas 6 colunas, achei {len(c)}")
        out.append(c)
    return out


def montar():
    d = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, "i18n", "dict_*.tsv"))):
        for c in ler(f):
            d[re.sub(r"\s+", " ", c[0])] = dict(zip(L, c[1:]))
    r = [[c[0], dict(zip(L, c[1:]))] for c in ler(os.path.join(RAIZ, "i18n", "regras.tsv"))]
    js = ("/* gerado por tools/i18n_build.py a partir de i18n/*.tsv: não edite à mão */\n"
          "window.I18N_DICT = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n"
          "window.I18N_RULES = " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) + ";\n")
    open(os.path.join(RAIZ, "i18n", "dict.js"), "w", encoding="utf-8").write(js)
    return d, r, js


CSS = ("select.lang-sel{font:500 12.5px 'JetBrains Mono',Consolas,monospace;background:var(--card,#fff);color:var(--tx,#111);"
       "border:1px solid var(--line,#ccc);border-radius:9px;padding:6px 8px;min-height:36px;cursor:pointer;max-width:9.5em}"
       "@media(max-width:420px){select.lang-sel{max-width:5.2em}}")


def injetar(pagina, js):
    s = open(pagina, encoding="utf-8").read()
    motor = open(os.path.join(RAIZ, "i18n", "i18n.js"), encoding="utf-8").read()
    bloco = f"<!-- i18n:inicio -->\n<style>{CSS}</style>\n<script>\n{js}</script>\n<script>\n{motor}</script>\n<!-- i18n:fim -->"
    if "<!-- i18n:inicio -->" in s:
        s = re.sub(r"<!-- i18n:inicio -->.*?<!-- i18n:fim -->", lambda m: bloco, s, flags=re.S)
    else:
        s = s.replace("</body>", bloco + "\n</body>", 1)
    s = s.replace('<blockquote lang="la">', '<blockquote lang="la" translate="no">')   # a frase do autor (latim) nunca é traduzida
    open(pagina, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    d, r, js = montar()
    pags = [os.path.join(RAIZ, "index.html"), os.path.join(RAIZ, "tutorial.html")]
    if "--site" in sys.argv:
        pags.append(os.path.join(sys.argv[sys.argv.index("--site") + 1], "index.html"))
    for p in pags:
        injetar(p, js)
    print(f"i18n: {len(d)} textos e {len(r)} regras em 5 idiomas além do português; injetado em {len(pags)} página(s)")
