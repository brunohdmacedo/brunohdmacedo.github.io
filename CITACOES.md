# Citações automáticas do portfólio

A seção **Produção** de `index.html` mostra o total de citações, o índice h e o selo "citado N×" em cada publicação. Tudo é atualizado sozinho.

## Como funciona

| Peça | O que faz |
|---|---|
| `.github/workflows/citacoes.yml` | roda toda segunda-feira às 9h (UTC) e também quando você executa à mão |
| `scripts/atualizar_citacoes.py` | busca as citações e grava `data/citacoes.json` |
| `site/js/citacoes.js` | lê o JSON direto do GitHub e marca cada publicação pelo título ou DOI; se o JSON estiver vazio ou desatualizado, consulta o OpenAlex ao vivo |

**Fontes:**

- **OpenAlex:** gratuito e aberto, pelo ORCID 0000-0002-8152-0950. Funciona sem nenhuma configuração.
- **Google Acadêmico:** o Google proíbe a raspagem do Scholar, então os números dele vêm do SerpApi, que oferece uma API para esses dados. É opcional.

## Ativar (uma vez)

1. Faça o push deste repositório.
2. No GitHub, abra **Actions → Atualizar citações → Run workflow** para a primeira atualização. Depois disso ele roda toda semana.
3. Para os números do Google Acadêmico:
   - crie uma conta em https://serpapi.com (há plano gratuito com buscas mensais suficientes para 1 busca por semana);
   - copie a sua API key;
   - no repositório, vá em **Settings → Secrets and variables → Actions → New repository secret**, com nome `SERPAPI_KEY` e a sua chave como valor;
   - rode o workflow de novo.

## Nova publicação

Acrescente um bloco `<div class="pub" data-t="art" data-title="Título exato">…</div>` na lista `#pubs` do `index.html`. Use `data-doi="10.xxxx/…"` quando houver DOI. O selo de citações aparece sozinho quando o trabalho for citado nas bases.

## Observações

- O Google Acadêmico costuma contar mais citações que o OpenAlex, porque indexa também teses, anais e repositórios.
- Se uma fonte falhar numa semana, os números anteriores dela são mantidos e o motivo fica em `avisos`, dentro do JSON.
