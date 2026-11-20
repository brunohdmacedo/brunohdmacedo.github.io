# Bibliotecas e fontes embutidas no aplicativo de computador

O aplicativo do Bruma (Windows `.exe` e `bruma-gui`) roda a mesma interface do site, sem internet. Para isso, as dependências que o site carrega de CDNs ficam aqui, nas **mesmas versões**:

| Arquivo | Versão | Licença |
|---|---|---|
| `plotly.min.js` | Plotly.js 2.27.0 | MIT (`licencas/plotly-LICENSE.txt`) |
| `jszip.min.js` | JSZip 3.10.1 | MIT ou GPLv3 (`licencas/jszip-LICENSE.md`) |
| `mathjax/` (tex-chtml e fontes) | MathJax 3.2.2, para as fórmulas do tutorial | Apache 2.0 (`licencas/mathjax-LICENSE.txt`) |
| `fonts/SpaceGrotesk.ttf` | Space Grotesk | SIL OFL 1.1 (`licencas/SpaceGrotesk-OFL.txt`) |
| `fonts/JetBrainsMono.ttf` | JetBrains Mono | SIL OFL 1.1 (`licencas/JetBrainsMono-OFL.txt`) |

`tools/montar_app.py` copia o site para `bruma_app/web/` e troca os endereços dos CDNs por estes arquivos.
