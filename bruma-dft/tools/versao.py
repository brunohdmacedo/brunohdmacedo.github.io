#!/usr/bin/env python3
"""Troca a versão do Bruma em todos os arquivos de uma vez.

    python3 tools/versao.py            # mostra a versão atual em cada arquivo
    python3 tools/versao.py 1.1.0      # muda para 1.1.0 (e a data de lançamento para hoje)
    python3 tools/versao.py 1.1.0 --site ../brunohdmacedo.github.io   # também copia para o site

Arquivos: bruma.py, pyproject.toml, index.html, CITATION.cff, bruma.bib, docs/bruma.bib,
bruma-tutorial.tex, docs/bruma-tutorial.tex e packaging/windows/bruma.iss.
"""
import datetime
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
HOJE = datetime.date.today()

REGRAS = [  # (arquivo, padrão com um grupo para a versão)
    ("bruma.py", r'^VERSAO = "([^"]+)"'),
    ("pyproject.toml", r'^version = "([^"]+)"'),
    ("index.html", r"versao: '([^']+)'"),
    ("CITATION.cff", r'^version: "([^"]+)"'),
    ("bruma.bib", r"version\s*=\s*\{([^}]+)\},\s*\n\s*howpublished\s*=\s*\{\\url\{https://brunohdmacedo\.tech/bruma"),
    ("docs/bruma.bib", r"version\s*=\s*\{([^}]+)\},\s*\n\s*howpublished\s*=\s*\{\\url\{https://brunohdmacedo\.tech/bruma"),
    ("bruma-tutorial.tex", r"\\date\{Versão ([0-9.]+)"),
    ("docs/bruma-tutorial.tex", r"\\date\{Versão ([0-9.]+)"),
    ("packaging/windows/bruma.iss", r'#define AppVersion "([^"]+)"'),
]


def ler(p):
    return open(os.path.join(RAIZ, p), encoding="utf-8").read()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    site = sys.argv[sys.argv.index("--site") + 1] if "--site" in sys.argv else None
    if site and site in args:
        args.remove(site)
    nova = args[0] if args else None
    if nova and not re.fullmatch(r"\d+\.\d+\.\d+", nova):
        sys.exit("Use o formato X.Y.Z, por exemplo 1.1.0")
    for arq, pad in REGRAS:
        if not os.path.exists(os.path.join(RAIZ, arq)):
            print(f"  (sem {arq})")
            continue
        s = ler(arq)
        m = re.search(pad, s, re.M)
        if not m:
            print(f"  ATENÇÃO: versão não encontrada em {arq}")
            continue
        if not nova:
            print(f"  {arq:<32} {m.group(1)}")
            continue
        s = s[:m.start(1)] + nova + s[m.end(1):]
        if arq == "CITATION.cff":
            s = re.sub(r'^date-released: "[^"]+"', f'date-released: "{HOJE.isoformat()}"', s, flags=re.M)
        if arq.endswith(".tex"):
            s = re.sub(r"(\\date\{Versão [0-9.]+ — )[^}]+\}", lambda k: k.group(1) + f"{MESES[HOJE.month - 1]} de {HOJE.year}}}", s)
        if arq == "index.html":
            s = re.sub(r"data: '[^']+'", f"data: '{MESES[HOJE.month - 1]} de {HOJE.year}'", s)
        open(os.path.join(RAIZ, arq), "w", encoding="utf-8").write(s)
        print(f"  {arq:<32} -> {nova}")
    if nova:
        print(f"\nVersão {nova} aplicada. Próximos passos:\n"
              f"  1. recompile o PDF do tutorial (seção F do manual)\n"
              f"  2. git commit -am \"Versão {nova}\" && git tag v{nova} && git push && git push --tags")
        if site:
            subprocess.run(["bash", os.path.join(RAIZ, "tools", "copiar_para_site.sh"), site], check=False)


if __name__ == "__main__":
    main()
