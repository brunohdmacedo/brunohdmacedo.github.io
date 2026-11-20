#!/usr/bin/env bash
# Copia a versão web do BrUMaRe para a pasta /brumare/ do repositório do site pessoal
# e mantém /bruma/ e /castep/ como redirecionamentos para o endereço novo.
# Uso:  bash tools/copiar_para_site.sh ../brunohdmacedo.github.io
set -euo pipefail
SITE="${1:?Informe a pasta do repositório do site, ex.: ../brunohdmacedo.github.io}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$SITE/CNAME" ] || [ -f "$SITE/index.html" ] || { echo "Não parece o repositório do site: $SITE"; exit 1; }
D="$SITE/brumare"
mkdir -p "$D/assets" "$D/img"
cp "$RAIZ"/{index.html,tutorial.html,brumare-tutorial.pdf,brumare-tutorial.tex,brumare.bib,CITATION.cff,LICENCA.md,CONTRIBUTING.md} "$D/"
cp "$RAIZ"/tutorial.*.html "$RAIZ"/brumare-tutorial.*.pdf "$D/" 2>/dev/null || true      # tutorial em outros idiomas
mkdir -p "$D/vendor" && cp "$RAIZ/vendor/brumare-jxl.js" "$RAIZ/vendor/brumare-moyo.js" "$D/vendor/"   # codificador JPEG XL (exportação .jxl)
cp "$RAIZ"/img/*.jxl "$D/img/" 2>/dev/null || true
cp "$RAIZ/LICENSE" "$D/LICENSE.txt"
cp "$RAIZ"/img/* "$D/img/"
cp "$RAIZ"/assets/brumare-*.svg "$RAIZ"/assets/brumare-512.png "$RAIZ"/assets/brumare-logo-*.png "$RAIZ"/assets/brumare-og.png "$D/assets/"
[ -f "$RAIZ/docs/teoria/teoria-brumare.pdf" ] && cp "$RAIZ/docs/teoria/teoria-brumare.pdf" "$D/" || true   # teoria completa
# redirecionamentos dos endereços antigos (links já divulgados continuam funcionando)
redir () {  # $1 = arquivo, $2 = destino
  mkdir -p "$(dirname "$1")"
  cat > "$1" <<HTML
<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>BrUMaRe: novo endereço</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="https://brunohdmacedo.tech$2">
<meta http-equiv="refresh" content="0; url=$2">
<script>location.replace('$2' + location.hash);</script>
</head><body style="font-family:system-ui,sans-serif;padding:40px">
<p>O BrUMaRe agora se chama <b>BrUMaRe</b> (Brillouin-zone Utilities for Materials Research). Você será levado para <a href="$2">$2</a>.</p>
</body></html>
HTML
}
rm -rf "$SITE/bruma"
redir "$SITE/bruma/index.html" "/brumare/"
redir "$SITE/bruma/tutorial.html" "/brumare/tutorial.html"
redir "$SITE/castep/index.html" "/brumare/"
redir "$SITE/castep/tutorial.html" "/brumare/tutorial.html"
echo "BrUMaRe copiado para $SITE/brumare/ (redirecionamentos: /bruma/ e /castep/)."
echo "Agora, no site:  git add -A && git commit -m 'BrUMaRe' && git push"
