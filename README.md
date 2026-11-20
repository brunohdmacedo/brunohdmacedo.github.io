# brunohdmacedo.tech

Portfólio de **Bruno Henrique Dourado Macedo** (Engenharia Física e mestrado em Física Aplicada, UNILA) e página do **BrUMaRe**, publicados pelo GitHub Pages.

## Estrutura

```
index.html              portfólio (página principal)
404.html                página de erro
assets/                 tudo o que o portfólio usa: site.css, site.js, favicon.svg e img/
brumare/                BrUMaRe: ferramenta, tutoriais (6 idiomas), PDFs, teoria e módulos (vendor/)
bruma/  castep/         redirecionamentos dos endereços antigos para /brumare/
cs/                     páginas do time (index, sorteios, eclypse)
robenedet/              site de Renata Olmedo Benedet
data/citacoes.json      citações do Google Acadêmico (atualizado automaticamente)
scripts/                atualizador de citações (usado pela automação)
.github/workflows/      static.yml (publicação), citacoes.yml (citações, toda segunda-feira), snake.yml
CNAME · robots.txt · sitemap.xml · ads.txt · googleea98cecbf58918b7.html (verificação do Google)
```

## Manutenção

- **BrUMaRe:** gerado a partir do repositório do programa (`tools/copiar_para_site.sh`); não edite `brumare/` à mão.
- **Citações:** a automação `citacoes.yml` usa os segredos `SERPAPI_KEY` e `SERPAPI_AUTHOR_ID` (Settings → Secrets) e grava `data/citacoes.json`. Detalhes em `CITACOES.md`.
- **Imagens:** use WebP ou JPEG para fotos (PNG só para desenhos e logos); as versões `.jxl` entram por `<picture>`.
