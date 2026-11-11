#!/usr/bin/env bash
# Gera manual-bruma.tex e manual-bruma.pdf a partir do MANUAL.md (fonte única),
# procurado em ../MANUAL.md (repositório) ou ./MANUAL.md (pacote avulso).
# Requer: pandoc (>= 2.11), python3 e XeLaTeX (TeX Live ou MiKTeX).
set -euo pipefail
export LC_ALL=C.UTF-8 LANG=C.UTF-8
cd "$(dirname "$0")"
python3 - <<'PY'
import re
import os
s = open("../MANUAL.md" if os.path.exists("../MANUAL.md") else "MANUAL.md", encoding="utf-8").read()
s = re.sub(r"^# Manual do autor.*\n", "", s, count=1, flags=re.M)                 # título vai para a capa
s = re.sub(r"^## Sumário\n.*?\n---\n", "", s, count=1, flags=re.M | re.S)         # sumário do LaTeX substitui o manual
s = s.replace("](#", "](#")                                                          # âncoras mantidas
s = ('---\ntitle: "Manual do autor: Bruma e site brunohdmacedo.tech"\nauthor: "Bruno Henrique Dourado Macedo"\n'
     'date: "Versão 1.0.0 · novembro de 2026"\ntoc-title: "Sumário"\n---\n\n') + s     # metadados só para o pandoc
open("manual_tmp.md", "w", encoding="utf-8").write(s)
PY
pandoc manual_tmp.md -s -o manual-bruma.tex \
  --shift-heading-level-by=-1 --toc --toc-depth=2 \
  --pdf-engine=xelatex --include-in-header=preambulo.tex \
  -V fontfamily=fontspec -V lang=pt-BR -V documentclass=article -V fontsize=10pt -V colorlinks=true \
  -V linkcolor=ciano -V urlcolor=ciano -V toccolor=tinta --lua-filter=quebra_codigo.lua \
  --highlight-style=tango
rm -f manual_tmp.md
xelatex -interaction=nonstopmode manual-bruma.tex > /dev/null
xelatex -interaction=nonstopmode manual-bruma.tex > /dev/null
echo "OK: manual-bruma.tex e manual-bruma.pdf"
