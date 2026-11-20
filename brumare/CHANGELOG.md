# Histórico de versões

## 1.3.0 — novembro de 2026
- **Aba Zona de Brillouin** (site, aplicativo e `--zona-brillouin` na linha de comando): 1.ª zona por construção de Wigner–Seitz, tipo de rede pela forma da zona com tolerância de simetria, pontos e caminhos de Setyawan–Curtarolo, malhas Monkhorst–Pack e entradas prontas para CASTEP, VASP, Quantum ESPRESSO e SIESTA.
- **Simetria e estruturas:** grupo espacial, Wyckoff e células padronizadas pelo moyo (spglib) no site e no Python; leitura de CIF, POSCAR, .cell, XSF, QE e XYZ; biblioteca com 51 materiais da literatura; busca no COD; todas as 14 redes de Bravais (25 casos de Setyawan–Curtarolo), conferidas ponto a ponto contra o pymatgen.
- **Interface modernizada:** abas com ícones, notificações, tela de boas-vindas e atalhos de teclado (tecla ?).
- **PDF de teoria completa** (`docs/teoria/teoria-brumare.pdf`).
- **Bader com refinamento das bordas** (near-grid; Tang, Sanville e Henkelman, 2009): diferença média para o pybader cai de 0,013 para 0,0008 e por átomo. Na linha de comando é o padrão; o navegador mantém a atribuição on-grid, mais rápida.
- **Correção do gap:** tesoura (Δ informado ou gap de referência) e modelo empírico PBE → G₀W₀ (Morales-García, Valero e Illas, 2017), no site, no aplicativo e na linha de comando.
- **Nível de Fermi:** energias originais por padrão, com linha traço-ponto e valor de E_F; a opção E − E_F continua disponível.
- **Quantum ESPRESSO e ORCA:** leitura de `data-file-schema.xml` e de saídas `.out` (moléculas, com gap HOMO–LUMO e cálculos com spin).
- **Formatos de figura:** PNG, JPG, JXL (JPEG XL, sem perdas idêntico ao PNG), WEBP, SVG e "todos" (.zip); `--format` aceita vários e `--qualidade` ajusta JPG/WEBP/JXL.
- **Seis idiomas:** interface, tutorial (página e PDF), portfólio e ajuda `-h` em português, inglês, espanhol, francês, italiano e latim.
- **Testes automatizados** (pytest, 80 testes) e **comparação com pymatgen, sumo, sisl, cclib e pybader** (`tools/comparar_ferramentas.py`), executados por integração contínua.
- Nome oficial **BrUMaRe** (Brillouin-zone Utilities for Materials Research) e nova logo.

## 1.2.0
- Aplicativo de computador (mesma interface do site, offline), instalador para Windows e pacote `pip install brumare`.
- Leitura de VASP e SIESTA; comparação entre cálculos de programas diferentes; citação automática (.bib).

## 1.1.0 e anteriores
- Ferramenta web e script Python para CASTEP: bandas, DOS, PDOS, bandas projetadas, defeitos, termodinâmica e densidade de carga.
