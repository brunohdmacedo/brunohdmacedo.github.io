#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo
"""Gera tutorial.<idioma>.html a partir de tutorial.html (português) e de i18n/tutorial/<idioma>.html.

Cada arquivo de idioma traz só o texto traduzido: título e descrição (<!--meta …-->), a abertura
(<!--intro …-->) e o corpo (sumário e artigo). As citações e as referências bibliográficas ficam no
original (marcadores <!--keep-citations--> e <!--keep-references-->). Cabeçalho, rodapé e estilos
vêm da página em português. Rode depois de editar o tutorial:  python3 tools/tutorial_build.py
"""
import glob, json, os, re
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_LANG = {"pt": "pt-BR", "en": "en", "es": "es", "fr": "fr", "it": "it", "la": "la"}
URL = "https://brunohdmacedo.tech/brumare/"


def attrs(comment, nome):
    m = re.search(r"<!--" + nome + r"\s+(.*?)-->", comment, re.S)
    return dict(re.findall(r'(\w+)="(.*?)"', m.group(1), re.S)) if m else {}


def main():
    pt = open(os.path.join(RAIZ, "tutorial.html"), encoding="utf-8").read()
    i, j = pt.index("<main"), pt.index("</main>")
    corpo_pt = pt[i:j]
    ini = corpo_pt.index('<div class="w tut">')
    intro_pt, art_pt = corpo_pt[:ini], corpo_pt[ini:]
    a = art_pt.index("<h3>ABNT (NBR 6023)</h3>") + len("<h3>ABNT (NBR 6023)</h3>")
    citas = art_pt[a:art_pt.index('<h2 id="biblio">')]
    refs = re.search(r'<ol class="refs">.*?</ol>', art_pt, re.S).group(0)
    langs = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(RAIZ, "i18n", "tutorial", "*.html")))
    pages = {"pt": "tutorial.html", **{l: f"tutorial.{l}.html" for l in langs}}
    alternates = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{URL}{p}">\n' for l, p in pages.items()) + \
        f'<link rel="alternate" hreflang="x-default" href="{URL}tutorial.html">\n'

    def marcar(html, lang):
        html = re.sub(r'<html lang="[^"]*"( data-i18n-pages=\'[^\']*\' data-i18n-page-lang="[^"]*")?',
                      f'<html lang="{HTML_LANG[lang]}" data-i18n-pages=\'{json.dumps(pages)}\' data-i18n-page-lang="{lang}"', html, count=1)
        html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n', "", html)
        return html.replace("</head>", alternates + "</head>", 1)

    open(os.path.join(RAIZ, "tutorial.html"), "w", encoding="utf-8").write(marcar(pt, "pt"))
    for l in langs:
        t = open(os.path.join(RAIZ, "i18n", "tutorial", f"{l}.html"), encoding="utf-8").read()
        meta, intro = attrs(t, "meta"), attrs(t, "intro")
        corpo = re.sub(r"<!--(meta|intro)\s.*?-->\n?", "", t, flags=re.S)
        corpo = corpo.replace("<!--keep-citations-->", citas.strip()).replace("<!--keep-references-->", refs)
        it = intro_pt
        it = re.sub(r"(</svg></span>).*?(</h1>)", lambda m: m.group(1) + intro["h1"] + m.group(2), it, count=1, flags=re.S)
        it = re.sub(r"(</h1>\s*<p>).*?(</p>)", lambda m: m.group(1) + intro["p"] + m.group(2), it, count=1, flags=re.S)
        for k, href in (("a1", "./"), ("a2", "brumare-tutorial.pdf"), ("a3", "#citar")):
            it = re.sub(r'(<a class="b[^"]*" href="' + re.escape(href) + r'">)[^<]*(</a>)', lambda m, v=intro[k]: m.group(1) + v + m.group(2), it, count=1)
        html = pt[:i] + it + corpo + pt[j:]
        if os.path.exists(os.path.join(RAIZ, f"brumare-tutorial.{l}.pdf")) or True:
            html = html.replace('href="brumare-tutorial.pdf"', f'href="brumare-tutorial.{l}.pdf"')
        html = re.sub(r"<title>.*?</title>", f"<title>{meta['title']}</title>", html, count=1)
        html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{meta["desc"]}">', html, count=1)
        html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{meta["title"].split(" | ")[0]}">', html, count=1)
        html = html.replace(f'<link rel="canonical" href="{URL}tutorial.html">', f'<link rel="canonical" href="{URL}tutorial.{l}.html">')
        html = html.replace(f'<meta property="og:url" content="{URL}tutorial.html">', f'<meta property="og:url" content="{URL}tutorial.{l}.html">')
        open(os.path.join(RAIZ, f"tutorial.{l}.html"), "w", encoding="utf-8").write(marcar(html, l))
    print(f"tutorial: português + {len(langs)} idioma(s) {langs} -> " + ", ".join(pages.values()))


if __name__ == "__main__":
    main()
