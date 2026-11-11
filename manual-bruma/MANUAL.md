# Manual do autor: Bruma e site brunohdmacedo.tech

Este manual explica **como você faz tudo**:

- publicar e manter o site pessoal;
- publicar o Bruma no GitHub, no PyPI e no Windows;
- usar cada versão do programa (web, cluster, janela e Windows);
- manter as citações automáticas;
- lançar novas versões;
- compilar os documentos em LaTeX;
- resolver os problemas mais comuns.

> **Manual ou tutorial?** O *tutorial* (`tutorial.html` e `bruma-tutorial.pdf`) ensina a **usar o Bruma** para analisar cálculos. Este *manual* ensina a **publicar e manter** tudo o que foi criado.

## Sumário

0. [O que foi criado](#0-o-que-foi-criado)
1. [Antes de começar](#1-antes-de-começar)
2. [Parte A: site pessoal](#parte-a-site-pessoal-brunohdmacedotech)
3. [Parte B: repositório do Bruma](#parte-b-repositório-do-bruma-bruma-dft)
4. [Parte C: usar o Bruma](#parte-c-usar-o-bruma-nas-quatro-formas)
5. [Parte D: programa para Windows](#parte-d-programa-para-windows)
6. [Parte E: PyPI e DOI no Zenodo](#parte-e-pypi-e-doi-no-zenodo)
7. [Parte F: documentos em LaTeX](#parte-f-documentos-em-latex)
8. [Parte G: logo](#parte-g-logo)
9. [Parte H: manutenção e novas versões](#parte-h-manutenção-e-novas-versões)
10. [Parte I: solução de problemas](#parte-i-solução-de-problemas)
11. [Apêndice: comandos rápidos e mapa de arquivos](#apêndice-comandos-rápidos-e-mapa-de-arquivos)

---

## 0. O que foi criado

| Entrega | Onde fica | Para quê |
|---|---|---|
| **Site pessoal** | repositório `brunohdmacedo/brunohdmacedo.github.io` → brunohdmacedo.tech | portfólio, publicações com citações automáticas, Bruma em `/bruma/` |
| **Bruma (web)** | `bruma-dft/index.html`, publicado em brunohdmacedo.tech/bruma | análise no navegador, sem instalar nada |
| **Bruma (linha de comando)** | `bruma-dft/bruma.py` | cluster, scripts, filas SLURM/PBS |
| **Bruma (janela)** | `bruma-dft/bruma_gui.py` | uso local com cliques (Linux, macOS, Windows) |
| **Bruma (Windows)** | GitHub → Releases: `Bruma-Setup-<versão>.exe` | quem não usa Python |
| **Tutorial** | `tutorial.html` e `bruma-tutorial.pdf` (fonte `.tex`) | como analisar cálculos com o Bruma |
| **Citações** | `bruma.bib`, `CITATION.cff` | citar o Bruma, o TCC, o artigo e a base de dados |
| **Logo** | `bruma-dft/assets/` (e `logo-bruma.zip`) | SVG, PNG de 16 a 1024 px, `.ico` |
| **Citações automáticas do site** | `.github/workflows/citacoes.yml`, `scripts/atualizar_citacoes.py` | números do OpenAlex e do Google Acadêmico toda semana |
| **Compilação para Windows** | `.github/workflows/windows.yml`, `packaging/windows/` | gera os `.exe` e o instalador |
| **Publicação no PyPI** | `.github/workflows/pypi.yml`, `pyproject.toml` | `pip install bruma-dft` |
| **Ferramentas** | `tools/versao.py`, `tools/copiar_para_site.sh` | trocar a versão em todos os arquivos; copiar o Bruma para o site |
| **Exemplos de cluster** | `examples/slurm_bruma.sh`, `pbs_bruma.sh`, `castep_depois_bruma.sh` | jobs prontos |

São **dois repositórios** no GitHub:

1. **`brunohdmacedo.github.io`:** o site (já existe).
2. **`bruma-dft`:** o software (você vai criar). O site recebe uma *cópia* da versão web do Bruma na pasta `/bruma/`.

---

## 1. Antes de começar

### Contas

| Conta | Para quê | Obrigatória? |
|---|---|---|
| GitHub (`brunohdmacedo`) | repositórios, site, Actions, Releases | sim |
| PyPI (pypi.org) | `pip install bruma-dft` | não |
| Zenodo (zenodo.org) | DOI para cada versão do Bruma | não, mas recomendado |
| SerpApi (serpapi.com) | números do Google Acadêmico no site | não |
| Overleaf (overleaf.com) | compilar o LaTeX sem instalar nada | não |

### Programas no seu computador

- **Git:** <https://git-scm.com>. Configure uma vez:
  ```bash
  git config --global user.name "Bruno Henrique Dourado Macedo"
  git config --global user.email "brunohdmacedo@gmail.com"
  ```
- **Python 3.8 ou mais novo:** <https://python.org>. No Windows, marque *Add python.exe to PATH* na instalação.
- **Opcional:**
  - TeX Live ou MiKTeX, para compilar o LaTeX localmente;
  - Inno Setup 6, para gerar o instalador no seu Windows;
  - GitHub Desktop, se preferir não usar a linha de comando.

### Arquivos entregues

| Arquivo | Conteúdo |
|---|---|
| `bruma-dft.zip` | repositório completo do Bruma |
| `brunohdmacedo.github.io.zip` | site completo, com as páginas antigas mantidas |
| `logo-bruma.zip` | todos os arquivos da logo |

---

## Parte A: site pessoal (brunohdmacedo.tech)

### A1. Publicar a versão nova do site

1. Baixe o seu repositório (se ainda não tiver):
   ```bash
   git clone https://github.com/brunohdmacedo/brunohdmacedo.github.io.git
   cd brunohdmacedo.github.io
   ```
2. Descompacte o `brunohdmacedo.github.io.zip` **por cima** dessa pasta. O zip não contém a pasta `.git`, então o histórico é preservado.
3. Confira o que mudou:
   ```bash
   git status
   git diff --stat
   ```
4. Envie:
   ```bash
   git add -A
   git commit -m "Site: Bruma, publicações, citações automáticas"
   git push
   ```
5. Em 1 a 3 minutos o site está no ar. Para acompanhar, abra a aba **Actions** do repositório.

### A2. Configuração do GitHub Pages (uma vez)

Em **Settings → Pages**:

- **Source:** o repositório tem um workflow `static.yml`, que publica o site a cada `push`. Deixe **Source = GitHub Actions**. Se preferir **Deploy from a branch** (`main`, pasta `/root`), também funciona; nesse caso o `static.yml` pode ser apagado.
- **Custom domain:** `brunohdmacedo.tech`. O arquivo `CNAME` já existe e não deve ser apagado.
- **Enforce HTTPS:** marcado.

O repositório também tem vários workflows de exemplo (Jekyll, Gatsby, Next.js, npm). Se aparecerem falhando na aba Actions, desative-os em **Actions → (workflow) → ··· → Disable workflow**, ou apague os arquivos de `.github/workflows/` que não usa. **Não apague** `static.yml` (se usar Source = GitHub Actions) nem `citacoes.yml`.

### A3. Editar o conteúdo do site

Tudo está no `index.html` da raiz.

| Quero mudar… | Onde | Como |
|---|---|---|
| Contadores do topo (4 anos, 3 anos, 7 prêmios, 20 apresentações) | `<div class="stats">` | troque o `data-n="…"` (número) e o texto do `<span>` |
| Texto digitado no topo | `site/js/main.js`, lista `var ph=[…]` | edite as frases entre aspas |
| Texto "sobre" | `<section id="sobre">` | edite os parágrafos `<p>` |
| Linha do tempo | `<section id="trajetoria">`, blocos `<div class="ti">` | copie um bloco e edite; `class="ti m"` destaca o ponto em âmbar |
| Prêmios | `<section id="premios">` | copie uma linha e edite |
| Publicações | `<div id="pubs">` | veja a seção A4 |
| Cartão do Bruma | comentário `<!-- Bruma:` na seção laboratório | texto e botões |

Para testar localmente antes de enviar:

```bash
python3 -m http.server 8000
```

Depois abra `http://localhost:8000` no navegador.

### A4. Adicionar uma publicação

Cada publicação é um bloco dentro de `<div id="pubs">`:

```html
<div class="pub" data-t="art" data-title="Título exato da publicação" data-doi="10.xxxx/yyyy">
  <time>2026</time>
  <div>
    <b><a href="https://link.da.publicacao" target="_blank" rel="noopener" style="color:inherit">Título exato da publicação</a></b>
    <span>Macedo, B. H. D.; Coautor, X. · Revista, v. 1, p. 1–10, 2026</span>
  </div>
</div>
```

- **`data-t`** define o filtro: `art` (artigo), `cong` (congresso), `tcc`, `dat` (base de dados) ou `sw` (software). Para criar um filtro novo, copie um botão `<button data-f="…">` dentro de `<div class="fl" id="fl">`.
- **`data-title`** (o título exato) e **`data-doi`** (quando existir) permitem que o selo "citado N×" apareça sozinho.
- A ordem na lista é a ordem do arquivo. Mantenha as mais recentes no topo.

### A5. Citações automáticas (Google Acadêmico e OpenAlex)

**Como funciona:**

- **`citacoes.yml`:** roda toda segunda-feira às 9h (UTC) e chama o `scripts/atualizar_citacoes.py`.
- **`atualizar_citacoes.py`:** consulta o **OpenAlex** pelo seu ORCID (gratuito) e o **Google Acadêmico** pelo SerpApi (se houver chave), e grava o resultado em `data/citacoes.json`.
- **`site/js/citacoes.js`:** lê o JSON direto do GitHub e mostra o total, o índice h e os selos em cada publicação. Se o JSON estiver vazio, consulta o OpenAlex ao vivo.

**Ativar (uma vez):**

1. Faça o push do site (A1).
2. **Actions → Atualizar citações → Run workflow**.
3. Para os números do Google Acadêmico:
   - crie uma conta em <https://serpapi.com> (o plano gratuito basta para uma busca por semana);
   - copie a API key;
   - em **Settings → Secrets and variables → Actions → New repository secret**, use o nome `SERPAPI_KEY` e cole a chave como valor;
   - rode o workflow de novo.

Se o workflow falhar com *permission denied* ao fazer push, vá em **Settings → Actions → General → Workflow permissions** e marque **Read and write permissions**.

> O Google Acadêmico proíbe raspagem automática, por isso o caminho é o SerpApi. O OpenAlex costuma mostrar menos citações que o Scholar, porque indexa menos teses e anais.

### A6. Google e buscadores

- O `sitemap.xml` e o `robots.txt` já estão na raiz.
- No **Google Search Console** (<https://search.google.com/search-console>), o arquivo de verificação `googleea98cecbf58918b7.html` já está no site. Envie `https://brunohdmacedo.tech/sitemap.xml` em **Sitemaps**.
- O endereço antigo `/castep/` redireciona para `/bruma/`. Não apague a pasta `castep/`.

---

## Parte B: repositório do Bruma (`bruma-dft`)

### B1. Criar e enviar (uma vez)

1. No GitHub, abra **New repository**:
   - nome: `bruma-dft`;
   - visibilidade: **Public**;
   - sem README (o zip já tem).
2. No seu computador:
   ```bash
   unzip bruma-dft.zip
   cd bruma-dft
   git init -b main
   git add -A
   git commit -m "Bruma 1.0.0"
   git remote add origin https://github.com/brunohdmacedo/bruma-dft.git
   git push -u origin main
   ```
3. **Licença:** **Add file → Create new file**, com o nome `LICENSE`. Clique em **Choose a license template** e escolha **MIT** (comum em software científico).
4. **Descrição e tópicos** (engrenagem ao lado de *About*):
   - descrição: *Bandas, DOS, PDOS, densidade de carga, defeitos e termodinâmica a partir de cálculos CASTEP*;
   - site: `https://brunohdmacedo.tech/bruma/`;
   - tópicos: `castep`, `dft`, `band-structure`, `density-of-states`, `charge-density`, `materials-science`, `hydrogen-storage`.

O arquivo `CITATION.cff` faz aparecer o botão **Cite this repository** na página do repositório.

### B2. Versão web no repositório (opcional)

A versão oficial da web fica no seu site (`/bruma/`). Se quiser também um endereço no próprio repositório: **Settings → Pages → Deploy from a branch → main / (root)**. Ele ficará em `https://brunohdmacedo.github.io/bruma-dft/`.

### B3. Atualizar a cópia do Bruma no site

Sempre que mudar o `index.html`, o `tutorial.html` ou os PDFs do Bruma:

```bash
cd bruma-dft
bash tools/copiar_para_site.sh ../brunohdmacedo.github.io
cd ../brunohdmacedo.github.io
git add bruma
git commit -m "Atualiza o Bruma"
git push
```

No Windows, sem Bash, copie à mão para a pasta `bruma/` do site estes arquivos:

- `index.html`, `tutorial.html`, `bruma-tutorial.pdf`, `bruma-tutorial.tex`, `bruma.bib` e `CITATION.cff`;
- as pastas `img/` e `assets/`.

---

## Parte C: usar o Bruma nas quatro formas

Detalhes de cada análise estão no **tutorial**. Aqui está como pôr cada forma para funcionar.

### C1. Web

Abra <https://brunohdmacedo.tech/bruma/> e arraste os arquivos do cálculo (`.bands`, `.pdos_bin`, `.castep`, `.cell`, `.den_fmt` ou `CHGCAR`). Os arquivos **não saem do seu computador**: tudo roda no navegador. A aba **Sobre** e a seção **Sobre o Bruma** trazem o autor e a citação.

### C2. Linha de comando no cluster

**Opção 1, sem instalar:** copie o script e use o Python do cluster.

```bash
scp bruma.py usuario@cluster:~/                  # do seu computador
ssh usuario@cluster
module load python                               # se o cluster usar módulos
python3 -m pip install --user numpy matplotlib   # uma vez, se faltar
cd /caminho/do/calculo
python3 ~/bruma.py mgh2_Fe -e Mg,H,Fe
```

**Opção 2, instalado:** quando o Bruma estiver no PyPI (Parte E).

```bash
python3 -m pip install --user bruma-dft
export PATH="$HOME/.local/bin:$PATH"             # ponha no ~/.bashrc
bruma mgh2_Fe -e Mg,H,Fe
```

**Em fila (SLURM/PBS):** use os exemplos da pasta `examples/`.

```bash
sbatch slurm_bruma.sh mgh2_Fe                    # SLURM
qsub -v SEED=mgh2_Fe pbs_bruma.sh                # PBS/Torque
```

O `castep_depois_bruma.sh` roda o CASTEP e o Bruma em sequência no mesmo job.

**Trazer os resultados** (no seu computador):

```bash
rsync -av usuario@cluster:/caminho/do/calculo/mgh2_Fe_plots ./
```

**Comandos úteis:**

| Comando | Faz |
|---|---|
| `bruma mgh2_Fe` | análise completa (bandas, DOS, PDOS, análise, defeito, densidade se houver) |
| `bruma mgh2_Fe --ref mgh2_puro` | defeito com a estrutura pura de referência |
| `bruma mgh2_Fe --gerar-referencias` | gera os `.cell`/`.param` das referências |
| `bruma mgh2_Fe --planes todos --vesta --subtract mgh2_puro.den_fmt --diff-sign puro-defeito` | densidade, galeria de planos e pacote VESTA com Δρ |
| `bruma --sobre` | autor, links e como citar |
| `bruma -h` | todas as opções |

Sem o pacote instalado, troque `bruma` por `python3 bruma.py`.

### C3. Interface gráfica

**Instalar e abrir:**

```bash
pip install "bruma-dft[gui]"                     # ou: pip install numpy matplotlib pillow
bruma-gui                                        # ou: python3 bruma_gui.py
```

- **Linux:** se aparecer *No module named tkinter*, instale o `python3-tk` (`sudo apt install python3-tk`).
- **macOS e Windows:** o Python de python.org já inclui o Tkinter.

**Na janela:**

1. **Análise:** escolha a pasta, o cálculo e as etapas, e clique em **Executar análise**. O botão **Ver comando** mostra o comando equivalente para o cluster.
2. **Resultados:** lista e prévia das figuras. Um clique duplo abre o arquivo (Origin, VESTA, editor).
3. **Sobre:** autor, foto, redes e citação com botões de copiar.

### C4. Windows (instalador)

1. Baixe o `Bruma-Setup-<versão>.exe` em <https://github.com/brunohdmacedo/bruma-dft/releases/latest>.
2. Execute. Se aparecer **"O Windows protegeu o computador"** (o programa não é assinado digitalmente), clique em **Mais informações → Executar assim mesmo**.
3. Escolha os atalhos e, se quiser, a opção de colocar o comando `bruma` no PATH.
4. Abra o **Bruma** pelo menu Iniciar. A linha de comando fica em `C:\Program Files\Bruma\cli\bruma.exe`.

---

## Parte D: programa para Windows

Um `.exe` de Windows precisa ser compilado **num Windows**. Há três caminhos.

### D1. Pelo GitHub Actions, com uma versão publicada (recomendado)

```bash
git tag v1.0.0
git push --tags
```

O workflow `windows.yml` roda numa máquina Windows do GitHub:

1. instala o Python e as dependências;
2. baixa a sua foto do Lattes e a embute no programa;
3. compila o `Bruma.exe` (janela) e o `bruma.exe` (linha de comando) com o PyInstaller;
4. testa o `bruma.exe --versao` e o `bruma.exe --sobre`;
5. monta o `Bruma-Setup-<versão>.exe` com o Inno Setup;
6. publica os três arquivos em **Releases**.

Acompanhe em **Actions → Windows (.exe e instalador)**. Leva cerca de 5 a 10 minutos.

### D2. Pelo GitHub Actions, sem publicar versão (para testar)

Em **Actions → Windows (.exe e instalador) → Run workflow**. Ao terminar, baixe o zip **Bruma-Windows** em *Artifacts*, na página da execução.

### D3. No seu Windows

1. Instale o Python e, para gerar o instalador, o Inno Setup 6 (<https://jrsoftware.org/isdl.php>).
2. Dê dois cliques em `packaging\windows\build_windows.bat`.
3. Os arquivos aparecem em `dist\`.

### D4. Assinatura digital (opcional)

O aviso do SmartScreen some quando o programa é assinado com um certificado de *code signing*. Há serviços gratuitos para projetos de código aberto, como o SignPath Foundation; certificados comerciais são pagos. Sem assinatura, o programa funciona normalmente, com o aviso descrito em C4.

---

## Parte E: PyPI e DOI no Zenodo

### E1. Publicar no PyPI (para `pip install bruma-dft`)

**Automático, recomendado (Trusted Publishing, sem senha):**

1. Crie a conta em <https://pypi.org> e ative a verificação em duas etapas.
2. Em **Your account → Publishing → Add a new pending publisher**, preencha:
   - PyPI project name: `bruma-dft`;
   - Owner: `brunohdmacedo`;
   - Repository: `bruma-dft`;
   - Workflow: `pypi.yml`;
   - Environment: `pypi`.
3. No GitHub, crie o ambiente em **Settings → Environments → New environment**, com o nome `pypi`.
4. A cada **Release** publicada (D1), o workflow `pypi.yml` envia a versão ao PyPI.

**Manual:**

```bash
python -m pip install --upgrade build twine
python -m build                  # cria dist/*.whl e dist/*.tar.gz
python -m twine upload dist/*    # usuário: __token__ ; senha: o token do PyPI
```

Para ensaiar antes, publique no TestPyPI (`twine upload -r testpypi dist/*`).

### E2. DOI para cada versão (Zenodo)

Um DOI torna o Bruma citável como software em artigos, no TCC e na dissertação.

1. Entre em <https://zenodo.org> com a conta do GitHub.
2. Em **(seu nome) → GitHub**, ative o repositório `bruma-dft`.
3. Publique uma Release (D1). O Zenodo arquiva a versão e gera um DOI.
4. Copie o DOI. Acrescente `doi: "10.5281/zenodo.XXXXXXX"` ao `CITATION.cff`, `doi = {10.5281/zenodo.XXXXXXX}` à entrada `macedo2026bruma` do `bruma.bib`, e o selo de DOI do Zenodo ao topo do `README.md`.

O Zenodo dá um DOI por versão e também um *concept DOI*, que aponta sempre para a mais recente. Para citar o software em geral, use o concept DOI.

---

## Parte F: documentos em LaTeX

| Documento | Arquivos |
|---|---|
| Tutorial do Bruma | `bruma-tutorial.tex` + `bruma.bib` + `img/` |
| Este manual | `docs/manual/manual-bruma.tex` + `docs/manual/img/` |

### F1. Compilar no seu computador

Os dois documentos usam **XeLaTeX** (por causa do português com o `polyglossia`):

```bash
xelatex bruma-tutorial
bibtex  bruma-tutorial
xelatex bruma-tutorial
xelatex bruma-tutorial
```

Para o manual, que não usa BibTeX:

```bash
cd docs/manual
xelatex manual-bruma
xelatex manual-bruma
```

### F2. Compilar no Overleaf

1. **New Project → Upload Project** e envie um zip com o `.tex`, o `.bib` e a pasta `img/`.
2. **Menu → Compiler → XeLaTeX**.
3. Clique em **Recompile**.

### F3. Regerar o manual a partir do Markdown

A fonte deste manual é o `docs/MANUAL.md` (a versão do GitHub). Para atualizar o LaTeX e o PDF depois de editá-lo:

```bash
cd docs/manual
bash gerar_manual.sh             # pandoc + xelatex
```

### F4. Citar no TCC e na dissertação

Inclua as entradas do `bruma.bib` no seu `.bib` e use `\cite{macedo2026bruma}` (software), `\cite{macedo2025tcc}` (TCC), `\cite{macedo2024rbic}` (artigo) e `\cite{macedo2024dataset}` (base de dados). Com o **abnTeX2**, as mesmas entradas funcionam; para o TCC, troque `@misc` por `@monography` com `type = {Trabalho de Conclusão de Curso}`, se o seu modelo pedir.

Antes de usar, confira os campos marcados com **CONFIRA** nos comentários do `bruma.bib`: o título e o ano da dissertação, e o nome completo do coautor do trabalho de 2025.

---

## Parte G: logo

| Arquivo | Uso |
|---|---|
| `bruma-mark.svg` | símbolo (ícones, avatar, slides) |
| `bruma-mark-pequeno.svg` | símbolo simplificado para 16–32 px (favicon) |
| `bruma-logo-escuro.svg` / `.png` | logo horizontal para fundo escuro |
| `bruma-logo-claro.svg` / `.png` | logo horizontal para fundo claro (documentos, pôsteres) |
| `bruma-16.png` … `bruma-1024.png` | ícone em vários tamanhos |
| `bruma.ico` | ícone do Windows (16–256 px) |

**Significado:**

- **linhas onduladas:** bandas de valência (ciano) e de condução (violeta), como camadas de névoa;
- **linha âmbar tracejada:** o nível de Fermi;
- **ponto âmbar:** um estado de defeito no gap.

**Cores:**

| Cor | Código |
|---|---|
| fundo | `#070C0B` |
| ciano | `#4FE3C1` |
| âmbar | `#F5B544` |
| violeta | `#8B7CF6` |

A fonte é a Space Grotesk 600, a mesma do site. Ela já está convertida em contornos nos SVG.

**Regerar PNG e ICO depois de editar um SVG:**

```bash
inkscape bruma-mark.svg -w 256 -h 256 -o bruma-256.png          # um tamanho
magick bruma-16.png bruma-24.png bruma-32.png bruma-48.png bruma-64.png bruma-128.png bruma-256.png bruma.ico
```

Sem o ImageMagick, use o Pillow:

```python
from PIL import Image
ims = [Image.open(f"bruma-{s}.png") for s in (16, 24, 32, 48, 64, 128, 256)]
ims[-1].save("bruma.ico", sizes=[im.size for im in ims])
```

---

## Parte H: manutenção e novas versões

### H1. Lançar uma versão nova do Bruma (roteiro)

1. Faça as mudanças no código e teste: `python3 bruma.py <seed>`, `python3 bruma_gui.py` e o `index.html` no navegador.
2. Troque a versão em todos os arquivos de uma vez:
   ```bash
   python3 tools/versao.py            # mostra a versão atual em cada arquivo
   python3 tools/versao.py 1.1.0      # aplica a 1.1.0 e a data de hoje
   ```
3. Recompile o tutorial (F1) e copie o PDF para a raiz e para `docs/`.
4. Envie e publique:
   ```bash
   git commit -am "Versão 1.1.0"
   git tag v1.1.0
   git push
   git push --tags
   ```
   Isso gera o Windows (D1), o PyPI (E1, se configurado) e o DOI (E2, se configurado).
5. Atualize o site (B3):
   ```bash
   bash tools/copiar_para_site.sh ../brunohdmacedo.github.io
   ```

Use **versionamento semântico**:

| Mudança | Exemplo |
|---|---|
| correção | 1.0.0 → 1.0.1 |
| recurso novo compatível | 1.0.0 → 1.1.0 |
| mudança que quebra o uso antigo | 1.0.0 → 2.0.0 |

### H2. Mudar os seus dados (foto, links, afiliação)

| Dado | Onde mudar |
|---|---|
| Nome, afiliação, links, foto, citação (linha de comando e janela) | `bruma.py`: constantes `AUTOR`, `AFILIACAO`, `LINKS`, `FOTO_URL`, `CITACAO_ABNT`, `CITACAO_BIBTEX` |
| Mesmos dados na versão web | `index.html` do Bruma: objetos `AUTOR` e `BRUMA` e a constante `BIB_BRUMA` (procure por "Sobre o Bruma") |
| Texto da janela (afiliação e pesquisa na aba Sobre) | `bruma_gui.py`: função `_build_about` |
| Site pessoal | `index.html` da raiz do site (A3) |
| Citações | `bruma.bib`, `CITATION.cff` |

A **foto** vem do Lattes (`FOTO_URL`). Se você trocar a foto no Lattes, todas as versões passam a mostrar a nova; o instalador do Windows só a atualiza na próxima compilação.

### H3. Cópias de segurança

O GitHub guarda todo o histórico. Mesmo assim, de tempos em tempos, baixe um zip de cada repositório (**Code → Download ZIP**) e guarde junto com os seus cálculos.

---

## Parte I: solução de problemas

| Problema | Causa provável | Solução |
|---|---|---|
| O site não mudou depois do push | publicação em andamento ou cache | veja a aba **Actions**; recarregue com Ctrl+F5 |
| "There isn't a GitHub Pages site here" | Pages desativado | **Settings → Pages → Source** (A2) |
| Domínio perdeu o HTTPS | `CNAME` apagado | restaure o `CNAME` com `brunohdmacedo.tech` |
| Citações não aparecem no site | workflow nunca rodou | **Actions → Atualizar citações → Run workflow** (A5) |
| O workflow de citações falha no push | token sem permissão de escrita | **Settings → Actions → General → Read and write** |
| Só aparecem números do OpenAlex | `SERPAPI_KEY` ausente ou cota esgotada | confira o secret; veja `avisos` em `data/citacoes.json` |
| `No module named tkinter` | Tk não instalado | `sudo apt install python3-tk` (Linux) |
| `bruma: command not found` | `~/.local/bin` fora do PATH | `export PATH="$HOME/.local/bin:$PATH"` |
| Erro de display no cluster | matplotlib tentando abrir janela | `export MPLBACKEND=Agg` (o Bruma já usa Agg) |
| "O Windows protegeu o computador" | programa sem assinatura digital | **Mais informações → Executar assim mesmo** (D4) |
| O workflow do Windows falhou no Inno Setup | instalação do Chocolatey falhou | rode de novo (**Re-run jobs**) |
| Foto aparece como "BM" | sem internet ou Lattes fora do ar | normal; a foto aparece quando houver conexão |
| `xelatex` reclama de `polyglossia` | TeX incompleto | instale o TeX Live completo ou use o Overleaf |
| Referência "??" no PDF | BibTeX não rodou | rode `xelatex → bibtex → xelatex → xelatex` |
| `pip install bruma-dft` não acha o pacote | ainda não publicado no PyPI | Parte E1, ou use `bruma.py` direto |

---

## Apêndice: comandos rápidos e mapa de arquivos

### Comandos rápidos

```bash
# Site
cd brunohdmacedo.github.io && git add -A && git commit -m "…" && git push
python3 -m http.server 8000                          # testar localmente

# Bruma: análise
python3 bruma.py mgh2_Fe -e Mg,H,Fe                  # cluster
python3 bruma_gui.py                                 # janela
python3 bruma.py --sobre                             # autor e citação

# Bruma: manutenção
python3 tools/versao.py 1.1.0                        # nova versão em todos os arquivos
bash tools/copiar_para_site.sh ../brunohdmacedo.github.io
git tag v1.1.0 && git push --tags                    # Windows, PyPI e DOI

# LaTeX
xelatex bruma-tutorial && bibtex bruma-tutorial && xelatex bruma-tutorial && xelatex bruma-tutorial
```

### Mapa do repositório `bruma-dft`

```
bruma-dft/
├── bruma.py                     linha de comando (motor de análise)
├── bruma_gui.py                 interface gráfica (Tkinter)
├── index.html · tutorial.html   versão web e tutorial
├── bruma-tutorial.tex / .pdf    tutorial em LaTeX/PDF
├── bruma.bib · CITATION.cff     citações
├── pyproject.toml               pacote PyPI (comandos bruma e bruma-gui)
├── requirements.txt
├── assets/                      logo e ícones
├── img/ · docs/img/             figuras
├── docs/MANUAL.md               este manual (GitHub)
├── docs/manual/                 este manual em LaTeX e PDF
├── examples/                    jobs SLURM e PBS
├── tools/versao.py              troca a versão em todos os arquivos
├── tools/copiar_para_site.sh    copia a versão web para o site
├── packaging/windows/           Inno Setup (bruma.iss) e build_windows.bat
└── .github/workflows/           windows.yml (exe) e pypi.yml (PyPI)
```

### Mapa do repositório do site

```
brunohdmacedo.github.io/
├── index.html                   página principal
├── site/js/main.js              animações e texto digitado
├── site/js/citacoes.js          citações automáticas
├── data/citacoes.json           gerado pelo workflow (não editar à mão)
├── scripts/atualizar_citacoes.py
├── .github/workflows/citacoes.yml
├── bruma/                       cópia da versão web do Bruma
├── castep/                      redirecionamento para /bruma/
├── CITACOES.md · MANUAL.md      guias
├── sitemap.xml · robots.txt · CNAME
└── (páginas e pastas antigas mantidas: v1, v2, v3, portfolio, project-*, 1/, 2/, 3/, robenedet/, cs/…)
```

---

*Bruma 1.0.0 · Bruno Henrique Dourado Macedo · <https://brunohdmacedo.tech/bruma/> · ORCID 0000-0002-8152-0950*
