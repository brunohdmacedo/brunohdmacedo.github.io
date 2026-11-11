#!/usr/bin/env bash
# Copia a versão web do Bruma para a pasta /bruma/ do repositório do site pessoal.
# Uso:  bash tools/copiar_para_site.sh ../brunohdmacedo.github.io
set -euo pipefail
SITE="${1:?Informe a pasta do repositório do site, ex.: ../brunohdmacedo.github.io}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$SITE/CNAME" ] || [ -f "$SITE/index.html" ] || { echo "Não parece o repositório do site: $SITE"; exit 1; }
mkdir -p "$SITE/bruma/assets" "$SITE/bruma/img"
cp "$RAIZ"/{index.html,tutorial.html,bruma-tutorial.pdf,bruma-tutorial.tex,bruma.bib,CITATION.cff} "$SITE/bruma/"
cp "$RAIZ"/img/* "$SITE/bruma/img/"
cp "$RAIZ"/assets/*.svg "$RAIZ"/assets/bruma-512.png "$RAIZ"/assets/bruma-logo-*.png "$SITE/bruma/assets/"
[ -f "$RAIZ/docs/manual/manual-bruma.pdf" ] && cp "$RAIZ/docs/manual/manual-bruma.pdf" "$SITE/bruma/" || true
echo "Bruma copiado para $SITE/bruma/. Agora, no site:  git add bruma && git commit -m 'Atualiza o Bruma' && git push"
