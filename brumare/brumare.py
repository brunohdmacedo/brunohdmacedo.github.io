#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##############################################################################
#  BrUMaRe 1.3.0  -  Brillouin-zone Utilities for Materials Research          #
#  Bandas, DOS, PDOS, densidade de carga, defeitos e termodinamica a partir  #
#  de calculos CASTEP, VASP e SIESTA.                                        #
#                                                                            #
#  Autor: Bruno Henrique Dourado Macedo (UNILA, PPGFISA)                     #
#         https://brunohdmacedo.tech  ·  ORCID 0000-0002-8152-0950           #
#  Site e tutorial: https://brunohdmacedo.tech/brumare/                      #
#  Codigo-fonte:    https://github.com/brunohdmacedo/brumare                 #
#                                                                            #
#  SPDX-License-Identifier: GPL-3.0-or-later                                 #
#  Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo                     #
#  Este programa e software livre: voce pode redistribui-lo e/ou modifica-lo #
#  sob os termos da GNU General Public License, versao 3 ou posterior. Ele e #
#  distribuido SEM QUALQUER GARANTIA. Veja o arquivo LICENSE.                #
#  O nome BrUMaRe e a logo identificam a versao oficial do autor.            #
##############################################################################
import argparse
import glob
import os
import re
import json
import struct
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")                      # cluster: sem display
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# --------------------------------------------------------------------------- #
#                         IDENTIFICACAO DO PROGRAMA                           #
# --------------------------------------------------------------------------- #
NOME = "BrUMaRe"
SUBTITULO = "Brillouin-zone Utilities for Materials Research"
VERSAO = "1.3.0"
DESCRICAO = "Brillouin-zone Utilities for Materials Research: bandas, DOS, PDOS, densidade de carga, defeitos e termodinâmica a partir de cálculos CASTEP, VASP e SIESTA"
AUTOR = "Bruno Henrique Dourado Macedo"
AFILIACAO = "Engenheiro Físico (UNILA) e mestrando em Física Aplicada (PPGFISA/UNILA), bolsista CNPq"
FOTO_URL = "https://wwws.cnpq.br/cvlattesweb/pkg_util_img.show_foto?v_cod=K4494050P3"
LINKS = [("Site", "https://brunohdmacedo.tech/"), ("BrUMaRe", "https://brunohdmacedo.tech/brumare/"),
         ("Codigo-fonte", "https://github.com/brunohdmacedo/brumare"), ("Lattes", "http://lattes.cnpq.br/7842985016416991"),
         ("ORCID", "https://orcid.org/0000-0002-8152-0950"), ("Google Academico", "https://scholar.google.com/citations?user=zl-LdTMAAAAJ&hl=pt-BR"),
         ("LinkedIn", "https://bit.ly/3VlPBAE"), ("GitHub", "https://bit.ly/47dlUt0"), ("YouTube", "https://bit.ly/3HGUTDW"),
         ("Instagram", "https://bit.ly/465SETR"), ("E-mail", "mailto:brunohdmacedo@gmail.com")]
LICENCA = "GPL-3.0-or-later"
LICENCA_URL = "https://www.gnu.org/licenses/gpl-3.0.html"
COPYRIGHT = "Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo"
# Frase do autor: sempre em latim, em qualquer idioma escolhido.
FRASE = ("«Scientia, bonum commune generis humani, ab hominibus nata est ut universam naturam describeret: "
         "quod ab omnibus creatur, omnibus reddendum est. Docere est liberare; discere ius est, non privilegium. "
         "Ab unoquoque secundum facultates suas, unicuique secundum necessitates suas — sic et scientia.» "
         "— Bruno Macedo")
RODAPE = ("BrUMaRe é um software open e seu uso deve ser citado - desenvolvimento por Macedo B.H.D. - "
          "Dissertação de Mestrado em Física Aplicada pela PPGFISA UNILA.")
CITACAO_ABNT = ("MACEDO, B. H. D. BrUMaRe: Brillouin-zone Utilities for Materials Research — análise de estrutura de bandas, "
                "DOS, PDOS, densidade de carga, defeitos e termodinâmica a partir de cálculos CASTEP, VASP e SIESTA. Versão "
                + VERSAO + ". Foz do Iguaçu, 2026. Software livre (GPL-3.0). Disponível em: https://brunohdmacedo.tech/brumare/.")
CITACAO_BIBTEX = """@misc{macedo2026brumare,
  author       = {Macedo, Bruno Henrique Dourado},
  title        = {{BrUMaRe}: {Brillouin-zone Utilities for Materials Research} --- análise de estrutura de bandas, {DOS}, {PDOS}, densidade de carga, defeitos e termodinâmica a partir de cálculos {CASTEP}, {VASP} e {SIESTA}},
  year         = {2026},
  version      = {""" + VERSAO + """},
  howpublished = {\\url{https://brunohdmacedo.tech/brumare/}},
  note         = {Software livre (GPL-3.0-or-later). Código-fonte: \\url{https://github.com/brunohdmacedo/brumare}}
}"""
CITACAO_CASTEP = "S. J. Clark et al., Z. Kristallogr. 220, 567-570 (2005), doi:10.1524/zkri.220.5.567.65075"
CITACAO_VASP = "G. Kresse e J. Furthmuller, Phys. Rev. B 54, 11169 (1996), doi:10.1103/PhysRevB.54.11169"
CITACAO_SIESTA = "J. M. Soler et al., J. Phys.: Condens. Matter 14, 2745 (2002), doi:10.1088/0953-8984/14/11/302"
CITACAO_PROGRAMAS = [("CASTEP", CITACAO_CASTEP), ("VASP", CITACAO_VASP), ("SIESTA", CITACAO_SIESTA)]
BIB_PROGRAMAS = {
    "CASTEP": """@article{clark2005castep,
  author  = {Clark, Stewart J. and Segall, Matthew D. and Pickard, Chris J. and Hasnip, Phil J. and Probert, Matt I. J. and Refson, Keith and Payne, Mike C.},
  title   = {First principles methods using {CASTEP}},
  journal = {Zeitschrift f{\\"u}r Kristallographie},
  volume  = {220},
  number  = {5--6},
  pages   = {567--570},
  year    = {2005},
  doi     = {10.1524/zkri.220.5.567.65075}
}""",
    "VASP": """@article{kresse1996vasp,
  author  = {Kresse, G. and Furthm{\\"u}ller, J.},
  title   = {Efficient iterative schemes for \\textit{ab initio} total-energy calculations using a plane-wave basis set},
  journal = {Physical Review B},
  volume  = {54},
  number  = {16},
  pages   = {11169--11186},
  year    = {1996},
  doi     = {10.1103/PhysRevB.54.11169}
}""",
    "SIESTA": """@article{soler2002siesta,
  author  = {Soler, Jos{\\'e} M. and Artacho, Emilio and Gale, Julian D. and Garc{\\'i}a, Alberto and Junquera, Javier and Ordej{\\'o}n, Pablo and S{\\'a}nchez-Portal, Daniel},
  title   = {The {SIESTA} method for \\textit{ab initio} order-{N} materials simulation},
  journal = {Journal of Physics: Condensed Matter},
  volume  = {14},
  number  = {11},
  pages   = {2745--2779},
  year    = {2002},
  doi     = {10.1088/0953-8984/14/11/302}
}""",
}
AGRADECIMENTO = "Agradecimento a Benedet, R. O. - sem ela, isso nunca teria acontecido."


def banner():
    print(f" {NOME} {VERSAO}  ·  {DESCRICAO}")
    print(f" {AUTOR}  ·  brunohdmacedo.tech/brumare  ·  como citar: {os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else 'brumare'} --sobre")

# Textos do software em 6 idiomas (a frase do autor fica sempre no original). Escolha: --idioma ou BRUMARE_LANG.
IDIOMAS = ("pt", "en", "es", "fr", "it", "la")
TXT = {
    "rodape": {"pt": RODAPE,
               "en": "BrUMaRe is open software and its use must be cited - developed by Macedo B.H.D. - Master's Dissertation in Applied Physics at PPGFISA UNILA.",
               "es": "BrUMaRe es un software abierto y su uso debe ser citado - desarrollo por Macedo B.H.D. - Disertación de Maestría en Física Aplicada por el PPGFISA UNILA.",
               "fr": "BrUMaRe est un logiciel ouvert et son utilisation doit être citée - développement par Macedo B.H.D. - Mémoire de Master en Physique Appliquée au PPGFISA UNILA.",
               "it": "BrUMaRe è un software open e il suo uso deve essere citato - sviluppo di Macedo B.H.D. - Tesi di Laurea Magistrale in Fisica Applicata presso il PPGFISA UNILA.",
               "la": "BrUMaRe est programma apertum et usus eius citandus est - elaboratum a Macedo B.H.D. - Dissertatio Magistralis in Physica Applicata apud PPGFISA UNILA."},
    "agradecimento": {"pt": "Agradecimento a Benedet, R. O. - sem ela, isso nunca teria acontecido.",
                      "en": "Acknowledgment to Benedet, R. O. - without her, this would never have happened.",
                      "es": "Agradecimiento a Benedet, R. O. - sin ella, esto nunca habría sucedido.",
                      "fr": "Remerciements à Benedet, R. O. - sans elle, cela ne serait jamais arrivé.",
                      "it": "Ringraziamento a Benedet, R. O. - senza di lei, tutto questo non sarebbe mai accaduto.",
                      "la": "Gratiae Benedet, R. O. - sine ea, hoc numquam accidisset."},
    "autor": {"pt": "Autor", "en": "Author", "es": "Autor", "fr": "Auteur", "it": "Autore", "la": "Auctor"},
    "como_citar": {"pt": "Como citar (ABNT)", "en": "How to cite (ABNT)", "es": "Cómo citar (ABNT)", "fr": "Comment citer (ABNT)", "it": "Come citare (ABNT)", "la": "Quomodo citare (ABNT)"},
    "cite_prog": {"pt": "Cite também o programa usado no cálculo:", "en": "Also cite the code used for the calculation:", "es": "Cite también el programa usado en el cálculo:",
                  "fr": "Citez aussi le code utilisé pour le calcul :", "it": "Cita anche il programma usato nel calcolo:", "la": "Cita etiam programma in computatione adhibitum:"},
    "licenca": {"pt": "Licença", "en": "License", "es": "Licencia", "fr": "Licence", "it": "Licenza", "la": "Licentia"},
    "sem_garantia": {"pt": "Software livre, sem garantia. O nome BrUMaRe e a logo identificam a versão oficial.",
                     "en": "Free software, without warranty. The name BrUMaRe and the logo identify the official version.",
                     "es": "Software libre, sin garantía. El nombre BrUMaRe y el logo identifican la versión oficial.",
                     "fr": "Logiciel libre, sans garantie. Le nom BrUMaRe et le logo identifient la version officielle.",
                     "it": "Software libero, senza garanzia. Il nome BrUMaRe e il logo identificano la versione ufficiale.",
                     "la": "Programma liberum, sine cautione. Nomen BrUMaRe et signum versionem officialem designant."},
    "titulo_citar": {"pt": "COMO CITAR", "en": "HOW TO CITE", "es": "CÓMO CITAR", "fr": "COMMENT CITER", "it": "COME CITARE", "la": "QUOMODO CITARE"},
    "software": {"pt": "Software:", "en": "Software:", "es": "Software:", "fr": "Logiciel :", "it": "Software:", "la": "Programma:"},
    "programas": {"pt": "Programa(s) de cálculo:", "en": "Calculation code(s):", "es": "Programa(s) de cálculo:", "fr": "Code(s) de calcul :", "it": "Programma/i di calcolo:", "la": "Programma(ta) computationis:"},
    "metodos": {"pt": "Métodos usados nesta análise:", "en": "Methods used in this analysis:", "es": "Métodos usados en este análisis:", "fr": "Méthodes utilisées dans cette analyse :", "it": "Metodi usati in questa analisi:", "la": "Methodi in hac analysi adhibiti:"},
    "bib_completo": {"pt": "BibTeX completo", "en": "Full BibTeX", "es": "BibTeX completo", "fr": "BibTeX complet", "it": "BibTeX completo", "la": "BibTeX integrum"},
}
LANG = {"v": (os.environ.get("BRUMARE_LANG") or "pt")[:2].lower()}


def t(chave):
    d = TXT[chave]
    return d.get(LANG["v"]) or d["pt"]


BIB_METODOS = {
    'tang2009': ('refinamento das bordas de Bader (near-grid)', """@article{tang2009bader,
  author  = {Tang, W. and Sanville, E. and Henkelman, G.},
  title   = {A grid-based {Bader} analysis algorithm without lattice bias},
  journal = {Journal of Physics: Condensed Matter},
  volume  = {21},
  number  = {8},
  pages   = {084204},
  year    = {2009},
  doi     = {10.1088/0953-8984/21/8/084204}
}"""),
    'morales2017': ('modelo empírico PBE->G0W0 de correção do gap', """@article{morales2017,
  author  = {Morales-Garc{\\'i}a, {\\'A}ngel and Valero, Rosendo and Illas, Francesc},
  title   = {An Empirical, yet Practical Way To Predict the Band Gap in Solids by Using Density Functional Band Structure Calculations},
  journal = {The Journal of Physical Chemistry C},
  volume  = {121},
  number  = {34},
  pages   = {18862--18866},
  year    = {2017},
  doi     = {10.1021/acs.jpcc.7b07421}
}"""),
    'henkelman2006': ('partição de Bader (on-grid)', '@article{henkelman2006,\n  author  = {Henkelman, Graeme and Arnaldsson, Andri and Jónsson, Hannes},\n  title   = {A fast and robust algorithm for {Bader} decomposition of charge density},\n  journal = {Computational Materials Science},\n  volume  = {36},\n  number  = {3},\n  pages   = {354--360},\n  year    = {2006},\n  doi     = {10.1016/j.commatsci.2005.04.010},\n}'),
    'setyawan2010': ('caminho de alta simetria na zona de Brillouin', '@article{setyawan2010,\n  author  = {Setyawan, Wahyu and Curtarolo, Stefano},\n  title   = {High-throughput electronic band structure calculations: Challenges and tools},\n  journal = {Computational Materials Science},\n  volume  = {49},\n  number  = {2},\n  pages   = {299--312},\n  year    = {2010},\n  doi     = {10.1016/j.commatsci.2010.05.010},\n}'),
    'voronoi1908': ('cargas por átomo (células de Voronoi)', '@article{voronoi1908,\n  author  = {Voronoi, Georges},\n  title   = {Nouvelles applications des paramètres continus à la théorie des formes quadratiques. {Deuxième} mémoire},\n  journal = {Journal für die reine und angewandte Mathematik},\n  volume  = {134},\n  pages   = {198--287},\n  year    = {1908},\n  doi     = {10.1515/crll.1908.134.198},\n}'),
    'momma2011vesta': ('visualização no VESTA', '@article{momma2011vesta,\n  author  = {Momma, Koichi and Izumi, Fujio},\n  title   = {{VESTA 3} for three-dimensional visualization of crystal, volumetric and morphology data},\n  journal = {Journal of Applied Crystallography},\n  volume  = {44},\n  number  = {6},\n  pages   = {1272--1276},\n  year    = {2011},\n  doi     = {10.1107/S0021889811038970},\n}'),
    'robinson1971': ('distorção do poliedro de coordenação (⟨λ⟩, σ²)', '@article{robinson1971,\n  author  = {Robinson, Keith and Gibbs, Gerald V. and Ribbe, Paul H.},\n  title   = {Quadratic Elongation: A Quantitative Measure of Distortion in Coordination Polyhedra},\n  journal = {Science},\n  volume  = {172},\n  number  = {3983},\n  pages   = {567--570},\n  year    = {1971},\n  doi     = {10.1126/science.172.3983.567},\n}'),
    'mulliken1955': ('população de Mulliken', '@article{mulliken1955,\n  author  = {Mulliken, Robert S.},\n  title   = {Electronic Population Analysis on {LCAO--MO} Molecular Wave Functions. {I}},\n  journal = {The Journal of Chemical Physics},\n  volume  = {23},\n  number  = {10},\n  pages   = {1833--1840},\n  year    = {1955},\n  doi     = {10.1063/1.1740588},\n}'),
    'segall1996': ('Mulliken em base de ondas planas', '@article{segall1996,\n  author  = {Segall, Matthew D. and Shah, Rickesh and Pickard, Chris J. and Payne, Mike C.},\n  title   = {Population analysis of plane-wave electronic structure calculations of bulk materials},\n  journal = {Physical Review B},\n  volume  = {54},\n  number  = {23},\n  pages   = {16317--16320},\n  year    = {1996},\n  doi     = {10.1103/PhysRevB.54.16317},\n}'),
}
USADOS = set()          # métodos efetivamente usados nesta execução (entram no .bib final)


def write_citation(outdir, base, programas):
    """.bib e texto ABNT com o BrUMaRe, o(s) programa(s) de cálculo e os métodos usados nesta execução."""
    os.makedirs(outdir, exist_ok=True)
    progs = [p for p in ("CASTEP", "VASP", "SIESTA") if p in programas]
    partes = [f"% Citações geradas pelo {NOME} {VERSAO} ({SUBTITULO})", f"% Execução: {base}. Cite o {NOME} e o(s) programa(s) de cálculo.", "", CITACAO_BIBTEX]
    partes += [BIB_PROGRAMAS[p] for p in progs]
    met = [k for k in BIB_METODOS if k in USADOS]
    if met:
        partes.append("% Métodos usados nesta análise")
        partes += [BIB_METODOS[k][1] for k in met]
    fb = os.path.join(outdir, f"{base}_citacao.bib")
    open(fb, "w", encoding="utf-8").write("\n\n".join(partes) + "\n")
    txt = [f"{t('titulo_citar')} ({NOME} {VERSAO})", "=" * 72, "", t('software'), "  " + CITACAO_ABNT, ""]
    if progs:
        txt += [t('programas')] + [f"  {p}: {dict(CITACAO_PROGRAMAS)[p]}" for p in progs] + [""]
    if met:
        txt += [t('metodos')] + [f"  {BIB_METODOS[k][0]} [{k}]" for k in met] + [""]
    txt += [f"{t('bib_completo')}: {os.path.basename(fb)}", "", "-" * 72, FRASE, "", t('rodape')]
    open(os.path.join(outdir, f"{base}_como_citar.txt"), "w", encoding="utf-8").write("\n".join(txt) + "\n")
    print(f" -> {fb}  (cite o {NOME}" + (" e o " + ", ".join(progs) if progs else "") + ")")


AJUDA_I18N = """
seedname (ex: mgh2_Fe) ou o arquivo .bands. Se omitido, procura um .bands na pasta atual ¦ seedname (e.g. mgh2_Fe) or the .bands file. If omitted, looks for a .bands in the current folder ¦ seedname (ej.: mgh2_Fe) o el archivo .bands. Si se omite, busca un .bands en la carpeta actual ¦ seedname (ex. : mgh2_Fe) ou le fichier .bands. Si omis, cherche un .bands dans le dossier courant ¦ seedname (es.: mgh2_Fe) o il file .bands. Se omesso, cerca un .bands nella cartella corrente ¦ seedname (e.g. mgh2_Fe) vel fasciculus .bands. Si omittitur, .bands in capsa praesenti quaeritur
mostra autor, links e como citar o BrUMaRe, e sai ¦ shows author, links and how to cite BrUMaRe, and exits ¦ muestra autor, enlaces y cómo citar BrUMaRe, y sale ¦ affiche l’auteur, les liens et comment citer BrUMaRe, puis quitte ¦ mostra autore, link e come citare BrUMaRe, ed esce ¦ auctorem, nexus et modum citandi BrUMaRe ostendit, et exit
idioma do --sobre, do rodapé e do como_citar.txt: pt, en, es, fr, it ou la (latim) ¦ language of --sobre, the footer, como_citar.txt and this help: pt, en, es, fr, it or la (Latin) ¦ idioma de --sobre, del pie de página, de como_citar.txt y de esta ayuda: pt, en, es, fr, it o la (latín) ¦ langue de --sobre, du pied de page, de como_citar.txt et de cette aide : pt, en, es, fr, it ou la (latin) ¦ lingua di --sobre, del piè di pagina, di como_citar.txt e di questo aiuto: pt, en, es, fr, it o la (latino) ¦ lingua --sobre, pedis paginae, como_citar.txt et huius auxilii: pt, en, es, fr, it vel la (Latina)
compara calculos de qualquer programa (seeds do CASTEP/SIESTA ou pastas do VASP), como a aba Comparacao do site ¦ compares calculations from any code (CASTEP/SIESTA seeds or VASP folders), like the Comparison tab of the site ¦ compara cálculos de cualquier programa (seeds de CASTEP/SIESTA o carpetas de VASP), como la pestaña Comparación del sitio ¦ compare des calculs de tout code (seeds CASTEP/SIESTA ou dossiers VASP), comme l’onglet Comparaison du site ¦ confronta calcoli di qualsiasi programma (seed di CASTEP/SIESTA o cartelle di VASP), come la scheda Confronto del sito ¦ computationes cuiusvis programmatis comparat (seeds CASTEP/SIESTA vel capsae VASP), ut tabula Comparatio situs
nao mostra o cabecalho com nome e autor ¦ does not show the header with name and author ¦ no muestra el encabezado con nombre y autor ¦ n’affiche pas l’en-tête avec le nom et l’auteur ¦ non mostra l’intestazione con nome e autore ¦ caput cum nomine et auctore non ostendit
arquivo .cell (padrao: <seed>.cell) ¦ .cell file (default: <seed>.cell) ¦ archivo .cell (por defecto: <seed>.cell) ¦ fichier .cell (par défaut : <seed>.cell) ¦ file .cell (predefinito: <seed>.cell) ¦ fasciculus .cell (praefinitum: <seed>.cell)
arquivo .pdos_bin (padrao: <seed>.pdos_bin) ¦ .pdos_bin file (default: <seed>.pdos_bin) ¦ archivo .pdos_bin (por defecto: <seed>.pdos_bin) ¦ fichier .pdos_bin (par défaut : <seed>.pdos_bin) ¦ file .pdos_bin (predefinito: <seed>.pdos_bin) ¦ fasciculus .pdos_bin (praefinitum: <seed>.pdos_bin)
elementos para PDOS, ex: Mg,H,Fe (padrao: todos) ¦ elements for the PDOS, e.g. Mg,H,Fe (default: all) ¦ elementos para la PDOS, ej.: Mg,H,Fe (por defecto: todos) ¦ éléments pour la PDOS, ex. : Mg,H,Fe (par défaut : tous) ¦ elementi per la PDOS, es.: Mg,H,Fe (predefinito: tutti) ¦ elementa pro PDOS, e.g. Mg,H,Fe (praefinitum: omnia)
seedname de um calculo de DOS separado (malha MP densa). Padrao: usa o mesmo do .bands ¦ seedname of a separate DOS calculation (dense MP mesh). Default: the same as the .bands ¦ seedname de un cálculo de DOS separado (malla MP densa). Por defecto: el mismo del .bands ¦ seedname d’un calcul de DOS séparé (grille MP dense). Par défaut : le même que le .bands ¦ seedname di un calcolo di DOS separato (griglia MP densa). Predefinito: lo stesso del .bands ¦ seedname computationis DOS separatae (reticulum MP densum). Praefinitum: idem ac .bands
alargamento gaussiano da DOS (eV) ¦ Gaussian broadening of the DOS (eV) ¦ ensanchamiento gaussiano de la DOS (eV) ¦ élargissement gaussien de la DOS (eV) ¦ allargamento gaussiano della DOS (eV) ¦ dilatatio Gaussiana DOS (eV)
passo da DOS (eV) ¦ DOS step (eV) ¦ paso de la DOS (eV) ¦ pas de la DOS (eV) ¦ passo della DOS (eV) ¦ gradus DOS (eV)
referencia de energia: 'original' (padrao) = energias do programa, sem deslocar, com linha traco-ponto em E_F; 'spin' = E - E_F de cada canal; 'up'/'down'/'mean' = E - E_F comum; 'none' = energias absolutas sem linha de E_F rotulada ¦ energy reference: 'original' (default) = code energies, unshifted, with a dash-dot line at E_F; 'spin' = E - E_F of each channel; 'up'/'down'/'mean' = E - common E_F; 'none' = absolute energies without a labeled E_F line ¦ referencia de energía: 'original' (por defecto) = energías del programa, sin desplazar, con línea de trazo y punto en E_F; 'spin' = E - E_F de cada canal; 'up'/'down'/'mean' = E - E_F común; 'none' = energías absolutas sin línea de E_F rotulada ¦ référence d’énergie : 'original' (par défaut) = énergies du code, non décalées, avec une ligne tiret-point à E_F ; 'spin' = E - E_F de chaque canal ; 'up'/'down'/'mean' = E - E_F commun ; 'none' = énergies absolues sans ligne de E_F étiquetée ¦ riferimento di energia: 'original' (predefinito) = energie del programma, non traslate, con linea tratto-punto a E_F; 'spin' = E - E_F di ogni canale; 'up'/'down'/'mean' = E - E_F comune; 'none' = energie assolute senza linea di E_F etichettata ¦ relatio energiae: 'original' (praefinitum) = energiae programmatis, non translatae, cum linea ductus-puncti ad E_F; 'spin' = E - E_F cuiusque canalis; 'up'/'down'/'mean' = E - E_F communis; 'none' = energiae absolutae sine linea E_F inscripta
rotulos dos pontos k, ex: G,X,M,G,Z,R,A,Z ¦ k-point labels, e.g. G,X,M,G,Z,R,A,Z ¦ etiquetas de los puntos k, ej.: G,X,M,G,Z,R,A,Z ¦ étiquettes des points k, ex. : G,X,M,G,Z,R,A,Z ¦ etichette dei punti k, es.: G,X,M,G,Z,R,A,Z ¦ tituli punctorum k, e.g. G,X,M,G,Z,R,A,Z
png, pdf, svg, eps... ¦ png, pdf, svg, eps... ¦ png, pdf, svg, eps... ¦ png, pdf, svg, eps... ¦ png, pdf, svg, eps... ¦ png, pdf, svg, eps...
pasta de saida (padrao: <seed>_plots) ¦ output folder (default: <seed>_plots) ¦ carpeta de salida (por defecto: <seed>_plots) ¦ dossier de sortie (par défaut : <seed>_plots) ¦ cartella di output (predefinito: <seed>_plots) ¦ capsa exitus (praefinitum: <seed>_plots)
arquivo .castep (ordem dos orbitais e camadas; padrao: <seed>.castep) ¦ .castep file (orbital and shell order; default: <seed>.castep) ¦ archivo .castep (orden de orbitales y capas; por defecto: <seed>.castep) ¦ fichier .castep (ordre des orbitales et couches ; par défaut : <seed>.castep) ¦ file .castep (ordine di orbitali e strati; predefinito: <seed>.castep) ¦ fasciculus .castep (ordo orbitalium et stratorum; praefinitum: <seed>.castep)
PDOS de atomos individuais, ex: Fe1,H23,Mg5 ¦ PDOS of individual atoms, e.g. Fe1,H23,Mg5 ¦ PDOS de átomos individuales, ej.: Fe1,H23,Mg5 ¦ PDOS d’atomes individuels, ex. : Fe1,H23,Mg5 ¦ PDOS di atomi singoli, es.: Fe1,H23,Mg5 ¦ PDOS atomorum singulorum, e.g. Fe1,H23,Mg5
nao gerar bandas projetadas (fat bands) ¦ do not produce projected bands (fat bands) ¦ no generar bandas proyectadas (fat bands) ¦ ne pas produire les bandes projetées (fat bands) ¦ non generare bande proiettate (fat bands) ¦ fascias proiectas (fat bands) non generare
espessura maxima das fat bands (pt) ¦ maximum width of the fat bands (pt) ¦ grosor máximo de las fat bands (pt) ¦ épaisseur maximale des fat bands (pt) ¦ spessore massimo delle fat bands (pt) ¦ crassitudo maxima fasciarum proiectarum (pt)
grava a DOS de spin down com sinal negativo nos .dat ¦ writes the spin-down DOS with negative sign in the .dat files ¦ escribe la DOS de espín down con signo negativo en los .dat ¦ écrit la DOS de spin down avec un signe négatif dans les .dat ¦ scrive la DOS di spin down con segno negativo nei .dat ¦ DOS spin deorsum signo negativo in .dat scribit
seed da estrutura PURA (sem defeito) para mapear atomos e deslocamentos ¦ seed of the PURE structure (no defect) to map atoms and displacements ¦ seed de la estructura PURA (sin defecto) para mapear átomos y desplazamientos ¦ seed de la structure PURE (sans défaut) pour apparier atomes et déplacements ¦ seed della struttura PURA (senza difetto) per mappare atomi e spostamenti ¦ seed structurae PURAE (sine vitio) ad atomos et translationes describendos
centro da analise: rotulo (Fe1, H25) ou 'x y z' fracionario. Padrao: automatico ¦ analysis center: label (Fe1, H25) or fractional 'x y z'. Default: automatic ¦ centro del análisis: etiqueta (Fe1, H25) o 'x y z' fraccionario. Por defecto: automático ¦ centre de l’analyse : étiquette (Fe1, H25) ou 'x y z' fractionnaire. Par défaut : automatique ¦ centro dell’analisi: etichetta (Fe1, H25) o 'x y z' frazionario. Predefinito: automatico ¦ centrum analysis: titulus (Fe1, H25) vel 'x y z' fractum. Praefinitum: automaticum
1a camada = d_min x fator ¦ 1st shell = d_min x factor ¦ 1.ª capa = d_min x factor ¦ 1re couche = d_min x facteur ¦ 1° strato = d_min x fattore ¦ strata prima = d_min x factor
raio fixo da 1a camada (A); 0 = automatico ¦ fixed 1st-shell radius (A); 0 = automatic ¦ radio fijo de la 1.ª capa (A); 0 = automático ¦ rayon fixe de la 1re couche (A) ; 0 = automatique ¦ raggio fisso del 1° strato (A); 0 = automatico ¦ radius fixus stratae primae (A); 0 = automaticum
distancia minima ao centro para o 'bulk' (A); 0 = automatico ¦ minimum distance from the center for the 'bulk' (A); 0 = automatic ¦ distancia mínima al centro para el 'bulk' (A); 0 = automático ¦ distance minimale au centre pour le « massif » (A) ; 0 = automatique ¦ distanza minima dal centro per il 'bulk' (A); 0 = automatico ¦ distantia minima a centro pro 'massa' (A); 0 = automaticum
potenciais quimicos em eV/atomo, ex: 'Mg=-975.3,Fe=@fe_bcc,H=@h2' (@seed le o .castep) ¦ chemical potentials in eV/atom, e.g. 'Mg=-975.3,Fe=@fe_bcc,H=@h2' (@seed reads the .castep) ¦ potenciales químicos en eV/átomo, ej.: 'Mg=-975.3,Fe=@fe_bcc,H=@h2' (@seed lee el .castep) ¦ potentiels chimiques en eV/atome, ex. : 'Mg=-975.3,Fe=@fe_bcc,H=@h2' (@seed lit le .castep) ¦ potenziali chimici in eV/atomo, es.: 'Mg=-975.3,Fe=@fe_bcc,H=@h2' (@seed legge il .castep) ¦ potentialia chimica in eV/atomum, e.g. 'Mg=-975.3,Fe=@fe_bcc,H=@h2' (@seed .castep legit)
energia total usada (auto: estimativa a 0 K nos metais, Final energy nos demais) ¦ total energy used (auto: 0 K estimate for metals, Final energy otherwise) ¦ energía total usada (auto: estimación a 0 K en metales, Final energy en los demás) ¦ énergie totale utilisée (auto : estimation à 0 K pour les métaux, Final energy sinon) ¦ energia totale usata (auto: stima a 0 K nei metalli, Final energy negli altri) ¦ energia tota adhibita (auto: aestimatio ad 0 K in metallis, Final energy in ceteris)
escreve .cell/.param da estrutura pura, sem H (perto e longe) e das referencias elementares ¦ writes .cell/.param of the pure structure, without H (near and far) and of the elemental references ¦ escribe .cell/.param de la estructura pura, sin H (cerca y lejos) y de las referencias elementales ¦ écrit les .cell/.param de la structure pure, sans H (près et loin) et des références élémentaires ¦ scrive .cell/.param della struttura pura, senza H (vicino e lontano) e dei riferimenti elementari ¦ .cell/.param structurae purae, sine H (prope et procul) et relationum elementarium scribit
arquivo de densidade (padrao: <seed>.den_fmt ou <seed>.cube, se existir) ¦ density file (default: <seed>.den_fmt or <seed>.cube, if present) ¦ archivo de densidad (por defecto: <seed>.den_fmt o <seed>.cube, si existe) ¦ fichier de densité (par défaut : <seed>.den_fmt ou <seed>.cube, s’il existe) ¦ file di densità (predefinito: <seed>.den_fmt o <seed>.cube, se esiste) ¦ fasciculus densitatis (praefinitum: <seed>.den_fmt vel <seed>.cube, si adest)
rho total, up/down (rho de cada spin), spin (up-down), absm (|up-down|), zeta ((up-down)/rho) ou diff ¦ total rho, up/down (rho of each spin), spin (up-down), absm (|up-down|), zeta ((up-down)/rho) or diff ¦ rho total, up/down (rho de cada espín), spin (up-down), absm (|up-down|), zeta ((up-down)/rho) o diff ¦ rho totale, up/down (rho de chaque spin), spin (up-down), absm (|up-down|), zeta ((up-down)/rho) ou diff ¦ rho totale, up/down (rho di ogni spin), spin (up-down), absm (|up-down|), zeta ((up-down)/rho) o diff ¦ rho tota, up/down (rho cuiusque spin), spin (up-down), absm (|up-down|), zeta ((up-down)/rho) vel diff
cargas e momentos por atomo (particao de Voronoi) ¦ charges and moments per atom (Voronoi partition) ¦ cargas y momentos por átomo (partición de Voronoi) ¦ charges et moments par atome (partition de Voronoï) ¦ cariche e momenti per atomo (partizione di Voronoi) ¦ onera et momenta per atomum (partitio Voronoi)
para --field diff: densidades a subtrair, ex: 'a.den_fmt,b.den_fmt' ¦ for --field diff: densities to subtract, e.g. 'a.den_fmt,b.den_fmt' ¦ para --field diff: densidades a restar, ej.: 'a.den_fmt,b.den_fmt' ¦ pour --field diff : densités à soustraire, ex. : 'a.den_fmt,b.den_fmt' ¦ per --field diff: densità da sottrarre, es.: 'a.den_fmt,b.den_fmt' ¦ pro --field diff: densitates subtrahendae, e.g. 'a.den_fmt,b.den_fmt'
corte 2D: tres atomos 'Fe1,H30,H68' ou 'hkl:0 0 1@Fe1' (padrao: centro e 2 vizinhos) ¦ 2D slice: three atoms 'Fe1,H30,H68' or 'hkl:0 0 1@Fe1' (default: center and 2 neighbors) ¦ corte 2D: tres átomos 'Fe1,H30,H68' o 'hkl:0 0 1@Fe1' (por defecto: centro y 2 vecinos) ¦ coupe 2D : trois atomes 'Fe1,H30,H68' ou 'hkl:0 0 1@Fe1' (par défaut : centre et 2 voisins) ¦ sezione 2D: tre atomi 'Fe1,H30,H68' o 'hkl:0 0 1@Fe1' (predefinito: centro e 2 vicini) ¦ sectio 2D: tres atomi 'Fe1,H30,H68' vel 'hkl:0 0 1@Fe1' (praefinitum: centrum et 2 vicini)
lado do corte 2D (A) ¦ side of the 2D slice (A) ¦ lado del corte 2D (A) ¦ côté de la coupe 2D (A) ¦ lato della sezione 2D (A) ¦ latus sectionis 2D (A)
galeria de planos pelo defeito, ex: '1 1 0; -1 1 0; 0 0 1' ou 'todos' ¦ gallery of planes through the defect, e.g. '1 1 0; -1 1 0; 0 0 1' or 'todos' (all) ¦ galería de planos por el defecto, ej.: '1 1 0; -1 1 0; 0 0 1' o 'todos' ¦ galerie de plans par le défaut, ex. : '1 1 0; -1 1 0; 0 0 1' ou 'todos' (tous) ¦ galleria di piani per il difetto, es.: '1 1 0; -1 1 0; 0 0 1' o 'todos' (tutti) ¦ pinacotheca planorum per vitium, e.g. '1 1 0; -1 1 0; 0 0 1' vel 'todos' (omnia)
indices (h k l) da celula base detectada (padrao, ex.: rutilo) ou da supercelula ¦ (h k l) indices of the detected base cell (default, e.g. rutile) or of the supercell ¦ índices (h k l) de la celda base detectada (por defecto, ej.: rutilo) o de la supercelda ¦ indices (h k l) de la maille de base détectée (par défaut, ex. : rutile) ou de la supermaille ¦ indici (h k l) della cella base rilevata (predefinito, es.: rutilo) o della supercella ¦ indices (h k l) cellulae basis detectae (praefinitum, e.g. rutilum) vel supercellulae
perfil entre dois atomos, ex: 'Fe1,H30' (padrao: centro e vizinho mais proximo) ¦ profile between two atoms, e.g. 'Fe1,H30' (default: center and nearest neighbor) ¦ perfil entre dos átomos, ej.: 'Fe1,H30' (por defecto: centro y vecino más cercano) ¦ profil entre deux atomes, ex. : 'Fe1,H30' (par défaut : centre et plus proche voisin) ¦ profilo tra due atomi, es.: 'Fe1,H30' (predefinito: centro e vicino più prossimo) ¦ profilum inter duos atomos, e.g. 'Fe1,H30' (praefinitum: centrum et vicinus proximus)
exporta a densidade para .xsf (VESTA/XCrySDen) ¦ exports the density to .xsf (VESTA/XCrySDen) ¦ exporta la densidad a .xsf (VESTA/XCrySDen) ¦ exporte la densité en .xsf (VESTA/XCrySDen) ¦ esporta la densità in .xsf (VESTA/XCrySDen) ¦ densitatem in .xsf exportat (VESTA/XCrySDen)
exporta a densidade como CHGCAR (VASP 5, com elementos) para o VESTA, como o den2vasp ¦ exports the density as CHGCAR (VASP 5, with elements) for VESTA, like den2vasp ¦ exporta la densidad como CHGCAR (VASP 5, con elementos) para VESTA, como den2vasp ¦ exporte la densité en CHGCAR (VASP 5, avec les éléments) pour VESTA, comme den2vasp ¦ esporta la densità come CHGCAR (VASP 5, con elementi) per VESTA, come den2vasp ¦ densitatem ut CHGCAR (VASP 5, cum elementis) pro VESTA exportat, sicut den2vasp
exporta para o VESTA (CHGCAR VASP 5) rho, rho_up, rho_down, spin e, com --subtract, as diferencas de cada um ¦ exports to VESTA (CHGCAR VASP 5) rho, rho_up, rho_down, spin and, with --subtract, the differences of each ¦ exporta a VESTA (CHGCAR VASP 5) rho, rho_up, rho_down, spin y, con --subtract, las diferencias de cada uno ¦ exporte vers VESTA (CHGCAR VASP 5) rho, rho_up, rho_down, spin et, avec --subtract, les différences de chacun ¦ esporta per VESTA (CHGCAR VASP 5) rho, rho_up, rho_down, spin e, con --subtract, le differenze di ciascuno ¦ ad VESTA exportat (CHGCAR VASP 5) rho, rho_up, rho_down, spin et, cum --subtract, differentias singulorum
raio maximo (A) do perfil radial da diferenca de densidade ¦ maximum radius (A) of the radial profile of the density difference ¦ radio máximo (A) del perfil radial de la diferencia de densidad ¦ rayon maximal (A) du profil radial de la différence de densité ¦ raggio massimo (A) del profilo radiale della differenza di densità ¦ radius maximus (A) profili radialis differentiae densitatis
sentido das diferencas (--field diff e --vesta) ¦ sign of the differences (--field diff and --vesta) ¦ sentido de las diferencias (--field diff y --vesta) ¦ sens des différences (--field diff et --vesta) ¦ verso delle differenze (--field diff e --vesta) ¦ sensus differentiarum (--field diff et --vesta)
com --chgcar e --field rho: inclui a densidade de spin como 2o bloco ¦ with --chgcar and --field rho: includes the spin density as a 2nd block ¦ con --chgcar y --field rho: incluye la densidad de espín como 2.º bloque ¦ avec --chgcar et --field rho : inclut la densité de spin comme 2e bloc ¦ con --chgcar e --field rho: include la densità di spin come 2° blocco ¦ cum --chgcar et --field rho: densitatem spin ut alterum caudicem includit
entropia de dessorcao (J/mol K) para T_d = dH/dS ¦ desorption entropy (J/mol K) for T_d = dH/dS ¦ entropía de desorción (J/mol K) para T_d = dH/dS ¦ entropie de désorption (J/mol K) pour T_d = dH/dS ¦ entropia di desorbimento (J/mol K) per T_d = dH/dS ¦ entropia desorptionis (J/mol K) pro T_d = dH/dS
seed da estrutura com H a menos (energia de remocao de H) ¦ seed of the structure with one H less (H removal energy) ¦ seed de la estructura con un H menos (energía de remoción de H) ¦ seed de la structure avec un H en moins (énergie de retrait de H) ¦ seed della struttura con un H in meno (energia di rimozione di H) ¦ seed structurae uno H minus (energia remotionis H)
nao fazer a analise de defeito ¦ skip the defect analysis ¦ no hacer el análisis de defecto ¦ ne pas faire l’analyse du défaut ¦ non eseguire l’analisi del difetto ¦ analysin vitii omittere
nao escrever <seed>_up.bands / <seed>_down.bands ¦ do not write <seed>_up.bands / <seed>_down.bands ¦ no escribir <seed>_up.bands / <seed>_down.bands ¦ ne pas écrire <seed>_up.bands / <seed>_down.bands ¦ non scrivere <seed>_up.bands / <seed>_down.bands ¦ <seed>_up.bands / <seed>_down.bands non scribere
defeito e termodinamica ¦ defect and thermodynamics ¦ defecto y termodinámica ¦ défaut et thermodynamique ¦ difetto e termodinamica ¦ vitium et thermodynamica
densidade de carga (.den_fmt ou .cube) ¦ charge density (.den_fmt, .cube, CHGCAR or .RHO) ¦ densidad de carga (.den_fmt, .cube, CHGCAR o .RHO) ¦ densité de charge (.den_fmt, .cube, CHGCAR ou .RHO) ¦ densità di carica (.den_fmt, .cube, CHGCAR o .RHO) ¦ densitas oneris (.den_fmt, .cube, CHGCAR vel .RHO)
@@usage ¦ usage ¦ uso ¦ utilisation ¦ uso ¦ usus
@@positional ¦ positional arguments ¦ argumentos posicionales ¦ arguments positionnels ¦ argomenti posizionali ¦ argumenta positionalia
@@options ¦ options ¦ opciones ¦ options ¦ opzioni ¦ optiones
@@help ¦ show this help message and exit ¦ muestra esta ayuda y sale ¦ affiche cette aide et quitte ¦ mostra questo aiuto ed esce ¦ hoc auxilium ostendit et exit
@@version ¦ show the version and exit ¦ muestra la versión y sale ¦ affiche la version et quitte ¦ mostra la versione ed esce ¦ versionem ostendit et exit
@@desc ¦ Brillouin-zone Utilities for Materials Research: bands, DOS, PDOS, charge density, defects and thermodynamics from CASTEP, VASP and SIESTA calculations ¦ Brillouin-zone Utilities for Materials Research: bandas, DOS, PDOS, densidad de carga, defectos y termodinámica a partir de cálculos de CASTEP, VASP y SIESTA ¦ Brillouin-zone Utilities for Materials Research : bandes, DOS, PDOS, densité de charge, défauts et thermodynamique à partir de calculs CASTEP, VASP et SIESTA ¦ Brillouin-zone Utilities for Materials Research: bande, DOS, PDOS, densità di carica, difetti e termodinamica da calcoli CASTEP, VASP e SIESTA ¦ Brillouin-zone Utilities for Materials Research: fasciae, DOS, PDOS, densitas oneris, vitia et thermodynamica ex computationibus CASTEP, VASP et SIESTA
"""


def _ajuda_traduzida(p):
    """Traduz a ajuda (-h) para LANG['v'] (en, es, fr, it, la); a fonte é o português."""
    lg = LANG["v"]
    if lg == "pt" or lg not in IDIOMAS:
        return
    k = IDIOMAS.index(lg) - 1
    tab = {}
    for linha in AJUDA_I18N.strip().splitlines():
        c = [x.strip() for x in linha.split(" ¦ ")]
        tab[c[0]] = c[1:]
    for act in p._actions:
        if act.help in tab:
            act.help = tab[act.help][k].replace("%", "%%")
        elif act.dest == "help":
            act.help = tab["@@help"][k]
        elif act.dest == "version":
            act.help = tab["@@version"][k]
    for g in p._action_groups:
        if g.title in tab:
            g.title = tab[g.title][k]
        elif g.title in ("positional arguments",):
            g.title = tab["@@positional"][k]
        elif g.title in ("options", "optional arguments"):
            g.title = tab["@@options"][k]
    p.description = f"{NOME} {VERSAO}: {tab['@@desc'][k]}. {AUTOR}."
    uso = tab["@@usage"][k]

    class _F(p.formatter_class):
        def add_usage(self, usage, actions, groups, prefix=None):
            return super().add_usage(usage, actions, groups, prefix=uso + ": ")
    p.formatter_class = _F


def sobre_texto():
    L = [f"{NOME} {VERSAO}", "=" * 72, DESCRICAO if LANG["v"] == "pt" else f"{SUBTITULO}: bands, DOS, PDOS, charge density, defects and thermodynamics (CASTEP, VASP, SIESTA)", "",
         f"{t('autor')}: {AUTOR}", f"       {AFILIACAO}", "",
         "Links:"] + [f"  {n:<17}{u}" for n, u in LINKS] + ["",
         f"{t('como_citar')}:", "  " + CITACAO_ABNT, "", "BibTeX:", CITACAO_BIBTEX, "",
         t('cite_prog')] + [f"  {n:<7} {c}" for n, c in CITACAO_PROGRAMAS] + ["",
         f"{t('licenca')}: {LICENCA} ({LICENCA_URL}). {COPYRIGHT}.", t('sem_garantia'),
         "", "-" * 72, FRASE, "", t('rodape'), "", t('agradecimento')]
    return "\n".join(L)


HA2EV = 27.211386245988                    # CODATA 2018 (mesmo do CASTEP)
BOHR2ANG = 0.529177210903
ORB_NAMES = ["s", "p", "d", "f"]
COLORS = ["#CC33A7", "#A7CC33", "#33A7CC", "#E69F00", "#D55E00",
          "#0072B2", "#009E73", "#7F7F7F", "#8C564B", "#17BECF"]
ORB_COLORS = {"s": "#1f77b4", "p": "#d62728", "d": "#2ca02c", "f": "#9467bd"}
SPIN_TAG = {0: "up", 1: "down"}


# =========================================================================== #
#                                 LEITURA                                     #
# =========================================================================== #
def read_bands(fname):
    """Le o .bands. Retorna dict com energias em Hartree (sem nenhum shift)."""
    v = _virt(fname)
    if v is not None:
        return v
    with open(fname) as f:
        lines = f.readlines()
    hdr = {}
    i = 0
    while not lines[i].startswith("K-point"):
        l = lines[i]
        if l.startswith("Number of k-points"):
            hdr["nk"] = int(l.split()[-1])
        elif l.startswith("Number of spin components"):
            hdr["ns"] = int(l.split()[-1])
        elif l.startswith("Number of electrons"):
            hdr["nelec"] = [float(x) for x in l.split()[3:]]
        elif l.startswith("Number of eigenvalues"):
            hdr["neig"] = [int(x) for x in l.split()[3:]]
        elif l.startswith("Fermi energ"):
            hdr["efermi"] = [float(x) for x in l.split(")")[-1].split()]
        elif l.startswith("Unit cell vectors"):
            hdr["lattice"] = np.array([[float(x) for x in lines[i + j].split()]
                                       for j in (1, 2, 3)])
            i += 3
        i += 1
    nk, ns, nb = hdr["nk"], hdr["ns"], max(hdr["neig"])
    if len(hdr["efermi"]) == 1:
        hdr["efermi"] = hdr["efermi"] * ns
    kidx = np.zeros(nk, int)
    kfrac = np.zeros((nk, 3))
    kw = np.zeros(nk)
    eig = np.full((ns, nk, nb), np.nan)
    ik = -1
    while i < len(lines):
        l = lines[i]
        if l.startswith("K-point"):
            ik += 1
            p = l.split()
            kidx[ik] = int(p[1])
            kfrac[ik] = [float(x) for x in p[2:5]]
            kw[ik] = float(p[5])
            i += 1
        elif l.startswith("Spin component"):
            s = int(l.split()[-1]) - 1
            n = hdr["neig"][s]
            eig[s, ik, :n] = [float(lines[i + 1 + j]) for j in range(n)]
            i += n + 1
        else:
            i += 1
    order = np.argsort(kidx)                  # garante a ordem do caminho
    return dict(hdr=hdr, header_lines=lines[:lines.index(next(
        x for x in lines if x.startswith("K-point")))],
        kidx=kidx[order], kfrac=kfrac[order], kw=kw[order],
        eig=eig[:, order, :])


def read_cell_species(fname):
    """Especies na ordem de aparicao no bloco de posicoes (ordem do CASTEP)."""
    v = _virt(fname, "species")
    if v is not None:
        return list(v)
    species, inblock = [], False
    with open(fname) as f:
        for l in f:
            u = l.strip().upper()
            if u.startswith("%BLOCK") and "POSITIONS" in u:
                inblock = True
                continue
            if u.startswith("%ENDBLOCK") and "POSITIONS" in u:
                break
            if inblock and l.split() and not u.startswith(("ANG", "BOHR", "NM")):
                sp = l.split()[0].split(":")[0]    # aceita Fe:1 etc.
                if sp not in species:
                    species.append(sp)
    if not species:
        sys.exit(f"ERRO: nao encontrei POSITIONS_FRAC/ABS em {fname}")
    return species


def read_pdos_bin(fname):
    """Le o .pdos_bin (Fortran sequencial, big-endian)."""
    v = _virt(fname)
    if v is not None:
        return v
    with open(fname, "rb") as f:
        data = f.read()
    end = ">"
    if struct.unpack(">i", data[:4])[0] != 8:
        end = "<"
    pos = [0]

    def rec():
        n = struct.unpack(end + "i", data[pos[0]:pos[0] + 4])[0]
        b = data[pos[0] + 4:pos[0] + 4 + n]
        pos[0] += n + 8
        return b
    i4 = lambda b: np.frombuffer(b, end + "i4")
    rec(); rec()                                    # versao, cabecalho
    nk, ns, norb, maxe = [int(i4(rec())[0]) for _ in range(4)]
    sp, ion, am = i4(rec()).copy(), i4(rec()).copy(), i4(rec()).copy()
    kidx = np.zeros(nk, int)
    kfrac = np.zeros((nk, 3))
    w = np.zeros((ns, nk, maxe, norb))
    for ik in range(nk):
        # o indice gravado aponta para o 1o k-ponto IDENTICO (Gamma repetido = 1),
        # por isso a ordem correta e a do arquivo, conferida pelas coordenadas
        r = rec()
        kidx[ik] = struct.unpack(end + "i", r[:4])[0]
        kfrac[ik] = np.frombuffer(r[4:28], end + "f8")
        for _ in range(ns):
            s = int(i4(rec())[0]) - 1
            ne = int(i4(rec())[0])
            for ie in range(ne):
                w[s, ik, ie] = np.frombuffer(rec(), end + "f8")
    return dict(species=sp, ion=ion, am=am, w=w, kidx=kidx, kfrac=kfrac)


def align_k(B, P):
    """Reordena os pesos do .pdos_bin para a ordem dos k-pontos do .bands,
    casando pelas coordenadas. Retorna False se os k-pontos nao batem."""
    if P["w"].shape[1] != len(B["kfrac"]):
        return False
    used, order = set(), []
    for k, kb in enumerate(B["kfrac"]):
        cand = [k] + list(range(len(P["kfrac"])))
        r = next((j for j in cand if j not in used and
                  np.allclose(kb, P["kfrac"][j], atol=1e-5)), None)
        if r is None:
            return False
        used.add(r)
        order.append(r)
    P["w"] = P["w"][:, order]
    P["kfrac"] = P["kfrac"][order]
    return True


def read_castep_extra(fname):
    """Mulliken por atomo, ligacoes e informacoes gerais do .castep."""
    out = dict(mull=[], bonds=[], info={}, species=[])
    v = _virt(fname, "extra") if fname else None
    if v is not None:
        return v
    if not fname or not _vexists(fname):
        return out
    with open(fname, errors="replace") as f:
        L = f.read().splitlines()
    last = lambda pat: max([i for i, l in enumerate(L) if re.search(pat, l)], default=-1)
    k = last(r"Atomic Populations \(Mulliken\)")
    if k >= 0:
        bars, cur = 0, None
        for l in L[k:]:
            if re.match(r"^\s*=+\s*$", l):
                bars += 1
                if bars == 2:
                    break
                continue
            if bars != 1:
                continue
            t = l.split()
            if len(t) < 5:
                continue
            sp = t.pop(0) if re.match(r"^[A-Za-z]", t[0]) else None
            ion = int(t.pop(0))
            tag = t.pop(0).lower().rstrip(":") if t[0].lower() in ("up:", "dn:") else None
            v = [float(x) for x in t]
            if tag == "dn" and cur:
                cur["dn"] = v[:5]
                continue
            cur = dict(sp=sp or cur["sp"], ion=ion, up=v[:5], dn=None,
                       charge=v[5] if len(v) > 5 else float("nan"),
                       spin=v[6] if len(v) > 6 else 0.0)
            out["mull"].append(cur)
    k = last(r"Bond\s+Population")
    if k >= 0:
        for l in L[k + 1:]:
            m = re.match(r"^\s*([A-Za-z]+)\s+(\d+)\s+--\s+([A-Za-z]+)\s+(\d+)\s+(-?[\d.]+)\s+"
                         r"(?:(-?[\d.]+)\s+)?(-?[\d.]+)\s*$", l)
            if m:
                out["bonds"].append(dict(a=m[1] + m[2], b=m[3] + m[4], pop=float(m[5]),
                                         spin=float(m[6]) if m[6] else None, len=float(m[7])))
            elif out["bonds"] and re.match(r"^\s*=+\s*$", l):
                break
    k = next((i for i, l in enumerate(L) if "Cell Contents" in l), -1)
    if k >= 0:
        for l in L[k:k + 200000]:
            m = re.match(r"^\s*x\s+([A-Za-z]+)\s+\d+\s+-?[\d.]+\s+-?[\d.]+\s+-?[\d.]+\s+x", l)
            if m and m[1] not in out["species"]:
                out["species"].append(m[1])
            elif out["species"] and re.match(r"^\s*x+\s*$", l):
                break
    pats = dict(functional=r"using functional\s*:\s*(.+)$", cutoff=r"basis set cut-off\s*:\s*([-\d.]+)",
                volume=r"Current cell volume =\s*([-\d.]+)", energy=r"Final energy(?:, E)?\s*=\s*([-\d.E+]+)",
                spin=r"Integrated Spin Density\s*=\s*([-\d.E+]+)",
                abs_spin=r"Integrated \|Spin Density\|\s*=\s*([-\d.E+]+)")
    for key, pat in pats.items():
        for l in L:
            m = re.search(pat, l)
            if m:
                out["info"][key] = m[1].strip()
    return out


def band_edges(eig_ev, neig, nelec, ns, ef, dist, ticks, labels, kfrac):
    """VBM/CBM pela contagem de eletrons (banda N e N+1) e teste de E_F dentro
    de banda (tolerancia 5 meV). eig_ev: (nk, nb) em eV, absoluto."""
    lab = lambda k: next((labels[t] for t, x in enumerate(ticks) if abs(x - dist[k]) < 1e-6),
                         "(" + ", ".join(f"{v:.3f}" for v in kfrac[k]) + ")")
    E = eig_ev[:, :neig]
    inside = [(b, (np.nanmax(E[:, b]) - np.nanmin(E[:, b])) * 1000) for b in range(neig)
              if np.nanmin(E[:, b]) < ef - 0.005 and np.nanmax(E[:, b]) > ef + 0.005]
    ne = nelec / (2 if ns == 1 else 1)
    N = int(round(ne))
    if abs(ne - N) < 1e-6 and 1 <= N < neig:
        vk, ck = int(np.nanargmax(E[:, N - 1])), int(np.nanargmin(E[:, N]))
        vbm, cbm, vb, cb = E[vk, N - 1], E[ck, N], N - 1, N
    else:
        occ = np.where(E <= ef, E, -np.inf)
        emp = np.where(E > ef, E, np.inf)
        vk, vb = np.unravel_index(np.argmax(occ), E.shape)
        ck, cb = np.unravel_index(np.argmin(emp), E.shape)
        vbm, cbm = E[vk, vb], E[ck, cb]
    return dict(vbm=vbm, cbm=cbm, vb=vb, cb=cb, vk=int(vk), ck=int(ck), gap=cbm - vbm, vkl=lab(vk), ckl=lab(ck),
                direct=abs(dist[vk] - dist[ck]) < 1e-6, inside=inside)


def write_table(fn, comments, cols, data, fmt="%.6f"):
    """Tabela pronta para Origin/Excel: comentarios '#', 1 linha de nomes, TAB."""
    with open(fn, "w", encoding="utf-8") as f:
        for c in comments:
            f.write("# " + c + "\n")
        f.write("\t".join(cols) + "\n")
        np.savetxt(f, data, fmt=fmt, delimiter="\t")


# =========================================================================== #
#                         CAMINHO NO ESPACO K                                  #
# =========================================================================== #
def special_points(lat_ang):
    """Tabela de pontos especiais conforme o tipo de rede detectado."""
    a, b, c = np.linalg.norm(lat_ang, axis=1)
    ang = lambda u, v: np.degrees(np.arccos(np.dot(u, v) /
                                            np.linalg.norm(u) / np.linalg.norm(v)))
    al, be, ga = ang(lat_ang[1], lat_ang[2]), ang(lat_ang[0], lat_ang[2]), \
        ang(lat_ang[0], lat_ang[1])
    eq = lambda x, y: abs(x - y) / max(x, y) < 1e-2
    ortho = all(abs(x - 90) < 1.0 for x in (al, be, ga))
    G = {"\u0393": (0, 0, 0)}
    if ortho and eq(a, b) and eq(b, c):
        typ, P = "cubica", {"X": (0, .5, 0), "M": (.5, .5, 0), "R": (.5, .5, .5)}
    elif ortho and (eq(a, b) or eq(a, c) or eq(b, c)):
        u = 2 if eq(a, b) else (1 if eq(a, c) else 0)      # eixo unico
        base = {"X": (0, .5, 0), "M": (.5, .5, 0), "Z": (0, 0, .5),
                "R": (0, .5, .5), "A": (.5, .5, .5)}
        perm = {2: (0, 1, 2), 1: (0, 2, 1), 0: (2, 1, 0)}[u]
        P = {k: tuple(v[perm[j]] for j in range(3)) for k, v in base.items()}
        typ = "tetragonal"
    elif ortho:
        typ, P = "ortorrombica", {"X": (.5, 0, 0), "Y": (0, .5, 0), "Z": (0, 0, .5),
                                  "S": (.5, .5, 0), "U": (.5, 0, .5),
                                  "T": (0, .5, .5), "R": (.5, .5, .5)}
    elif eq(a, b) and abs(ga - 120) < 1.0 and abs(al - 90) < 1 and abs(be - 90) < 1:
        typ, P = "hexagonal", {"M": (.5, 0, 0), "K": (1 / 3, 1 / 3, 0),
                               "A": (0, 0, .5), "L": (.5, 0, .5),
                               "H": (1 / 3, 1 / 3, .5)}
    else:
        typ, P = "generica", {}
    G.update(P)
    return typ, G


def kpath(kfrac, lat_ang, user_labels=None):
    USADOS.add("setyawan2010")
    rec = 2 * np.pi * np.linalg.inv(lat_ang).T            # 1/Angstrom
    cart = kfrac @ rec
    step = np.linalg.norm(np.diff(cart, axis=0), axis=1)
    med = np.median(step[step > 1e-8]) if np.any(step > 1e-8) else 1.0
    jump = step > 4.0 * med                                # descontinuidades
    dist = np.concatenate([[0], np.cumsum(np.where(jump, 0.0, step))])

    # vertices: inicio, fim, mudanca de direcao, saltos
    vert = [0]
    for i in range(1, len(kfrac) - 1):
        if jump[i - 1] or jump[i]:
            vert.append(i)
            continue
        d1, d2 = cart[i] - cart[i - 1], cart[i + 1] - cart[i]
        n1, n2 = np.linalg.norm(d1), np.linalg.norm(d2)
        if n1 < 1e-8 or n2 < 1e-8 or np.dot(d1, d2) / n1 / n2 < 0.999:
            vert.append(i)
    vert.append(len(kfrac) - 1)
    vert = sorted(set(vert))

    typ, table = special_points(lat_ang)

    def name(k):
        kk = (np.asarray(k) + 0.5) % 1.0 - 0.5            # reduz para [-0.5,0.5)
        for lab, v in table.items():
            for sgn in (1, -1):
                if np.allclose(np.abs(kk), np.abs(sgn * np.array(v)), atol=2e-3):
                    return lab
        return "(" + ",".join(f"{x:g}" for x in np.round(k, 3)) + ")"

    ticks, labels = [], []
    for i in vert:
        lab = name(kfrac[i])
        if ticks and abs(dist[i] - ticks[-1]) < 1e-8:      # salto: "X|U"
            if labels[-1] != lab:
                labels[-1] = labels[-1] + "|" + lab
            continue
        ticks.append(dist[i])
        labels.append(lab)
    if user_labels:
        ul = [x.strip().replace("G", "\u0393") if x.strip() in ("G", "GAMMA", "Gamma")
              else x.strip() for x in user_labels.split(",")]
        if len(ul) == len(labels):
            labels = ul
        else:
            print(f"AVISO: --labels tem {len(ul)} rotulos mas o caminho tem "
                  f"{len(labels)} vertices; usando rotulos automaticos.")
    return dist, np.array(ticks), labels, typ


# =========================================================================== #
#                                   DOS                                       #
# =========================================================================== #
def gaussian_dos(energies, kw, weights, egrid, sigma):
    """DOS por binning + convolucao gaussiana (rapido e escalavel).
    energies (nk,nb) [eV]; weights (nk,nb,ng) ou None; retorna (ng+1, nE)."""
    de = egrid[1] - egrid[0]
    e = energies.ravel()
    ok = np.isfinite(e)
    idx = np.rint((e[ok] - egrid[0]) / de).astype(int)
    inside = (idx >= 0) & (idx < len(egrid))
    idx = idx[inside]
    wk = np.repeat(kw[:, None], energies.shape[1], axis=1).ravel()[ok][inside]
    cols = [wk]
    if weights is not None:
        W = weights.reshape(-1, weights.shape[-1])[ok][inside]
        cols += [wk * W[:, g] for g in range(W.shape[1])]
    hist = np.array([np.bincount(idx, c, minlength=len(egrid)) for c in cols])
    if sigma > 0:
        nker = int(np.ceil(5 * sigma / de))
        x = np.arange(-nker, nker + 1) * de
        ker = np.exp(-0.5 * (x / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        hist = np.array([np.convolve(h, ker, mode="same") for h in hist])
    else:
        hist /= de
    return hist


# =========================================================================== #
#                               ESCRITA .DAT                                  #
# =========================================================================== #
def write_split_bands(B, seed, outdir):
    """Escreve <seed>_up.bands e <seed>_down.bands com cabecalho correto
    (1 componente de spin, Fermi ORIGINAL de cada spin)."""
    h = B["hdr"]
    if h["ns"] != 2:
        return []
    out = []
    for s in (0, 1):
        fn = os.path.join(outdir, f"{seed}_{SPIN_TAG[s]}.bands")
        nb = h["neig"][s]
        with open(fn, "w") as f:
            for l in B["header_lines"]:
                if l.startswith("Number of spin components"):
                    l = "Number of spin components 1\n"
                elif l.startswith("Number of electrons"):
                    l = f"Number of electrons  {h['nelec'][s]:.1f}\n"
                elif l.startswith("Number of eigenvalues"):
                    l = f"Number of eigenvalues {nb:8d}\n"
                elif l.startswith("Fermi energ"):
                    l = f"Fermi energy (in atomic units) {h['efermi'][s]:12.6f}\n"
                f.write(l)
            for ik in range(len(B["kidx"])):
                k = B["kfrac"][ik]
                f.write(f"K-point {B['kidx'][ik]:8d} {k[0]:11.8f} {k[1]:11.8f} "
                        f"{k[2]:11.8f} {B['kw'][ik]:11.8f}\n")
                f.write("Spin component 1\n")
                for e in B["eig"][s, ik, :nb]:
                    f.write(f"{e:15.8f}\n")
        out.append(fn)
    return out


def write_bands_dat(fn, dist, E, ticks, labels, ef_ev, shifted, ref=0.0):
    nk, nb = E.shape
    write_table(fn, [f"E_F do CASTEP (sem alteracao) = {ef_ev:.6f} eV = {ef_ev / HA2EV:.6f} Ha",
                     f"Energias {'E - E_ref' if shifted else 'absolutas'} (eV); E_ref = {ref:.6f} eV",
                     "Pontos de alta simetria: " + "  ".join(f"{l}={t:.6f}" for l, t in zip(labels, ticks)),
                     "Origin: coluna 1 = eixo x (k); plote todas as outras colunas como Line"],
                ["k(1/A)"] + [f"banda{j + 1}" for j in range(nb)], np.column_stack([dist, E]))
    # formato em blocos (gnuplot / xmgrace): uma banda por bloco
    with open(fn.replace(".dat", "_blocos.dat"), "w") as f:
        f.write(f"# E_F = {ef_ev:.6f} eV ; colunas: k(1/A)  E(eV)\n")
        for j in range(nb):
            f.write(f"# banda {j + 1}\n")
            for i in range(nk):
                f.write(f"{dist[i]:12.6f} {E[i, j]:12.5f}\n")
            f.write("\n")


# =========================================================================== #
#                                 GRAFICOS                                    #
# =========================================================================== #
def style(base):
    plt.rcParams.update({
        "font.size": base, "axes.linewidth": 1.2, "axes.labelsize": base + 2,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.major.width": 1.2, "ytick.major.width": 1.2,
        "legend.frameon": True, "legend.framealpha": 0.9, "legend.edgecolor": "0.8", "savefig.bbox": "tight",
        "font.family": "DejaVu Sans", "mathtext.default": "regular"})


# Energia original no eixo: os dados ficam relativos a um E_F comum e o eixo mostra E = valor + E_F,
# com marcações em energias redondas e linha traço-ponto em E_F (padrão: --fermi-ref original).
EIXO = {"orig": False, "off": 0.0}


def linha_ef(ax, eixo, rotulo=True):
    """Linha de E_F (em 0 nos dados). Na energia original: traço-ponto com o valor de E_F."""
    if not EIXO["orig"]:
        (ax.axhline if eixo == "y" else ax.axvline)(0, color="gray", ls="--", lw=0.9)
        return
    ax._eixo_e = eixo
    (ax.axhline if eixo == "y" else ax.axvline)(0, color="#555555", ls="-.", lw=1.1)
    if rotulo:
        import matplotlib.transforms as mtr
        txt = rf"E$_F$ = {EIXO['off']:.3f} eV"
        if eixo == "y":
            ax.text(0.995, 0, txt, transform=mtr.blended_transform_factory(ax.transAxes, ax.transData),
                    ha="right", va="bottom", fontsize=8, color="#555555")
        else:
            ax.text(0, 0.98, " " + txt, transform=mtr.blended_transform_factory(ax.transData, ax.transAxes),
                    ha="left", va="top", fontsize=8, color="#555555")


def _eixo_original(fig):
    if not EIXO["orig"]:
        return
    from matplotlib.ticker import MaxNLocator
    off = EIXO["off"]
    for ax in fig.axes:
        e = getattr(ax, "_eixo_e", None)
        if not e:
            continue
        lo, hi = ax.get_ylim() if e == "y" else ax.get_xlim()
        ta = [t for t in MaxNLocator(nbins=8, steps=[1, 2, 2.5, 5, 10]).tick_values(lo + off, hi + off) if lo + off - 1e-9 <= t <= hi + off + 1e-9]
        pos, lab = [t - off for t in ta], [f"{t:g}" for t in ta]
        if e == "y":
            ax.set_yticks(pos); ax.set_yticklabels(lab); ax.set_ylim(lo, hi)
        else:
            ax.set_xticks(pos); ax.set_xticklabels(lab); ax.set_xlim(lo, hi)


_savefig_original = plt.Figure.savefig


# Formatos de imagem: --format aceita vários (png,jpg,jxl,webp,svg,pdf,eps,tif); cada figura sai em todos.
FMTS = {"lista": ["png"], "q": 100}
_AVISO_JXL = []


def _gravar_jxl(fig, caminho, kw):
    """JPEG XL via libjxl (imagecodecs): sem perdas com qualidade 100; senão distância visual da libjxl."""
    try:
        import imagecodecs
    except ImportError:
        if not _AVISO_JXL:
            print(" AVISO: para .jxl instale: pip install imagecodecs  (ou pip install \"brumare[jxl]\")")
            _AVISO_JXL.append(1)
        return None
    import io
    from PIL import Image
    buf = io.BytesIO()
    k = {x: v for x, v in kw.items() if x not in ("format", "pil_kwargs")}
    _savefig_original(fig, buf, format="png", **k)
    arr = np.asarray(Image.open(io.BytesIO(buf.getvalue())).convert("RGBA"))
    q = FMTS["q"]
    if q >= 100:
        dados = imagecodecs.jpegxl_encode(arr, lossless=True, effort=7)
    else:
        dist = 0.1 + (100 - q) * 0.09 if q >= 30 else 6.4 + (30 - q) ** 2 / 155   # escala de qualidade do cjxl
        dados = imagecodecs.jpegxl_encode(arr, distance=dist, effort=7)
    with open(caminho, "wb") as fh:
        fh.write(dados)
    return caminho


def _savefig(self, *args, **kw):
    _eixo_original(self)
    alvo = args[0] if args else kw.get("fname")
    if not isinstance(alvo, (str, os.PathLike)):
        return _savefig_original(self, *args, **kw)
    alvo = str(alvo); base, ext = os.path.splitext(alvo); ext = ext.lstrip(".").lower()
    lista = FMTS["lista"]
    destinos = [base + "." + f for f in lista] if ext == lista[0] else [alvo]
    res = None
    for d in destinos:
        e = os.path.splitext(d)[1].lstrip(".").lower()
        k = dict(kw); k.pop("fname", None)
        if e == "jxl":
            _gravar_jxl(self, d, k)
            continue
        if e in ("jpg", "jpeg", "webp"):
            k["pil_kwargs"] = dict(k.get("pil_kwargs") or {}, quality=min(FMTS["q"], 100))
            if e == "webp" and FMTS["q"] >= 100:
                k["pil_kwargs"]["lossless"] = True
        res = _savefig_original(self, d, *args[1:], **k)
    return res


plt.Figure.savefig = _savefig


def deco_bands(ax, dist, ticks, labels, ymin, ymax, ylabel=True):
    for t in ticks[1:-1]:
        ax.axvline(t, color="k", lw=0.8)
    linha_ef(ax, "y")
    ax.set_xlim(dist[0], dist[-1])
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    if ylabel:
        ax.set_ylabel(r"E $-$ E$_F$ (eV)" if ylabel is True else ylabel)


def plot_bands(ax, dist, E, color, ls="-", lw=1.3, label=None):
    for j in range(E.shape[1]):
        ax.plot(dist, E[:, j], color=color, ls=ls, lw=lw,
                label=label if j == 0 else None)


# =========================================================================== #
#                 ORBITAIS: camadas (n,l) e componentes m                     #
# =========================================================================== #
M_DEFAULT = {0: ["s"], 1: ["px", "py", "pz"],
             2: ["dz2", "dyz", "dxz", "dx2-y2", "dxy"],
             3: [f"f{i}" for i in range(1, 8)]}
CASTEP2M = {"S": "s", "PX": "px", "PY": "py", "PZ": "pz", "DZZ": "dz2",
            "DZY": "dyz", "DZX": "dxz", "DXX-YY": "dx2-y2", "DXY": "dxy"}
PRETTY = {"px": "p$_x$", "py": "p$_y$", "pz": "p$_z$", "dz2": "d$_{z^2}$",
          "dyz": "d$_{yz}$", "dxz": "d$_{xz}$", "dx2-y2": "d$_{x^2-y^2}$",
          "dxy": "d$_{xy}$", "t2g": "t$_{2g}$", "eg": "e$_g$"}
M_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2"]


def read_castep_orbitals(fname):
    """Do .castep: camadas do pseudo-atomo (n,l) por elemento e a ordem dos
    orbitais m (tabela 'Orbital Populations' de Mulliken)."""
    import re
    shells, mlab = {}, {}
    v = _virt(fname, "orbitals") if fname else None
    if v is not None:
        return v
    if not fname or not _vexists(fname):
        return shells, mlab
    with open(fname, errors="replace") as f:
        lines = f.readlines()
    cur = None
    for l in lines:
        m = re.search(r"Element:\s+(\S+)", l)
        if m:
            cur = m.group(1)
            shells.setdefault(cur, {})
            continue
        m = re.match(r"\s*\|\s+(\d)([spdf])\s+[-\d.]+\s+[-\d.]+", l)
        if cur and m:
            n, lq = int(m.group(1)), "spdf".index(m.group(2))
            lst = shells[cur].setdefault(lq, [])
            if n not in lst:
                lst.append(n)
    starts = [i for i, l in enumerate(lines) if "Orbital Populations" in l]
    if starts:
        first = {}
        for l in lines[starts[-1]:]:
            if "Total:" in l:
                break
            m = re.match(r"\s*(\S+)\s+(\d+)\s+([A-Za-z][\w\-]*)\s+-?\d", l)
            if m:
                el, at, lab = m.group(1), int(m.group(2)), m.group(3)
                first.setdefault(el, at)
                if at == first[el]:
                    mlab.setdefault(el, []).append(lab)
    for el in shells:
        for lq in shells[el]:
            shells[el][lq].sort()
    return shells, mlab


def _shell_n(ref, l, c):
    lst = ref.get(l, [])
    if c < len(lst):
        return lst[c]
    if lst:
        return lst[-1] + (c - len(lst) + 1)
    if not ref:
        return None
    ns_ = max(ref.get(0, [0]) or [0])
    return max(ns_, l + 1) + c


def build_orbitals(P, species, castepf):
    """Descreve cada orbital do .pdos_bin: elemento, ion, l, camada (ex 3d), m."""
    norb = len(P["am"])
    if "mnames" in P:                                   # VASP/SIESTA: o proprio arquivo diz l, m (e n no SIESTA)
        el_a = np.array([species[i - 1] if i - 1 < len(species) else f"X{i}" for i in P["species"]], object)
        return dict(el=el_a, shell=np.array(P["shells"], object), m=np.array(P["mnames"], object), l=P["am"], ion=P["ion"]), \
            f"orbitais lidos do {CODE['name']} ({norb} projecoes)"
    ref, mlab = read_castep_orbitals(castepf)
    el_a = np.empty(norb, object)
    shell_a = np.empty(norb, object)
    m_a = np.empty(norb, object)
    pairs = list(dict.fromkeys(zip(P["species"].tolist(), P["ion"].tolist())))
    for spi, ion in pairs:
        el = species[spi - 1] if spi - 1 < len(species) else f"X{spi}"
        idx = np.where((P["species"] == spi) & (P["ion"] == ion))[0]
        labs = mlab.get(el)
        if labs is not None and len(labs) != len(idx):
            labs = None
        j, count = 0, {}
        while j < len(idx):
            l = int(P["am"][idx[j]])
            nm = 2 * l + 1
            block = idx[j:j + nm]
            if len(block) < nm or np.any(P["am"][block] != l):
                block = idx[j:j + 1]
            c = count.get(l, 0)
            count[l] = c + 1
            n = _shell_n(ref.get(el, {}), l, c)
            shell = f"{n}{'spdf'[l]}" if n else f"{'spdf'[l]}({c + 1})"
            for k, o in enumerate(block):
                if labs:
                    mm = CASTEP2M.get(labs[j + k].upper(), labs[j + k].lower())
                else:
                    mm = M_DEFAULT[l][k] if k < len(M_DEFAULT[l]) else f"m{k}"
                el_a[o], shell_a[o], m_a[o] = el, shell, mm
            j += len(block)
    src = ("camadas/orbitais m lidos de " + castepf) if mlab else \
        "AVISO: .castep sem tabela de Mulliken; usando ordem padrao do CASTEP"
    return dict(el=el_a, shell=shell_a, m=m_a, l=P["am"], ion=P["ion"]), src


def make_groups(O, els, orbs, sites):
    """Cria grupos (mascaras) de projecao em varios niveis de detalhe."""
    G = []

    def add(cat, el, name, label, mask, **kw):
        if mask.any():
            G.append(dict(cat=cat, el=el, name=name, label=label, mask=mask, **kw))
    for el in els:
        me = O["el"] == el
        add("el", el, el, el, me)
        for l, o in enumerate(ORB_NAMES):
            if o not in orbs:
                continue
            ml = me & (O["l"] == l)
            add("l", el, f"{el}_{o}", f"{el}-{o}", ml, l=l)
            shells = list(dict.fromkeys(O["shell"][ml]))
            for sh in shells:
                msh = ml & (O["shell"] == sh)
                add("shell", el, f"{el}_{sh}", f"{el}-{sh}", msh, l=l, shell=sh)
                if l == 0:
                    continue
                for mm in dict.fromkeys(O["m"][msh]):
                    add("lm", el, f"{el}_{sh[:-1]}{mm}",
                        f"{el} {sh[:-1]}{PRETTY.get(mm, mm)}",
                        msh & (O["m"] == mm), l=l, shell=sh, m=mm)
                if l == 2:
                    t2g = msh & np.isin(O["m"], ["dxy", "dyz", "dxz"])
                    eg = msh & np.isin(O["m"], ["dz2", "dx2-y2"])
                    add("eg", el, f"{el}_{sh}_t2g", f"{el} {sh} t$_{{2g}}$",
                        t2g, l=l, shell=sh, m="t2g")
                    add("eg", el, f"{el}_{sh}_eg", f"{el} {sh} e$_g$",
                        eg, l=l, shell=sh, m="eg")
    import re
    for st in sites:
        m = re.match(r"^([A-Za-z]+)(\d+)$", st.strip())
        if not m:
            print(f" AVISO: sitio '{st}' invalido (use ex: Fe1, H23).")
            continue
        el, ion = m.group(1), int(m.group(2))
        ms = (O["el"] == el) & (O["ion"] == ion)
        if not ms.any():
            print(f" AVISO: sitio {st} nao encontrado.")
            continue
        add("site", el, st, st, ms, site=st)
        for l, o in enumerate(ORB_NAMES):
            add("site_l", el, f"{st}_{o}", f"{st}-{o}", ms & (O["l"] == l),
                l=l, site=st)
    return G


def draw_fat(ax, dist, E, W, color, scale, bands):
    """Bandas 'gordas': largura da linha proporcional ao peso do orbital."""
    from matplotlib.collections import LineCollection
    segs, widths = [], []
    for j in bands:
        ax.plot(dist, E[:, j], color="0.78", lw=0.5, zorder=1)
        pts = np.column_stack([dist, E[:, j]])
        segs.append(np.stack([pts[:-1], pts[1:]], axis=1))
        widths.append(0.5 * (W[:-1, j] + W[1:, j]))
    if segs:
        lc = LineCollection(np.concatenate(segs), linewidths=scale *
                            np.concatenate(widths), colors=color, alpha=0.85,
                            capstyle="round", zorder=2)
        ax.add_collection(lc)


# =========================================================================== #
#                                   MAIN                                      #
# =========================================================================== #
# =========================================================================== #
#        ESTRUTURA, DEFEITO (VIZINHOS E DISTORCAO) E TERMODINAMICA            #
# =========================================================================== #
EV2KJMOL = 96.485332
MASS = dict(H=1.008, He=4.0026, Li=6.94, Be=9.0122, B=10.81, C=12.011, N=14.007, O=15.999, F=18.998, Ne=20.180,
            Na=22.990, Mg=24.305, Al=26.982, Si=28.085, P=30.974, S=32.06, Cl=35.45, Ar=39.948, K=39.098, Ca=40.078,
            Sc=44.956, Ti=47.867, V=50.942, Cr=51.996, Mn=54.938, Fe=55.845, Co=58.933, Ni=58.693, Cu=63.546, Zn=65.38,
            Ga=69.723, Ge=72.630, As=74.922, Se=78.971, Br=79.904, Kr=83.798, Rb=85.468, Sr=87.62, Y=88.906, Zr=91.224,
            Nb=92.906, Mo=95.95, Tc=98.0, Ru=101.07, Rh=102.91, Pd=106.42, Ag=107.87, Cd=112.41, In=114.82, Sn=118.71,
            Sb=121.76, Te=127.60, I=126.90, Xe=131.29, Cs=132.91, Ba=137.33, La=138.91, Ce=140.12, Pr=140.91, Nd=144.24,
            Pm=145.0, Sm=150.36, Eu=151.96, Gd=157.25, Tb=158.93, Dy=162.50, Ho=164.93, Er=167.26, Tm=168.93, Yb=173.05,
            Lu=174.97, Hf=178.49, Ta=180.95, W=183.84, Re=186.21, Os=190.23, Ir=192.22, Pt=195.08, Au=196.97, Hg=200.59,
            Tl=204.38, Pb=207.2, Bi=208.98, Po=209.0, At=210.0, Rn=222.0, Fr=223.0, Ra=226.0, Ac=227.0, Th=232.04,
            Pa=231.04, U=238.03, Np=237.0, Pu=244.0)


def read_cell_struct(fname):
    """Rede (A), posicoes fracionarias e massas de um .cell."""
    v = _virt(fname, "struct")
    if v is not None:
        return v
    if not fname or not _vexists(fname):
        return None
    blocks, cur = {}, None
    with open(fname, errors="replace") as f:
        for raw in f:
            l = re.sub(r"[!#].*$", "", raw).strip()
            if not l:
                continue
            m = re.match(r"%block\s+(\S+)", l, re.I)
            if m:
                cur = m[1].lower()
                blocks[cur] = []
                continue
            if re.match(r"%endblock", l, re.I):
                cur = None
                continue
            if cur:
                blocks[cur].append(l)

    def unit(rows):
        if rows and re.match(r"^(ang|bohr|a0|nm)", rows[0], re.I):
            u = rows.pop(0).lower()
            return BOHR2ANG if u.startswith(("bohr", "a0")) else (10.0 if u == "nm" else 1.0)
        return 1.0
    lat = None
    if "lattice_cart" in blocks:
        r = list(blocks["lattice_cart"]); sc = unit(r)
        lat = np.array([[float(x) for x in l.split()[:3]] for l in r[:3]]) * sc
    elif "lattice_abc" in blocks:
        r = list(blocks["lattice_abc"]); sc = unit(r)
        a, b, c = [float(x) * sc for x in r[0].split()[:3]]
        al, be, ga = np.radians([float(x) for x in r[1].split()[:3]])
        cx = c * np.cos(be); cy = c * (np.cos(al) - np.cos(be) * np.cos(ga)) / np.sin(ga)
        lat = np.array([[a, 0, 0], [b * np.cos(ga), b * np.sin(ga), 0], [cx, cy, np.sqrt(max(0, c * c - cx * cx - cy * cy))]])
    sp, fr = [], []
    if "positions_frac" in blocks:
        for l in blocks["positions_frac"]:
            p = l.split(); sp.append(p[0].split(":")[0]); fr.append([float(x) for x in p[1:4]])
    elif "positions_abs" in blocks and lat is not None:
        r = list(blocks["positions_abs"]); sc = unit(r)
        for l in r:
            p = l.split(); sp.append(p[0].split(":")[0])
            fr.append(np.linalg.solve(lat.T, np.array([float(x) for x in p[1:4]]) * sc))
    masses = {}
    if "species_mass" in blocks:
        r = list(blocks["species_mass"])
        if r and re.match(r"^(amu|kg|g|me)$", r[0], re.I):
            r.pop(0)
        for l in r:
            p = l.split(); masses[p[0]] = float(p[1])
    if lat is None or not sp:
        return None
    return dict(lat=lat, sp=sp, f=np.array(fr, float), masses=masses, src="cell")


def read_castep_struct(fname):
    """Ultima geometria, forcas, energias e pressao de um .castep."""
    out = dict(lat=None, sp=None, f=None, forces=None, E={}, pressure=None, info={})
    v = _virt(fname, "struct") if fname else None
    if v is not None:
        return v
    if not fname or not _vexists(fname):
        return out
    with open(fname, errors="replace") as fh:
        L = fh.read().splitlines()
    k = max([i for i, l in enumerate(L) if "Real Lattice(A)" in l], default=-1)
    if k >= 0:
        try:
            out["lat"] = np.array([[float(x) for x in L[k + j].split()[:3]] for j in (1, 2, 3)])
        except ValueError:
            pass
    k = max([i for i, l in enumerate(L) if re.match(r"^\s*x\s+Element\s+Atom", l)], default=-1)
    if k >= 0:
        sp, fr = [], []
        for l in L[k + 1:]:
            m = re.match(r"^\s*x\s+([A-Za-z][\w:]*)\s+(\d+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+x", l)
            if m:
                sp.append(m[1].split(":")[0]); fr.append([float(m[3]), float(m[4]), float(m[5])])
            elif sp and re.match(r"^\s*x+\s*$", l):
                break
        if sp:
            out["sp"], out["f"] = sp, np.array(fr)
    num = r"(-?[\d.]+(?:E[-+]?\d+)?)"
    pats = dict(final=r"^\s*Final energy(?:, E)?\s*=\s*" + num, free=r"Final free energy \(E-TS\)\s*=\s*" + num,
                zeroK=r"NB est\. 0K energy \(E-0\.5TS\)\s*=\s*" + num,
                corrected=r"Total energy corrected for finite basis set\s*=\s*" + num)
    for key, pat in pats.items():
        for l in L:
            m = re.search(pat, l, re.I)
            if m:
                out["E"][key] = float(m[1])
    for l in L:
        m = re.match(r"^\s*\*\s*Pressure:\s*(-?[\d.]+)", l)
        if m:
            out["pressure"] = float(m[1])
        m = re.search(r"using functional\s*:\s*(.+)$", l)
        if m:
            out["info"]["functional"] = m[1].strip()
        m = re.search(r"basis set cut-off\s*:\s*([-\d.]+)", l)
        if m:
            out["info"]["cutoff"] = float(m[1])
    k = max([i for i, l in enumerate(L) if re.search(r"\*+ (Symmetrised )?Forces \*+", l)], default=-1)
    if k >= 0:
        F = []
        for l in L[k + 1:]:
            m = re.match(r"^\s*\*\s*[A-Za-z][\w:]*\s+\d+\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)", l)
            if m:
                F.append([float(m[1]), float(m[2]), float(m[3])])
            elif F and re.match(r"^\s*\*+\s*$", l):
                break
        out["forces"] = np.array(F) if F else None
    return out


def struct_of(seed):
    """Estrutura de um seed: geometria do .castep (calculada) ou do .cell."""
    C = read_castep_struct(seed + ".castep")
    cell = read_cell_struct(seed + ".cell")
    if C["lat"] is not None and C["sp"]:
        fr = C["f"]
        if cell and cell["sp"] == C["sp"]:                       # mesma estrutura: usa a precisao completa do .cell
            d = cell["f"] - fr; d -= np.round(d)
            if np.abs(d).max() < 2e-5:
                fr = cell["f"]
        st = dict(lat=C["lat"], sp=C["sp"], f=fr, masses=(cell or {}).get("masses", {}), src="castep")
    elif cell:
        st = cell
    else:
        return None
    cnt, lab = {}, []
    for s in st["sp"]:
        cnt[s] = cnt.get(s, 0) + 1; lab.append(f"{s}{cnt[s]}")
    st.update(count=cnt, label=lab, V=abs(np.linalg.det(st["lat"])), castep=C, name=os.path.basename(seed))
    return st


IMG = np.array([[i, j, k] for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)], float)


def mic_vec(f0, F, L):
    """Menor vetor (A) do ponto f0 ate cada posicao fracionaria em F (27 imagens)."""
    df = np.atleast_2d(F) - f0
    df -= np.round(df)
    c = (df[:, None, :] + IMG[None]) @ L
    d = np.linalg.norm(c, axis=2)
    i = np.argmin(d, axis=1)
    return c[np.arange(len(df)), i], d[np.arange(len(df)), i]


def neighbors(st, f0, rmax, skip=-1):
    v, d = mic_vec(f0, st["f"], st["lat"])
    idx = [j for j in np.argsort(d) if j != skip and 1e-4 < d[j] <= rmax]
    return [dict(j=int(j), sp=st["sp"][j], label=st["label"][j], d=float(d[j]), v=v[j]) for j in idx]


def first_shell(nb, factor, rcut=0):
    if not nb:
        return []
    lim = rcut if rcut > 0 else nb[0]["d"] * factor
    return [n for n in nb if n["d"] <= lim]


def hetero_shell(st, j, factor):
    nb = [n for n in neighbors(st, st["f"][j], 4.5, j) if n["sp"] != st["sp"][j]]
    return first_shell(nb, factor)


def hull_volume(V):
    n = len(V)
    if n < 4:
        return np.nan
    vol = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                nr = np.cross(V[j] - V[i], V[k] - V[i])
                if np.linalg.norm(nr) < 1e-8:
                    continue
                s = [(V[t] - V[i]) @ nr for t in range(n) if t not in (i, j, k)]
                if any(x > 1e-6 for x in s) and any(x < -1e-6 for x in s):
                    continue
                vol += abs(V[i] @ nr) / 6
    return vol


def poly_metrics(vecs):
    V = np.array(vecs); n = len(V)
    if n == 0:
        return dict(cn=0)
    d = np.linalg.norm(V, axis=1); dav = d.mean()
    dw = d.min()
    for _ in range(30):
        w = np.exp(1 - (d / dw) ** 6); dw = (d * w).sum() / w.sum()
    ang = [np.degrees(np.arccos(np.clip(V[i] @ V[j] / d[i] / d[j], -1, 1))) for i in range(n) for j in range(i + 1, n)]
    vol = hull_volume(V)
    r = dict(cn=n, d=d, dav=dav, dmin=d.min(), dmax=d.max(), baur=np.mean(np.abs(d - dav) / dav),
             econ=np.exp(1 - (d / dw) ** 6).sum(), angmin=min(ang) if ang else np.nan, angmax=max(ang) if ang else np.nan,
             V=vol, lam=np.nan, s2=np.nan, shape=f"{n} vizinhos")
    if n == 6:
        cis = [a for a in ang if a < 135]; l0 = (3 * vol / 4) ** (1 / 3)
        r.update(shape="octaedro", lam=np.mean((d / l0) ** 2), s2=sum((a - 90) ** 2 for a in cis) / max(1, len(cis) - 1))
    elif n == 4:
        l0 = (vol * 9 * np.sqrt(3) / 8) ** (1 / 3)
        r.update(shape="tetraedro", lam=np.mean((d / l0) ** 2), s2=sum((a - 109.4712) ** 2 for a in ang) / 5)
    return r


def map_to_ref(dft, ref, tol=1.0):
    pairs = []
    for i in range(len(dft["sp"])):
        df = ref["f"] - dft["f"][i]; df -= np.round(df)
        d = np.linalg.norm(df @ dft["lat"], axis=1)
        for j in np.where(d < tol)[0]:
            pairs.append((d[j], i, int(j)))
    pairs.sort()
    d2r = -np.ones(len(dft["sp"]), int); r2d = -np.ones(len(ref["sp"]), int)
    for _, i, j in pairs:
        if d2r[i] < 0 and r2d[j] < 0:
            d2r[i], r2d[j] = j, i
    defects = []
    for i, j in enumerate(d2r):
        if j < 0:
            defects.append(dict(type="intersticial", label=f"{dft['label'][i]} (intersticial)", atom=i, f=dft["f"][i], sp=dft["sp"][i]))
        elif ref["sp"][j] != dft["sp"][i]:
            defects.append(dict(type="substitucional", label=f"{dft['sp'][i]} no sitio de {ref['sp'][j]} ({dft['label'][i]} <-> {ref['label'][j]})",
                                atom=i, ref_atom=int(j), f=dft["f"][i], sp=dft["sp"][i], host=ref["sp"][j]))
    for j, i in enumerate(r2d):
        if i < 0:
            defects.append(dict(type="vacancia", label=f"vacancia de {ref['sp'][j]} (sitio {ref['label'][j]} da referencia)",
                                ref_atom=j, f=ref["f"][j], sp="V", host=ref["sp"][j]))
    return d2r, defects


def analyze_defect(dft, ref, center="", factor=1.25, rcut=0.0, rfar=0.0):
    res = dict(warn=[])
    L = dft["lat"]
    widths = [dft["V"] / np.linalg.norm(np.cross(L[(i + 1) % 3], L[(i + 2) % 3])) for i in range(3)]
    rfar = rfar or max(3.0, 0.45 * min(widths)); res["rfar"] = rfar
    d2r = None
    if ref is not None:
        d2r, cands = map_to_ref(dft, ref)
        if not cands:
            res["warn"].append("Nenhuma diferenca de composicao ou de sitio em relacao a referencia (tolerancia 1 A).")
    else:
        cnt = dft["count"]; mx = max(cnt.values())
        minor = [s for s, n in cnt.items() if n <= 4 and n < mx / 4]
        cands = [dict(type="dopante", label=f"{dft['label'][i]} (dopante)", atom=i, f=dft["f"][i], sp=s)
                 for s in minor for i, x in enumerate(dft["sp"]) if x == s]
        res["warn"].append("Tipo de sitio inferido pela coordenacao (sem estrutura de referencia)." if cands else
                           "Nenhuma especie minoritaria (dopante). Para vacancias e intersticiais use --ref ou --center.")
    res["cands"] = cands
    C = None
    if center:
        p = re.split(r"[\s,;]+", center.strip())
        if len(p) == 3 and all(re.match(r"^-?[\d.]+$", x) for x in p):
            C = dict(type="ponto", label=f"ponto ({center})", f=np.array([float(x) for x in p]), sp=".")
        elif center in dft["label"]:
            i = dft["label"].index(center)
            C = next((c for c in cands if c.get("atom") == i), None) or dict(type="atomo", label=center, atom=i, f=dft["f"][i], sp=dft["sp"][i])
            if d2r is not None and "ref_atom" not in C and d2r[i] >= 0:
                C["ref_atom"] = int(d2r[i])
        else:
            res["warn"].append(f"Centro '{center}' nao encontrado.")
    if C is None:
        C = next((c for c in cands if c["type"] in ("substitucional", "dopante")), cands[0] if cands else None)
    if C is None:
        return res
    res["C"] = C
    ai = C.get("atom", -1)
    nb = neighbors(dft, C["f"], 6.0, ai)
    sh = first_shell(nb, factor, rcut)
    res.update(shell=sh, poly=poly_metrics([n["v"] for n in sh]), second=[n for n in nb if n not in sh][:12])
    res["hop"] = [(n, [b for b in hetero_shell(dft, n["j"], factor) if b["j"] != ai]) for n in sh]
    # bulk da propria supercelula
    _, dc = mic_vec(C["f"], dft["f"], L)
    stats = {}
    for i in np.where(dc >= rfar)[0]:
        for b in hetero_shell(dft, i, factor):
            stats.setdefault("-".join(sorted([dft["sp"][i], b["sp"]])), []).append(b["d"])
    res["bulk"] = {k: (np.mean(v), np.std(v)) for k, v in stats.items()}
    host = C.get("host")
    if ref is None and C["type"] in ("dopante", "atomo"):
        cat = sorted([s for s in dft["count"] if s not in ("H", C["sp"])], key=lambda s: -dft["count"][s])
        host = cat[0] if cat else None
    res["host"] = host
    if host and host != "V":
        far = [i for i in np.where(dc >= rfar)[0] if dft["sp"][i] == host]
        if far:
            i = max(far, key=lambda k: dc[k])
            res["host_poly"] = (dft["label"][i], poly_metrics([b["v"] for b in hetero_shell(dft, i, factor)]))
            if ref is None:
                nh = [n for n in nb if n["sp"] == host]
                hh = [n for n in neighbors(dft, dft["f"][i], 6.0, i) if n["sp"] == host]
                if nh and hh:
                    ratio = nh[0]["d"] / hh[0]["d"]; dcn = abs(res["poly"]["cn"] - res["host_poly"][1]["cn"])
                    res["site"] = (f"substitucional, provavelmente no sitio de {host}" if dcn <= 1 and 0.85 < ratio < 1.15 else "intersticial (provavel)")
                    res["site_why"] = (f"coordenacao {res['poly']['cn']} ({host} no bulk: {res['host_poly'][1]['cn']}); {host} mais proximo a "
                                       f"{nh[0]['d']:.3f} A vs {host}-{host} no bulk {hh[0]['d']:.3f} A")
    if ref is not None:
        fR = ref["f"][C["ref_atom"]] if "ref_atom" in C else C["f"]
        for n in sh:
            j = d2r[n["j"]]
            n["dref"] = float(mic_vec(fR, ref["f"][j], ref["lat"])[1][0]) if j >= 0 else np.nan
        rsh = first_shell(neighbors(ref, fR, 6.0, C.get("ref_atom", -1)), factor, rcut)
        res["ref_poly"] = poly_metrics([n["v"] for n in rsh])
        for n, bonds in res["hop"]:
            for b in bonds:
                a1, a2 = d2r[n["j"]], d2r[b["j"]]
                b["dref"] = float(mic_vec(ref["f"][a1], ref["f"][a2], ref["lat"])[1][0]) if a1 >= 0 and a2 >= 0 else np.nan
        ok = np.where(d2r >= 0)[0]
        df = dft["f"][ok] - ref["f"][d2r[ok]]; df -= np.round(df)
        u = df @ L; shift = u.mean(axis=0); u -= shift
        rv, rr = mic_vec(fR, ref["f"][d2r[ok]], ref["lat"])
        rad = np.where(rr > 1e-6, np.einsum("ij,ij->i", u, rv) / np.maximum(rr, 1e-9), 0)
        order = np.argsort(rr)
        res["disp"] = [(dft["label"][ok[k]], dft["sp"][ok[k]], rr[k], np.linalg.norm(u[k]), rad[k]) for k in order]
        res["shift"] = np.linalg.norm(shift)
        bins = {}
        for _, _, r, uu, _ in res["disp"]:
            bins.setdefault(int(r), []).append(uu)
        res["bins"] = [(b, len(v), np.mean(v), np.max(v)) for b, v in sorted(bins.items())]
        res["rpert"] = next((b for b, n, m, _ in res["bins"] if b >= 1 and m < 0.02), None)
        res["dV"] = 100 * (dft["V"] - ref["V"]) / ref["V"]
        res["lp"] = (np.linalg.norm(dft["lat"], axis=1), np.linalg.norm(ref["lat"], axis=1))
    return res


def thermo(dft, ref, edef, eref, mu, dS, hless=None):
    sp = sorted(set(dft["count"]) | (set(ref["count"]) if ref else set()))
    need = [s for s in sp if not np.isfinite(mu.get(s, np.nan))]
    N = lambda st, s: st["count"].get(s, 0) if st else 0
    summu = lambda st: sum(N(st, s) * mu.get(s, 0) for s in sp)
    mass = lambda st: sum(n * st["masses"].get(s, MASS.get(re.match(r"[A-Z][a-z]?", s)[0], 0)) for s, n in st["count"].items())
    out = dict(need=need, wt=lambda st: 100 * N(st, "H") * MASS["H"] / mass(st))
    if ref and np.isfinite(edef) and np.isfinite(eref):
        out["dn"] = [(s, N(dft, s) - N(ref, s)) for s in sp if N(dft, s) - N(ref, s)]
        if all(np.isfinite(mu.get(s, np.nan)) for s, _ in out["dn"]):
            out["Ef"] = edef - eref - sum(n * mu[s] for s, n in out["dn"])
    dH = lambda st, E: (E - summu(st)) / (N(st, "H") / 2) * EV2KJMOL if (N(st, "H") and not need and np.isfinite(E)) else np.nan
    out["dHdef"] = dH(dft, edef); out["dHref"] = dH(ref, eref) if ref else np.nan
    T = lambda h: -h * 1000 / dS if np.isfinite(h) and h < 0 else np.nan
    out["Tdef"], out["Tref"] = T(out["dHdef"]), T(out["dHref"])
    if hless and np.isfinite(hless[1]) and np.isfinite(mu.get("H", np.nan)):
        n = N(dft, "H") - N(hless[0], "H")
        if n > 0:
            out["edes"] = (n, (hless[1] + n * mu["H"] - edef) / n)
    return out


def defect_report(seed, a, outdir):
    """Gera defeito.txt, .dat de vizinhos e deslocamentos e a figura."""
    USADOS.add("robinson1971")
    dft = struct_of(seed)
    if dft is None:
        print(" AVISO: sem .cell/.castep com estrutura: analise do defeito ignorada.")
        return
    ref = struct_of(a.ref) if a.ref else None
    if a.ref and ref is None:
        print(f" AVISO: nao consegui ler a estrutura de referencia {a.ref}.")
    res = analyze_defect(dft, ref, a.center or "", a.shell_factor, a.rcut, a.rfar)
    base = dft["name"]; out = lambda n: os.path.join(outdir, f"{base}_{n}")
    def E(st):
        if not st:
            return np.nan
        e = st["castep"]["E"]; t = a.energy
        if t == "auto":
            t = "zeroK" if e.get("zeroK") is not None else "final"
        return e.get(t, e.get("final", np.nan))
    # potenciais quimicos: "Mg=-975.3" ou "Mg=@seed_Mg" (energia por atomo do .castep)
    mu = {}
    for item in (a.mu or "").split(","):
        if "=" not in item:
            continue
        k, v = [x.strip() for x in item.split("=", 1)]
        if v.startswith("@"):
            st = struct_of(v[1:])
            mu[k] = E(st) / len(st["sp"]) if st and np.isfinite(E(st)) else np.nan
            if not np.isfinite(mu[k]):
                print(f" AVISO: sem energia em {v[1:]}.castep para mu({k}).")
        else:
            mu[k] = float(v)
    hl = struct_of(a.h_less) if a.h_less else None
    th = thermo(dft, ref, E(dft), E(ref), mu, a.dS, (hl, E(hl)) if hl else None)
    W = []; w = W.append
    f_ = lambda x, d=4: f"{x:.{d}f}" if x is not None and np.isfinite(x) else "-"
    pc = lambda x, y: 100 * (x - y) / y if np.isfinite(x) and np.isfinite(y) and y else np.nan
    w(f"ANALISE DO DEFEITO: {base}" + (f"   (referencia pura: {ref['name']})" if ref else ""))
    w("=" * 78)
    comp = lambda st: " ".join(f"{k}{v}" for k, v in st["count"].items())
    w(f"Estrutura: {comp(dft)}  ({len(dft['sp'])} atomos, V = {dft['V']:.3f} A^3, geometria do .{dft['src']})")
    if ref:
        w(f"Referencia: {comp(ref)}  ({len(ref['sp'])} atomos, V = {ref['V']:.3f} A^3)")
    for x in res["warn"]:
        w("Obs.: " + x)
    C = res.get("C")
    if not C:
        open(out("defeito.txt"), "w", encoding="utf-8").write("\n".join(W) + "\n")
        print(f" -> {out('defeito.txt')}")
        return
    w(f"Centro: [{C['type']}] {C['label']}")
    if res.get("site"):
        w(f"Sitio provavel: {res['site']}  ({res['site_why']})")
    for c in res["cands"]:
        if c is not C:
            w(f"Outro defeito encontrado: {c['label']}")
    host = res.get("host"); bk = res["bulk"]
    hk = lambda s: "-".join(sorted([host, s])) if host else None
    w("")
    w(f"PRIMEIROS VIZINHOS DO CENTRO ({len(res['shell'])})")
    w("-" * 78)
    w(f"{'vizinho':<10}{'esp':<5}{'d (A)':>10}" + (f"{'d_ref (A)':>12}{'Dd (A)':>10}{'Dd (%)':>9}" if ref else "") + f"{'vs bulk (%)':>13}")
    for n in res["shell"]:
        b = bk.get(hk(n["sp"]))
        w(f"{n['label']:<10}{n['sp']:<5}{n['d']:10.4f}" + (f"{n['dref']:12.4f}{n['d'] - n['dref']:+10.4f}{pc(n['d'], n['dref']):+9.2f}" if ref else "")
          + f"{pc(n['d'], b[0]) if b else np.nan:+13.2f}")
    for k, (m, s) in bk.items():
        w(f"  bulk {k}: {m:.4f} +- {s:.4f} A")
    w("")
    w("LIGACOES DOS PRIMEIROS VIZINHOS (ex.: H-Mg)")
    w("-" * 78)
    hop = {}
    for n, bonds in res["hop"]:
        for b in bonds:
            k = "-".join(sorted([n["sp"], b["sp"]])); hop.setdefault(k, []).append(b["d"])
            w(f"  {n['label']:<8} - {b['label']:<8}{b['d']:10.4f}" + (f"   ref {b['dref']:.4f} ({pc(b['d'], b['dref']):+.2f} %)" if ref else "")
              + (f"   bulk {pc(b['d'], bk[k][0]):+.2f} %" if k in bk else ""))
    for k, v in hop.items():
        w(f"  media {k} dos vizinhos: {np.mean(v):.4f} A ({len(v)} ligacoes)" + (f", bulk {bk[k][0]:.4f} A ({pc(np.mean(v), bk[k][0]):+.2f} %)" if k in bk else ""))
    w("")
    w("POLIEDRO DE COORDENACAO E DISTORCAO")
    w("-" * 78)
    cols = [("defeito", res["poly"])] + ([("ref. mesmo sitio", res["ref_poly"])] if "ref_poly" in res else []) + \
           ([(f"{res['host_poly'][0]} bulk", res["host_poly"][1])] if "host_poly" in res else [])
    w(f"{'':<30}" + "".join(f"{c[0]:>18}" for c in cols))
    for name, key, d in [("coordenacao", "cn", 0), ("<d> (A)", "dav", 4), ("d min (A)", "dmin", 4), ("d max (A)", "dmax", 4), ("Baur D", "baur", 5),
                         ("ECoN", "econ", 3), ("volume (A^3)", "V", 3), ("<lambda>", "lam", 5), ("sigma^2 (grau^2)", "s2", 2),
                         ("angulo min (grau)", "angmin", 1), ("angulo max (grau)", "angmax", 1)]:
        w(f"{name:<30}" + "".join(f"{(str(m[key]) if d == 0 else f_(m.get(key), d)):>18}" for _, m in cols))
    if res["second"]:
        w("")
        w("SEGUNDA CAMADA: " + ", ".join(f"{n['label']} {n['d']:.3f}" for n in res["second"]))
    if "disp" in res:
        w("")
        w("CAMPO DE DESLOCAMENTOS (vs estrutura pura; translacao media removida: %.4f A)" % res["shift"])
        w("-" * 78)
        for b, n, m, mx in res["bins"]:
            w(f"  {b:2d}-{b + 1:<2d} A  {n:4d} atomos   <|dr|> = {m:.4f} A   max = {mx:.4f} A")
        top = sorted(res["disp"], key=lambda x: -x[3])[:8]
        w("  maiores: " + ", ".join(f"{l} {u:.3f} A (r={r:.2f}, radial {ra:+.3f})" for l, _, r, u, ra in top))
        if res["rpert"] is not None:
            w(f"  a perturbacao cai abaixo de 0,02 A a partir de ~{res['rpert']} A do centro")
        lpd, lpr = res["lp"]
        w(f"  celula: a,b,c = {lpd.round(4)} vs {lpr.round(4)} A;  dV/V = {res['dV']:+.3f} %")
    w("")
    w("TERMODINAMICA (energia: %s)" % a.energy)
    w("-" * 78)
    w(f"E(defeito) = {f_(E(dft), 6)} eV" + (f"   E(pura) = {f_(E(ref), 6)} eV" if ref else ""))
    w("mu (eV/atomo): " + (", ".join(f"{k} = {v:.6f}" for k, v in mu.items()) or "nao informado (use --mu)"))
    if th["need"]:
        w("Faltam: " + ", ".join(f"mu({s})" for s in th["need"]))
    if "dn" in th:
        w("Atomos trocados com os reservatorios: " + ", ".join(f"{n:+d} {s}" for s, n in th["dn"]))
    if "Ef" in th:
        w(f"Energia de formacao do defeito Ef = {th['Ef']:.4f} eV")
    if np.isfinite(th["dHdef"]):
        w(f"Entalpia de formacao do hidreto (defeito) = {th['dHdef']:.2f} kJ/mol H2   T_d = {f_(th['Tdef'], 1)} K")
    if np.isfinite(th["dHref"]):
        w(f"Entalpia de formacao do hidreto (pura)    = {th['dHref']:.2f} kJ/mol H2   T_d = {f_(th['Tref'], 1)} K")
        if np.isfinite(th["dHdef"]):
            w(f"Efeito do defeito: ddH = {th['dHdef'] - th['dHref']:+.2f} kJ/mol H2 ("
              + ("desestabiliza" if th["dHdef"] > th["dHref"] else "estabiliza") + " o hidreto)")
    if any(np.isfinite(x) and abs(x) > 500 for x in (th["dHdef"], th["dHref"])):
        w("ATENCAO: dH fora da faixa fisica (-20 a -200 kJ/mol H2): confira se cada mu e energia POR ATOMO, mesmo funcional/corte.")
    if "edes" in th:
        w(f"Energia de remocao de H: {th['edes'][1]:.4f} eV por H ({th['edes'][0]} H)")
    w(f"Capacidade gravimetrica de H: {th['wt'](dft):.3f} %" + (f"  (pura: {th['wt'](ref):.3f} %)" if ref else ""))
    for st, nm in ((dft, "defeito"), (ref, "referencia")):
        if st is not None and st["castep"]["forces"] is not None:
            fm = np.linalg.norm(st["castep"]["forces"], axis=1).max()
            w(f"Forca maxima ({nm}): {fm:.4f} eV/A" + ("  (acima de 0,05: estrutura talvez nao relaxada)" if fm > 0.05 else ""))
    if ref and dft["castep"]["info"] and ref["castep"]["info"] and dft["castep"]["info"] != ref["castep"]["info"]:
        w(f"ATENCAO: configuracoes diferentes entre defeito e referencia: {dft['castep']['info']} vs {ref['castep']['info']}")
    w("Obs.: energias eletronicas a 0 K, sem ponto zero; T_d = dH/dS com dS = %.1f J/mol K." % a.dS)
    open(out("defeito.txt"), "w", encoding="utf-8").write("\n".join(W) + "\n")
    print(f" -> {out('defeito.txt')}")
    # .dat (Origin)
    with open(out("defeito_vizinhos.dat"), "w", encoding="utf-8") as fh:
        fh.write(f"# Vizinhos e ligacoes em torno de {C['label']}\ntipo\tde\tpara\tespecie\td(A)\td_ref(A)\n")
        cl = dft["label"][C["atom"]] if "atom" in C else ("vacancia" if C["sp"] == "V" else "ponto")
        for n in res["shell"]:
            fh.write(f"1a camada\t{cl}\t{n['label']}\t{n['sp']}\t{n['d']:.5f}\t{n.get('dref', np.nan):.5f}\n")
        for n, bonds in res["hop"]:
            for b in bonds:
                fh.write(f"ligacao do vizinho\t{n['label']}\t{b['label']}\t{b['sp']}\t{b['d']:.5f}\t{b.get('dref', np.nan):.5f}\n")
        for k, (m, s) in bk.items():
            fh.write(f"bulk (media)\t{k}\tdesvio {s:.5f}\t\t{m:.5f}\tnan\n")
    print(f" -> {out('defeito_vizinhos.dat')}")
    fig, ax = plt.subplots(figsize=(a.width * 0.9, a.height * 0.75))
    if "disp" in res:
        write_table(out("defeito_deslocamentos.dat"), [f"Deslocamentos vs {ref['name']}; centro {C['label']}"],
                    ["r_centro(A)", "deslocamento(A)", "radial(A)"], np.array([[r, u, ra] for _, _, r, u, ra in res["disp"]]), fmt="%.5f")
        print(f" -> {out('defeito_deslocamentos.dat')}")
        for s in sorted(set(x[1] for x in res["disp"])):
            pts = [(r, u) for _, sp_, r, u, _ in res["disp"] if sp_ == s and r > 0]
            if pts:
                ax.scatter(*zip(*pts), s=22, label=s, alpha=.8)
        ax.plot([b + .5 for b, *_ in res["bins"]], [m for _, _, m, _ in res["bins"]], "k--", lw=1.2, label="média por faixa")
        ax.set_xlabel("distância ao centro na estrutura pura (Å)"); ax.set_ylabel(r"$|\Delta r|$ (Å)")
    else:
        cats, ys = [], []
        for n in res["shell"]:
            cats.append(f"{C['sp']}-{n['sp']}"); ys.append(n["d"])
        for n, bonds in res["hop"]:
            for b in bonds:
                cats.append("-".join(sorted([n["sp"], b["sp"]])) + "\n(vizinhos)"); ys.append(b["d"])
        u = list(dict.fromkeys(cats)) + [f"{k}\n(bulk)" for k in bk]
        xs = [u.index(c) + np.random.uniform(-.12, .12) for c in cats]
        ax.scatter(xs, ys, s=28, alpha=.8, color="#0072B2", label="em torno do defeito")
        for k, (m, s) in bk.items():
            ax.errorbar(u.index(f"{k}\n(bulk)"), m, yerr=s, fmt="D", color="k", capsize=4, label="bulk (média ± σ)")
        ax.set_xticks(range(len(u))); ax.set_xticklabels(u); ax.set_ylabel("comprimento de ligação (Å)")
    ax.set_title(f"{base}: entorno de {C['label']}", fontsize=a.fontsize)
    h_, l_ = ax.get_legend_handles_labels(); dd = dict(zip(l_, h_)); ax.legend(dd.values(), dd.keys(), fontsize=a.fontsize - 3)
    fig.savefig(out(f"defeito.{a.format}"), dpi=a.dpi); plt.close(fig)
    print(f" -> {out('defeito.' + a.format)}")
    for l in W:
        if l.startswith(("Centro", "Sitio", "Energia de formacao", "Entalpia", "Efeito", "ATENCAO")):
            print(" " + l)


# =========================================================================== #
#        GERADOR DE CALCULOS DE REFERENCIA E DENSIDADE DE CARGA               #
# =========================================================================== #
ELEM_REF = dict(
    hcp=dict(Mg=(3.209, 5.211), Ti=(2.951, 4.686), Zr=(3.232, 5.147), Co=(2.507, 4.069), Zn=(2.665, 4.947), Sc=(3.309, 5.273),
             Y=(3.647, 5.731), Be=(2.286, 3.584), Hf=(3.195, 5.051), Cd=(2.979, 5.619), Ru=(2.706, 4.282), Re=(2.761, 4.456)),
    bcc=dict(Fe=2.866, V=3.024, Cr=2.885, Nb=3.300, Mo=3.147, W=3.165, Li=3.510, Na=4.291, K=5.328, Ta=3.303, Ba=5.028, Mn=2.89),
    fcc=dict(Al=4.050, Ni=3.524, Cu=3.615, Pd=3.891, Ag=4.086, Pt=3.924, Au=4.078, Ca=5.588, Sr=6.085, Pb=4.950, Rh=3.803, Ir=3.839, Ce=5.161, La=5.30),
    diamante=dict(Si=5.431, Ge=5.658, C=3.567, Sn=6.489),
    molecula=dict(H=0.741, N=1.098, O=1.208, F=1.412, Cl=1.988))
MAGMOM = dict(Fe=2.5, Co=1.7, Ni=0.7, Mn=3.0, Cr=1.0, O=1.0)
FUNC_MAP = [(r"PBE for solids", "PBESOL"), (r"revised Perdew Burke Ernzerhof|RPBE", "RPBE"), (r"Perdew Burke Ernzerhof", "PBE"),
            (r"Perdew Wang", "PW91"), (r"Wu-Cohen", "WC"), (r"Local Density Approximation|LDA", "LDA")]


def calc_settings(seed):
    st = dict(pot={}, mass={}, hub=[], kgrid=None, func="PBE", func_raw="", cutoff=None, spin=False, fbc=None, etol=None,
              nonmetal=False, fixcom=False)
    if _vexists(seed + ".cell"):
        cur = None
        for raw in open(seed + ".cell", errors="replace"):
            l = raw.strip(); m = re.match(r"%block\s+(\S+)", l, re.I)
            if m:
                cur = m[1].lower(); continue
            if re.match(r"%endblock", l, re.I):
                cur = None; continue
            if cur == "species_pot" and l:
                p = l.split(); st["pot"][p[0]] = " ".join(p[1:])
            if cur == "species_mass" and l and not re.match(r"^(amu|kg|g|me)$", l, re.I):
                p = l.split(); st["mass"][p[0]] = p[1]
            if cur == "hubbard_u" and l:
                st["hub"].append(raw.rstrip())
            k = None if cur else re.match(r"kpoints?_mp_grid\s*[:=]?\s*(\d+)\s+(\d+)\s+(\d+)", l, re.I)
            if k:
                st["kgrid"] = [int(k[1]), int(k[2]), int(k[3])]
            if not cur and re.match(r"fix_com\s*[:=]?\s*true", l, re.I):
                st["fixcom"] = True
    if _vexists(seed + ".castep"):
        t = open(seed + ".castep", errors="replace").read(400000)
        g = lambda p: (re.search(p, t) or [None, None])[1]
        st["func_raw"] = (g(r"using functional\s*:\s*(.+)") or "").strip()
        st["func"] = next((k for p, k in FUNC_MAP if re.search(p, st["func_raw"])), "PBE")
        c = g(r"basis set cut-off\s*:\s*([\d.]+)"); st["cutoff"] = float(c) if c else None
        st["spin"] = bool(re.search(r"treating system as spin-polarized", t, re.I))
        st["fbc"] = g(r"finite basis set correction\s*:\s*(\S+)")
        e = g(r"total energy / atom convergence tol\.\s*:\s*([\d.E+-]+)"); st["etol"] = float(e) if e else None
        st["nonmetal"] = "Treating system as non-metallic" in t
        k = re.search(r"MP grid size for SCF calculation is\s+(\d+)\s+(\d+)\s+(\d+)", t)
        if k and not st["kgrid"]:
            st["kgrid"] = [int(k[1]), int(k[2]), int(k[3])]
    return st


def kgrid_like(lat, ref_lat, ref_grid):
    rl = lambda L: np.linalg.norm(np.linalg.inv(L), axis=0)
    if ref_grid is None:
        return [max(1, int(np.ceil(30 * b - 1e-6))) for b in rl(lat)]
    if np.allclose(lat, ref_lat, atol=1e-4):
        return list(ref_grid)
    leff = min(n / b for n, b in zip(ref_grid, rl(ref_lat)))
    return [max(1, int(np.ceil(leff * b - 1e-6))) for b in rl(lat)]


def element_structure(el):
    hexa = lambda a, c: np.array([[a, 0, 0], [-a / 2, a * np.sqrt(3) / 2, 0], [0, 0, c]])
    r = dict(metal=el in {**ELEM_REF["hcp"], **ELEM_REF["bcc"], **ELEM_REF["fcc"]}, mag=MAGMOM.get(el, 0), note="", molecule=False)
    if el in ELEM_REF["hcp"]:
        a, c = ELEM_REF["hcp"][el]; r.update(kind="hcp", lat=hexa(a, c), f=[[1 / 3, 2 / 3, .25], [2 / 3, 1 / 3, .75]])
    elif el in ELEM_REF["bcc"]:
        a = ELEM_REF["bcc"][el]; r.update(kind="bcc", lat=np.eye(3) * a, f=[[0, 0, 0], [.5, .5, .5]])
    elif el in ELEM_REF["fcc"]:
        a = ELEM_REF["fcc"][el]; r.update(kind="fcc", lat=np.eye(3) * a, f=[[0, 0, 0], [.5, .5, 0], [.5, 0, .5], [0, .5, .5]])
    elif el in ELEM_REF["diamante"]:
        a = ELEM_REF["diamante"][el]; b = [[0, 0, 0], [.5, .5, 0], [.5, 0, .5], [0, .5, .5]]
        r.update(kind="diamante", lat=np.eye(3) * a, f=b + [[x + .25 for x in p] for p in b])
    elif el in ELEM_REF["molecula"]:
        d = ELEM_REF["molecula"][el]; L = 12.0
        r.update(kind="molecula", lat=np.diag([L, L + .3, L + .6]), f=[[.5 - d / 2 / L, .5, .5], [.5 + d / 2 / L, .5, .5]], molecule=True, metal=False)
    else:
        r.update(kind="atomo", lat=np.diag([12, 12.3, 12.6]), f=[[.5, .5, .5]], molecule=True, metal=False,
                 note=f"Sem estrutura padrao para {el}: atomo isolado (NAO e o estado de referencia usual).")
    if el == "Mn":
        r["note"] = "O estado fundamental do Mn e o alfa-Mn (58 atomos); bcc e so uma aproximacao."
    return r


def write_cell_file(fn, title, lat, sp, fr, S, kg, spin=None, fixcell=False, symmetry=False, notes=()):
    with open(fn, "w", encoding="utf-8") as f:
        f.write(f"! {title}\n! Gerado pelo brumare.py (BrUMaRe)\n" + "".join(f"! {n}\n" for n in notes))
        f.write("\n%BLOCK LATTICE_CART\n   ANG\n" + "".join("  " + " ".join(f"{x:15.10f}" for x in r) + "\n" for r in lat) + "%ENDBLOCK LATTICE_CART\n\n")
        f.write("%BLOCK POSITIONS_FRAC\n")
        for i, (s, p) in enumerate(zip(sp, fr)):
            f.write(f"   {s:<4}" + " ".join(f"{x:16.12f}" for x in p) + (f"   SPIN={spin[i]:.2f}" if spin is not None and spin[i] else "") + "\n")
        f.write("%ENDBLOCK POSITIONS_FRAC\n\n" + f"KPOINTS_MP_GRID : {' '.join(map(str, kg))}\n")
        if symmetry:
            f.write("SYMMETRY_GENERATE\nSNAP_TO_SYMMETRY\n")
        if fixcell:
            f.write("FIX_ALL_CELL : true\n")
        if S["fixcom"]:
            f.write("FIX_COM : true\n")
        u = list(dict.fromkeys(sp))
        if any(s in S["pot"] for s in u):
            f.write("\n%BLOCK SPECIES_POT\n" + "".join(f"   {s:<6}{S['pot'][s]}\n" for s in u if s in S["pot"]) + "%ENDBLOCK SPECIES_POT\n")
        if any(s in S["mass"] for s in u):
            f.write("\n%BLOCK SPECIES_MASS\n   AMU\n" + "".join(f"   {s:<6}{S['mass'][s]}\n" for s in u if s in S["mass"]) + "%ENDBLOCK SPECIES_MASS\n")
        hub = [l for l in S["hub"] if any(l.strip().startswith(s) for s in u)]
        if hub:
            f.write("\n%BLOCK HUBBARD_U\n" + "\n".join(hub) + "\n%ENDBLOCK HUBBARD_U\n")


def write_param_file(fn, title, S, metal=False, spin=False, varcell=True, molecule=False, task="GeometryOptimization"):
    L = [f"! {title}", "! Mesmos funcional, corte, tolerancia e spin do calculo original. Confira antes de rodar.", "",
         f"TASK                    : {task}", f"XC_FUNCTIONAL           : {S['func']}",
         f"CUT_OFF_ENERGY          : {S['cutoff'] or 500} eV", f"SPIN_POLARIZED          : {'true' if spin else 'false'}",
         f"FINITE_BASIS_CORR       : {0 if not S['fbc'] or 'none' in S['fbc'].lower() else 2}",
         f"ELEC_ENERGY_TOL         : {(S['etol'] or 1e-7):.1e} eV", "MAX_SCF_CYCLES          : 300"]
    if metal:
        L += ["METALS_METHOD           : dm", "SMEARING_WIDTH          : 0.10 eV   ! metal: use a NB est. 0K energy (--energy auto)", "FIX_OCCUPANCY           : false"]
    elif molecule:
        L += ["METALS_METHOD           : dm", "SMEARING_WIDTH          : 0.05 eV", "FIX_OCCUPANCY           : false"]
    elif S["nonmetal"]:
        L += ["FIX_OCCUPANCY           : true    ! como no calculo original"]
    if task == "GeometryOptimization":
        L += ["GEOM_METHOD             : BFGS", "GEOM_MAX_ITER           : 300", "GEOM_ENERGY_TOL         : 5.0e-6 eV",
              "GEOM_FORCE_TOL          : 0.01 eV/ang", "GEOM_DISP_TOL           : 5.0e-4 ang"]
    else:
        L += ["! single point na geometria do defeito: mesma celula e corte => mesma grade FFT da densidade"]
    if varcell and task == "GeometryOptimization":
        L += ["GEOM_STRESS_TOL         : 0.02 GPa", "CALCULATE_STRESS        : true"]
    L += ["POPN_CALCULATE          : true", "WRITE_FORMATTED_DENSITY : true", "WRITE_CELL_STRUCTURE    : true", "NUM_DUMP_CYCLES         : 0"]
    open(fn, "w", encoding="utf-8").write("\n".join(L) + "\n")


def generate_references(seed, a, outdir):
    """Escreve .cell e .param das referencias em <outdir>/referencias_<seed>/."""
    dft = struct_of(seed)
    if dft is None:
        print(" AVISO: sem estrutura para gerar referencias."); return
    S = calc_settings(seed)
    res = analyze_defect(dft, struct_of(a.ref) if a.ref else None, a.center or "", a.shell_factor, a.rcut, a.rfar)
    base = dft["name"]; root = os.path.join(outdir, f"referencias_{base}"); os.makedirs(root, exist_ok=True)
    log = []

    def calc(name, title, lat, sp, fr, **kw):
        d = os.path.join(root, name); os.makedirs(d, exist_ok=True)
        kg = kw.pop("kgrid", None) or kgrid_like(np.array(lat), dft["lat"], S["kgrid"])
        spin = kw.pop("spin_on", S["spin"])
        write_cell_file(os.path.join(d, name + ".cell"), title, lat, sp, fr, S, kg, spin=kw.pop("spins", None),
                        fixcell=kw.get("fixcell", False), symmetry=kw.get("symmetry", False), notes=kw.get("notes", ()))
        write_param_file(os.path.join(d, name + ".param"), title, S, metal=kw.get("metal", False), spin=spin,
                         varcell=not kw.get("fixcell", False), molecule=kw.get("molecule", False), task=kw.get("task", "GeometryOptimization"))
        log.append((name, title, kw.get("use", ""), kw.get("notes", ()), kg))
    C = res.get("C")
    sp = list(dft["sp"]); fr = dft["f"]
    if C and "atom" in C and C["type"] in ("dopante", "substitucional", "intersticial"):
        host = C.get("host") or res.get("host")
        if C["type"] == "intersticial" or (C["type"] == "dopante" and "substitucional" not in res.get("site", "substitucional")):
            keep = [i for i in range(len(sp)) if i != C["atom"]]
            calc(f"{base}_puro", f"{base}: supercelula pura (sem {dft['label'][C['atom']]})", dft["lat"], [sp[i] for i in keep], fr[keep],
                 notes=["Relaxe: as posicoes partem do defeito."], use="--ref (estrutura pura)")
        else:
            s2 = list(sp); s2[C["atom"]] = host
            calc(f"{base}_puro", f"{base}: supercelula pura ({dft['label'][C['atom']]} -> {host})", dft["lat"], s2, fr,
                 notes=["Relaxe: as posicoes partem do defeito."], use="--ref (estrutura pura)")
            calc(f"{base}_dif_puro_fixo", f"{base}: hospedeiro puro na geometria do defeito ({dft['label'][C['atom']]} -> {host}), single point", dft["lat"], s2, fr,
                 task="SinglePoint", fixcell=True, notes=["Nao relaxe: mesmas posicoes e celula do defeito."], use="--field diff --subtract <...>_dif_puro_fixo.den_fmt")
        X = sp[C["atom"]]; keep = [i for i in range(len(sp)) if i != C["atom"]]
        calc(f"{base}_dif_sem_{X}", f"{base} sem {dft['label'][C['atom']]}, geometria do defeito, single point", dft["lat"], [sp[i] for i in keep], fr[keep],
             task="SinglePoint", fixcell=True, notes=["Nao relaxe: vacancia no sitio do dopante."], use="1o termo subtraido da densidade de ligacao")
        calc(f"{base}_dif_so_{X}", f"so o {dft['label'][C['atom']]} na mesma celula, single point", dft["lat"], [X], fr[[C["atom"]]],
             task="SinglePoint", fixcell=True, metal=True, spin_on=True, spins=[MAGMOM.get(X, 0)] if MAGMOM.get(X) else None,
             notes=["Atomo isolado na mesma celula, com alargamento e spin."], use="2o termo subtraido da densidade de ligacao")
    if "H" in dft["count"]:
        hs = [(n, bonds) for n, bonds in res.get("hop", []) if n["sp"] == "H"]
        if hs:
            near = max(hs, key=lambda x: np.mean([b["d"] for b in x[1]]) if x[1] else 0)[0]["j"]
            keep = [i for i in range(len(sp)) if i != near]
            calc(f"{base}_semH_perto", f"{base} sem {dft['label'][near]} (H ligado ao centro)", dft["lat"], [sp[i] for i in keep], fr[keep],
                 notes=["Um H a menos, perto do defeito."], use="--h-less (energia de remocao de H perto do defeito)")
        fc = C["f"] if C else np.full(3, .5)
        _, dd = mic_vec(fc, fr, dft["lat"]); far = max((i for i in range(len(sp)) if sp[i] == "H"), key=lambda i: dd[i])
        keep = [i for i in range(len(sp)) if i != far]
        calc(f"{base}_semH_longe", f"{base} sem {dft['label'][far]} (H a {dd[far]:.2f} A do centro)", dft["lat"], [sp[i] for i in keep], fr[keep],
             notes=["Um H a menos, longe do defeito."], use="compare a energia de remocao perto x longe")
    for el in dft["count"]:
        e = element_structure(el); n = len(e["f"])
        notes = [f"Molecula {el}2 com ligacao experimental, caixa de 12 A, ponto Gamma." if e["kind"] == "molecula" else f"Estrutura {e['kind']} experimental: sera relaxada."] + ([e["note"]] if e["note"] else [])
        calc(f"{el}_{el + '2' if e['kind'] == 'molecula' else e['kind']}", f"{el}: referencia elementar ({e['kind']})", e["lat"], [el] * n, e["f"],
             spins=[e["mag"]] * n if e["mag"] else None, spin_on=S["spin"] or e["mag"] > 0, metal=e["metal"], molecule=e["molecule"],
             fixcell=e["molecule"], symmetry=not e["molecule"], kgrid=[1, 1, 1] if e["molecule"] else None, notes=notes,
             use=f"mu({el}) = energia por atomo" + (" (= E(H2)/2)" if el == "H" else ""))
    with open(os.path.join(root, "LEIAME.txt"), "w", encoding="utf-8") as f:
        f.write(f"CALCULOS DE REFERENCIA para {base}\nFuncional {S['func']} ({S['func_raw']}), corte {S['cutoff']} eV, spin {'sim' if S['spin'] else 'nao'}, "
                f"malha original {S['kgrid']}\nPseudopotenciais: " + "; ".join(f"{k} {v}" for k, v in S["pot"].items()) + "\n\n")
        for name, title, use, notes, kg in log:
            f.write(f"* {name}  (malha k {' '.join(map(str, kg))})\n    {title}\n    uso: {use}\n" + "".join(f"    obs.: {n}\n" for n in notes) + "\n")
        f.write("Depois de rodar:\n  python3 brumare.py " + base + f" --ref {base}_puro --mu \"" +
                ",".join(f"{el}=@{el}_{el + '2' if element_structure(el)['kind'] == 'molecula' else element_structure(el)['kind']}" for el in dft["count"]) +
                f"\" --h-less {base}_semH_perto --energy auto\n(copie os .castep/.cell de cada pasta para a pasta da analise)\n")
    with open(os.path.join(root, "rodar_todas.sh"), "w") as f:
        f.write('#!/bin/bash\nCASTEP="mpirun -np ${NP:-16} castep.mpi"\nfor s in ' + " ".join(x[0] for x in log) + '; do\n  (cd "$s" && $CASTEP "$s")\ndone\n')
    print(f" -> {root}/  ({len(log)} calculos: {', '.join(x[0] for x in log)})")


# ------------------------------- densidade ---------------------------------- #
def read_chgcar(fn):
    """CHGCAR do VASP (formato 4 ou 5, ex.: o gerado pelo den2vasp). Valores em rho*V."""
    L = open(fn).read().splitlines(); k = 0
    title = L[0].strip(); scale = float(L[1].split()[0]); k = 2
    lat = np.array([[float(x) for x in L[k + i].split()[:3]] for i in range(3)]); k += 3
    lat = lat * (scale if scale > 0 else (-scale / abs(np.linalg.det(lat))) ** (1 / 3))
    t = L[k].split(); names = None
    if t[0][0].isalpha():
        names = [x.split("/")[0].split("_")[0] for x in t]; k += 1; t = L[k].split()
    counts = [int(x) for x in t]; k += 1
    if L[k].strip()[:1].lower() == "s":
        k += 1
    cart = L[k].strip()[:1].lower() in "ck"; k += 1
    nat = sum(counts)
    pos = np.array([[float(x) for x in L[k + i].split()[:3]] for i in range(nat)]); k += nat
    if cart:
        pos = pos @ np.linalg.inv(lat)
    sp = sum(([names[i] if names else ("X" if len(counts) == 1 else f"X{i + 1}")] * c for i, c in enumerate(counts)), [])
    while not L[k].strip():
        k += 1
    n = [int(x) for x in L[k].split()[:3]]; N = int(np.prod(n)); k += 1
    def block(k):
        vals = []
        while len(vals) < N and k < len(L):
            vals.extend(L[k].split()); k += 1
        if len(vals) < N:
            raise ValueError(f"CHGCAR incompleto: {len(vals)} de {N} valores")
        return np.array(vals[:N], float), k
    blocks = []; b0, k = block(k); blocks.append(b0)
    for j in range(k, len(L)):                       # 2o bloco (magnetizacao): mesma linha de grade
        p = L[j].split()
        if len(p) == 3 and all(x.isdigit() for x in p) and [int(x) for x in p] == n:
            try:
                b1, _ = block(j + 1); blocks.append(b1)
            except ValueError:
                pass
            break
    V = abs(np.linalg.det(lat))
    to3 = lambda b: b.reshape(n[2], n[1], n[0]).transpose(2, 1, 0)       # x mais rapido
    rho = to3(blocks[0]); out = dict(lat=lat, n=n, rho=rho / V, spin=None, V=V, Nel=rho.mean(), chg_sp=sp, chg_f=pos, title=title,
                                     species_known=names is not None)
    if len(blocks) > 1 and blocks[1].size == N:
        m = to3(blocks[1]); out.update(spin=m / V, Sint=m.mean(), Sabs=np.abs(m).mean())
    return out


def write_chgcar(fn, st, G, arr, arr2=None, title="BrUMaRe"):
    """CHGCAR formato VASP 5 (com elementos), valores rho*V, x mais rapido. Abre direto no VESTA."""
    order = list(dict.fromkeys(st["sp"]))
    groups = [[i for i, s in enumerate(st["sp"]) if s == e] for e in order]
    with open(fn, "w") as f:
        f.write(title[:78] + "\n   1.00000000000000\n")
        for r in G["lat"]:
            f.write("".join(f"{x:16.10f}" for x in r) + "\n")
        f.write("".join(f"{re.match(r'[A-Z][a-z]?', e)[0]:>5}" for e in order) + "\n" + "".join(f"{len(g):5d}" for g in groups) + "\nDirect\n")
        for g in groups:
            for i in g:
                f.write("".join(f"{x % 1:14.10f}" for x in st["f"][i]) + "\n")
        for A in [arr] + ([arr2] if arr2 is not None else []):
            f.write("\n " + " ".join(f"{x:4d}" for x in G["n"]) + "\n")
            v = (A * G["V"]).transpose(2, 1, 0).ravel()
            full = len(v) // 5 * 5
            np.savetxt(f, v[:full].reshape(-1, 5), fmt=" %17.10E", delimiter="")
            if len(v) > full:
                f.write("".join(f" {x:17.10E}" for x in v[full:]) + "\n")


def read_density(fn):
    """.den_fmt (CASTEP), .cube, CHGCAR (VASP) ou .RHO (SIESTA) -> dict(lat, n, rho (e/A^3), spin, V, Nel)."""
    v = _virt(fn)
    if v is not None:
        return v
    if fn.endswith(".RHO"):
        return read_siesta_rho(fn)
    b = os.path.basename(fn)
    if re.match(r"^(CHGCAR|CHG|AECCAR\d|PARCHG)", b, re.I) or b.lower().endswith((".vasp", ".chgcar")):
        return read_chgcar(fn)
    if fn.endswith(".cube"):
        L = open(fn).read().splitlines()
        h = L[2].split(); nat = abs(int(h[0]))
        ax = [list(map(float, L[i].split())) for i in (3, 4, 5)]
        n = [abs(int(x[0])) for x in ax]; unit = BOHR2ANG if ax[0][0] > 0 else 1.0
        lat = np.array([[v * abs(x[0]) * unit for v in x[1:4]] for x in ax])
        start = 6 + nat + (1 if int(h[0]) < 0 else 0)
        vals = np.array(" ".join(L[start:]).split(), float)[: n[0] * n[1] * n[2]].reshape(n) / BOHR2ANG ** 3
        V = abs(np.linalg.det(lat))
        return dict(lat=lat, n=n, rho=vals, spin=None, V=V, Nel=vals.mean() * V)
    txt = open(fn).read(); e = txt.index("END header")
    H = txt[:e].splitlines(); k = next(i for i, l in enumerate(H) if "Real Lattice" in l)
    lat = np.array([[float(x) for x in H[k + j].split()[:3]] for j in (1, 2, 3)])
    n = [int(x) for x in next(l for l in H if "fine FFT grid" in l).split()[:3]]
    body = txt[txt.index("\n", e) + 1:]
    data = np.array(body.split(), float)
    ncol = len(body.strip().splitlines()[0].split()); data = data.reshape(-1, ncol)
    idx = data[:, :3].astype(int) - 1; V = abs(np.linalg.det(lat))
    rho = np.zeros(n); rho[idx[:, 0], idx[:, 1], idx[:, 2]] = data[:, 3]
    spin = None
    if ncol > 4:
        spin = np.zeros(n); spin[idx[:, 0], idx[:, 1], idx[:, 2]] = data[:, 4]
    out = dict(lat=lat, n=n, rho=rho / V, spin=None if spin is None else spin / V, V=V, Nel=rho.mean())
    if spin is not None:
        out.update(Sint=spin.mean(), Sabs=np.abs(spin).mean())
    return out


def interp(G, arr, F):
    """Interpolacao trilinear periodica nos pontos fracionarios F (N,3)."""
    n = np.array(G["n"]); x = (np.mod(F, 1) * n)
    i0 = np.floor(x).astype(int) % n; d = x - np.floor(x); i1 = (i0 + 1) % n
    out = 0
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                w = (d[:, 0] if a else 1 - d[:, 0]) * (d[:, 1] if b else 1 - d[:, 1]) * (d[:, 2] if c else 1 - d[:, 2])
                out = out + w * arr[(i1 if a else i0)[:, 0], (i1 if b else i0)[:, 1], (i1 if c else i0)[:, 2]]
    return out


def density_report(seed, a, outdir):
    fn = a.density or next((seed + e for e in (".den_fmt", ".cube") if _vexists(seed + e)), None)
    if not fn or not _vexists(fn):
        dica = {"VASP": "sem CHGCAR na pasta do calculo (LCHARG = .TRUE.)", "SIESTA": f"sem {os.path.basename(seed)}.RHO (SaveRho true)"}.get(
            CODE["name"], f"sem {seed}.den_fmt (no .param: WRITE_FORMATTED_DENSITY : true)")
        print(f" Densidade: {dica}; analise de densidade ignorada.")
        planes_report(seed, a, outdir)              # celula e galeria so com os atomos
        return
    G = read_density(fn); st = struct_of(seed); base = os.path.basename(seed)
    if "chg_sp" in G:
        # posicoes e celula do proprio CHGCAR; do .cell so os elementos (mesma ordem), se o CHGCAR nao os tiver
        sp = list(G["chg_sp"])
        if not G["species_known"] and st is not None and len(st["sp"]) == len(sp):
            sp = list(st["sp"]); print(f" CHGCAR sem elementos (VASP 4): elementos tirados de {seed}.cell pela ordem; posicoes do CHGCAR")
        elif not G["species_known"]:
            print(" AVISO: CHGCAR sem elementos e sem .cell com o mesmo numero de atomos: atomos sairao como X")
        G["chg_sp"] = sp; st = None
    if st is None and "chg_sp" in G:
        cnt, lab = {}, []
        for s_ in G["chg_sp"]:
            cnt[s_] = cnt.get(s_, 0) + 1; lab.append(f"{s_}{cnt[s_]}")
        st = dict(lat=G["lat"], sp=list(G["chg_sp"]), f=G["chg_f"], label=lab, count=cnt, V=G["V"], masses={}, castep=dict(E={}, forces=None, info={}), name=base)

    out = lambda n: os.path.join(outdir, f"{base}_{n}")
    field = a.field
    if field in ("spin", "up", "down", "absm", "zeta"):
        if G["spin"] is None:
            print(" AVISO: densidade sem spin; usando rho."); field = "rho"; arr = G["rho"]
        else:
            r, m = G["rho"], G["spin"]
            arr = {"spin": m, "up": 0.5 * (r + m), "down": 0.5 * (r - m), "absm": np.abs(m),
                   "zeta": np.where(r > 1e-3, np.clip(m / np.maximum(r, 1e-12), -1, 1), 0)}[field]
    else:
        arr = G["rho"].copy()
    sgn = -1.0 if getattr(a, "diff_sign", "defeito-puro") == "puro-defeito" else 1.0
    if field == "diff":
        if not (a.subtract or "").strip():
            print(" AVISO: --field diff sem --subtract: informe a densidade pura, ex: --subtract mgh2_puro.den_fmt")
        for other in (a.subtract or "").split(","):
            if other.strip():
                H = read_density(other.strip())
                if list(H["n"]) != list(G["n"]):
                    fr_ = (np.indices(G["n"]).reshape(3, -1).T / np.array(G["n"]))
                    arr -= interp(H, H["rho"], fr_).reshape(G["n"])
                    print(f" Grade de {other} ({H['n']}) reamostrada na grade {G['n']} (interpolacao trilinear)")
                else:
                    arr -= H["rho"]
                if abs(H["V"] - G["V"]) / G["V"] > 0.005:
                    print(f" AVISO: volumes diferentes ({G['V']:.1f} vs {H['V']:.1f} A^3): diferenca feita em coordenadas fracionarias")
        arr = sgn * arr
        dv = G["V"] / arr.size
        print(f" Delta rho ({'puro - defeito' if sgn < 0 else 'defeito - puro'}): ganho {arr[arr > 0].sum() * dv:.3f} e, perda {arr[arr < 0].sum() * dv:.3f} e, saldo {arr.sum() * dv:.3f} e")
    lab = {"rho": r"$\rho$ (e/Å$^3$)", "up": r"$\rho_\uparrow$ (e/Å$^3$)", "down": r"$\rho_\downarrow$ (e/Å$^3$)", "spin": r"$\rho_\uparrow-\rho_\downarrow$ (e/Å$^3$)",
           "absm": r"$|\rho_\uparrow-\rho_\downarrow|$ (e/Å$^3$)", "zeta": r"$\zeta$", "diff": r"$\Delta\rho$ (e/Å$^3$)"}[field]
    print(f" Densidade {os.path.basename(_VNAME.get(fn, fn))}: grade {G['n']}, eletrons integrados {G['Nel']:.3f}" + (f", spin {G['Sint']:.4f} / |spin| {G['Sabs']:.4f}" if G.get("Sint") is not None else ""))
    if st is None:
        st = dict(lat=G["lat"], sp=[], f=np.zeros((0, 3)), label=[])
    # plano
    def cart(i):
        return st["f"][i] @ st["lat"]

    def near_img(i, j):
        v, _ = mic_vec(st["f"][i], st["f"][j:j + 1], st["lat"]); return cart(i) + v[0]
    res = analyze_defect(st, None, "") if st["sp"] else {}
    C = res.get("C")
    ci = C["atom"] if C and "atom" in C else 0
    nb = neighbors(st, st["f"][ci], 5, ci) if st["sp"] else []
    if a.plane and a.plane.lower().startswith("hkl"):
        m = re.match(r"hkl\s*[:=]?\s*([-\d\s]+)(?:@\s*(\S+))?", a.plane, re.I)
        hkl = parse_hkl(m[1]); at = m[2]
        o = cart(st["label"].index(at)) if at in st.get("label", []) else (cart(ci) if st["sp"] else np.array([.5, .5, .5]) @ st["lat"])
        Bp = st["lat"] if a.hkl_base == "super" else st["lat"] / np.array(detect_multiplicity(st))[:, None]
        plo, _sec = oriented_plane(st, Bp, hkl, o)
        e1, e2, nrm = plo["e1"], plo["e2"], plo["n"]; ttl = f"plano {miller_str(hkl)}"
    else:
        labs = [x for x in re.split(r"[\s,;]+", a.plane or "") if x]
        if len(labs) >= 3:
            ii = [st["label"].index(x) for x in labs[:3]]
        else:
            v1 = nb[0]["v"]; third = next((x for x in nb[1:] if np.linalg.norm(np.cross(v1, x["v"])) / np.linalg.norm(v1) / np.linalg.norm(x["v"]) > .3), nb[1])
            ii = [ci, nb[0]["j"], third["j"]]
        p1, p2, p3 = cart(ii[0]), near_img(ii[0], ii[1]), near_img(ii[0], ii[2])
        e1 = (p2 - p1) / np.linalg.norm(p2 - p1); nrm = np.cross(p2 - p1, p3 - p1); nrm /= np.linalg.norm(nrm); e2 = np.cross(nrm, e1)
        o = (p1 + p2 + p3) / 3; ttl = "plano " + "-".join(st["label"][i] for i in ii)
    if st["sp"]:
        planes_report(seed, a, outdir, G, arr, field, st)
        if a.voronoi != "off":
            voronoi_report(seed, a, G, st, out("cargas_voronoi.txt" if field != "diff" else "transferencia_carga_voronoi.txt"), arr if field == "diff" else None)
        if field == "diff":
            diff_report(base, a, G, st, arr, out, sgn)
        if getattr(a, "bader", False) and field != "diff":
            zion = _virt(seed + ".castep", "zion") or {}
            if not zion and _vexists(seed + ".castep"):
                zion = {m[1]: float(m[2]) for m in re.finditer(r"Element:\s+(\S+)\s+Ionic charge:\s+([\d.]+)", open(seed + ".castep", errors="replace").read(300000))}
            bader_report(seed, G, st, out("bader.txt"), zion)
    W, N = a.plane_size, 181; u = np.linspace(-W / 2, W / 2, N)
    P = o + u[None, :, None] * e1 + u[:, None, None] * e2
    Z = interp(G, arr, (P.reshape(-1, 3) @ np.linalg.inv(G["lat"]))).reshape(N, N)
    write_table(out(f"densidade_corte2d_{field}.dat"), [f"Corte 2D {ttl}; campo {field} (e/A^3)", f"origem {o.round(4)} e1 {e1.round(4)} e2 {e2.round(4)}"],
                ["x(A)", "y(A)", "valor"], np.column_stack([np.tile(u, N), np.repeat(u, N), Z.ravel()]), fmt="%.6e")
    fig, ax = plt.subplots(figsize=(a.width * 0.85, a.width * 0.75))
    if field == "rho":
        im = ax.contourf(u, u, np.log10(np.maximum(Z, 1e-4)), 40, cmap="viridis"); cb = fig.colorbar(im, ax=ax); cb.set_label(r"log$_{10}\,\rho$ (e/Å$^3$)")
        ax.contour(u, u, np.log10(np.maximum(Z, 1e-4)), 20, colors="k", linewidths=.4, alpha=.4)
    else:
        m = np.abs(Z).max() or 1; lv = np.linspace(-m, m, 41); im = ax.contourf(u, u, Z, lv, cmap="RdBu_r"); cb = fig.colorbar(im, ax=ax); cb.set_label(lab)
        ax.contour(u, u, Z, 20, colors="k", linewidths=.4, alpha=.4)
    for i in range(len(st["sp"])):
        for img in IMG:
            r = (st["f"][i] + img) @ st["lat"] - o
            if abs(r @ nrm) < .6 and abs(r @ e1) <= W / 2 and abs(r @ e2) <= W / 2:
                ax.plot(r @ e1, r @ e2, "o", ms=6, mfc="w", mec="k"); ax.annotate(st["label"][i], (r @ e1, r @ e2), xytext=(3, 3), textcoords="offset points", fontsize=a.fontsize - 5, color="w" if field == "rho" else "k")
    ax.set_aspect("equal"); ax.set_xlabel("x no plano (Å)"); ax.set_ylabel("y no plano (Å)"); ax.set_title(f"{base}: {ttl}", fontsize=a.fontsize)
    fig.savefig(out(f"densidade_corte2d_{field}.{a.format}"), dpi=a.dpi); plt.close(fig)
    print(f" -> {out(f'densidade_corte2d_{field}.{a.format}')}")
    # perfil
    if st["sp"]:
        labs = [x for x in re.split(r"[\s,;]+", a.line or "") if x]
        ia, ib = (st["label"].index(labs[0]), st["label"].index(labs[1])) if len(labs) >= 2 else (ci, nb[0]["j"])
        pA, pB = cart(ia), near_img(ia, ib); s_ = np.linspace(0, 1, 400); d = np.linalg.norm(pB - pA)
        v = interp(G, arr, ((pA + np.outer(s_, pB - pA)) @ np.linalg.inv(G["lat"])))
        write_table(out(f"perfil_{st['label'][ia]}_{st['label'][ib]}_{field}.dat"), [f"Perfil {st['label'][ia]} -> {st['label'][ib]} ({d:.4f} A)"],
                    ["distancia(A)", "valor(e/A3)"], np.column_stack([s_ * d, v]), fmt="%.6e")
        fig, ax = plt.subplots(figsize=(a.width * 0.8, a.height * 0.6))
        ax.plot(s_ * d, v, lw=2)
        if field == "rho":
            k = 40 + int(np.argmin(v[40:360])); ax.plot(s_[k] * d, v[k], "D", color="#D55E00", label=f"mínimo {v[k]:.4g} e/Å³ a {s_[k] * d:.3f} Å"); ax.legend(fontsize=a.fontsize - 3)
            print(f"   minimo ao longo de {st['label'][ia]}-{st['label'][ib]}: {v[k]:.4g} e/A^3 a {s_[k] * d:.3f} A")
        ax.set_xlabel(f"distância a partir de {st['label'][ia]} (Å)"); ax.set_ylabel(lab)
        fig.savefig(out(f"perfil_{st['label'][ia]}_{st['label'][ib]}_{field}.{a.format}"), dpi=a.dpi); plt.close(fig)
    if a.chgcar and st["sp"]:
        two = G["spin"] if (field == "rho" and G["spin"] is not None and a.chgcar_spin) else None
        nm = out("CHGCAR.vasp" if field == "rho" else f"{field}_CHGCAR.vasp")
        write_chgcar(nm, st, G, arr, two, f"{base} {dict(rho='densidade de carga', spin='densidade de spin', diff='diferenca de densidade')[field]} (BrUMaRe)")
        print(f" -> {nm}  (CHGCAR VASP 5 com elementos: abra no VESTA)")
    if a.vesta and st["sp"]:
        vesta_export(base, a, G, st, out, sgn)
    if a.xsf and st["sp"]:
        n1, n2, n3 = G["n"]; ext = np.pad(arr, ((0, 1), (0, 1), (0, 1)), mode="wrap")
        with open(out(f"densidade_{field}.xsf"), "w") as f:
            f.write("CRYSTAL\nPRIMVEC\n" + "".join(" ".join(f"{x:.8f}" for x in r) + "\n" for r in G["lat"]) + f"PRIMCOORD\n{len(st['sp'])} 1\n")
            f.write("".join(f"{re.match(r'[A-Z][a-z]?', s)[0]} " + " ".join(f"{x:.8f}" for x in (fr @ st["lat"])) + "\n" for s, fr in zip(st["sp"], st["f"])))
            f.write(f"BEGIN_BLOCK_DATAGRID_3D\ndensidade\nBEGIN_DATAGRID_3D_{field}\n{n1 + 1} {n2 + 1} {n3 + 1}\n0 0 0\n" + "".join(" ".join(f"{x:.8f}" for x in r) + "\n" for r in G["lat"]))
            np.savetxt(f, ext.transpose(2, 1, 0).ravel().reshape(-1, 1), fmt="%.6e")
            f.write("END_DATAGRID_3D\nEND_BLOCK_DATAGRID_3D\n")
        print(f" -> {out(f'densidade_{field}.xsf')}  (abra no VESTA para a isosuperficie 3D)")


# =========================================================================== #
#        PLANOS (h k l), SUPERCELULA E INFORMACOES DA CELULA                  #
# =========================================================================== #
def miller_str(v, br="()"):
    return br[0] + "".join((f"{-x}\u0304" if x < 0 else str(x)) for x in v) + br[1]


def parse_hkl(t):
    t = re.sub(r"[()\[\]{}]", "", str(t)).strip()
    v = [int(x) for x in re.split(r"[\s,]+", t)] if re.search(r"[\s,]", t) else [int(x) for x in re.findall(r"-?\d", t)]
    if len(v) != 3 or not any(v):
        raise ValueError(f"indices (h k l) invalidos: {t}")
    return v


def detect_multiplicity(st):
    m = [1, 1, 1]; F, L, sp = st["f"], st["lat"], np.array(st["sp"]); N = len(sp)
    for ax in range(3):
        for k in range(8, 1, -1):
            if np.linalg.norm(L[ax]) / k < 1.2:
                continue
            G = F.copy(); G[:, ax] += 1 / k; ok = 0
            for s in set(sp):
                A, Bm = G[sp == s], F[sp == s]
                d = A[:, None, :] - Bm[None]; d -= np.round(d)
                ok += (np.linalg.norm(d @ L, axis=2).min(axis=1) < 0.45).sum()
            if ok >= 0.9 * N:
                m[ax] = k; break
    return m


def plane_hkl(B, hkl, p0, off=0.0):
    R = np.linalg.inv(B).T; n = np.array(hkl, float) @ R; d = 1 / np.linalg.norm(n); n = n * d
    cand = []
    for u in range(-4, 5):
        for v in range(-4, 5):
            for w in range(-4, 5):
                if (u, v, w) == (0, 0, 0) or hkl[0] * u + hkl[1] * v + hkl[2] * w or np.gcd.reduce([u, v, w]) != 1:
                    continue
                c = np.array([u, v, w]) @ B; cand.append(((round(np.linalg.norm(c), 6), sum(x < 0 for x in (u, v, w)), [x != 0 for x in (u, v, w)].index(True)), [u, v, w], c))
    cand.sort(key=lambda x: x[0]); a1 = cand[0]
    a2 = min((c for c in cand if abs(c[2] @ a1[2]) / np.linalg.norm(c[2]) / np.linalg.norm(a1[2]) < 0.999),
             key=lambda c: abs(c[2] @ a1[2]) / np.linalg.norm(c[2]) / np.linalg.norm(a1[2]) * 10 + c[0][0] * 0.01)
    e1 = a1[2] / np.linalg.norm(a1[2]); e2 = np.cross(n, e1)
    if e2 @ a2[2] < 0:
        e2 = -e2
    perp = abs(a2[2] @ a1[2]) / np.linalg.norm(a2[2]) / np.linalg.norm(a1[2]) < 0.02
    return dict(o=p0 + n * off, e1=e1, e2=e2, n=n, d=d, lab1=miller_str(a1[1], "[]"), lab2=miller_str(a2[1], "[]") if perp else "⊥ " + miller_str(a1[1], "[]"))


def cell_section(L, pl):
    C = [np.array([i, j, k], float) for i in (0, 1) for j in (0, 1) for k in (0, 1)]; pts = []
    for a in range(8):
        for b in range(a + 1, 8):
            if np.abs(C[a] - C[b]).sum() != 1:
                continue
            ca, cb = C[a] @ L, C[b] @ L; s0, s1 = pl["n"] @ (ca - pl["o"]), pl["n"] @ (cb - pl["o"])
            if (s0 > 1e-9 and s1 > 1e-9) or (s0 < -1e-9 and s1 < -1e-9) or abs(s0 - s1) < 1e-12:
                continue
            r = ca + (cb - ca) * s0 / (s0 - s1) - pl["o"]; q = (r @ pl["e1"], r @ pl["e2"])
            if all(np.hypot(q[0] - x[0], q[1] - x[1]) > 1e-6 for x in pts):
                pts.append(q)
    if len(pts) < 3:
        return None
    P = np.array(pts); c = P.mean(0); P = P[np.argsort(np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0]))]
    A = 0.5 * abs(np.dot(P[:, 0], np.roll(P[:, 1], -1)) - np.dot(P[:, 1], np.roll(P[:, 0], -1)))
    return dict(poly=P, area=A, xr=(P[:, 0].min(), P[:, 0].max()), yr=(P[:, 1].min(), P[:, 1].max()))


def oriented_plane(st, B, hkl, p0, off=0.0):
    pl = plane_hkl(B, hkl, p0, off); sec = cell_section(st["lat"], pl)
    if sec is not None and (sec["yr"][1] - sec["yr"][0]) > 1.05 * (sec["xr"][1] - sec["xr"][0]):
        pl = dict(pl, e1=pl["e2"], e2=pl["e1"], n=-pl["n"], lab1=pl["lab2"], lab2=pl["lab1"]); sec = cell_section(st["lat"], pl)
    return pl, sec


def atoms_in_slab(st, pl, xr, yr, tol):
    out = []
    for i in range(len(st["sp"])):
        for img in np.array([[a, b, c] for a in (-2, -1, 0, 1, 2) for b in (-2, -1, 0, 1, 2) for c in (-2, -1, 0, 1, 2)]):
            r = (st["f"][i] + img) @ st["lat"] - pl["o"]; x, y, h = r @ pl["e1"], r @ pl["e2"], r @ pl["n"]
            if abs(h) <= tol and xr[0] - .3 <= x <= xr[1] + .3 and yr[0] - .3 <= y <= yr[1] + .3:
                out.append((st["label"][i], st["sp"][i], x, y))
    return out


def cell_report(st, out):
    """estrutura.txt: celula, supercelula detectada, densidade, coordenacao, distancias e d_hkl."""
    m = detect_multiplicity(st); B = st["lat"] / np.array(m)[:, None]; nb = int(np.prod(m))
    ab = lambda L: (np.linalg.norm(L, axis=1), [np.degrees(np.arccos(L[i] @ L[j] / np.linalg.norm(L[i]) / np.linalg.norm(L[j]))) for i, j in ((1, 2), (0, 2), (0, 1))])
    (l1, g1), (l2, g2) = ab(st["lat"]), ab(B)
    mass = sum(st["masses"].get(s, MASS.get(re.match(r"[A-Z][a-z]?", s)[0], 0)) for s in st["sp"])
    nH = st["count"].get("H", 0); W = []; w = W.append
    w(f"CELULA E SUPERCELULA: {st['name']}"); w("=" * 72)
    w("Composicao: " + " ".join(f"{k}{v}" for k, v in st["count"].items()) + f"  ({len(st['sp'])} atomos)")
    w(f"Supercelula: a,b,c = {l1.round(4)} A; alfa,beta,gama = {np.round(g1, 2)}; V = {st['V']:.3f} A^3")
    w(f"Multiplicidade detectada: {m[0]} x {m[1]} x {m[2]} ({nb} celulas base)")
    w(f"Celula base: a,b,c = {l2.round(4)} A; angulos = {np.round(g2, 2)}; V = {st['V'] / nb:.3f} A^3; c/a = {l2[2] / l2[0]:.4f}")
    w("Atomos por celula base (media): " + ", ".join(f"{k} {v / nb:.3f}" for k, v in st["count"].items()))
    w(f"Densidade: {mass * 1.66053907e-24 / (st['V'] * 1e-24):.4f} g/cm3")
    if nH:
        w(f"Hidrogenio: {100 * nH * MASS['H'] / mass:.3f} % em massa; {nH * MASS['H'] * 1.66053907e-27 / (st['V'] * 1e-30):.1f} kg H/m3")
    w(""); w("COORDENACAO (1a camada, d_min x 1.25)"); w("-" * 72)
    coord, pair, homo = {}, {}, {}
    for i, s in enumerate(st["sp"]):
        nbs = neighbors(st, st["f"][i], 4.5, i); sh = first_shell(nbs, 1.25)
        c = coord.setdefault(s, [0, 0, {}]); c[0] += 1; c[1] += len(sh)
        for x in sh:
            c[2][x["sp"]] = c[2].get(x["sp"], 0) + 1; pair.setdefault("-".join(sorted([s, x["sp"]])), []).append(x["d"])
        same = next((x for x in nbs if x["sp"] == s), None)
        if same:
            homo[s] = min(homo.get(s, 99), same["d"])
    for s, (n, cn, comp) in coord.items():
        w(f"  {s:<4} {n:4d} atomos  NC = {cn / n:5.2f}  (" + " + ".join(f"{v / n:.2f} {k}" for k, v in comp.items()) + ")" + (f"  {s}-{s} min {homo[s]:.4f} A" if s in homo else ""))
    w(""); w("DISTANCIAS DE 1a CAMADA POR PAR (min / media / max, A)"); w("-" * 72)
    for k, d in pair.items():
        w(f"  {k:<8} {min(d):.4f} / {np.mean(d):.4f} / {max(d):.4f}")
    w(""); w("ESPACAMENTOS INTERPLANARES (A)        celula base     indices da supercelula"); w("-" * 72)
    for t in ["1 1 0", "-1 1 0", "0 0 1", "1 0 0", "0 1 0", "1 0 1", "0 1 1", "1 1 1", "-1 1 1", "2 1 0"]:
        hk = parse_hkl(t); w(f"  {miller_str(hk):<12}{1 / np.linalg.norm(np.array(hk) @ np.linalg.inv(B).T):18.4f}{1 / np.linalg.norm(np.array(hk) @ np.linalg.inv(st['lat']).T):22.4f}")
    open(out, "w", encoding="utf-8").write("\n".join(W) + "\n")
    print(f" -> {out}  (supercelula {m[0]}x{m[1]}x{m[2]} detectada)")
    return m, B


def planes_report(seed, a, outdir, G=None, arr=None, field="rho", st=None):
    """Galeria de planos (h k l) pelo defeito: figura e um .dat por plano."""
    st = st or struct_of(seed)
    if st is None:
        return
    base = os.path.basename(seed); out = lambda n: os.path.join(outdir, f"{base}_{n}")
    m, Bb = cell_report(st, out("estrutura.txt"))
    if not a.planes:
        return
    B = st["lat"] if a.hkl_base == "super" else Bb
    lst = [parse_hkl(x) for x in (a.planes if a.planes.lower() != "todos" else "1 1 0;-1 1 0;0 0 1;1 0 0;0 1 0;1 0 1;0 1 1;1 1 1").split(";") if x.strip()]
    res = analyze_defect(st, None, ""); C = res.get("C")
    p0 = st["f"][C["atom"]] @ st["lat"] if C and "atom" in C else np.full(3, .5) @ st["lat"]
    nc = min(4, len(lst)); nr = int(np.ceil(len(lst) / nc))
    fig, axs = plt.subplots(nr, nc, figsize=(4.2 * nc, 3.6 * nr), squeeze=False)
    for ax in axs.ravel()[len(lst):]:
        ax.axis("off")
    zs = []
    for hk, ax in zip(lst, axs.ravel()):
        pl, sec = oriented_plane(st, B, hk, p0)
        xr = (sec["xr"][0] - .3, sec["xr"][1] + .3) if sec else (-4, 4); yr = (sec["yr"][0] - .3, sec["yr"][1] + .3) if sec else (-4, 4)
        if G is not None:
            sc = max(xr[1] - xr[0], yr[1] - yr[0]) / 179; nx, ny = int((xr[1] - xr[0]) / sc) + 1, int((yr[1] - yr[0]) / sc) + 1
            x, y = np.linspace(*xr, nx), np.linspace(*yr, ny)
            P = pl["o"] + x[None, :, None] * pl["e1"] + y[:, None, None] * pl["e2"]
            Z = interp(G, arr, P.reshape(-1, 3) @ np.linalg.inv(G["lat"])).reshape(ny, nx)
            write_table(out(f"plano_{''.join(('m' + str(-v)) if v < 0 else str(v) for v in hk)}_{field}.dat"),
                        [f"Plano {miller_str(hk)} ({'supercelula' if a.hkl_base == 'super' else 'celula base'}) por {res['C']['label'] if C else 'centro'}; x = {pl['lab1']}, y = {pl['lab2']}; d = {pl['d']:.4f} A"],
                        ["x(A)", "y(A)", "valor"], np.column_stack([np.tile(x, ny), np.repeat(y, nx), Z.ravel()]), fmt="%.6e")
            if field == "rho":
                im = ax.imshow(np.log10(np.maximum(Z, 1e-3)), origin="lower", extent=(*xr, *yr), cmap="viridis", vmin=-1.6)
            else:
                mm = np.abs(Z).max() or 1; im = ax.imshow(Z, origin="lower", extent=(*xr, *yr), cmap="RdBu_r", vmin=-mm, vmax=mm)
            zs.append(im)
        if sec is not None:
            q = np.vstack([sec["poly"], sec["poly"][:1]]); ax.plot(q[:, 0], q[:, 1], "k:", lw=1)
        for lab, s, x_, y_ in atoms_in_slab(st, pl, xr, yr, 0.6):
            ax.plot(x_, y_, "o", ms=3 + 4 * COVR.get(re.match(r"[A-Z][a-z]?", s)[0], 1), mfc=CPKC.get(s, "#ff1493"), mec="k", mew=.5)
            if s not in ("H", "Mg") or (abs(x_) < .01 and abs(y_) < .01):
                ax.annotate(lab, (x_, y_), xytext=(2, 3), textcoords="offset points", fontsize=7, color="w" if G is not None and field == "rho" else "k")
        ax.set_xlim(*xr); ax.set_ylim(*yr); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{miller_str(hk)}  d = {pl['d']:.3f} Å\n→ {pl['lab1']}   ↑ {pl['lab2']}", fontsize=9)
    if zs:
        cb = fig.colorbar(zs[0], ax=axs.ravel().tolist(), shrink=.8); cb.set_label(r"log$_{10}\,\rho$ (e/Å$^3$)" if field == "rho" else "valor (e/Å$^3$)")
    fig.suptitle(f"{base}: planos pela posição {C['label'] if C else 'centro'}", fontsize=11)
    nm = out(f"planos_{field if G is not None else 'estrutura'}.{a.format}")
    fig.savefig(nm, dpi=a.dpi); plt.close(fig)
    print(f" -> {nm}  ({len(lst)} planos)")


COVR = dict(H=0.31, Li=1.28, B=0.84, C=0.76, N=0.71, O=0.66, Na=1.66, Mg=1.41, Al=1.21, Si=1.11, Ti=1.60, V=1.53, Cr=1.39, Mn=1.39, Fe=1.32, Co=1.26, Ni=1.24, Cu=1.32, Zn=1.22, Zr=1.75, Nb=1.64, Pd=1.39)
CPKC = dict(H="#d9d9d9", Mg="#8aff00", Fe="#e06633", Ni="#50d050", Co="#f090a0", Ti="#bfc2c7", Al="#bfa6a6", V="#a6a6ab", Cr="#8a99c7", Mn="#9c7ac7", Cu="#c88033", Zn="#7d80b0", O="#ff0d0d", C="#909090", N="#3050f8", Li="#cc80ff", Na="#ab5cf2")


def voronoi_report(seed, a, G, st, fn, delta=None):
    USADOS.add("voronoi1908")
    """Eletrons e momento por atomo (Voronoi radical ou comum), carga liquida com Z do .castep."""
    n = np.array(G["n"]); L = G["lat"]; F = np.mod(st["f"], 1.0)
    R2 = np.array([(COVR.get(re.match(r"[A-Z][a-z]?", s)[0], 1.2) if a.voronoi == "radical" else 0) ** 2 for s in st["sp"]])
    Gm = L @ L.T
    idx = np.indices(n).reshape(3, -1).T; fr = idx / n
    owner = np.empty(len(fr), int)
    for c in range(0, len(fr), 20000):
        d = fr[c:c + 20000, None, :] - F[None]; d -= np.round(d)
        d2 = np.einsum("pai,ij,paj->pa", d, Gm, d) - R2[None]
        owner[c:c + 20000] = np.argmin(d2, axis=1)
    rho = (G["rho"] if delta is None else delta)[idx[:, 0], idx[:, 1], idx[:, 2]]; dv = G["V"] / len(fr)
    Q = np.bincount(owner, rho, len(st["sp"])) * dv
    M = np.bincount(owner, G["spin"][idx[:, 0], idx[:, 1], idx[:, 2]], len(st["sp"])) * dv if (G["spin"] is not None and delta is None) else None
    Vv = np.bincount(owner, None, len(st["sp"])) * dv
    zion = {}
    if _virt(seed + ".castep", "zion"):
        zion.update(_virt(seed + ".castep", "zion"))
    elif _vexists(seed + ".castep"):
        for m in re.finditer(r"Element:\s+(\S+)\s+Ionic charge:\s+([\d.]+)", open(seed + ".castep", errors="replace").read(300000)):
            zion[m[1]] = float(m[2])
    res = analyze_defect(st, None, ""); C = res.get("C"); show = []
    if C and "atom" in C:
        show = [C["atom"]] + [x["j"] for x in res["shell"]]
    if delta is not None:
        zion = {}
        W = [f"TRANSFERENCIA DE CARGA POR ATOMO (integral de Delta rho na celula de Voronoi): {st['name']}", "=" * 72,
             "Delta eletrons > 0: o atomo ganhou eletrons em relacao a referencia subtraida.", f"{'atomo':<14}{'Delta e':>10}"]
        for i in show:
            W.append(f"{st['label'][i]:<14}{Q[i]:+10.4f}")
        for s in dict.fromkeys(st["sp"]):
            ii = [i for i, x in enumerate(st["sp"]) if x == s]; W.append(f"{s + ' (soma)':<14}{Q[ii].sum():+10.4f}")
        W.append(f"Saldo: {Q.sum():+.3f} eletrons"); open(fn, "w", encoding="utf-8").write("\n".join(W) + "\n"); print(f" -> {fn}"); return
    W = [f"CARGAS E MOMENTOS POR ATOMO ({'Voronoi radical' if a.voronoi == 'radical' else 'Voronoi comum'}): {st['name']}", "=" * 72,
         f"{'atomo':<14}{'eletrons':>10}{'Z':>7}{'carga':>9}" + (f"{'momento':>10}" if M is not None else "") + f"{'vol (A3)':>10}"]
    def line(lab, q, z, m, v):
        return f"{lab:<14}{q:10.3f}{z:7.2f}{z - q:9.3f}" + (f"{m:10.4f}" if M is not None else "") + f"{v:10.2f}" if np.isfinite(z) else f"{lab:<14}{q:10.3f}{'-':>7}{'-':>9}" + (f"{m:10.4f}" if M is not None else "") + f"{v:10.2f}"
    for i in show:
        W.append(line(st["label"][i], Q[i], zion.get(re.match(r"[A-Z][a-z]?", st["sp"][i])[0], np.nan), M[i] if M is not None else 0, Vv[i]))
    for s in dict.fromkeys(st["sp"]):
        ii = [i for i, x in enumerate(st["sp"]) if x == s]
        W.append(line(f"{s} (media {len(ii)})", Q[ii].mean(), zion.get(re.match(r"[A-Z][a-z]?", s)[0], np.nan), M[ii].mean() if M is not None else 0, Vv[ii].mean()))
    W.append(f"Soma: {Q.sum():.3f} eletrons" + (f", momento {M.sum():.4f} muB" if M is not None else "") + ". Estimativa: para valores quantitativos use Bader (com o CHGCAR exportado).")
    open(fn, "w", encoding="utf-8").write("\n".join(W) + "\n")
    print(f" -> {fn}")


def density_component(G, k):
    """rho, up, down ou spin (e/A^3) de uma densidade lida."""
    if k == "rho":
        return G["rho"]
    if G["spin"] is None:
        raise ValueError("densidade sem spin")
    return {"spin": G["spin"], "up": 0.5 * (G["rho"] + G["spin"]), "down": 0.5 * (G["rho"] - G["spin"])}[k]


def on_grid(G, H, arr):
    """arr (definido na grade de H) na grade de G, por interpolacao trilinear se for preciso."""
    if list(H["n"]) == list(G["n"]):
        return arr
    fr = np.indices(G["n"]).reshape(3, -1).T / np.array(G["n"])
    return interp(H, arr, fr).reshape(G["n"])


def vesta_export(base, a, G, st, out, sgn):
    USADOS.add("momma2011vesta")
    """CHGCARs para o VESTA: componentes do proprio calculo e diferencas contra --subtract."""
    refs = [read_density(x.strip()) for x in (a.subtract or "").split(",") if x.strip()]
    tag = "puro_menos_defeito" if sgn < 0 else "defeito_menos_puro"
    names = dict(rho="rho", up="rho_up", down="rho_down", spin="spin")
    log = []
    for k in ("rho", "up", "down", "spin"):
        try:
            A = density_component(G, k)
        except ValueError:
            continue
        fn = out(f"{names[k]}_CHGCAR.vasp"); write_chgcar(fn, st, G, A, None, f"{base} {names[k]} (BrUMaRe)"); log.append(fn)
        if refs:
            try:
                D = A.copy()
                for H in refs:
                    D = D - on_grid(G, H, density_component(H, k))
            except ValueError:
                continue
            D = sgn * D
            fn = out(f"delta_{names[k]}_{tag}_CHGCAR.vasp")
            write_chgcar(fn, st, G, D, None, f"{base} delta {names[k]} {tag.replace('_', ' ')} (BrUMaRe)")
            log.append(f"{fn}  (faixa {D.min():.4g} a {D.max():.4g} e/A^3)")
    with open(out("LEIAME_VESTA.txt"), "w", encoding="utf-8") as fh:
        fh.write("VISUALIZACAO NO VESTA (BrUMaRe)\nArquivos CHGCAR em formato VASP 5 (com elementos), valores rho*V.\n"
                 f"Diferencas: {'rho(puro) - rho(defeito)' if sgn < 0 else 'rho(defeito) - rho(puro)'}; referencia reamostrada se a grade for diferente.\n\n"
                 + "\n".join("  " + x for x in log) +
                 "\n\nNo VESTA: File > Open; Properties > Isosurfaces com dois niveis (+0.01 e -0.01) para as diferencas e o spin;\n"
                 "Edit > Lattice Planes (1 1 0), (-1 1 0)... e Utilities > 2D Data Display para os cortes.\n")
    print(f" -> {len(log)} CHGCARs para o VESTA + {out('LEIAME_VESTA.txt')}")


# =========================================================================== #
#   CORRECAO DO GAP (tesoura e modelo empirico PBE -> G0W0)                    #
# =========================================================================== #
# Funcionais semilocais (LDA/GGA) subestimam o gap: o gap de Kohn-Sham nao e o gap
# fundamental (falta a descontinuidade da derivada; erro de deslocalizacao). Sem
# refazer o calculo, o BrUMaRe aplica uma TESOURA: desloca rigidamente as bandas
# DESOCUPADAS (indice > N por spin) por Delta. Ocupadas e E_F ficam como o programa escreveu.
#   tesoura: Delta dado;  ref: Delta = Eg(ref) - Eg(DFT);
#   mvi: Eg(G0W0) = 1.358 Eg(PBE) + 0.904 eV (Morales-Garcia, Valero e Illas, J. Phys. Chem. C 121, 18862, 2017)
MVI_A, MVI_B = 1.358, 0.904
GAPCORR = {}


def _n_ocupadas(B):
    h = B["hdr"]; ns = h["ns"]
    N = [h["nelec"][0] / 2.0] if ns == 1 else [float(x) for x in h["nelec"][:ns]]
    if any(abs(n - round(n)) > 1e-3 for n in N):
        return None
    return [int(round(n)) for n in N]


def aplicar_tesoura(B, delta_ev):
    N = _n_ocupadas(B)
    if N is None or not delta_ev:
        return False
    for s, n in enumerate(N):
        B["eig"][s][:, n:] += delta_ev / HA2EV
    return True


def correcao_gap(B, a):
    modo = getattr(a, "gap_corr", "nenhuma") or "nenhuma"
    if modo == "nenhuma":
        return {}
    N = _n_ocupadas(B)
    if N is None:
        print(" AVISO: ocupacoes fracionarias (metal ou smearing): correcao do gap nao aplicada.")
        return {}
    vbm = max(float(np.max(B["eig"][s][:, n - 1])) for s, n in enumerate(N)) * HA2EV
    cbm = min(float(np.min(B["eig"][s][:, n])) for s, n in enumerate(N)) * HA2EV
    eg = cbm - vbm
    av = []
    if eg <= 0.1:
        av.append("gap DFT nulo ou muito pequeno: a correcao nao e confiavel (o funcional pode ter fechado o gap)")
    if modo == "tesoura":
        delta = float(a.tesoura or 0.0); metodo = f"tesoura com Delta informado"
    elif modo == "ref":
        if a.gap_ref is None:
            sys.exit("ERRO: --gap-corr ref exige --gap-ref (gap experimental, HSE06 ou GW, em eV)")
        delta = float(a.gap_ref) - eg; metodo = f"tesoura ate o gap de referencia {a.gap_ref:.3f} eV"
    else:
        alvo = MVI_A * eg + MVI_B
        delta = alvo - eg; metodo = "modelo empirico PBE->G0W0 (Morales-Garcia, Valero e Illas, 2017)"
        USADOS.add("morales2017")
        av.append("modelo ajustado para PBE em 66 solidos (gaps de 0,1 a 9 eV); erro tipico de algumas decimas de eV; "
                  "nao use para LDA, metais ou oxidos de metais de transicao fortemente correlacionados")
    aplicar_tesoura(B, delta)
    av.append("a tesoura nao corrige a forma das bandas nem a posicao de niveis de defeito vazios no gap; "
              "para isso use HSE06, rSCAN ou DFT+U no proprio CASTEP")
    info = dict(modo=modo, metodo=metodo, eg_dft=eg, delta=delta, eg_corr=eg + delta, avisos=av)
    print(f" Correcao do gap: {metodo}: {eg:.4f} eV (DFT) + {delta:+.4f} eV = {eg + delta:.4f} eV")
    return info


# =========================================================================== #
#   ZONA DE BRILLOUIN: 1.a zona, pontos de alta simetria e caminho k          #
# =========================================================================== #
# Igual à aba do site: Wigner-Seitz da rede recíproca por planos k.G = |G|^2/2 sobre base reduzida (LLL);
# tipo de rede pela geometria da zona; rótulos e caminhos de Setyawan e Curtarolo (2010).
BZ_CAM = {"CUB": [["Γ", "X", "M", "Γ", "R", "X"], ["M", "R"]], "FCC": [["Γ", "X", "W", "K", "Γ", "L", "U", "W", "L", "K"], ["U", "X"]],
          "BCC": [["Γ", "H", "N", "Γ", "P", "H"], ["P", "N"]], "HEX": [["Γ", "M", "K", "Γ", "A", "L", "H", "A"], ["L", "M"], ["K", "H"]],
          "TET": [["Γ", "X", "M", "Γ", "Z", "R", "A", "Z"], ["X", "R"], ["M", "A"]],
          "ORC": [["Γ", "X", "S", "Y", "Γ", "Z", "U", "R", "T", "Z"], ["Y", "T"], ["U", "X"], ["S", "R"]]}


def bz_rede_texto(t):
    p = t.replace(",", " ").split()
    if len(p) == 6 and all(re.match(r"^[\d.eE+-]+$", x) for x in p):
        return bz_lat_par(*map(float, p))
    tp, v = p[0].lower(), list(map(float, p[1:]))
    a = v[0]; b = v[1] if tp == "orc" else a; c = v[-1] if tp in ("hex", "tet", "orc") else a
    r3 = np.sqrt(3)
    return np.array({"sc": [[a, 0, 0], [0, a, 0], [0, 0, a]], "fcc": [[0, a/2, a/2], [a/2, 0, a/2], [a/2, a/2, 0]],
                     "bcc": [[-a/2, a/2, a/2], [a/2, -a/2, a/2], [a/2, a/2, -a/2]], "hex": [[a/2, -a*r3/2, 0], [a/2, a*r3/2, 0], [0, 0, c]],
                     "tet": [[a, 0, 0], [0, a, 0], [0, 0, c]], "orc": [[a, 0, 0], [0, b, 0], [0, 0, c]]}[tp], float)


def bz_lat_par(a, b, c, al, be, ga):
    r = np.pi / 180; ca, cb, cg, sg = np.cos(al*r), np.cos(be*r), np.cos(ga*r), np.sin(ga*r)
    cx = c*cb; cy = c*(ca - cb*cg)/sg
    return np.array([[a, 0, 0], [b*cg, b*sg, 0], [cx, cy, np.sqrt(max(c*c - cx*cx - cy*cy, 0))]])


def bz_ideal(A, tol_ang=0.5, tol_len=0.005):
    L = np.linalg.norm(A, axis=1)
    ang = lambda u, v: np.degrees(np.arccos(np.clip(u @ v / np.linalg.norm(u) / np.linalg.norm(v), -1, 1)))
    p = [*L, ang(A[1], A[2]), ang(A[0], A[2]), ang(A[0], A[1])]; orig = list(p)
    for i in range(3, 6):
        for t in (60, 90, 120, 109.4712206, 70.5287794):
            if abs(p[i] - t) <= tol_ang:
                p[i] = t; break
    for i in range(3):
        for j in range(i + 1, 3):
            if abs(p[i] - p[j]) <= tol_len * max(p[i], p[j]):
                p[i] = p[j] = (p[i] + p[j]) / 2
    notas = [f"{n}: {o:.4f} -> {v:.4f}" for n, o, v in zip("abcαβγ", orig, p) if abs(o - v) > 5e-4]
    return (bz_lat_par(*p) if notas else np.asarray(A, float)), notas


def _bz_lll(B):
    B = [np.array(v, float) for v in B]; k = 1
    for _ in range(500):
        if k >= 3:
            break
        gs, mu = [], np.zeros((3, 3))
        for i in range(3):
            v = B[i].copy()
            for j in range(i):
                mu[i, j] = B[i] @ gs[j] / (gs[j] @ gs[j]); v -= mu[i, j] * gs[j]
            gs.append(v)
        red = False
        for j in range(k - 1, -1, -1):
            q = round(mu[k, j])
            if q:
                B[k] = B[k] - q * B[j]; red = True; break
        if red:
            k = 1; continue
        if gs[k] @ gs[k] >= (0.75 - mu[k, k-1]**2) * (gs[k-1] @ gs[k-1]):
            k += 1
        else:
            B[k], B[k-1] = B[k-1], B[k]; k = max(k - 1, 1)
    return B


def bz_compute(A):
    A = np.asarray(A, float); V = np.linalg.det(A)
    B = 2 * np.pi * np.linalg.inv(A).T
    VBZ = abs(np.linalg.det(B)); esc = VBZ ** (1/3); eps = 1e-7 * esc
    for R in (1, 2):
        Br = _bz_lll(B)
        G = [i*Br[0] + j*Br[1] + k*Br[2] for i in range(-R, R+1) for j in range(-R, R+1) for k in range(-R, R+1) if (i, j, k) != (0, 0, 0)]
        G.sort(key=lambda g: g @ g); P = G[:26 if R == 1 else 60]; Gm = np.array(G); D = (Gm*Gm).sum(1)/2
        verts = []
        for a_ in range(len(P)):
            for b_ in range(a_ + 1, len(P)):
                for c_ in range(b_ + 1, len(P)):
                    M = np.array([P[a_], P[b_], P[c_]])
                    if abs(np.linalg.det(M)) < 1e-12:
                        continue
                    x = np.linalg.solve(M, np.array([P[a_] @ P[a_], P[b_] @ P[b_], P[c_] @ P[c_]]) / 2)
                    if np.all(Gm @ x <= D + eps*np.linalg.norm(Gm, axis=1)) and not any(np.linalg.norm(v - x) < 1e-6*esc for v in verts):
                        verts.append(x)
        V3 = np.array(verts); faces = []
        for g in P:
            on = [i for i, v in enumerate(V3) if abs(g @ v - g @ g / 2) < 1e-6*esc*np.linalg.norm(g)]
            if len(on) < 3:
                continue
            c = g/2; n = g/np.linalg.norm(g); u = V3[on[0]] - c; u /= np.linalg.norm(u); w = np.cross(n, u)
            on.sort(key=lambda i: np.arctan2((V3[i]-c) @ w, (V3[i]-c) @ u)); faces.append(dict(g=g, c=c, v=on))
        vol = sum(abs(sum(np.cross(V3[f["v"][i]], V3[f["v"][(i+1) % len(f["v"])]]) for i in range(len(f["v"]))) @ (f["g"]/np.linalg.norm(f["g"]))) / 2
                  * np.linalg.norm(f["g"]) / 2 / 3 for f in faces)
        if abs(vol - VBZ)/VBZ < 1e-5 or R == 2:
            edges = []
            for i in range(len(faces)):
                for j in range(i + 1, len(faces)):
                    sh = [x for x in faces[i]["v"] if x in faces[j]["v"]]
                    if len(sh) == 2:
                        edges.append(dict(v=sh, f=(i, j), m=(V3[sh[0]] + V3[sh[1]])/2))
            deg = [sum(i in f["v"] for f in faces) for i in range(len(V3))]
            return dict(A=A, B=B, V=V, VBZ=VBZ, vol=vol, verts=V3, faces=faces, edges=edges, deg=deg)


def bz_classify(Z):
    F, E, Vt, deg = Z["faces"], Z["edges"], Z["verts"], Z["deg"]
    r = lambda f: np.linalg.norm(f["c"]); ng = [len(f["v"]) for f in F]
    eq = lambda x, y: abs(x - y) < 1e-4*max(x, y)
    def grupos(xs):
        g = []
        for x in xs:
            if not any(eq(x, y) for y in g):
                g.append(x)
        return sorted(g)
    orto = all(abs(c) < 1e-6 or abs(abs(c) - 1) < 1e-6 for f in F for h in F for c in [f["g"] @ h["g"] / np.linalg.norm(f["g"]) / np.linalg.norm(h["g"])])
    P = {"Γ": [np.zeros(3)]}; put = lambda k, p: P.setdefault(k, []).append(p)
    tipo, nome = "generica", "rede de baixa simetria (caminho automatico)"
    if len(F) == 6 and all(n == 4 for n in ng) and orto:
        gr = grupos([r(f) for f in F])
        if len(gr) == 1:
            tipo, nome = "CUB", "cubica simples"
            [put("X", f["c"]) for f in F]; [put("M", e["m"]) for e in E]; [put("R", v) for v in Vt]
        elif len(gr) == 2:
            nz = gr[0] if sum(eq(r(f), gr[0]) for f in F) == 2 else gr[1]; isz = lambda f: eq(r(f), nz)
            tipo, nome = "TET", "tetragonal simples"
            [put("Z" if isz(f) else "X", f["c"]) for f in F]; [put("R" if any(isz(F[i]) for i in e["f"]) else "M", e["m"]) for e in E]; [put("A", v) for v in Vt]
        else:
            tipo, nome = "ORC", "ortorrombica simples"
            lab = lambda f: "X" if eq(r(f), gr[2]) else ("Y" if eq(r(f), gr[1]) else "Z")
            [put(lab(f), f["c"]) for f in F]
            [put({"XY": "S", "XZ": "U", "YZ": "T"}["".join(sorted(lab(F[i]) for i in e["f"]))], e["m"]) for e in E]; [put("R", v) for v in Vt]
    elif len(F) == 14 and ng.count(6) == 8 and ng.count(4) == 6 and len(grupos([r(f) for f in F if len(f["v"]) == 6])) == 1:
        tipo, nome = "FCC", "cubica de faces centradas"
        [put("L" if len(f["v"]) == 6 else "X", f["c"]) for f in F]; [put("W", v) for v in Vt]
        [put("K" if all(len(F[i]["v"]) == 6 for i in e["f"]) else "U", e["m"]) for e in E]
    elif len(F) == 12 and all(n == 4 for n in ng) and len(grupos([r(f) for f in F])) == 1 and all(d in (3, 4) for d in deg):
        tipo, nome = "BCC", "cubica de corpo centrado"
        [put("N", f["c"]) for f in F]; [put("H" if deg[i] == 4 else "P", v) for i, v in enumerate(Vt)]
    elif len(F) == 8 and ng.count(6) == 2 and ng.count(4) == 6:
        tipo, nome = "HEX", "hexagonal"
        [put("A" if len(f["v"]) == 6 else "M", f["c"]) for f in F]
        [put("L" if any(len(F[i]["v"]) == 6 for i in e["f"]) else "K", e["m"]) for e in E]; [put("H", v) for v in Vt]
    else:
        vistos = []
        for f in F:
            if any(np.linalg.norm(g + f["g"]) < 1e-9 for g in vistos):
                continue
            vistos.append(f["g"]); put(f"F{len(vistos)}", f["c"])
    cam = BZ_CAM.get(tipo) or [sum([["Γ", k] for k in P if k != "Γ"], []) + ["Γ"]]
    return dict(tipo=tipo, nome=nome, P=P, cam=cam)


def _sc_def(Ap, bravais, conv):
    """Base primitiva, pontos (fracionários) e caminhos de Setyawan e Curtarolo (2010) para cada rede.
    Devolve (tipo, Asc, F, cam) ou None."""
    Ap = np.asarray(Ap, float); C = np.asarray(conv["lat"], float) if conv is not None else None
    if bravais == "tI":
        Lc = np.linalg.norm(C, axis=1); a = Lc[0]; c = Lc[2]
        Asc = np.array([[-a/2, a/2, c/2], [a/2, -a/2, c/2], [a/2, a/2, -c/2]])
        if c < a:
            e = (1 + c*c/(a*a))/4
            return "BCT1", Asc, {"M": (-.5, .5, .5), "N": (0, .5, 0), "P": (.25, .25, .25), "X": (0, 0, .5), "Z": (e, e, -e), "Z1": (-e, 1 - e, e)}, \
                [["Γ", "X", "M", "Γ", "Z", "P", "N", "Z1", "M"], ["X", "P"]]
        e = (1 + a*a/(c*c))/4; z = a*a/(2*c*c)
        return "BCT2", Asc, {"N": (0, .5, 0), "P": (.25, .25, .25), "Σ": (-e, e, e), "Σ1": (e, 1 - e, -e), "X": (0, 0, .5), "Y": (-z, z, .5), "Y1": (.5, .5, -z), "Z": (.5, .5, -.5)}, \
            [["Γ", "X", "Y", "Σ", "Γ", "Z", "Σ1", "N", "P", "Y1", "Z"], ["X", "P"]]
    bravais = {"mC": "mS", "oC": "oS", "oA": "oS"}.get(bravais, bravais)
    if bravais == "oS":
        a, b = sorted(np.linalg.norm(C, axis=1)[:2]); c = np.linalg.norm(C[2]); z = (1 + a*a/(b*b))/4
        return "ORCC", np.array([[a/2, -b/2, 0], [a/2, b/2, 0], [0, 0, c]]), \
            {"A": (z, z, .5), "A1": (-z, 1 - z, .5), "R": (0, .5, .5), "S": (0, .5, 0), "T": (-.5, .5, .5), "X": (z, z, 0), "X1": (-z, 1 - z, 0), "Y": (-.5, .5, 0), "Z": (0, 0, .5)}, \
            [["Γ", "X", "S", "R", "A", "Z", "Γ", "Y", "X1", "A1", "T", "Y"], ["Z", "T"]]
    if bravais == "oF":
        a, b, c = sorted(np.linalg.norm(C, axis=1)); Asc = np.array([[0, b/2, c/2], [a/2, 0, c/2], [a/2, b/2, 0]])
        q = 1/a**2 - 1/b**2 - 1/c**2
        if abs(q) < 1e-6 * (1/a**2) or q > 0:
            z = (1 + a*a/(b*b) - a*a/(c*c))/4; e = (1 + a*a/(b*b) + a*a/(c*c))/4
            F = {"A": (.5, .5 + z, z), "A1": (.5, .5 - z, 1 - z), "L": (.5, .5, .5), "T": (1, .5, .5), "X": (0, e, e), "X1": (1, 1 - e, 1 - e), "Y": (.5, 0, .5), "Z": (.5, .5, 0)}
            if q > 0 and abs(q) >= 1e-6 * (1/a**2):
                return "ORCF1", Asc, F, [["Γ", "Y", "T", "Z", "Γ", "X", "A1", "Y"], ["T", "X1"], ["X", "A", "Z"], ["L", "Γ"]]
            return "ORCF3", Asc, F, [["Γ", "Y", "T", "Z", "Γ", "X", "A1", "Y"], ["X", "A", "Z"], ["L", "Γ"]]
        e = (1 + a*a/(b*b) - a*a/(c*c))/4; f = (1 + c*c/(b*b) - c*c/(a*a))/4; d = (1 + b*b/(a*a) - b*b/(c*c))/4
        return "ORCF2", Asc, {"C": (.5, .5 - e, 1 - e), "C1": (.5, .5 + e, e), "D": (.5 - d, .5, 1 - d), "D1": (.5 + d, .5, d), "L": (.5, .5, .5),
                              "H": (1 - f, .5 - f, .5), "H1": (f, .5 + f, .5), "X": (0, .5, .5), "Y": (.5, 0, .5), "Z": (.5, .5, 0)}, \
            [["Γ", "Y", "C", "D", "X", "Γ", "Z", "D1", "H", "C"], ["C1", "Z"], ["X", "H1"], ["H", "Y"], ["L", "Γ"]]
    if bravais == "oI":
        a, b, c = sorted(np.linalg.norm(C, axis=1)); Asc = np.array([[-a/2, b/2, c/2], [a/2, -b/2, c/2], [a/2, b/2, -c/2]])
        z = (1 + a*a/(c*c))/4; e = (1 + b*b/(c*c))/4; d = (b*b - a*a)/(4*c*c); m = (a*a + b*b)/(4*c*c)
        return "ORCI", Asc, {"L": (-m, m, .5 - d), "L1": (m, -m, .5 + d), "L2": (.5 - d, .5 + d, -m), "R": (0, .5, 0), "S": (.5, 0, 0), "T": (0, 0, .5),
                             "W": (.25, .25, .25), "X": (-z, z, z), "X1": (z, 1 - z, -z), "Y": (e, -e, e), "Y1": (1 - e, e, -e), "Z": (.5, .5, -.5)}, \
            [["Γ", "X", "L", "T", "W", "R", "X1", "Z", "Γ", "Y", "S", "W"], ["L1", "Y"], ["Y1", "Z"]]
    if bravais in ("mP", "mS"):
        # convenção do moyo: eixo único b, ângulo β entre a e c. Setyawan-Curtarolo: eixo único a, ângulo α < 90° entre b e c
        L = np.linalg.norm(C, axis=1); be = np.degrees(np.arccos(np.clip(C[0] @ C[2] / (L[0]*L[2]), -1, 1)))
        al = np.radians(min(be, 180 - be)); ca, sa = np.cos(al), np.sin(al)
        if bravais == "mP":
            a = L[1]; b, c = sorted((L[0], L[2])); Asc = np.array([[a, 0, 0], [0, b, 0], [0, c*ca, c*sa]])
            e = (1 - b*ca/c)/(2*sa*sa); v = .5 - e*c*ca/b
            return "MCL", Asc, {"A": (.5, .5, 0), "C": (0, .5, .5), "D": (.5, 0, .5), "D1": (.5, 0, -.5), "E": (.5, .5, .5), "H": (0, e, 1 - v), "H1": (0, 1 - e, v),
                                "H2": (0, e, -v), "M": (.5, e, 1 - v), "M1": (.5, 1 - e, v), "M2": (.5, e, -v), "X": (0, .5, 0), "Y": (0, 0, .5), "Y1": (0, 0, -.5), "Z": (.5, 0, 0)}, \
                [["Γ", "Y", "H", "C", "E", "M1", "A", "X", "H1"], ["M", "D", "Z"], ["Y", "D"]]
        a, b, c = L[1], L[0], L[2]                                             # eixo único (b do moyo) = a de SC; C centrado no plano a-b
        Asc = np.array([[a/2, b/2, 0], [-a/2, b/2, 0], [0, c*ca, c*sa]]); Bs = 2*np.pi*np.linalg.inv(Asc).T
        kg = np.degrees(np.arccos(np.clip(Bs[0] @ Bs[1] / (np.linalg.norm(Bs[0])*np.linalg.norm(Bs[1])), -1, 1)))
        if kg > 90 + 1e-6 or abs(kg - 90) <= 1e-6:
            z = (2 - b*ca/c)/(4*sa*sa); e = .5 + 2*z*c*ca/b; p = .75 - a*a/(4*b*b*sa*sa); f = p + (.75 - p)*b*ca/c
            F = {"N": (.5, 0, 0), "N1": (0, -.5, 0), "F": (1 - z, 1 - z, 1 - e), "F1": (z, z, e), "F2": (-z, -z, 1 - e),
                 "I": (f, 1 - f, .5), "I1": (1 - f, f - 1, .5), "L": (.5, .5, .5), "M": (.5, 0, .5), "X": (1 - p, p - 1, 0), "X1": (p, 1 - p, 0),
                 "X2": (p - 1, -p, 0), "Y": (.5, .5, 0), "Y1": (-.5, -.5, 0), "Z": (0, 0, .5)}
            if kg > 90 + 1e-6:
                return "MCLC1", Asc, F, [["Γ", "Y", "F", "L", "I"], ["I1", "Z", "F1"], ["Y", "X1"], ["X", "Γ", "N"], ["M", "Γ"]]
            return "MCLC2", Asc, F, [["Γ", "Y", "F", "L", "I"], ["I1", "Z", "F1"], ["N", "Γ", "M"]]
        q = b*ca/c + b*b*sa*sa/(a*a)
        if q <= 1 + 1e-9:
            m = (1 + b*b/(a*a))/4; d = b*c*ca/(2*a*a); z = m - .25 + (1 - b*ca/c)/(4*sa*sa); e = .5 + 2*z*c*ca/b; f = 1 + z - 2*m; p = e - 2*d
            F = {"F": (1 - f, 1 - f, 1 - p), "F1": (f, f - 1, p), "F2": (1 - f, -f, 1 - p), "H": (z, z, e), "H1": (1 - z, -z, 1 - e), "H2": (-z, -z, 1 - e),
                 "I": (.5, -.5, .5), "M": (.5, 0, .5), "N": (.5, 0, 0), "N1": (0, -.5, 0), "X": (.5, -.5, 0), "Y": (m, m, d), "Y1": (1 - m, -m, -d),
                 "Y2": (-m, -m, -d), "Y3": (m, m - 1, d), "Z": (0, 0, .5)}
            if q < 1 - 1e-9:
                return "MCLC3", Asc, F, [["Γ", "Y", "F", "H", "Z", "I", "F1"], ["H1", "Y1", "X", "Γ", "N"], ["M", "Γ"]]
            return "MCLC4", Asc, F, [["Γ", "Y", "F", "H", "Z", "I"], ["H1", "Y1", "X", "Γ", "N"], ["M", "Γ"]]
        z = (b*b/(a*a) + (1 - b*ca/c)/(sa*sa))/4; e = .5 + 2*z*c*ca/b; m = e/2 + b*b/(4*a*a) - b*c*ca/(2*a*a); v = 2*m - z
        w = (4*v - 1 - b*b*sa*sa/(a*a))*c/(2*b*ca); d = z*c*ca/b + w/2 - .25; r = 1 - z*a*a/(b*b)
        return "MCLC5", Asc, {"F": (v, v, w), "F1": (1 - v, 1 - v, 1 - w), "F2": (v, v - 1, w), "H": (z, z, e), "H1": (1 - z, -z, 1 - e), "H2": (-z, -z, 1 - e),
                              "I": (r, 1 - r, .5), "I1": (1 - r, r - 1, .5), "L": (.5, .5, .5), "M": (.5, 0, .5), "N": (.5, 0, 0), "N1": (0, -.5, 0),
                              "X": (.5, -.5, 0), "Y": (m, m, d), "Y1": (1 - m, -m, -d), "Y2": (-m, -m, -d), "Y3": (m, m - 1, d), "Z": (0, 0, .5)}, \
            [["Γ", "Y", "F", "L", "I"], ["I1", "Z", "H", "F1"], ["H1", "Y1", "X", "Γ", "N"], ["M", "Γ"]]
    if bravais == "hR":
        a = np.linalg.norm(Ap[0]); al = np.arccos(np.clip(Ap[0] @ Ap[1] / (a*np.linalg.norm(Ap[1])), -1, 1)); ca, h = np.cos(al), np.cos(al/2)
        Asc = a*np.array([[h, -np.sin(al/2), 0], [h, np.sin(al/2), 0], [ca/h, 0, np.sqrt(max(1 - ca*ca/(h*h), 0))]])
        if al < np.pi/2:
            e = (1 + 4*ca)/(2 + 4*ca); v = .75 - e/2
            return "RHL1", Asc, {"B": (e, .5, 1 - e), "B1": (.5, 1 - e, e - 1), "F": (.5, .5, 0), "L": (.5, 0, 0), "L1": (0, 0, -.5), "P": (e, v, v),
                                 "P1": (1 - v, 1 - v, 1 - e), "P2": (v, v, e - 1), "Q": (1 - v, v, 0), "X": (v, 0, -v), "Z": (.5, .5, .5)}, \
                [["Γ", "L", "B1"], ["B", "Z", "Γ", "X"], ["Q", "F", "P1", "Z"], ["L", "P"]]
        e = 1/(2*np.tan(al/2)**2); v = .75 - e/2
        return "RHL2", Asc, {"F": (.5, -.5, 0), "L": (.5, 0, 0), "P": (1 - v, -v, 1 - v), "P1": (v, v - 1, v - 1), "Q": (e, e, e), "Q1": (1 - e, -e, -e), "Z": (.5, -.5, .5)}, \
            [["Γ", "P", "Z", "Q", "Γ", "F", "P1", "Q1", "L", "Z"]]
    return None


BZ_NOMES = {"BCT1": "tetragonal de corpo centrado (c < a)", "BCT2": "tetragonal de corpo centrado (c > a)", "RHL1": "romboedrica (alfa < 90)",
            "RHL2": "romboedrica (alfa > 90)", "ORCC": "ortorrombica de base centrada", "ORCF1": "ortorrombica de faces centradas (ORCF1)",
            "ORCF2": "ortorrombica de faces centradas (ORCF2)", "ORCF3": "ortorrombica de faces centradas (ORCF3)", "ORCI": "ortorrombica de corpo centrado",
            "MCL": "monoclinica primitiva", "MCLC1": "monoclinica de base centrada (MCLC1)", "MCLC2": "monoclinica de base centrada (MCLC2)",
            "MCLC3": "monoclinica de base centrada (MCLC3)", "MCLC4": "monoclinica de base centrada (MCLC4)", "MCLC5": "monoclinica de base centrada (MCLC5)",
            "TRI1a": "triclinica (TRI1a)", "TRI1b": "triclinica (TRI1b)", "TRI2a": "triclinica (TRI2a)", "TRI2b": "triclinica (TRI2b)"}


def _na_superficie(Ap, P):
    Z = bz_compute(Ap); G = np.array([fc["g"] for fc in Z["faces"]])
    return all(k == "Γ" or abs(np.max(G @ v[0] / ((G*G).sum(1)/2)) - 1) <= 1e-6 for k, v in P.items())


def _bz_tri(Ap):
    """Triclínica: base recíproca reduzida com ângulos todos >= 90° (TRI1a/2a) ou todos <= 90° (TRI1b/2b)."""
    import itertools
    B = 2*np.pi*np.linalg.inv(np.asarray(Ap, float)).T; melhor = None
    ang = lambda u, v: np.degrees(np.arccos(np.clip(u @ v / (np.linalg.norm(u)*np.linalg.norm(v)), -1, 1)))
    for m in itertools.product((-1, 0, 1), repeat=9):
        M = np.array(m, float).reshape(3, 3)
        if abs(abs(np.linalg.det(M)) - 1) > 1e-9:
            continue
        Bp = M @ B; ka, kb, kg = ang(Bp[1], Bp[2]), ang(Bp[0], Bp[2]), ang(Bp[0], Bp[1]); t = 1e-6
        if min(ka, kb, kg) >= 90 - t and kg <= min(ka, kb) + t:
            tipo = "TRI2a" if abs(kg - 90) <= t else "TRI1a"
        elif max(ka, kb, kg) <= 90 + t and kg >= max(ka, kb) - t:
            tipo = "TRI2b" if abs(kg - 90) <= t else "TRI1b"
        else:
            continue
        n2 = float((Bp*Bp).sum())
        if melhor is None or n2 < melhor[0] - 1e-9:
            melhor = (n2, tipo, Bp)
    if melhor is None:
        return None
    _, tipo, Bp = melhor
    F = ({"L": (.5, .5, 0), "M": (0, .5, .5), "N": (.5, 0, .5), "R": (.5, .5, .5), "X": (.5, 0, 0), "Y": (0, .5, 0), "Z": (0, 0, .5)} if tipo.endswith("a") else
         {"L": (.5, -.5, 0), "M": (0, 0, .5), "N": (-.5, -.5, .5), "R": (0, -.5, .5), "X": (0, -.5, 0), "Y": (.5, 0, 0), "Z": (-.5, 0, .5)})
    P = {"Γ": [np.zeros(3)]}
    for k, fr in F.items():
        P[k] = [np.array(fr) @ Bp]
    if not _na_superficie(Ap, P):
        return None
    return tipo, P, [["X", "Γ", "Y"], ["L", "Γ", "Z"], ["N", "Γ", "M"], ["R", "Γ"]]


def bz_sc_extra(Ap, bravais, conv=None):
    """Pontos e caminhos de Setyawan e Curtarolo para BCT, ORCC, ORCF, ORCI, MCL, MCLC, RHL e TRI, alinhados à base primitiva Ap.
    Devolve (tipo, P, cam) ou None se a base não casar ou algum ponto não cair na superfície da zona."""
    Ap = np.asarray(Ap, float)
    if bravais == "aP":
        return _bz_tri(Ap)
    dfn = _sc_def(Ap, bravais, conv)
    if dfn is None:
        return None
    tipo, Asc, F, cam = dfn
    Gsc, Gp = Asc @ Asc.T, Ap @ Ap.T; M = None
    import itertools
    for m in itertools.product((-1, 0, 1), repeat=9):
        Mm = np.array(m, float).reshape(3, 3)
        if abs(abs(np.linalg.det(Mm)) - 1) < 1e-9 and np.allclose(Mm @ Gsc @ Mm.T, Gp, atol=1e-4*np.abs(Gp).max()):
            M = Mm; break
    if M is None:
        return None
    R = np.linalg.solve(M @ Asc, Ap)                                         # Ap = M·Asc·R (R ortogonal)
    Bsc = 2*np.pi*np.linalg.inv(Asc).T
    P = {"Γ": [np.zeros(3)]}
    for k, fr in F.items():
        P[k] = [np.array(fr) @ Bsc @ R]
    if not _na_superficie(Ap, P):                                              # salvaguarda: todo ponto na superfície
        return None
    return tipo, P, cam


def bz_path(Z, C, dens=30.0):
    frac = lambda k: np.array([a @ k / (2*np.pi) for a in Z["A"]])
    prev = np.zeros(3); pts, seg = [], []
    for sub in C["cam"]:
        ant = None
        for L in sub:
            cand = C["P"].get(L)
            if not cand:
                continue
            best = min(cand, key=lambda p: np.linalg.norm(p - prev) - 1e-6*(p[0] + 2*p[1] + 3*p[2]))
            pt = dict(L=L, k=best, f=np.where(np.abs(frac(best)) < 1e-10, 0, frac(best)), quebra=(ant is None and len(pts) > 0))
            pts.append(pt)
            if ant is not None:
                ln = float(np.linalg.norm(best - ant["k"])); seg.append(dict(de=ant["L"], para=L, len=ln, n=max(2, int(round(ln*dens)))))
            ant = pt; prev = best
    return pts, seg


def bz_textos(Z, C, pts, seg, dk=0.2):
    lin = lambda p: " ".join(f"{x: .6f}" for x in p["f"])
    lb = lambda L, s=False: {"Γ": "\\Gamma" if s else "G", "Σ": "\\Sigma" if s else "SIGMA", "Σ1": "\\Sigma_1" if s else "SIGMA_1"}.get(L, L)
    mp = [max(1, int(np.ceil(np.linalg.norm(b)/dk - 1e-9))) for b in Z["B"]]; out = {}
    t = "%BLOCK SPECTRAL_KPOINT_PATH\n"
    for p in pts:
        t += ("BREAK\n" if p["quebra"] else "") + f"{lin(p)}   ! {lb(p['L'])}\n"
    out["castep"] = t + f"%ENDBLOCK SPECTRAL_KPOINT_PATH\n\nKPOINTS_MP_GRID : {mp[0]} {mp[1]} {mp[2]}\n"
    nmed = max(2, round(sum(s["n"] for s in seg)/max(len(seg), 1)))
    v = f"Caminho k do BrUMaRe ({C['tipo']}; Setyawan e Curtarolo, 2010)\n{nmed}\nLine-mode\nReciprocal\n"
    for i in range(1, len(pts)):
        if not pts[i]["quebra"]:
            v += f"{lin(pts[i-1])}   ! {lb(pts[i-1]['L'])}\n{lin(pts[i])}   ! {lb(pts[i]['L'])}\n\n"
    out["vasp"] = v
    q = f"K_POINTS crystal_b\n{len(pts)}\n"; si = 0
    for i, p in enumerate(pts):
        prox = pts[i+1] if i + 1 < len(pts) else None
        n = 1 if (prox is None or prox["quebra"]) else seg[si]["n"]
        if prox is not None and not prox["quebra"]:
            si += 1
        q += f"{lin(p)} {n}   ! {lb(p['L'])}\n"
    out["qe"] = q
    sv = "BandLinesScale ReciprocalLatticeVectors\n%block BandLines\n"; si = 0
    for i, p in enumerate(pts):
        n = 1 if (i == 0 or p["quebra"]) else seg[si]["n"]
        if not (i == 0 or p["quebra"]):
            si += 1
        sv += f"{n:4d}  {lin(p)}   {lb(p['L'], True)}\n"
    out["siesta"] = sv + "%endblock BandLines\n"
    return out, mp


def bz_completo(A, st=None, symprec=0.01, exata=False):
    """Zona de Brillouin com simetria: se houver estrutura (e moyopy), usa a célula primitiva padronizada;
    BCT e RHL recebem os pontos de Setyawan e Curtarolo; as demais redes, a classificação geométrica."""
    d = simetria(st, symprec) if st is not None else None
    Ause = np.asarray(d["prim"]["lat"] if d else A, float)
    Ai, notas = (Ause, []) if (exata or d) else bz_ideal(Ause)
    Z = bz_compute(Ai)
    ex = bz_sc_extra(Ai, d["bravais"], d["conv"]) if d and d["bravais"] in ("tI", "hR", "oS", "oC", "oA", "oF", "oI", "mP", "mS", "mC", "aP") else None
    if ex:
        tipo, P, cam = ex; C = dict(tipo=tipo, nome=BZ_NOMES[tipo], P=P, cam=cam)
    else:
        C = bz_classify(Z)
    return Z, C, notas, d


def bz_relatorio(A, base, a_args, out_fn, st=None):
    """Calcula e grava a zona de Brillouin: relatório, entradas de CASTEP/VASP/QE/SIESTA, JSON e figura."""
    USADOS.add("setyawan2010")
    Z, C, notas, d = bz_completo(A, st, getattr(a_args, "symprec", 0.01), getattr(a_args, "zb_exata", False))
    pts, seg = bz_path(Z, C, getattr(a_args, "zb_densidade", 30.0)); T, mp = bz_textos(Z, C, pts, seg, getattr(a_args, "zb_dk", 0.2))
    L = [f"ZONA DE BRILLOUIN ({base})", f"Rede: {C['nome']} ({C['tipo']}) | faces {len(Z['faces'])}, arestas {len(Z['edges'])}, vertices {len(Z['verts'])}",
         f"V real = {abs(Z['V']):.4f} A^3 | V_ZB = (2pi)^3/V = {Z['VBZ']:.4f} A^-3 (geometrico {Z['vol']:.4f})"]
    if notas:
        L.append("Rede idealizada (tolerancia de simetria): " + "; ".join(notas))
    if d:
        L += [f"Grupo espacial: {d['hm']} (n. {d['numero']}; Hall {d['hall']}) | completo: {d['hm_completo']} | Pearson {d['pearson']}",
              f"Sistema {d['sistema']} | Bravais {d['bravais']} | classe pontual {d['classe']} | {d['ops']} operacoes | centro de inversao: {'sim' if d['inversao'] else 'nao'}",
              f"Celula primitiva padronizada: {len(d['prim']['sp'])} atomos (convencional: {len(d['conv']['sp'])}); os pontos abaixo estao na base da primitiva",
              "Wyckoff (entrada): " + ", ".join(f"{e}{i + 1}:{w}({ss})" for i, (e, w, ss) in enumerate(zip(st['sp'], d['wyckoff'], d['sitio'])))[:2000]]
        for nome, cc in (("primitiva", d["prim"]), ("convencional", d["conv"])):
            for fmt, ext in (("poscar", "POSCAR"), ("cell", "cell"), ("qe", "qe.in"), ("cif", "cif")):
                open(out_fn(f"celula_{nome}.{ext}"), "w", encoding="utf-8").write(celula_texto(cc, fmt, f"{base}_{nome}"))
    L += [f"b{i+1} = ({b[0]: .5f}, {b[1]: .5f}, {b[2]: .5f}) A^-1  |b{i+1}| = {np.linalg.norm(b):.5f}" for i, b in enumerate(Z["B"])]
    L.append("Caminho: " + " | ".join("-".join(s) for s in C["cam"]))
    vist = {}
    for p in pts:
        vist.setdefault(p["L"], p)
    L += [f"  {k:<3} frac = ({p['f'][0]: .5f}, {p['f'][1]: .5f}, {p['f'][2]: .5f})   |k| = {np.linalg.norm(p['k']):.5f} A^-1" for k, p in vist.items()]
    L += [f"  {s['de']}-{s['para']}: {s['len']:.5f} A^-1, {s['n']} pontos" for s in seg]
    L.append(f"Malha Monkhorst-Pack (dk = {getattr(a_args, 'zb_dk', 0.2)} A^-1, com 2pi): {mp[0]} x {mp[1]} x {mp[2]}")
    open(out_fn("zona_brillouin.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    for k, nome in (("castep", "kpath_castep.cell"), ("vasp", "KPOINTS_bandas"), ("qe", "kpath_qe.in"), ("siesta", "kpath_siesta.fdf")):
        open(out_fn(nome), "w", encoding="utf-8").write(T[k])
    json.dump(dict(tipo=C["tipo"], rede=C["nome"], grupo_espacial=(dict(numero=d["numero"], hm=d["hm"], hall=d["hall"], pearson=d["pearson"], bravais=d["bravais"]) if d else None),
                   V=abs(Z["V"]), VBZ=Z["VBZ"], a=Z["A"].tolist(), b=Z["B"].tolist(), ajustes=notas,
                   pontos=[dict(rotulo=p["L"], frac=p["f"].tolist(), cart=p["k"].tolist()) for p in pts], segmentos=seg, malha_MP=mp),
              open(out_fn("zona_brillouin.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(6.4, 6)); ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection([Z["verts"][f["v"]] for f in Z["faces"]], facecolor="#4FE3C1", alpha=0.18, edgecolor="#333333", linewidths=0.8))
    seq = []
    for p in pts:
        if p["quebra"] and seq:
            ax.plot(*np.array(seq).T, color="#F5B544", lw=2.4); seq = []
        seq.append(p["k"])
    if seq:
        ax.plot(*np.array(seq).T, color="#F5B544", lw=2.4)
    for k, p in vist.items():
        ax.scatter(*p["k"], color="#C77D00", s=18); ax.text(*(p["k"] * 1.06), k, fontsize=12, color="#8a5300")
    for i, (b, c) in enumerate(zip(Z["B"], ("#e5484d", "#3fb950", "#4c8dff"))):
        u = b / np.linalg.norm(b) * Z["VBZ"]**(1/3) * 0.7; ax.quiver(0, 0, 0, *u, color=c, arrow_length_ratio=0.12); ax.text(*(u*1.08), f"b{i+1}", color=c)
    m = np.abs(Z["verts"]).max(); ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m, m); ax.set_box_aspect((1, 1, 1)); ax.set_axis_off()
    ax.set_title(f"1.a zona de Brillouin: {C['nome']}", fontsize=11)
    fig.savefig(out_fn(f"zona_brillouin.{a_args.format}"), dpi=a_args.dpi, bbox_inches="tight"); plt.close(fig)
    print(f" Zona de Brillouin: {C['nome']} ({C['tipo']}), {len(Z['faces'])} faces; caminho e entradas de CASTEP/VASP/QE/SIESTA gravados.")
    return Z, C, pts, seg


# =========================================================================== #
#   ESTRUTURAS (CIF, POSCAR, .cell, XSF, QE, XYZ estendido) E SIMETRIA (moyo)  #
# =========================================================================== #
Z_DE = {s: i + 1 for i, s in enumerate(("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr "
        "Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg "
        "Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu").split())}


def _el(x):
    m = re.match(r"([A-Z][a-z]?)", x.strip().capitalize() if x[:1].islower() else x.strip())
    return m.group(1) if m and m.group(1) in Z_DE else x.strip()


def _num(x):
    return float(re.sub(r"\(.*\)", "", x))


def _op_xyz(op):
    """'x+1/2,-y,z' -> (R, t) para coordenadas fracionárias."""
    R = np.zeros((3, 3)); t = np.zeros(3)
    for i, termo in enumerate(op.lower().replace(" ", "").replace("'", "").split(",")):
        for sinal, val in re.findall(r"([+-]?)([xyz]|[\d.]+(?:/[\d.]+)?)", termo):
            sg = -1.0 if sinal == "-" else 1.0
            if val in "xyz":
                R[i, "xyz".index(val)] += sg
            else:
                a, _, b = val.partition("/"); t[i] += sg * float(a) / (float(b) if b else 1.0)
    return R, t


def ler_estrutura(fn):
    """Lê CIF, POSCAR/CONTCAR, .cell (CASTEP), XSF, entrada do QE (pw.x) ou XYZ estendido.
    Devolve dict(lat 3x3 Å, f Nx3 fracionário, sp lista de elementos)."""
    txt = open(fn, encoding="utf-8", errors="replace").read(); low = fn.lower()
    if low.endswith(".cif") or "_cell_length_a" in txt:
        g = lambda k: _num(re.search(k + r"\s+(\S+)", txt).group(1))
        lat = bz_lat_par(g("_cell_length_a"), g("_cell_length_b"), g("_cell_length_c"), g("_cell_angle_alpha"), g("_cell_angle_beta"), g("_cell_angle_gamma"))
        ops, sites = [], []
        for bloco in re.split(r"\n\s*loop_", "\n" + txt)[1:]:
            linhas = [l.strip() for l in bloco.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
            cab = [l for l in linhas if l.startswith("_")]; dados = [l for l in linhas if not l.startswith("_")]
            if any("symop_operation_xyz" in c or "symmetry_equiv_pos_as_xyz" in c for c in cab):
                k = next(i for i, c in enumerate(cab) if "operation_xyz" in c or "equiv_pos_as_xyz" in c)
                for l in dados:
                    if l.startswith("_") or l.startswith("loop_"):
                        break
                    q = re.findall(r"'[^']*'|\"[^\"]*\"|\S+", l)
                    ops.append(q[k] if len(cab) > 1 and len(q) > k else (re.search(r"['\"]([^'\"]+)['\"]", l) or re.search(r"(\S+,\S+,\S+)", l)).group(1))
            if any(c.startswith("_atom_site_fract_x") for c in cab):
                ix = {c: i for i, c in enumerate(cab)}
                for l in dados:
                    q = l.split()
                    if len(q) < len(cab):
                        continue
                    nome = q[ix["_atom_site_type_symbol"]] if "_atom_site_type_symbol" in ix else q[ix.get("_atom_site_label", 0)]
                    sites.append((_el(nome), [_num(q[ix["_atom_site_fract_" + e]]) for e in "xyz"]))
        ops = ops or ["x,y,z"]
        f_, sp = [], []
        for el, p in sites:
            for o in ops:
                R, t = _op_xyz(o.strip("'\"")); x = (R @ np.array(p) + t) % 1.0
                if not any(np.linalg.norm(((x - y) + 0.5) % 1.0 - 0.5) < 1e-3 and e2 == el for y, e2 in zip(f_, sp)):
                    f_.append(x); sp.append(el)
        return dict(lat=lat, f=np.array(f_), sp=sp)
    if low.endswith(".cell"):
        st = read_cell_struct(fn)
        return dict(lat=np.asarray(st["lat"], float), f=np.array(st["f"]) % 1.0, sp=list(st["sp"]))
    if "PRIMVEC" in txt.upper():
        L = txt.splitlines(); i = next(i for i, l in enumerate(L) if l.strip().upper().startswith("PRIMVEC"))
        lat = np.array([[float(x) for x in L[i + 1 + k].split()[:3]] for k in range(3)])
        j = next(i for i, l in enumerate(L) if l.strip().upper().startswith("PRIMCOORD")); n = int(L[j + 1].split()[0])
        q = [L[j + 2 + k].split() for k in range(n)]
        sp = [_el(x[0]) if not x[0].isdigit() else list(Z_DE)[int(x[0]) - 1] for x in q]
        cart = np.array([[float(v) for v in x[1:4]] for x in q]); return dict(lat=lat, f=(cart @ np.linalg.inv(lat)) % 1.0, sp=sp)
    if re.search(r"&system", txt, re.I):
        alat = None; m = re.search(r"celldm\(1\)\s*=\s*([\d.eEdD+-]+)", txt)
        if m: alat = float(m.group(1).replace("d", "e").replace("D", "e")) * 0.529177
        m = re.search(r"\bA\s*=\s*([\d.eE+-]+)", txt); alat = alat or (float(m.group(1)) if m else None)
        cp = re.search(r"CELL_PARAMETERS\s*[({]?\s*(\w*)\s*[)}]?\s*\n((?:.*\n){3})", txt, re.I)
        un = cp.group(1).lower(); lat = np.array([[float(x.replace("d", "e")) for x in l.split()[:3]] for l in cp.group(2).strip().splitlines()[:3]])
        lat = lat * (0.529177 if un == "bohr" else alat if un == "alat" else 1.0)
        ap = re.search(r"ATOMIC_POSITIONS\s*[({]?\s*(\w*)\s*[)}]?\s*\n", txt, re.I); un = ap.group(1).lower()
        sp, pos = [], []
        for l in txt[ap.end():].splitlines():
            q = l.split()
            if len(q) < 4 or not re.match(r"^[A-Za-z]", q[0]) or q[0].upper() in ("K_POINTS", "CELL_PARAMETERS", "ATOMIC_SPECIES"):
                break
            sp.append(_el(q[0])); pos.append([float(x) for x in q[1:4]])
        pos = np.array(pos)
        f_ = pos if un == "crystal" else (pos * (0.529177 if un == "bohr" else alat if un == "alat" else 1.0)) @ np.linalg.inv(lat)
        return dict(lat=lat, f=f_ % 1.0, sp=sp)
    L = [l for l in txt.splitlines()]
    if len(L) > 1 and "Lattice=" in L[1]:
        lat = np.array([float(x) for x in re.search(r'Lattice="([^"]+)"', L[1]).group(1).split()]).reshape(3, 3)
        n = int(L[0]); q = [L[2 + k].split() for k in range(n)]
        cart = np.array([[float(v) for v in x[1:4]] for x in q]); return dict(lat=lat, f=(cart @ np.linalg.inv(lat)) % 1.0, sp=[_el(x[0]) for x in q])
    esc = float(L[1].split()[0]); lat = np.array([[float(x) for x in L[2 + k].split()[:3]] for k in range(3)]) * esc
    i = 5
    if re.match(r"^\s*[A-Za-z]", L[5]):
        nomes = L[5].split(); i = 6
    else:
        nomes = L[0].split()
    cont = [int(x) for x in L[i].split()]; i += 1
    if L[i].strip()[:1] in "sS":
        i += 1
    cart = L[i].strip()[:1] in "cCkK"; q = np.array([[float(v) for v in L[i + 1 + k].split()[:3]] for k in range(sum(cont))])
    sp = [n for n, c in zip(nomes, cont) for _ in range(c)]
    return dict(lat=lat, f=((q * esc) @ np.linalg.inv(lat) if cart else q) % 1.0, sp=[_el(x) for x in sp])


def simetria(st, symprec=0.01):
    """Grupo espacial e células padronizadas pelo moyo (mesmo algoritmo da versão web)."""
    try:
        import moyopy
    except ImportError:
        return None
    USADOS.add("moyo")
    cell = moyopy.Cell(np.asarray(st["lat"], float).tolist(), np.asarray(st["f"], float).tolist(), [Z_DE.get(x, 0) for x in st["sp"]])
    d = moyopy.MoyoDataset(cell, symprec=symprec)
    t = moyopy.SpaceGroupType(d.number)
    el = {v: k for k, v in Z_DE.items()}
    cel = lambda c: dict(lat=np.array(c.basis), f=np.array(c.positions), sp=[el.get(z, str(z)) for z in c.numbers])
    return dict(numero=d.number, hall=d.hall_number, hm=t.hm_short, hm_completo=t.hm_full, pearson=d.pearson_symbol, ops=d.operations.num_operations,
                sistema=t.crystal_system, bravais=t.bravais_class, classe=t.geometric_crystal_class, wyckoff=list(d.wyckoffs),
                sitio=list(d.site_symmetry_symbols), conv=cel(d.std_cell), prim=cel(d.prim_std_cell), inversao=any(np.allclose(np.array(r), -np.eye(3)) for r in d.operations.rotations))


def celula_texto(c, fmt, titulo="BrUMaRe"):
    lat, f, sp = c["lat"], c["f"], c["sp"]; els = list(dict.fromkeys(sp))
    if fmt == "poscar":
        o = [i for e in els for i, s in enumerate(sp) if s == e]
        return (f"{titulo}\n1.0\n" + "".join(f"  {v[0]:.10f} {v[1]:.10f} {v[2]:.10f}\n" for v in lat) + "  " + " ".join(els) + "\n  " +
                " ".join(str(sp.count(e)) for e in els) + "\nDirect\n" + "".join(f"  {f[i][0]:.10f} {f[i][1]:.10f} {f[i][2]:.10f} {sp[i]}\n" for i in o))
    if fmt == "cell":
        return ("%BLOCK LATTICE_CART\nANG\n" + "".join(f"  {v[0]:.10f} {v[1]:.10f} {v[2]:.10f}\n" for v in lat) + "%ENDBLOCK LATTICE_CART\n\n%BLOCK POSITIONS_FRAC\n" +
                "".join(f"  {s:<3} {x[0]:.10f} {x[1]:.10f} {x[2]:.10f}\n" for s, x in zip(sp, f)) + "%ENDBLOCK POSITIONS_FRAC\n")
    if fmt == "qe":
        return (f"CELL_PARAMETERS angstrom\n" + "".join(f"  {v[0]:.10f} {v[1]:.10f} {v[2]:.10f}\n" for v in lat) + "ATOMIC_POSITIONS crystal\n" +
                "".join(f"  {s:<3} {x[0]:.10f} {x[1]:.10f} {x[2]:.10f}\n" for s, x in zip(sp, f)) + f"! nat = {len(sp)}, ntyp = {len(els)}, ibrav = 0\n")
    L = np.linalg.norm(lat, axis=1); ang = lambda u, v: np.degrees(np.arccos(u @ v / np.linalg.norm(u) / np.linalg.norm(v)))
    return (f"data_{titulo}\n_symmetry_space_group_name_H-M 'P 1'\n_cell_length_a {L[0]:.6f}\n_cell_length_b {L[1]:.6f}\n_cell_length_c {L[2]:.6f}\n"
            f"_cell_angle_alpha {ang(lat[1], lat[2]):.4f}\n_cell_angle_beta {ang(lat[0], lat[2]):.4f}\n_cell_angle_gamma {ang(lat[0], lat[1]):.4f}\n"
            "loop_\n_symmetry_equiv_pos_as_xyz\n'x, y, z'\nloop_\n_atom_site_label\n_atom_site_type_symbol\n_atom_site_fract_x\n_atom_site_fract_y\n_atom_site_fract_z\n" +
            "".join(f"{s}{i + 1} {s} {x[0]:.8f} {x[1]:.8f} {x[2]:.8f}\n" for i, (s, x) in enumerate(zip(sp, f))))


def write_summary(fn, base, dname, B, D, X, species, lat, typ, dist, ticks, labels,
                  ef_ha, ef_ev, egrid, dos_tot, dos_g, groups, efpos, sites, a):
    """Escreve resumo.txt e mostra no terminal os numeros principais."""
    h, ns = B["hdr"], B["hdr"]["ns"]
    de = egrid[1] - egrid[0]
    L = []
    w = L.append
    sp_ = lambda s: (" up" if s == 0 else " down") if ns == 2 else ""
    an, bn, cn = np.linalg.norm(lat, axis=1)
    ang = lambda u, v: np.degrees(np.arccos(np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v)))
    w(f"RESUMO DA ANALISE: {base}   (DOS calculada a partir de: {dname})")
    w("=" * 74)
    w(f"k-pontos no .bands: {h['nk']}   spins: {ns}   autovalores: {h['neig']}")
    w(f"Rede: {typ}  a={an:.4f} b={bn:.4f} c={cn:.4f} A  alfa={ang(lat[1], lat[2]):.2f} "
      f"beta={ang(lat[0], lat[2]):.2f} gama={ang(lat[0], lat[1]):.2f} graus")
    w(f"Caminho k: {' - '.join(labels)}")
    for k, nome in (("functional", "Funcional"), ("cutoff", "Corte (eV)"),
                    ("volume", "Volume (A^3)"), ("energy", "Energia final (eV)")):
        if k in X["info"]:
            w(f"{nome}: {X['info'][k]}")
    w("")
    w("ENERGIA DE FERMI (valor do .bands, nao recalculado) E BORDAS DE BANDA")
    w("-" * 74)
    edges = []
    for s in range(ns):
        e = band_edges(B["eig"][s] * HA2EV, h["neig"][s], h["nelec"][s], ns, ef_ev[s],
                       dist, ticks, labels, B["kfrac"])
        edges.append(e)
        i0 = int(np.argmin(np.abs(egrid - efpos[s])))
        w(f"Spin{sp_(s)}:")
        w(f"  E_F = {ef_ha[s]:.6f} Ha = {ef_ev[s]:.4f} eV   eletrons = {h['nelec'][s]}")
        w(f"  VBM - E_F = {e['vbm'] - ef_ev[s]:+.4f} eV (banda {e['vb'] + 1}, k = {e['vkl']})")
        w(f"  CBM - E_F = {e['cbm'] - ef_ev[s]:+.4f} eV (banda {e['cb'] + 1}, k = {e['ckl']})")
        if CODE["name"] == "ORCA":
            w(f"  HOMO = {e['vbm']:.4f} eV (orbital {e['vb'] + 1}) | LUMO = {e['cbm']:.4f} eV (orbital {e['cb'] + 1})")
            w(f"  Gap HOMO-LUMO = {e['gap']:.4f} eV")
        else:
            w(f"  Gap banda N -> N+1 no caminho = {e['gap']:.4f} eV "
              f"({'direto' if e['direct'] else 'indireto'})")
        if B.get("pre") is None and not e["inside"]:
            Es = B["eig"][s] * HA2EV
            me = massas_efetivas(Es, dist, ticks, e["cb"], e["ck"], +1)
            mh = massas_efetivas(Es, dist, ticks, e["vb"], e["vk"], -1)
            if me:
                w(f"  m* eletron no CBM ({e['ckl']}) = " + " ; ".join(f"{x:.3f}" for x in me) + " m_e (ajuste parabolico ao longo do caminho)")
            if mh:
                w(f"  m* buraco no VBM ({e['vkl']}) = " + " ; ".join(f"{x:.3f}" for x in mh) + " m_e")
        w("  E_F dentro de banda: " + ("; ".join(f"sim, banda {b + 1} (largura {wd:.1f} meV)"
                                                for b, wd in e["inside"]) or "nao"))
        w(f"  N(E_F) = {dos_tot[s][i0]:.4f} estados/eV")
    if GAPCORR:
        w(f"CORRECAO DO GAP: {GAPCORR['metodo']}")
        w(f"  Gap DFT original = {GAPCORR['eg_dft']:.4f} eV | Delta = {GAPCORR['delta']:+.4f} eV | Gap corrigido = {GAPCORR['eg_corr']:.4f} eV")
        w("  Bandas desocupadas deslocadas por Delta; ocupadas e E_F sem alteracao (valores abaixo ja corrigidos).")
        for x in GAPCORR["avisos"]:
            w(f"  Aviso: {x}")
    if ns == 2:
        vb = max(e["vbm"] - ef_ev[s] for s, e in enumerate(edges))
        cb = min(e["cbm"] - ef_ev[s] for s, e in enumerate(edges))
        nu, nd = [dos_tot[s][int(np.argmin(np.abs(egrid - efpos[s])))] for s in (0, 1)]
        w(f"Gap considerando os dois spins = {cb - vb:.4f} eV")
        if nu + nd > 0.05:
            w(f"Polarizacao de spin em E_F = {100 * (nu - nd) / (nu + nd):.2f} %")
        else:
            w(f"Polarizacao de spin em E_F: nao definida (N(E_F) = {nu + nd:.2e} estados/eV: E_F no gap)")
        w(f"E_F(up) - E_F(down) = {(ef_ha[0] - ef_ha[1]) * HA2EV * 1000:.3f} meV")
        if "spin" in X["info"]:
            w(f"Spin integrado = {float(X['info']['spin']):.5f} hbar/2 "
              f"(momento = {float(X['info']['spin']):.5f} muB);  |spin| = {X['info'].get('abs_spin', '-')}")
    w("Obs.: bordas e gap vem so dos k-pontos do caminho; N(E_F) depende de sigma e da malha k.")
    if groups:
        w("")
        w("OCUPACAO INTEGRADA DA PDOS ATE E_F (eletrons, soma sobre os atomos)")
        w("-" * 74)
        w(f"{'projecao':<14}" + "".join(f"{'ocup' + sp_(s):>14}" for s in range(ns)) + f"{'total':>12}")
        dlines = []
        for i, g in enumerate(groups):
            if g["cat"] not in ("el", "l"):
                continue
            occ = [dos_g[s][i][egrid <= efpos[s]].sum() * de for s in range(ns)]
            tot = sum(dos_g[s][i].sum() * de for s in range(ns))
            w(f"{g['label']:<14}" + "".join(f"{x:14.3f}" for x in occ) + f"{tot:12.3f}")
            if g["cat"] == "l" and g.get("l") == 2 and tot > 0.05:
                cen = []
                for s in range(ns):
                    c, m = dos_g[s][i], egrid <= efpos[s]
                    x = egrid - efpos[s]
                    cen += [(c[m] * x[m]).sum() / c[m].sum() if c[m].sum() > 0 else np.nan,
                            (c * x).sum() / c.sum() if c.sum() > 0 else np.nan]
                dlines.append(f"{g['label']:<14}" + "".join(f"{v:12.3f}" for v in cen))
        if dlines:
            w("")
            w("CENTRO DA BANDA d (eV, relativo a E_F de cada spin)")
            w("-" * 74)
            w(f"{'projecao':<14}" + "".join(f"{'ocup' + sp_(s):>12}{'total' + sp_(s):>12}" for s in range(ns)))
            L.extend(dlines)
    if X["mull"]:
        w("")
        w("MULLIKEN POR ESPECIE (media)        s       p       d       f   carga  spin")
        w("-" * 74)
        by = {}
        for m in X["mull"]:
            by.setdefault(m["sp"], []).append(m)
        tot = lambda m, j: m["up"][j] + (m["dn"][j] if m["dn"] else 0)
        for k, lst in by.items():
            w(f"{k:<6}({len(lst):4d} atomos)          " +
              "".join(f"{np.mean([tot(m, j) for m in lst]):8.3f}" for j in range(4)) +
              f"{np.mean([m['charge'] for m in lst]):8.3f}{np.mean([m['spin'] for m in lst]):7.3f}")
        dop = {k for k, v in by.items() if len(v) <= 4}
        want = set(sites)
        ind = [m for m in X["mull"] if m["sp"] in dop or f"{m['sp']}{m['ion']}" in want or abs(m["spin"]) > 0.01]
        if ind:
            w("Atomos (dopantes, escolhidos com --sites e |spin| > 0.01):")
            for m in ind:
                w(f"  {m['sp'] + str(m['ion']):<10}" + "".join(f"{tot(m, j):8.3f}" for j in range(4)) +
                  f"{m['charge']:8.3f}{m['spin']:7.3f}")
        targ = dop | want
        bonds = sorted([b for b in X["bonds"] if any(t in (b["a"], b["b"], re.sub(r"\d+$", "", b["a"]),
                                                          re.sub(r"\d+$", "", b["b"])) for t in targ)],
                       key=lambda b: b["len"])[:40]
        if bonds:
            w("")
            w("LIGACOES DOS DOPANTES / ATOMOS ESCOLHIDOS     populacao   comprimento (A)")
            w("-" * 74)
            for b in bonds:
                w(f"  {b['a'] + ' - ' + b['b']:<28}{b['pop']:10.2f}{b['len']:16.5f}")
    if D["hdr"]["nk"] < 100 and CODE["name"] != "ORCA":
        w("")
        w(f"AVISO: a DOS usa {D['hdr']['nk']} k-pontos. Para valores quantitativos rode "
          "SPECTRAL_TASK : DOS com malha MP densa e use --dos-seed.")
    with open(fn, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f" -> {fn}")
    for l in L[L.index(next(x for x in L if x.startswith("ENERGIA"))):]:
        if l.startswith(("Spin", "  E_F", "  Gap", "  E_F dentro", "Gap", "Polariz", "Spin integ")):
            print(" " + l)


# =========================================================================== #
#        OUTROS CODIGOS: VASP E SIESTA (camada de entrada unica)               #
# =========================================================================== #
# Os leitores abaixo convertem as saidas do VASP e do SIESTA para as MESMAS
# estruturas internas usadas com o CASTEP (energias em Hartree, rede em Bohr no
# .bands, estrutura em Angstrom). Os dados convertidos ficam num registro de
# "arquivos virtuais" (seed.bands, seed.cell, seed.castep, seed.pdos_bin,
# seed.den_fmt): os leitores do CASTEP consultam esse registro antes do disco,
# e todo o resto do BrUMaRe funciona sem saber de qual programa vieram os dados.
_VIRT = {}
_VNAME = {}                                   # caminho virtual -> arquivo real (para as mensagens)
CODE = {"name": "CASTEP"}                     # programa do calculo principal

SYMBOLS = ("X H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr "
           "Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb "
           "Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu").split()

# componentes m: VASP (campos do vasprun) e SIESTA (harmonicos reais, m = -l..l)
VASP2M = {"s": "s", "py": "py", "pz": "pz", "px": "px", "dxy": "dxy", "dyz": "dyz", "dz2": "dz2",
          "dxz": "dxz", "dx2": "dx2-y2", "x2-y2": "dx2-y2", "dx2-y2": "dx2-y2"}
SIESTA_M = {0: {0: "s"}, 1: {-1: "py", 0: "pz", 1: "px"},
            2: {-2: "dxy", -1: "dyz", 0: "dz2", 1: "dxz", 2: "dx2-y2"}}


def _vexists(p):
    return (p in _VIRT) or os.path.isfile(p)


def _virt(p, key=None):
    """Objeto registrado para o caminho p (carregado sob demanda), ou None."""
    if p not in _VIRT:
        return None
    v = _VIRT[p]
    if callable(v):
        v = _VIRT[p] = v()
    return v if key is None else (v.get(key) if isinstance(v, dict) else None)


def _floats(txt):
    return np.array(txt.split(), float)


def _nelec_from_ef(eig_ev, ef_ev, kw):
    """Eletrons por spin contando os autovalores abaixo de E_F (media ponderada nos k)."""
    occ = (eig_ev < ef_ev).sum(axis=1)
    return float(np.sum(occ * kw) / np.sum(kw))


def _orbital_record(sp_idx, ion, am, m=None, shells=None):
    P = dict(species=np.array(sp_idx, int), ion=np.array(ion, int), am=np.array(am, int))
    if m is not None:
        P["mnames"] = list(m)
    if shells is not None:
        P["shells"] = list(shells)
    return P


# ------------------------------- VASP --------------------------------------- #
def read_kpoints_labels(fn):
    """Rotulos de um KPOINTS em modo de linha ('G,X,W,K|U,...'), ou None."""
    if not fn or not os.path.isfile(fn):
        return None
    L = open(fn, errors="replace").read().splitlines()
    if len(L) < 4 or not L[2].strip().lower().startswith("l"):
        return None
    pts = []
    for l in L[4:]:
        if not l.strip():
            continue
        lab = l.split("!")[1].strip() if "!" in l else "?"
        lab = lab.replace("\\Gamma", "G").replace("GAMMA", "G").replace("Gamma", "G").replace("\\G", "G") or "?"
        pts.append(lab)
    seq = []
    for a_, b_ in zip(pts[0::2], pts[1::2]):
        if not seq:
            seq = [a_, b_]
        elif seq[-1] == a_:
            seq.append(b_)
        else:
            seq[-1] = seq[-1] + "|" + a_
            seq.append(b_)
    return ",".join(seq) if seq else None


def read_vasprun(fn):
    """vasprun.xml em fluxo (iterparse): bandas, projecoes (LORBIT>=10), estrutura,
    energias, forcas, valencias. Usa o ULTIMO calculo do arquivo."""
    import xml.etree.ElementTree as ET
    R = dict(params={}, atoms=[], types=[], kfrac=None, kw=None, lat=None, frac=None, E={},
             forces=None, efermi=None, eig=None, occ=None, proj=None, fields=None, ncl=False, gen="")
    depth = 0
    for ev, el in ET.iterparse(fn, events=("start", "end")):
        if ev == "start":
            depth += 1
            continue
        depth -= 1
        tag = el.tag
        if tag == "i" and el.get("name") in ("NELECT", "ISPIN", "LNONCOLLINEAR", "LSORBIT", "ENCUT", "GGA", "LORBIT", "METAGGA"):
            R["params"].setdefault(el.get("name"), (el.text or "").strip())
        elif tag == "array" and el.get("name") == "atoms":
            R["atoms"] = [(r[0].text.strip(), int(r[1].text)) for r in el.iter("rc")]
        elif tag == "array" and el.get("name") == "atomtypes":
            R["types"] = [[c.text.strip() for c in r] for r in el.iter("rc")]
        elif tag == "kpoints" and R["kfrac"] is None and depth == 1:
            g = el.find("generation")
            R["gen"] = g.get("param", "") if g is not None else ""
            for va in el.iter("varray"):
                v = np.array([[float(x) for x in r.text.split()] for r in va.iter("v")])
                if va.get("name") == "kpointlist":
                    R["kfrac"] = v
                elif va.get("name") == "weights":
                    R["kw"] = v.ravel()
            el.clear()
        elif tag == "structure" and el.get("name") in (None, "finalpos"):
            for va in el.iter("varray"):
                v = np.array([[float(x) for x in r.text.split()] for r in va.iter("v")])
                if va.get("name") == "basis":
                    R["lat"] = v
                elif va.get("name") == "positions":
                    R["frac"] = v
            if el.get("name") == "finalpos":
                el.clear()
        elif tag == "calculation":
            en = el.find("energy")
            if en is not None:
                for i in en.iter("i"):
                    try:
                        R["E"][i.get("name")] = float(i.text)
                    except (TypeError, ValueError):
                        pass
            if not R["E"].get("e_0_energy"):                  # algumas versoes gravam 0 no bloco final
                v0 = [float(i.text) for sc in el.findall("scstep") for en2 in sc.findall("energy") for i in en2.findall("i")
                      if i.get("name") == "e_0_energy" and float(i.text) != 0.0]
                R["E"]["e_0_energy"] = v0[-1] if v0 else None
            for va in el.findall("varray"):
                if va.get("name") == "forces":
                    R["forces"] = np.array([[float(x) for x in r.text.split()] for r in va.iter("v")])
            eg = el.find("eigenvalues")
            if eg is not None:
                sets = eg.find("array").find("set").findall("set")       # spins
                eig, occ = [], []
                for sset in sets:
                    ks = sset.findall("set")
                    blk = [_floats(" ".join(r.text for r in kset.findall("r"))).reshape(-1, 2) for kset in ks]
                    eig.append(np.array([b[:, 0] for b in blk]))
                    occ.append(np.array([b[:, 1] for b in blk]))
                R["eig"], R["occ"] = np.array(eig), np.array(occ)
            d = el.find("dos")
            if d is not None and d.find("i") is not None:
                for i in d.findall("i"):
                    if i.get("name") == "efermi":
                        R["efermi"] = float(i.text)
            pj = el.find("projected")
            if pj is not None:
                arr = pj.find("array")
                R["fields"] = [f.text.strip() for f in arr.findall("field")]
                spins = arr.find("set").findall("set")
                prj = []
                for sset in spins:
                    kl = []
                    for kset in sset.findall("set"):
                        kl.append([_floats(" ".join(r.text for r in bset.findall("r"))).reshape(-1, len(R["fields"]))
                                   for bset in kset.findall("set")])
                    prj.append(np.array(kl))               # (nk, nb, nion, norb)
                R["proj"] = np.array(prj)
            el.clear()
    if R["eig"] is None or R["kfrac"] is None or R["lat"] is None:
        raise ValueError(f"{fn}: vasprun.xml incompleto (sem autovalores, k-pontos ou rede)")
    R["ncl"] = R["params"].get("LNONCOLLINEAR", "F").upper().startswith("T") or R["eig"].shape[0] == 1 and \
        R["proj"] is not None and R["proj"].shape[0] == 4
    return R


def load_vasp(path):
    """Registra um calculo VASP (pasta ou vasprun.xml). Devolve o seed virtual."""
    vr = path if os.path.isfile(path) else os.path.join(path, "vasprun.xml")
    d = os.path.dirname(os.path.abspath(vr))
    name = os.path.basename(d) if os.path.basename(vr) == "vasprun.xml" else \
        re.sub(r"(^vasprun[._-]?|[._-]?vasprun|\.xml$)", "", os.path.basename(vr)) or os.path.basename(d)
    seed = os.path.join(d, name)
    R = read_vasprun(vr)
    ns, nk, nb = R["eig"].shape
    ef = R["efermi"] if R["efermi"] is not None else float(np.nanmax(R["eig"][R["occ"] > 0.5]))
    kw = R["kw"] / R["kw"].sum()
    nel_tot = float(R["params"].get("NELECT", "nan"))
    if ns == 2:
        nelec = [float(np.sum(R["occ"][s].sum(axis=1) * kw)) for s in range(2)]
        nelec = [round(x) if abs(x - round(x)) < 1e-3 else x for x in nelec]
    else:
        nelec = [nel_tot if np.isfinite(nel_tot) else 2 * _nelec_from_ef(R["eig"][0], ef, kw)]
    lat_bohr = R["lat"] / BOHR2ANG
    B = dict(hdr=dict(nk=nk, ns=ns, nelec=nelec, neig=[nb] * ns, efermi=[ef / HA2EV] * ns, lattice=lat_bohr),
             header_lines=[], kidx=np.arange(1, nk + 1), kfrac=R["kfrac"], kw=kw, eig=R["eig"] / HA2EV, code="VASP")
    lab = read_kpoints_labels(os.path.join(d, "KPOINTS"))
    if lab:
        B["labels"] = lab
    elif R["gen"] and not R["gen"].lower().startswith("list"):        # malha MP/Gamma: nao e um caminho
        print(f" AVISO: {name} usa uma malha de k-pontos ({R['gen']}), nao um caminho: o grafico de bandas segue a\n"
              "        ordem da malha. Gap, DOS e PDOS continuam validos; para bandas use KPOINTS em modo de linha.")
        x = np.linspace(0, 1, nk)
        B["pre"] = (x, np.array([0.0, 1.0]), ["k1", f"k{nk}"])
    sp = [a for a, _ in R["atoms"]]
    species = list(dict.fromkeys(sp))
    struct = dict(lat=R["lat"], sp=sp, f=R["frac"], masses={t[1]: float(t[2]) for t in R["types"] if len(t) > 2}, src="vasprun")
    E = R["E"]
    C = dict(lat=R["lat"], sp=sp, f=R["frac"], forces=R["forces"], pressure=None,
             E=dict(final=E.get("e_wo_entrp", E.get("e_fr_energy")), free=E.get("e_fr_energy"), zeroK=E.get("e_0_energy")),
             info=dict(functional=(R["params"].get("METAGGA") if R["params"].get("METAGGA") not in (None, "", "--") else
                                 "padrao do POTCAR (GGA = --)" if R["params"].get("GGA") in (None, "", "--") else R["params"]["GGA"]),
                       cutoff=R["params"].get("ENCUT", "")))
    X = dict(mull=[], bonds=[], info=dict(functional=C["info"]["functional"], cutoff=C["info"]["cutoff"],
                                         energy=str(C["E"]["final"])), species=species)
    zion = {t[1]: float(t[3]) for t in R["types"] if len(t) > 3}
    X["zion"] = zion
    _VIRT[seed + ".bands"] = B
    _VIRT[seed + ".cell"] = dict(species=species, struct=struct)
    _VIRT[seed + ".castep"] = dict(extra=X, struct=C, orbitals=({}, {}), zion=zion)
    if R["proj"] is not None:
        prj = R["proj"][:1] if R["ncl"] else R["proj"]            # nao colinear: so a parte total
        nsp, _, _, nion, nf = prj.shape
        cnt, sp_idx, ion, am, mm, sh = {}, [], [], [], [], []
        for a_ in sp:
            cnt[a_] = cnt.get(a_, 0) + 1
            for f in R["fields"]:
                sp_idx.append(species.index(a_) + 1); ion.append(cnt[a_])
                l = 0 if f == "s" else 1 if f in ("px", "py", "pz") else 2 if f.startswith("d") or f in ("x2-y2",) else 3
                am.append(l); mm.append(VASP2M.get(f, f)); sh.append("spdf"[l])
        P = _orbital_record(sp_idx, ion, am, mm, sh)
        P["w"] = prj.reshape(nsp, nk, nb, nion * nf)
        P["kidx"], P["kfrac"] = np.arange(1, nk + 1), R["kfrac"]
        _VIRT[seed + ".pdos_bin"] = P
    for nm in ("CHGCAR", "PARCHG", "CHG"):
        if os.path.isfile(os.path.join(d, nm)):
            fn = os.path.join(d, nm)
            _VIRT[seed + ".den_fmt"] = (lambda fn=fn: read_chgcar(fn)); _VNAME[seed + ".den_fmt"] = fn
            break
    CODE["vasp_ncl"] = R["ncl"]
    return seed


# ------------------------------ SIESTA -------------------------------------- #
def is_siesta_bands(fn):
    try:
        with open(fn) as f:
            first = f.readline().split()
        return len(first) == 1 and re.match(r"^-?[\d.]+(E[-+]?\d+)?$", first[0], re.I) is not None
    except (OSError, UnicodeDecodeError):
        return False


def read_siesta_bands(fn):
    """SystemLabel.bands nos dois formatos do SIESTA:
    BandLines  (4 linhas de cabecalho; por k: distancia acumulada e autovalores; rotulos no fim)
    BandPoints (3 linhas de cabecalho; por k: kx ky kz em 1/Bohr e autovalores; sem rotulos)."""
    L = open(fn).read().split("\n")
    ef = float(L[0].split()[0])
    isint = lambda t: len(t) >= 3 and all(re.match(r"^-?\d+$", x) for x in t[:3])
    if isint(L[2].split()):
        mode, h, ncol = "points", 2, 3
    else:
        mode, h, ncol = "lines", 3, 1
    nb, ns, nk = (int(x) for x in L[h].split()[:3])
    toks, i = [], h + 1
    need = nk * (ncol + nb * ns)
    while len(toks) < need and i < len(L):
        toks.extend(L[i].split()); i += 1
    v = np.array(toks[:need], float).reshape(nk, ncol + nb * ns)
    eig = v[:, ncol:].reshape(nk, ns, nb).transpose(1, 0, 2)    # (ns, nk, nb) eV
    out = dict(ef=ef, nb=nb, ns=ns, nk=nk, eig=eig, mode=mode)
    if mode == "points":
        out["kcart"] = v[:, :3]                                    # 1/Bohr
        return out
    ticks, labels = [], []
    while i < len(L) and not L[i].strip():
        i += 1
    if i < len(L) and L[i].split():
        nt = int(L[i].split()[0]); i += 1
        for l in L[i:i + nt]:
            m = re.match(r"\s*(-?[\d.Ee+-]+)\s+'(.*)'", l)
            if m:
                lab = m[2].strip()
                ticks.append(float(m[1])); labels.append("\u0393" if lab.lower() in ("gamma", "g", "\\gamma") else lab)
    out.update(dist=v[:, 0] / BOHR2ANG, ticks=np.array(ticks) / BOHR2ANG, labels=labels)
    return out


def read_siesta_eig(fn, kpfn=None, lat_bohr=None):
    """SystemLabel.EIG (+ .KP com os pesos)."""
    L = open(fn).read().split("\n")
    ef = float(L[0].split()[0])
    nb, ns, nk = (int(x) for x in L[1].split()[:3])
    toks = " ".join(L[2:]).split()
    per = nb * ns + 1
    v = np.array(toks[:nk * per], float).reshape(nk, per)[:, 1:]
    eig = v.reshape(nk, ns, nb).transpose(1, 0, 2)
    kw, kfrac = np.full(nk, 1.0 / nk), np.zeros((nk, 3))
    if kpfn and os.path.isfile(kpfn):
        K = np.array([l.split() for l in open(kpfn).read().split("\n")[1:] if len(l.split()) >= 5], float)[:nk]
        kw = K[:, 4] / K[:, 4].sum()
        if lat_bohr is not None:
            kfrac = K[:, 1:4] @ lat_bohr.T / (2 * np.pi)
    return dict(ef=ef, nb=nb, ns=ns, nk=nk, eig=eig, kw=kw, kfrac=kfrac)


def read_siesta_struct(seed):
    """STRUCT_OUT (Angstrom, fracionario) ou XV (Bohr, cartesiano)."""
    if os.path.isfile(seed + ".STRUCT_OUT"):
        L = open(seed + ".STRUCT_OUT").read().split("\n")
        lat = np.array([[float(x) for x in L[i].split()[:3]] for i in range(3)])
        n = int(L[3].split()[0])
        rows = [L[4 + i].split() for i in range(n)]
        return dict(lat=lat, sp=[SYMBOLS[int(r[1])] for r in rows], f=np.array([[float(x) for x in r[2:5]] for r in rows]), masses={}, src="STRUCT_OUT")
    if os.path.isfile(seed + ".XV"):
        L = open(seed + ".XV").read().split("\n")
        lat = np.array([[float(x) for x in L[i].split()[:3]] for i in range(3)]) * BOHR2ANG
        n = int(L[3].split()[0])
        rows = [L[4 + i].split() for i in range(n)]
        cart = np.array([[float(x) for x in r[2:5]] for r in rows]) * BOHR2ANG
        return dict(lat=lat, sp=[SYMBOLS[int(r[1])] for r in rows], f=cart @ np.linalg.inv(lat), masses={}, src="XV")
    return None


def read_siesta_out(seed):
    """Energias, E_F, forcas, momento, eletrons, valencias e funcional da saida do SIESTA."""
    d = os.path.dirname(os.path.abspath(seed)) or "."
    cands = [seed + ".out", os.path.join(d, "RUN.out")] + sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".out"))
    fn = next((c for c in cands if os.path.isfile(c) and "siesta" in open(c, errors="replace").read(4000).lower()), None)
    out = dict(E={}, forces=None, fmax=None, ef=None, spin=None, nel=None, zion={}, func="", cut="", fn=fn)
    if not fn:
        return out
    L = open(fn, errors="replace").read().splitlines()
    num = r"(-?[\d.]+(?:[EeDd][-+]?\d+)?)"
    for l in L:
        for key, pat in (("final", r"siesta:\s+Total\s*=\s*" + num), ("free", r"siesta: FreeEng\s*=\s*" + num),
                         ("ks", r"siesta: E_KS\(eV\)\s*=\s*" + num), ("etot", r"siesta: Etot\s*=\s*" + num)):
            m = re.search(pat, l)
            if m:
                out["E"][key] = float(m[1].replace("D", "E"))
        m = re.search(r"siesta:\s+Fermi\s*=\s*" + num, l) or re.search(r"Fermi\s*=\s*" + num, l)
        if m and "siesta:" in l:
            out["ef"] = float(m[1])
        m = re.search(r"spin moment: \{S\} , \|S\| = \{.*\}\s+" + num, l)
        if m:
            out["spin"] = float(m[1])
        m = re.search(r"Total number of electrons:\s*" + num, l)
        if m:
            out["nel"] = float(m[1])
        m = re.match(r"\s*Max\s+" + num + r"\s*$", l)
        if m:
            out["fmax"] = float(m[1])
    spl = [re.search(r"Label:\s*(\S+)", l)[1] for l in L if re.search(r"Species number:.*Label:", l)]
    val = [float(re.search(num, l.split(":")[-1])[1]) for l in L if "Valence charge in pseudo generation" in l]
    out["zion"] = {s_: v for s_, v in zip(spl, val)}
    for i, l in enumerate(L):
        if "xc_check: Exchange-correlation functional" in l and i + 1 < len(L):
            out["func"] = L[i + 1].replace("xc_check:", "").strip()
        m = re.search(r"MeshCutoff\s*[=:]?\s*" + num, l, re.I)
        if m and not out["cut"]:
            out["cut"] = m[1] + " Ry"
    k = max([i for i, l in enumerate(L) if "siesta: Atomic forces (eV/Ang):" in l], default=-1)
    if k >= 0:
        F = []
        for l in L[k + 1:]:
            m = re.match(r"^\s*(?:siesta:)?\s*\d+\s+" + num + r"\s+" + num + r"\s+" + num + r"\s*$", l)
            if m:
                F.append([float(m[1]), float(m[2]), float(m[3])])
            elif F or "Tot" in l:
                break
        out["forces"] = np.array(F) if F else None
    return out


def read_siesta_pdos(fn):
    """SystemLabel.PDOS / .PDOS.xml: curvas de PDOS ja calculadas pelo SIESTA, por orbital (n, l, m, zeta)."""
    import xml.etree.ElementTree as ET
    root = ET.parse(fn).getroot()
    ns = int(root.findtext("nspin").strip())
    ef = float(root.findtext("fermi_energy").strip())
    E = _floats(root.findtext("energy_values"))
    orbs, data = [], []
    for o in root.iter("orbital"):
        orbs.append(dict(sp=o.get("species"), atom=int(o.get("atom_index")), n=int(o.get("n")), l=int(o.get("l")),
                         m=int(o.get("m")), z=int(o.get("z"))))
        data.append(_floats(o.findtext("data")).reshape(len(E), -1)[:, :min(ns, 2)].T)    # (ns, nE)
    return dict(E=E, ef=ef, ns=min(ns, 2), orbs=orbs, data=np.array(data))            # data (norb, ns, nE)


def read_siesta_rho(fn):
    """SystemLabel.RHO (Fortran sem formato): celula (Bohr), grade, nspin e rho (e/Bohr^3) em precisao simples."""
    b = open(fn, "rb").read()
    end = "<" if struct.unpack("<i", b[:4])[0] in (72, 80) else ">"
    pos = 0

    def rec():
        nonlocal pos
        n = struct.unpack(end + "i", b[pos:pos + 4])[0]
        s = b[pos + 4:pos + 4 + n]
        pos += n + 8
        return s
    cell = np.frombuffer(rec()[:72], end + "f8").reshape(3, 3) * BOHR2ANG
    n1, n2, n3, nsp = struct.unpack(end + "4i", rec()[:16])
    rho = np.zeros((nsp, n1, n2, n3))
    for s_ in range(nsp):
        for k in range(n3):
            for j in range(n2):
                rho[s_, :, j, k] = np.frombuffer(rec(), end + "f4")
    rho /= BOHR2ANG ** 3                                         # e/Bohr^3 -> e/A^3
    V = abs(np.linalg.det(cell))
    tot = rho[0] + (rho[1] if nsp >= 2 else 0)
    out = dict(lat=cell, n=[n1, n2, n3], rho=tot, spin=None, V=V, Nel=tot.mean() * V)
    if nsp >= 2:
        m_ = rho[0] - rho[1]
        out.update(spin=m_, Sint=m_.mean() * V, Sabs=np.abs(m_).mean() * V)
    return out


def load_siesta(seed):
    """Registra um calculo SIESTA (SystemLabel). Devolve o seed (e o seed da DOS, se houver .EIG)."""
    st = read_siesta_struct(seed)
    O = read_siesta_out(seed)
    lat_bohr = st["lat"] / BOHR2ANG if st else None
    sp = st["sp"] if st else []
    species = list(dict.fromkeys(sp))
    dos_seed = None
    E = None
    if os.path.isfile(seed + ".EIG"):
        E = read_siesta_eig(seed + ".EIG", seed + ".KP", lat_bohr)
    ef = O["ef"] if O["ef"] is not None else (E["ef"] if E else None)

    def bands_from(e, eig, kfrac, kw, efv, pre=None):
        ns_ = eig.shape[0]
        nel = [_nelec_from_ef(eig[s], efv, kw) for s in range(ns_)]
        if ns_ == 1:
            nel = [O["nel"] if O["nel"] else 2 * nel[0]]
        B = dict(hdr=dict(nk=eig.shape[1], ns=ns_, nelec=[round(x) if abs(x - round(x)) < 1e-3 else x for x in nel],
                          neig=[eig.shape[2]] * ns_, efermi=[efv / HA2EV] * ns_,
                          lattice=lat_bohr if lat_bohr is not None else np.eye(3)),
                 header_lines=[], kidx=np.arange(1, eig.shape[1] + 1), kfrac=kfrac, kw=kw, eig=eig / HA2EV, code="SIESTA")
        if pre:
            B["pre"] = pre
        return B
    if os.path.isfile(seed + ".bands") and is_siesta_bands(seed + ".bands"):
        S = read_siesta_bands(seed + ".bands")
        efv = ef if ef is not None else S["ef"]
        wk = np.full(S["nk"], 1.0 / S["nk"])
        if S["mode"] == "lines":
            Bv = bands_from(S, S["eig"], np.zeros((S["nk"], 3)), wk, efv, pre=(S["dist"], S["ticks"], S["labels"]))
        elif lat_bohr is not None:                        # BandPoints + rede: fracionarias, rotulos automaticos
            Bv = bands_from(S, S["eig"], S["kcart"] @ lat_bohr.T / (2 * np.pi), wk, efv)
        else:                                              # BandPoints sem rede: distancia cartesiana acumulada
            kc = S["kcart"] / BOHR2ANG
            dist = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(kc, axis=0), axis=1))])
            print(" AVISO: .bands no formato BandPoints e sem STRUCT_OUT/XV: sem rotulos de alta simetria.")
            Bv = bands_from(S, S["eig"], np.zeros((S["nk"], 3)), wk, efv, pre=(dist, np.array([dist[0], dist[-1]]), ["k1", f"k{S['nk']}"]))
        _VIRT[seed + ".bands"] = Bv
        if E is not None:
            dos_seed = seed + "_EIG"
            _VIRT[dos_seed + ".bands"] = bands_from(E, E["eig"], E["kfrac"], E["kw"], efv)
    elif E is not None:                                    # so a malha do SCF: sem caminho de bandas
        print(" AVISO: sem .bands (BandLines/BandPoints): o grafico de bandas usa a ordem da malha de k-pontos\n"
              "        (sem significado de caminho). Gap, DOS e PDOS continuam validos.")
        x = np.linspace(0, 1, E["nk"])
        _VIRT[seed + ".bands"] = bands_from(E, E["eig"], E["kfrac"], E["kw"], ef, pre=(x, np.array([0.0, 1.0]), ["k1", f"k{E['nk']}"]))
    struct_ = dict(st) if st else None
    Ed = dict(final=O["E"].get("final", O["E"].get("etot")), free=O["E"].get("free"), zeroK=None,
              corrected=None)
    forces = O["forces"]
    if forces is None and O["fmax"] is not None and st:
        forces = np.zeros((len(sp), 3)); forces[0, 0] = O["fmax"]            # so a forca maxima e conhecida
    C = dict(lat=st["lat"] if st else None, sp=sp or None, f=st["f"] if st else None, forces=forces, pressure=None,
             E=Ed, info=dict(functional=O["func"], cutoff=O["cut"]))
    X = dict(mull=[], bonds=[], species=species, zion=O["zion"],
             info=dict(functional=O["func"], cutoff=O["cut"], energy=str(Ed["final"]), spin=O["spin"]))
    if st:
        _VIRT[seed + ".cell"] = dict(species=species, struct=struct_)
    _VIRT[seed + ".castep"] = dict(extra=X, struct=C, orbitals=({}, {}), zion=O["zion"])
    pd = next((seed + e for e in (".PDOS.xml", ".PDOS") if os.path.isfile(seed + e)), None)
    if pd:
        D = read_siesta_pdos(pd)
        sps = list(dict.fromkeys([o["sp"] for o in D["orbs"]]))
        for s_ in sps:
            if s_ not in species:
                species.append(s_)
        cnt, first = {}, {}
        for o in D["orbs"]:                                      # indice do atomo dentro da especie
            if o["atom"] not in first:
                cnt[o["sp"]] = cnt.get(o["sp"], 0) + 1; first[o["atom"]] = cnt[o["sp"]]
        P = _orbital_record([species.index(o["sp"]) + 1 for o in D["orbs"]], [first[o["atom"]] for o in D["orbs"]],
                            [o["l"] for o in D["orbs"]], [SIESTA_M.get(o["l"], {}).get(o["m"], f"m{o['m']}") for o in D["orbs"]],
                            [f"{o['n']}{'spdf'[min(o['l'], 3)]}" for o in D["orbs"]])
        P["curves"] = D
        for s_ in (seed, dos_seed):
            if s_:
                _VIRT[s_ + ".pdos_bin"] = P
    if os.path.isfile(seed + ".RHO"):
        _VIRT[seed + ".den_fmt"] = (lambda fn=seed + ".RHO": read_siesta_rho(fn)); _VNAME[seed + ".den_fmt"] = seed + ".RHO"
    return seed, dos_seed


# =========================================================================== #
#   NOVAS ANALISES: Quantum ESPRESSO, ORCA, Bader e massas efetivas           #
# =========================================================================== #
def read_qe_xml(fn):
    """data-file-schema.xml do pw.x (Quantum ESPRESSO): energias em Ha, posicoes em Bohr, k em 2pi/alat."""
    import xml.etree.ElementTree as ET
    root = ET.parse(fn).getroot()
    out = root.find("output")
    if out is None:
        raise ValueError(f"{fn}: sem bloco <output> (calculo incompleto?)")
    st = out.find("atomic_structure")
    alat = float(st.get("alat", 1.0))
    cell = np.array([[float(x) for x in st.find("cell").find(t).text.split()] for t in ("a1", "a2", "a3")])
    atoms = [(a.get("name"), [float(x) for x in a.text.split()]) for a in st.find("atomic_positions").findall("atom")]
    bs = out.find("band_structure")
    lsda = (bs.findtext("lsda") or "false").strip().lower() == "true"
    nel = float(bs.findtext("nelec"))
    if bs.find("fermi_energy") is not None:
        ef = [float(bs.findtext("fermi_energy"))] * (2 if lsda else 1)
    elif bs.find("two_fermi_energies") is not None:
        ef = [float(x) for x in bs.findtext("two_fermi_energies").split()]
    else:
        ho = bs.findtext("highestOccupiedLevel")
        lu = bs.findtext("lowestUnoccupiedLevel")
        ef = [float(ho) if lu is None else 0.5 * (float(ho) + float(lu))] * (2 if lsda else 1)
    ks = bs.findall("ks_energies")
    kc, kw, ev, oc = [], [], [], []
    for k in ks:
        kp = k.find("k_point")
        kc.append([float(x) for x in kp.text.split()]); kw.append(float(kp.get("weight")))
        ev.append([float(x) for x in k.findtext("eigenvalues").split()])
        oc.append([float(x) for x in k.findtext("occupations").split()])
    ev, oc = np.array(ev), np.array(oc)
    ns = 2 if lsda else 1
    nb = ev.shape[1] // ns
    eig = np.stack([ev[:, s * nb:(s + 1) * nb] for s in range(ns)])        # (ns, nk, nb) Ha
    occ = np.stack([oc[:, s * nb:(s + 1) * nb] for s in range(ns)])
    kfrac = np.array(kc) @ cell.T / alat                                     # k (2pi/alat, cart.) -> fracionario
    E = {}
    te = out.find("total_energy")
    if te is not None:
        for tag in ("etot", "eband", "demet"):
            if te.findtext(tag):
                E[tag] = float(te.findtext(tag)) * HA2EV
    func = (root.findtext("input/dft/functional") or out.findtext("dft/functional") or "").strip()
    cut = out.findtext("basis_set/ecutwfc")
    return dict(cell=cell * BOHR2ANG, atoms=[(n, np.array(p) * BOHR2ANG) for n, p in atoms], eig=eig, occ=occ, kfrac=kfrac,
                kw=np.array(kw), ef=ef, nel=nel, E=E, func=func, cut=f"{float(cut) * 2:.0f} Ry" if cut else "")


def load_qe(path):
    """Registra um calculo Quantum ESPRESSO (pasta .save, pasta com data-file-schema.xml ou o proprio XML)."""
    fn = path if os.path.isfile(path) else os.path.join(path, "data-file-schema.xml")
    d = os.path.dirname(os.path.abspath(fn))
    name = re.sub(r"\.save$", "", os.path.basename(d)) or "qe"
    seed = os.path.join(d, name)
    R = read_qe_xml(fn)
    ns, nk, nb = R["eig"].shape
    kw = R["kw"] / R["kw"].sum()
    if ns == 2:
        nelec = [float(np.sum(R["occ"][s].sum(axis=1) * kw)) for s in range(2)]
        nelec = [round(x) if abs(x - round(x)) < 1e-3 else x for x in nelec]
    else:
        nelec = [R["nel"]]
    ef = R["ef"] if len(R["ef"]) == ns else [R["ef"][0]] * ns
    B = dict(hdr=dict(nk=nk, ns=ns, nelec=nelec, neig=[nb] * ns, efermi=list(ef), lattice=R["cell"] / BOHR2ANG),
             header_lines=[], kidx=np.arange(1, nk + 1), kfrac=R["kfrac"], kw=kw, eig=R["eig"], code="QE")
    lat = R["cell"]
    sp = [n for n, _ in R["atoms"]]
    species = list(dict.fromkeys(sp))
    f = np.array([p for _, p in R["atoms"]]) @ np.linalg.inv(lat)
    struct = dict(lat=lat, sp=sp, f=f, masses={}, src="data-file-schema.xml")
    C = dict(lat=lat, sp=sp, f=f, forces=None, pressure=None, E=dict(final=R["E"].get("etot"), free=None, zeroK=None),
             info=dict(functional=R["func"], cutoff=R["cut"]))
    X = dict(mull=[], bonds=[], species=species, zion={}, info=dict(functional=R["func"], cutoff=R["cut"], energy=str(C["E"]["final"])))
    _VIRT[seed + ".bands"] = B
    _VIRT[seed + ".cell"] = dict(species=species, struct=struct)
    _VIRT[seed + ".castep"] = dict(extra=X, struct=C, orbitals=({}, {}), zion={})
    for cube in sorted(glob.glob(os.path.join(os.path.dirname(d), "*.cube")) + glob.glob(os.path.join(d, "*.cube"))):
        _VIRT[seed + ".den_fmt"] = (lambda fn=cube: read_density(fn)); _VNAME[seed + ".den_fmt"] = cube
        break
    return seed


def read_orca(fn):
    """Saida .out do ORCA: orbitais (ultimo bloco), energia final, geometria, cargas de Mulliken e Loewdin."""
    L = open(fn, errors="replace").read().splitlines()
    idx = [i for i, l in enumerate(L) if l.strip() == "ORBITAL ENERGIES"]
    if not idx:
        raise ValueError(f"{fn}: sem 'ORBITAL ENERGIES'")
    linha = re.compile(r"^\s*(\d+)\s+([\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)")
    blocos, i = [], idx[-1] + 1
    fim = min([k for k in range(idx[-1] + 1, len(L)) if "MULLIKEN" in L[k] or "MOLECULAR ORBITALS" in L[k] or "TIMINGS" in L[k]] or [len(L)])
    while i < fim:
        if re.match(r"^\s*NO\s+OCC\s+E\(Eh\)", L[i]):                  # cabeçalho de um bloco (restrito, spin up ou down)
            cur, i = [], i + 1
            while i < fim and linha.match(L[i]):
                m = linha.match(L[i]); cur.append((float(m[2]), float(m[3]))); i += 1
            if cur:
                blocos.append(cur)
        i += 1
    ns = len(blocos)
    nb = min(len(b) for b in blocos)
    eig = np.array([[[e for _, e in b[:nb]]] for b in blocos])             # (ns, 1, nb) Ha
    occ = np.array([[o for o, _ in b[:nb]] for b in blocos])
    homo = max(e for b in blocos for o, e in b if o > 0.5)
    E = [float(re.search(r"(-?[\d.]+)\s*$", l).group(1)) for l in L if "FINAL SINGLE POINT ENERGY" in l]
    g = [i for i, l in enumerate(L) if l.strip() == "CARTESIAN COORDINATES (ANGSTROEM)"]
    atoms = []
    if g:
        for l in L[g[-1] + 2:]:
            p = l.split()
            if len(p) != 4:
                break
            atoms.append((p[0], np.array([float(x) for x in p[1:]])))

    def cargas(titulo):
        k = [i for i, l in enumerate(L) if l.strip() == titulo]
        if not k:
            return []
        out = []
        for l in L[k[-1] + 2:]:
            m = re.match(r"^\s*(\d+)\s+(\w+)\s*:\s*(-?[\d.]+)", l)
            if not m:
                break
            out.append((f"{m[2]}{int(m[1]) + 1}", float(m[3])))
        return out
    func = next((re.sub(r".*Exchange Functional\s+\w+\s*", "", l).strip() for l in L if "Exchange Functional" in l), "")
    return dict(eig=eig, occ=occ, homo=homo, E=E[-1] * HA2EV if E else None, atoms=atoms,
                mulliken=cargas("MULLIKEN ATOMIC CHARGES"), loewdin=cargas("LOEWDIN ATOMIC CHARGES"), func=func)


def load_orca(fn):
    """Registra um calculo ORCA (molecula): niveis de orbitais como 'bandas' num unico ponto (diagrama de niveis),
    DOS por gaussianas, gap HOMO-LUMO, geometria numa caixa e cargas de Mulliken/Loewdin."""
    R = read_orca(fn)
    seed = os.path.splitext(os.path.abspath(fn))[0]
    ns, _, nb = R["eig"].shape
    eig = np.concatenate([R["eig"], R["eig"]], axis=1)                       # dois pontos iguais: linhas horizontais
    if ns == 2:
        nelec = [float(R["occ"][s].sum()) for s in range(2)]
    else:
        nelec = [float(R["occ"][0].sum())]
    xyz = np.array([p for _, p in R["atoms"]]) if R["atoms"] else np.zeros((1, 3))
    Lbox = float(np.ptp(xyz, axis=0).max() + 12.0)
    lat = np.eye(3) * Lbox
    f = (xyz - xyz.mean(axis=0)) / Lbox + 0.5
    sp = [n for n, _ in R["atoms"]]
    species = list(dict.fromkeys(sp))
    B = dict(hdr=dict(nk=2, ns=ns, nelec=nelec, neig=[nb] * ns, efermi=[R["homo"]] * ns, lattice=lat / BOHR2ANG),
             header_lines=[], kidx=np.array([1, 2]), kfrac=np.zeros((2, 3)), kw=np.array([0.5, 0.5]), eig=eig, code="ORCA",
             pre=(np.array([0.0, 1.0]), np.array([0.0, 1.0]), ["", ""]))
    C = dict(lat=lat, sp=sp, f=f, forces=None, pressure=None, E=dict(final=R["E"], free=None, zeroK=None), info=dict(functional=R["func"], cutoff=""))
    X = dict(mull=[], bonds=[], species=species, zion={}, info=dict(functional=R["func"], cutoff="", energy=str(R["E"])),
             orca=dict(mulliken=R["mulliken"], loewdin=R["loewdin"]))
    _VIRT[seed + ".bands"] = B
    _VIRT[seed + ".cell"] = dict(species=species, struct=dict(lat=lat, sp=sp, f=f, masses={}, src="ORCA"))
    _VIRT[seed + ".castep"] = dict(extra=X, struct=C, orbitals=({}, {}), zion={})
    return seed



def _bader_refinar(rho, lab, tgt, A, iters=4):
    """Refinamento das bordas das bacias (near-grid; Tang, Sanville e Henkelman, 2009).
    Os pontos de fronteira refazem a subida pelo gradiente verdadeiro, com vetor de correção que
    acumula a diferença entre o passo ideal e o passo na grade. Vetorizado: as trajetórias andam juntas."""
    n = np.array(rho.shape); N = rho.size
    gi = [(np.roll(rho, -1, axis=a) - np.roll(rho, 1, axis=a)).ravel() / 2.0 for a in range(3)]   # dρ/d(índice)
    Ainv = np.linalg.inv(A)
    M = Ainv @ Ainv.T                                       # direção de subida em índices: d = M · ∇_idx ρ
    flat = rho.ravel(); lab = lab.ravel().copy()

    def bordas(lb):
        L3 = lb.reshape(rho.shape); e = np.zeros(rho.shape, bool)
        for a in range(3):
            for sgn in (1, -1):
                e |= L3 != np.roll(L3, sgn, axis=a)
        return np.flatnonzero(e)

    def vizinhos(ix):
        p = np.array(np.unravel_index(ix, rho.shape))
        return p
    ed = bordas(lab)
    for _ in range(iters):
        if len(ed) == 0:
            break
        is_edge = np.zeros(N, bool); is_edge[ed] = True
        pos = np.array(np.unravel_index(ed, rho.shape)).T.astype(np.int64)      # posição atual (índices)
        cor = np.zeros(pos.shape)                                              # vetor de correção
        ativo = np.ones(len(ed), bool); novo = lab[ed].copy()
        for _p in range(int(3 * n.max())):
            if not ativo.any():
                break
            ia = np.flatnonzero(ativo); p = pos[ia]
            fi = np.ravel_multi_index((p % n).T, rho.shape)
            g = np.stack([gi[0][fi], gi[1][fi], gi[2][fi]], axis=1)
            d = g @ M.T
            mx = np.abs(d).max(axis=1)
            ok = mx > 0
            d[ok] /= mx[ok, None]
            passo = np.rint(d + cor[ia]).astype(np.int64)
            cor[ia] += d - passo
            nova = p + passo
            fn = np.ravel_multi_index((nova % n).T, rho.shape)
            sobe = (flat[fn] > flat[fi]) & ok & (np.abs(passo).sum(axis=1) > 0)
            fon = tgt[fi]                                                       # sem subida: usa o passo on-grid
            fn = np.where(sobe, fn, fon)
            nova = np.where(sobe[:, None], nova, np.array(np.unravel_index(fon, rho.shape)).T)
            cor[ia[~sobe]] = 0.0
            parou = (~is_edge[fn]) | (fn == fi)
            novo[ia[parou]] = lab[fn[parou]]
            ativo[ia[parou]] = False
            pos[ia] = nova % n
        mud = novo != lab[ed]
        lab[ed] = novo
        if not mud.any():
            break
        # próximas bordas: só as vizinhas de pontos que mudaram
        ed = bordas(lab)
    return lab


def bader_ongrid(G, st=None, refinar=True):
    """Particao de Bader pelo metodo on-grid (Henkelman, Arnaldsson e Jonsson, 2006), vetorizado.
    Cada ponto aponta para o vizinho (26) de maior subida; seguindo os ponteiros chega-se a um maximo.
    Cada maximo (bacia) e atribuido ao atomo mais proximo. Devolve eletrons por atomo e o volume de cada bacia."""
    USADOS.add("henkelman2006")
    rho = np.asarray(G["rho"], float)
    n = np.array(rho.shape)
    N = rho.size
    L = np.asarray(G["lat"])
    dv = G["V"] / N
    best = np.zeros(rho.shape)
    tgt = np.arange(N).reshape(rho.shape)
    idx = np.arange(N).reshape(rho.shape)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for dk in (-1, 0, 1):
                if di == dj == dk == 0:
                    continue
                dist = np.linalg.norm(np.array([di, dj, dk]) / n @ L)
                nb = np.roll(rho, (-di, -dj, -dk), axis=(0, 1, 2))
                g = (nb - rho) / dist
                m = g > best
                best = np.where(m, g, best)
                tgt = np.where(m, np.roll(idx, (-di, -dj, -dk), axis=(0, 1, 2)), tgt)
    t = tgt.ravel()
    for _ in range(64):                                                       # salto de ponteiros: log2(caminho) passos
        t2 = t[t]
        if np.array_equal(t2, t):
            break
        t = t2
    maxs = np.unique(t)
    flat = rho.ravel()
    lab = np.searchsorted(maxs, t)
    if refinar:                                                               # bordas pelo gradiente verdadeiro
        USADOS.add("tang2009")
        lab = _bader_refinar(rho, lab, tgt.ravel(), L / n[:, None])
    q_max = np.bincount(lab, weights=flat, minlength=len(maxs)) * dv
    v_max = np.bincount(lab, minlength=len(maxs)) * dv
    if st is None or not st.get("sp"):
        return dict(maximos=len(maxs), q=q_max, v=v_max)
    ijk = np.array(np.unravel_index(maxs, rho.shape)).T / n
    lat_s = st["lat"]
    d = ijk[:, None, :] - st["f"][None, :, :]
    d -= np.round(d)
    dd = np.linalg.norm(d @ lat_s, axis=2)
    dono = dd.argmin(axis=1)
    nat = len(st["sp"])
    q = np.bincount(dono, weights=q_max, minlength=nat)
    v = np.bincount(dono, weights=v_max, minlength=nat)
    return dict(maximos=len(maxs), q=q, v=v, dist_max=float(dd.min(axis=1).max()))


def bader_report(seed, G, st, path, zion=None):
    """Tabela de Bader: eletrons, carga liquida (com Z de valencia, se conhecido), volume da bacia."""
    r = bader_ongrid(G, st)
    zion = zion or {}
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Particao de Bader (on-grid, Henkelman et al. 2006): {r['maximos']} maximos de densidade; "
                f"eletrons integrados = {r['q'].sum():.4f}\n")
        f.write("# Estimativa: para precisao maxima use o programa bader (metodo weight) com o CHGCAR exportado.\n")
        f.write("atomo\telemento\teletrons\tZ_valencia\tcarga_liquida\tvolume(A3)\n")
        for i, (s_, q, v) in enumerate(zip(st["sp"], r["q"], r["v"])):
            z = zion.get(s_)
            f.write(f"{st['label'][i]}\t{s_}\t{q:.4f}\t{z if z is not None else 'NaN'}\t{(z - q) if z is not None else float('nan'):.4f}\t{v:.3f}\n")
    medias = {}
    for s_, q in zip(st["sp"], r["q"]):
        medias.setdefault(s_, []).append(q)
    print(f" Bader: {r['maximos']} maximos; " + ", ".join(f"{s_} {np.mean(v):.3f} e" + (f" (carga {zion[s_] - np.mean(v):+.3f})" if s_ in zion else "")
                                                     for s_, v in medias.items()) + f" -> {path}")
    return r


HB2_ME = 7.619964                                                           # hbar^2/m_e em eV*A^2


def massas_efetivas(E_ev, dist, ticks, idx_band, k0, sinal):
    """m*/m_e no extremo da banda (k0) por ajuste parabolico ao longo do caminho.
    Extremo dentro de um segmento: parabola completa E = c2 x^2 + c1 x + c0 com 2 pontos de cada lado
    (o minimo verdadeiro pode cair entre dois k-pontos). Extremo num vertice (ex.: Gamma): uma massa
    por direcao, com E = a x^2 + c. sinal = +1 (eletron) ou -1 (buraco). Devolve lista de m*/m_e."""
    y = E_ev[:, idx_band]
    vert = set(int(np.argmin(np.abs(dist - t))) for t in ticks)
    if np.mean(np.diff(dist) < 1e-9) > 0.2 or len(dist) < 15:              # malha, nao caminho: sem massa
        return []

    def lado(sgn):
        pts, k = [k0], k0
        while len(pts) < 3:
            k += sgn
            if k < 0 or k >= len(dist) or abs(dist[k] - dist[pts[-1]]) < 1e-9:
                break
            pts.append(k)
            if k in vert:
                break
        return pts
    esq, dir_ = lado(-1), lado(+1)
    out = []
    if k0 not in vert and len(esq) == 3 and len(dir_) == 3:
        pts = esq[::-1] + dir_[1:]
        x = dist[pts] - dist[k0]
        c2 = np.polyfit(x, y[pts], 2)[0]
        if abs(c2) > 1e-9:
            out.append(sinal * HB2_ME / (2 * c2))
        return out
    for pts in (esq, dir_):
        if len(pts) == 3:
            x = dist[pts] - dist[k0]
            a = np.polyfit(x ** 2, y[pts], 1)[0]
            if abs(a) > 1e-9:
                out.append(sinal * HB2_ME / (2 * a))
    return out


def detect_code(arg):
    """'vasp', 'siesta' ou 'castep' para o argumento de linha de comando."""
    if not arg:
        return "castep"
    if os.path.isdir(arg) and os.path.isfile(os.path.join(arg, "data-file-schema.xml")):
        return "qe"
    if os.path.isfile(arg) and arg.lower().endswith(".xml") and "<qes:espresso" in open(arg, errors="replace").read(3000):
        return "qe"
    if os.path.isfile(arg) and arg.lower().endswith((".out", ".log")) and re.search(r"O\s+R\s+C\s+A|\* O   R   C   A \*|Program Version [\d.]+ -\s+RELEASE", open(arg, errors="replace").read(20000)):
        return "orca"
    if os.path.isdir(arg) and os.path.isfile(os.path.join(arg, "vasprun.xml")):
        return "vasp"
    if os.path.isfile(arg) and arg.lower().endswith(".xml") and "vasprun" in os.path.basename(arg).lower():
        return "vasp"
    s = arg[:-6] if arg.endswith(".bands") else arg
    if any(os.path.isfile(s + e) for e in (".EIG", ".PDOS", ".PDOS.xml", ".STRUCT_OUT", ".XV", ".RHO")):
        return "siesta"
    if os.path.isfile(s + ".bands") and is_siesta_bands(s + ".bands"):
        return "siesta"
    return "castep"


def prepare_inputs(a):
    """Converte o calculo principal e os auxiliares (--dos-seed, --ref, --h-less, μ=@seed)
    de VASP/SIESTA para o formato interno. Os de CASTEP ficam como estao."""
    def conv(x, main=False):
        code = detect_code(x)
        if code in ("qe", "orca"):
            s = load_qe(x) if code == "qe" else load_orca(x)
            if main:
                CODE["name"] = "QE" if code == "qe" else "ORCA"
            return s, None
        if code == "vasp":
            s = load_vasp(x)
            if main:
                CODE["name"] = "VASP"
            return s, None
        if code == "siesta":
            s, ds = load_siesta(x[:-6] if x.endswith(".bands") else x)
            if main:
                CODE["name"] = "SIESTA"
            return s, ds
        return x, None
    if a.seed:
        a.seed, ds = conv(a.seed, True)
        if ds and not a.dos_seed:
            a.dos_seed = ds
            print(f" SIESTA: bandas do {os.path.basename(a.seed)}.bands e DOS do {os.path.basename(a.seed)}.EIG (malha de k-pontos)")
        B = _virt(a.seed + ".bands")
        if B is not None and B.get("labels") and not a.labels:
            a.labels = B["labels"]
    if a.dos_seed and not a.dos_seed.endswith("_EIG"):
        a.dos_seed = conv(a.dos_seed)[0]
    for att in ("ref", "h_less"):
        v = getattr(a, att, None)
        if v:
            setattr(a, att, conv(v)[0])
    if getattr(a, "mu", None):
        parts = []
        for p in a.mu.split(","):
            if "=@" in p:
                k, v = p.split("=@", 1)
                p = f"{k}=@{conv(v.strip())[0]}"
            parts.append(p)
        a.mu = ",".join(parts)
    if CODE["name"] != "CASTEP":
        a.no_split = True
        if a.gerar_referencias:
            print(" AVISO: --gerar-referencias escreve entradas do CASTEP; para "
                  f"{CODE['name']} prepare as referencias no proprio programa.")
            a.gerar_referencias = False


# =========================================================================== #
#   PARIDADE COM O SITE: relatorio da diferenca de densidade e comparacao      #
# =========================================================================== #
def diff_report(base, a, G, st, arr, out, sgn):
    """Relatorio da diferenca de densidade (como a aba 'Diferenca de densidade' do site):
    acumulo, deplecao, carga redistribuida, raios de 50/90 %, dipolo, extremos, perfil
    radial com DeltaQ(r) e medias planares ao longo de a, b e c."""
    L = G["lat"]; n = np.array(G["n"]); N = int(np.prod(n)); dv = G["V"] / N
    res = analyze_defect(st, None, "") if st["sp"] else {}
    C = res.get("C") or {}
    cf = st["f"][C["atom"]] if "atom" in C else (np.array(C["f"]) if "f" in C else np.full(3, 0.5))
    clab = C.get("label", "centro da celula")
    idx = np.indices(n).reshape(3, -1).T
    fr = idx / n
    d = fr - cf; d -= np.round(d)
    cart = d @ L
    r = np.linalg.norm(cart, axis=1)
    v = arr[idx[:, 0], idx[:, 1], idx[:, 2]]
    pos, neg = v[v > 0].sum() * dv, v[v < 0].sum() * dv
    absT = np.abs(v).sum() * dv
    dip = (v[:, None] * cart).sum(axis=0) * dv
    widths = [G["V"] / np.linalg.norm(np.cross(L[(i + 1) % 3], L[(i + 2) % 3])) for i in range(3)]
    rmax = max(2.0, min(a.rmax_diff, 0.5 * min(widths)))
    dr = 0.05; nb = int(np.ceil(rmax / dr))
    b = np.floor(r / dr).astype(int); ok = b < nb
    sumB = np.bincount(b[ok], v[ok], nb); absB = np.bincount(b[ok], np.abs(v[ok]), nb); cnt = np.bincount(b[ok], None, nb)
    rr = (np.arange(nb) + 0.5) * dr
    avg = np.divide(sumB, cnt, out=np.full(nb, np.nan), where=cnt > 0)
    cum, cumA = np.cumsum(sumB) * dv, np.cumsum(absB) * dv
    rq = lambda q: rr[np.argmax(cumA >= q * absT)] if np.any(cumA >= q * absT) else np.nan
    r50, r90, fin = rq(0.5), rq(0.9), cumA[-1] / absT if absT else np.nan
    imx, imn = int(np.argmax(v)), int(np.argmin(v))

    def perto(i):
        p = fr[i]
        dd = st["f"] - p; dd -= np.round(dd)
        dist = np.linalg.norm(dd @ st["lat"], axis=1)
        j = int(np.argmin(dist)) if len(dist) else 0
        return (st["label"][j], dist[j]) if len(dist) else ("-", np.nan)
    amx, amn = perto(imx), perto(imn)
    planar = []
    for ax in range(3):
        s_ = arr.mean(axis=tuple(k for k in range(3) if k != ax))
        x = (np.arange(n[ax]) / n[ax] - cf[ax]); x -= np.round(x); x *= np.linalg.norm(L[ax])
        o = np.argsort(x); planar.append((x[o], s_[o]))
    sentido = "rho(puro) - rho(defeito)" if sgn < 0 else "rho(defeito) - rho(puro)"
    W = [f"DIFERENCA DE DENSIDADE: {base}  ({sentido}; centro {clab})", "=" * 72,
         f"Acumulo (integral de Delta > 0):    {pos:10.4f} e",
         f"Deplecao (integral de Delta < 0):   {neg:10.4f} e",
         f"Saldo:                              {pos + neg:10.4f} e",
         f"Carga redistribuida (1/2 int |D|):  {absT / 2:10.4f} e",
         f"Raio de 50 % / 90 % da redistribuicao: {r50 if np.isfinite(r50) else '>' + format(rmax, '.1f')} / "
         f"{r90 if np.isfinite(r90) else '>' + format(rmax, '.1f')} A  ({100 * fin:.0f} % a menos de {rmax:.1f} A)",
         f"Maximo acumulo:  {v[imx]:.4g} e/A^3 a {amx[1]:.2f} A de {amx[0]}",
         f"Maxima deplecao: {v[imn]:.4g} e/A^3 a {amn[1]:.2f} A de {amn[0]}",
         f"Dipolo da redistribuicao (origem no centro): ({dip[0]:.4f}, {dip[1]:.4f}, {dip[2]:.4f}) e*A; "
         f"|p| = {np.linalg.norm(dip):.4f} e*A = {np.linalg.norm(dip) * 4.80320:.3f} D" + ("  (saldo != 0: depende da origem)" if abs(pos + neg) > 0.05 else "")]
    open(out("diferenca_resumo.txt"), "w", encoding="utf-8").write("\n".join(W) + "\n")
    write_table(out("diferenca_perfil_radial.dat"), [f"Perfil radial de {sentido} em volta de {clab}"],
                ["r(A)", "media_esferica(e/A3)", "dQ_acumulado(e)", "|D|_acumulado(e)"], np.column_stack([rr, avg, cum, cumA]), fmt="%.6e")
    write_table(out("diferenca_medias_planares.dat"), [f"Medias planares de {sentido}; origem no centro ({clab})"],
                ["x_a(A)", "media_a", "x_b(A)", "media_b", "x_c(A)", "media_c"],
                np.column_stack([np.pad(c, (0, max(len(p[0]) for p in planar) - len(c)), constant_values=np.nan) for p in planar for c in p]), fmt="%.6e")
    fig, ax1 = plt.subplots(figsize=(a.width, a.height * 0.8))
    ax1.plot(rr, avg, color="#0072B2", lw=1.8, label=r"$\langle\Delta\rangle(r)$")
    ax1.axhline(0, color="k", lw=0.6); ax1.set_xlabel("r (Å)"); ax1.set_ylabel(r"$\langle\Delta\rangle$ (e/Å$^3$)")
    for x_ in sorted({round(s_["d"], 2) for s_ in res.get("shell", [])} if res.get("shell") else []):
        ax1.axvline(x_, color="gray", ls=":", lw=0.8)
    ax2 = ax1.twinx(); ax2.plot(rr, cum, color="#D55E00", ls="--", lw=1.6, label=r"$\Delta Q(r)$"); ax2.set_ylabel(r"$\Delta Q(r)$ (e)", color="#D55E00")
    ax1.set_title(f"{sentido}: perfil radial em volta de {clab}", fontsize=a.fontsize)
    fig.tight_layout(); fig.savefig(out(f"diferenca_perfil_radial.{a.format}"), dpi=a.dpi); plt.close(fig)
    fig, ax = plt.subplots(figsize=(a.width, a.height * 0.8))
    for (x_, y_), lab, c in zip(planar, "abc", ("#0072B2", "#D55E00", "#009E73")):
        ax.plot(x_, y_, color=c, lw=1.6, label=f"ao longo de {lab}")
    ax.axhline(0, color="k", lw=0.6); ax.axvline(0, color="gray", ls="--", lw=0.8)
    ax.set_xlabel("distancia ao centro ao longo do eixo (Å)"); ax.set_ylabel(r"$\langle\Delta\rangle$ planar (e/Å$^3$)"); ax.legend()
    fig.tight_layout(); fig.savefig(out(f"diferenca_medias_planares.{a.format}"), dpi=a.dpi); plt.close(fig)
    print(f" -> {out('diferenca_resumo.txt')}  (saldo {pos + neg:.3f} e, redistribuida {absT / 2:.3f} e, |p| {np.linalg.norm(dip):.3f} e*A)")


def convert_input(x):
    """Seed (virtual, se for VASP/SIESTA/QE/ORCA), seed da DOS e programa de um calculo."""
    code = detect_code(x)
    if code == "qe":
        return load_qe(x), None, "QE"
    if code == "orca":
        return load_orca(x), None, "ORCA"
    if code == "vasp":
        return load_vasp(x), None, "VASP"
    if code == "siesta":
        s, ds = load_siesta(x[:-6] if x.endswith(".bands") else x)
        return s, ds, "SIESTA"
    return (x[:-6] if x.endswith(".bands") else x), None, "CASTEP"


def compare_report(items, a, outdir):
    """Comparacao entre calculos de qualquer programa (como a aba 'Comparacao' do site)."""
    os.makedirs(outdir, exist_ok=True)
    out = lambda nm: os.path.join(outdir, nm)
    rows, curves, bandsets = [], [], []
    for x in items:
        seed, dseed, code = convert_input(x)
        name = os.path.basename(os.path.normpath(x)) if code == "VASP" else os.path.basename(seed)
        R = dict(nome=name, programa=code)
        st = struct_of(seed)
        if st is not None and st["sp"]:
            cnt = st["count"]; mass = sum(st["masses"].get(s_, MASS.get(re.match(r"[A-Z][a-z]?", s_)[0], 0)) for s_ in st["sp"])
            lens = np.linalg.norm(st["lat"], axis=1)
            R.update(composicao=" ".join(f"{k}{v}" for k, v in cnt.items()), atomos=len(st["sp"]), a=lens[0], b=lens[1], c=lens[2], V=st["V"],
                     densidade=mass * 1.66053907e-24 / (st["V"] * 1e-24), H_massa=100 * cnt.get("H", 0) * MASS["H"] / mass if mass else np.nan)
            E = st["castep"]["E"] if st.get("castep") else {}
            e = E.get("final") if E.get("final") is not None else E.get("free")
            if e is not None:
                R.update(energia=e, energia_atomo=e / len(st["sp"]))
            F = st["castep"].get("forces") if st.get("castep") else None
            if F is not None and len(F):
                R["forca_max"] = float(np.max(np.linalg.norm(F, axis=1)))
        if _vexists(seed + ".bands"):
            B = read_bands(seed + ".bands"); h = B["hdr"]; ns = h["ns"]
            ef = [x_ * HA2EV for x_ in h["efermi"]]
            lat = h["lattice"] * BOHR2ANG
            if B.get("pre") is not None:
                dist, ticks, labels = B["pre"]
            else:
                dist, ticks, labels, _ = kpath(B["kfrac"], lat, B.get("labels"))
            ed = [band_edges(B["eig"][s_] * HA2EV, h["neig"][s_], h["nelec"][s_], ns, ef[s_], dist, ticks, labels, B["kfrac"]) for s_ in range(ns)]
            R.update(EF_up=ef[0], gap_up=ed[0]["gap"], tipo_gap=" / ".join(f"{'direto' if e_['direct'] else 'indireto'} {e_['vkl']}->{e_['ckl']}" for e_ in ed))
            if ns == 2:
                R.update(EF_down=ef[1], gap_down=ed[1]["gap"])
                R["gap_total"] = min(e_["cbm"] - ef[s_] for s_, e_ in enumerate(ed)) - max(e_["vbm"] - ef[s_] for s_, e_ in enumerate(ed))
            else:
                R["gap_total"] = ed[0]["gap"]
            meshonly = B.get("pre") is not None and labels and labels[0] == "k1"
            if not meshonly:
                bandsets.append((name, dist, ticks, labels, [B["eig"][s_] * HA2EV - ef[s_] for s_ in range(ns)], R["gap_total"]))
            D = read_bands(dseed + ".bands") if dseed else B
            P = read_pdos_bin((dseed or seed) + ".pdos_bin") if _vexists((dseed or seed) + ".pdos_bin") else None
            egrid = np.arange(a.ymin - 2, a.ymax + 2 + a.de, a.de)
            efd = [x_ * HA2EV for x_ in D["hdr"]["efermi"]]
            dos = []
            for s_ in range(ns):
                if P is not None and P.get("curves") is not None:
                    Cv = P["curves"]; sc = min(s_, Cv["ns"] - 1)
                    dos.append(np.interp(egrid + efd[s_], Cv["E"], Cv["data"][:, sc, :].sum(axis=0), left=0, right=0))
                else:
                    dos.append(gaussian_dos(D["eig"][s_] * HA2EV - efd[s_], D["kw"], None, egrid, a.sigma)[0])
            i0 = int(np.argmin(np.abs(egrid)))
            nef = [d_[i0] for d_ in dos]
            R["N_EF"] = sum(nef)
            if ns == 2:
                R["polarizacao"] = 100 * (nef[0] - nef[1]) / sum(nef) if sum(nef) > 0.05 else np.nan
            curves.append((name, egrid, dos))
        info = _virt(seed + ".castep", "extra") or read_castep_extra(seed + ".castep")
        if info.get("info", {}).get("functional"):
            R["funcional"] = info["info"]["functional"]
        rows.append(R)
    cols = [("nome", "calculo", "t"), ("programa", "programa", "t"), ("funcional", "funcional", "t"), ("composicao", "composicao", "t"),
            ("atomos", "atomos", 0), ("energia", "energia total (eV)", 5), ("energia_atomo", "energia por atomo (eV)", 5),
            ("EF_up", "E_F spin up (eV)", 4), ("EF_down", "E_F spin down (eV)", 4), ("gap_up", "gap up (eV)", 4), ("gap_down", "gap down (eV)", 4),
            ("gap_total", "gap total (eV)", 4), ("tipo_gap", "tipo de gap", "t"), ("N_EF", "N(E_F) (estados/eV)", 3), ("polarizacao", "polarizacao em E_F (%)", 2),
            ("a", "a (A)", 4), ("b", "b (A)", 4), ("c", "c (A)", 4), ("V", "V (A^3)", 3), ("densidade", "densidade (g/cm3)", 4),
            ("H_massa", "H (% em massa)", 3), ("forca_max", "forca maxima (eV/A)", 4)]
    fmt = lambda v, d: "NaN" if v is None or (isinstance(v, float) and not np.isfinite(v)) else (str(v) if d == "t" else f"{v:.{d}f}")
    with open(out("comparacao.dat"), "w", encoding="utf-8") as f:
        f.write("# Comparacao de calculos (BrUMaRe) - valores ausentes: NaN\ngrandeza\t" + "\t".join(r["nome"] for r in rows) + "\n")
        for k, lab, d in cols[1:]:
            f.write(lab + "\t" + "\t".join(fmt(r.get(k), d) for r in rows) + "\n")
    wid = max(len(c[1]) for c in cols) + 2
    cw = [max(12, max(len(fmt(r.get(k), d)) for k, _, d in cols) + 3) for r in rows]
    with open(out("comparacao.txt"), "w", encoding="utf-8") as f:
        f.write(f"COMPARACAO DE CALCULOS - {NOME} {VERSAO}\n" + "=" * 72 + "\n")
        for k, lab, d in cols:
            f.write(lab.ljust(wid) + "".join(fmt(r.get(k), d).rjust(w) for r, w in zip(rows, cw)) + "\n")
    cor = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
    if curves:
        fig, ax = plt.subplots(figsize=(a.width, a.height * 0.75))
        for i, (nm, eg, ds) in enumerate(curves):
            for s_, d_ in enumerate(ds):
                ax.plot(eg, -d_ if s_ == 1 else d_, color=cor[i % len(cor)], lw=1.3, label=nm if s_ == 0 else None)
        ax.axvline(0, color="gray", ls="--", lw=0.8); ax.axhline(0, color="k", lw=0.6)
        ax.set_xlim(a.ymin, a.ymax); ax.set_xlabel(r"E $-$ E$_F$ de cada calculo (eV)"); ax.set_ylabel("DOS (estados/eV)  [down < 0]"); ax.legend()
        fig.tight_layout(); fig.savefig(out(f"comparacao_dos.{a.format}"), dpi=a.dpi); plt.close(fig)
    if bandsets:
        nb_ = len(bandsets)
        fig, axs = plt.subplots(1, nb_, figsize=(max(a.width, 3.2 * nb_), a.height), sharey=True, squeeze=False)
        for ax, (nm, dist, ticks, labels, Es, gp) in zip(axs[0], bandsets):
            for s_, E_ in enumerate(Es):
                plot_bands(ax, dist, E_, "#1f4e9c" if s_ == 0 else "#c0392b", "-" if s_ == 0 else "--", 1.0)
            deco_bands(ax, dist, ticks, labels, a.ymin, a.ymax, r"E $-$ E$_F$ (eV)" if ax is axs[0][0] else False)
            ax.set_title(f"{nm}  gap {gp:.3f} eV", fontsize=a.fontsize - 1)
        fig.tight_layout(); fig.savefig(out(f"comparacao_bandas.{a.format}"), dpi=a.dpi); plt.close(fig)
    gps = [(r["nome"], r.get("gap_total")) for r in rows if r.get("gap_total") is not None]
    if gps:
        fig, ax = plt.subplots(figsize=(a.width * 0.8, a.height * 0.6))
        ax.bar([g[0] for g in gps], [g[1] for g in gps], color=[cor[i % len(cor)] for i in range(len(gps))])
        for i, g in enumerate(gps):
            ax.text(i, g[1], f"{g[1]:.3f}", ha="center", va="bottom", fontsize=a.fontsize - 2)
        ax.set_ylabel("gap total (eV)"); fig.tight_layout(); fig.savefig(out(f"comparacao_gap.{a.format}"), dpi=a.dpi); plt.close(fig)
    USADOS.add("setyawan2010") if bandsets else None
    write_citation(outdir, "comparacao", {r["programa"] for r in rows})
    print(f" -> {out('comparacao.dat')}, comparacao.txt e figuras ({len(rows)} calculos: " + ", ".join(f"{r['nome']} [{r['programa']}]" for r in rows) + ")")



def main(argv=None):
    for _s in (sys.stdout, sys.stderr):           # console do Windows: nunca quebrar por acento
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass
    p = argparse.ArgumentParser(
        prog="brumare", description=f"{NOME} {VERSAO}: {DESCRICAO}. Autor: {AUTOR}.",
        epilog="Como citar: brumare --sobre  ·  tutorial: https://brunohdmacedo.tech/brumare/tutorial.html",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("seed", nargs="?", help="seedname (ex: mgh2_Fe) ou o arquivo .bands. "
                   "Se omitido, procura um .bands na pasta atual")
    p.add_argument("--sobre", action="store_true", help="mostra autor, links e como citar o BrUMaRe, e sai")
    p.add_argument("--idioma", "--lang", choices=IDIOMAS, help="idioma do --sobre, do rodapé e do como_citar.txt: pt, en, es, fr, it ou la (latim)")
    p.add_argument("--comparar", metavar="A,B,...", help="compara calculos de qualquer programa (seeds do CASTEP/SIESTA ou pastas do VASP), como a aba Comparacao do site")
    p.add_argument("--versao", "--version", action="version", version=f"{NOME} {VERSAO}")
    p.add_argument("--quiet", action="store_true", help="nao mostra o cabecalho com nome e autor")
    p.add_argument("-c", "--cell", help="arquivo .cell (padrao: <seed>.cell)")
    p.add_argument("--pdos", help="arquivo .pdos_bin (padrao: <seed>.pdos_bin)")
    p.add_argument("-e", "--elements", help="elementos para PDOS, ex: Mg,H,Fe "
                   "(padrao: todos)")
    p.add_argument("-o", "--orbitals", default="s,p,d,f")
    p.add_argument("--dos-seed", help="seedname de um calculo de DOS separado "
                   "(malha MP densa). Padrao: usa o mesmo do .bands")
    p.add_argument("-g", "--sigma", type=float, default=0.05,
                   help="alargamento gaussiano da DOS (eV)")
    p.add_argument("--de", type=float, default=0.005, help="passo da DOS (eV)")
    p.add_argument("--ymin", type=float, default=-6.0)
    p.add_argument("--ymax", type=float, default=5.0)
    p.add_argument("--zona-brillouin", nargs="?", const="", default=None, metavar="REDE",
                   help="1a zona de Brillouin, pontos de alta simetria e caminho k (CASTEP, VASP, QE, SIESTA). Sem valor usa a celula do calculo; "
                   "com valor: 'fcc 5.431', 'bcc a', 'sc a', 'hex a c', 'tet a c', 'orc a b c' ou 'a b c alfa beta gama'")
    p.add_argument("--estrutura", metavar="ARQ", help="estrutura para simetria e zona de Brillouin: CIF, POSCAR/CONTCAR, .cell, XSF, entrada do QE ou XYZ estendido")
    p.add_argument("--symprec", type=float, default=0.01, help="tolerancia de simetria em A (moyo/spglib), padrao 0.01")
    p.add_argument("--zb-densidade", type=float, default=30.0, help="pontos por A^-1 no caminho k (zona de Brillouin)")
    p.add_argument("--zb-dk", type=float, default=0.2, help="espacamento da malha Monkhorst-Pack em A^-1 (com 2pi)")
    p.add_argument("--zb-exata", action="store_true", help="nao simetrizar a rede (zona exata da celula distorcida)")
    p.add_argument("--gap-corr", choices=["nenhuma", "tesoura", "ref", "mvi"], default="nenhuma",
                   help="correcao do gap: 'tesoura' (Delta de --tesoura), 'ref' (ate o gap de --gap-ref) ou 'mvi' (modelo PBE->G0W0 de Morales-Garcia, Valero e Illas, 2017)")
    p.add_argument("--tesoura", type=float, help="Delta da tesoura em eV (com --gap-corr tesoura)")
    p.add_argument("--gap-ref", type=float, help="gap de referencia em eV: experimental, HSE06 ou GW (com --gap-corr ref)")
    p.add_argument("--fermi-ref", choices=["original", "spin", "up", "down", "mean", "none"],
                   default="original",
                   help="referencia de energia: 'original' (padrao) = energias do programa, sem deslocar, com linha "
                   "traco-ponto em E_F; 'spin' = E - E_F de cada canal; 'up'/'down'/'mean' = E - E_F comum; "
                   "'none' = energias absolutas sem linha de E_F rotulada")
    p.add_argument("--labels", help="rotulos dos pontos k, ex: G,X,M,G,Z,R,A,Z")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--width", type=float, default=8.0)
    p.add_argument("--height", type=float, default=6.0)
    p.add_argument("--fontsize", type=int, default=13)
    p.add_argument("--format", default="png",
                   help="formato(s) das figuras, separados por virgula: png, jpg, jxl, webp, svg, pdf, eps, tif "
                   "(ex.: png,jxl,svg). Cada figura sai em todos os formatos pedidos")
    p.add_argument("--qualidade", type=int, default=100,
                   help="qualidade de JPG, WEBP e JXL (10-100). Em JXL e WEBP, 100 = sem perdas (padrao)")
    p.add_argument("--outdir", default=None, help="pasta de saida "
                   "(padrao: <seed>_plots)")
    p.add_argument("--castep", help="arquivo .castep (ordem dos orbitais e camadas; "
                   "padrao: <seed>.castep)")
    p.add_argument("--sites", help="PDOS de atomos individuais, ex: Fe1,H23,Mg5")
    p.add_argument("--no-fatbands", action="store_true",
                   help="nao gerar bandas projetadas (fat bands)")
    p.add_argument("--fat-scale", type=float, default=6.0,
                   help="espessura maxima das fat bands (pt)")
    p.add_argument("--down-negative", action="store_true",
                   help="grava a DOS de spin down com sinal negativo nos .dat")
    g = p.add_argument_group("defeito e termodinamica")
    g.add_argument("--ref", help="seed da estrutura PURA (sem defeito) para mapear atomos e deslocamentos")
    g.add_argument("--center", help="centro da analise: rotulo (Fe1, H25) ou 'x y z' fracionario. Padrao: automatico")
    g.add_argument("--shell-factor", type=float, default=1.25, help="1a camada = d_min x fator")
    g.add_argument("--rcut", type=float, default=0.0, help="raio fixo da 1a camada (A); 0 = automatico")
    g.add_argument("--rfar", type=float, default=0.0, help="distancia minima ao centro para o 'bulk' (A); 0 = automatico")
    g.add_argument("--mu", help="potenciais quimicos em eV/atomo, ex: 'Mg=-975.3,Fe=@fe_bcc,H=@h2' (@seed le o .castep)")
    g.add_argument("--energy", choices=["auto", "final", "corrected", "zeroK", "free"], default="auto",
                   help="energia total usada (auto: estimativa a 0 K nos metais, Final energy nos demais)")
    g.add_argument("--gerar-referencias", action="store_true",
                   help="escreve .cell/.param da estrutura pura, sem H (perto e longe) e das referencias elementares")
    d = p.add_argument_group("densidade de carga (.den_fmt ou .cube)")
    d.add_argument("--density", help="arquivo de densidade (padrao: <seed>.den_fmt ou <seed>.cube, se existir)")
    d.add_argument("--field", choices=["rho", "up", "down", "spin", "absm", "zeta", "diff"], default="rho",
                   help="rho total, up/down (rho de cada spin), spin (up-down), absm (|up-down|), zeta ((up-down)/rho) ou diff")
    d.add_argument("--voronoi", choices=["plain", "radical", "off"], default="plain", help="cargas e momentos por atomo (particao de Voronoi)")
    d.add_argument("--subtract", help="para --field diff: densidades a subtrair, ex: 'a.den_fmt,b.den_fmt'")
    d.add_argument("--plane", help="corte 2D: tres atomos 'Fe1,H30,H68' ou 'hkl:0 0 1@Fe1' (padrao: centro e 2 vizinhos)")
    d.add_argument("--plane-size", type=float, default=8.0, help="lado do corte 2D (A)")
    d.add_argument("--planes", help="galeria de planos pelo defeito, ex: '1 1 0; -1 1 0; 0 0 1' ou 'todos'")
    d.add_argument("--hkl-base", choices=["base", "super"], default="base",
                   help="indices (h k l) da celula base detectada (padrao, ex.: rutilo) ou da supercelula")
    d.add_argument("--line", help="perfil entre dois atomos, ex: 'Fe1,H30' (padrao: centro e vizinho mais proximo)")
    d.add_argument("--xsf", action="store_true", help="exporta a densidade para .xsf (VESTA/XCrySDen)")
    d.add_argument("--chgcar", action="store_true", help="exporta a densidade como CHGCAR (VASP 5, com elementos) para o VESTA, como o den2vasp")
    d.add_argument("--vesta", action="store_true",
                   help="exporta para o VESTA (CHGCAR VASP 5) rho, rho_up, rho_down, spin e, com --subtract, as diferencas de cada um")
    d.add_argument("--bader", action="store_true", help="particao de Bader (on-grid) da densidade: eletrons, carga liquida e volume por atomo")
    d.add_argument("--rmax-diff", type=float, default=6.0, help="raio maximo (A) do perfil radial da diferenca de densidade")
    d.add_argument("--diff-sign", choices=["defeito-puro", "puro-defeito"], default="defeito-puro",
                   help="sentido das diferencas (--field diff e --vesta)")
    d.add_argument("--chgcar-spin", action="store_true", help="com --chgcar e --field rho: inclui a densidade de spin como 2o bloco")
    g.add_argument("--dS", type=float, default=130.7, help="entropia de dessorcao (J/mol K) para T_d = dH/dS")
    g.add_argument("--h-less", help="seed da estrutura com H a menos (energia de remocao de H)")
    g.add_argument("--no-defect", action="store_true", help="nao fazer a analise de defeito")
    p.add_argument("--no-split", action="store_true",
                   help="nao escrever <seed>_up.bands / <seed>_down.bands")
    _av = list(sys.argv[1:] if argv is None else argv)
    for _i, _x in enumerate(_av):
        if _x in ("--idioma", "--lang") and _i + 1 < len(_av) and _av[_i + 1] in IDIOMAS:
            LANG["v"] = _av[_i + 1]
        elif _x.startswith(("--idioma=", "--lang=")) and _x.split("=", 1)[1] in IDIOMAS:
            LANG["v"] = _x.split("=", 1)[1]
    _ajuda_traduzida(p)
    a = p.parse_args(argv)
    _fm = [x.strip().lower().replace("jpeg", "jpg") for x in a.format.split(",") if x.strip()] or ["png"]
    FMTS.update(lista=list(dict.fromkeys(_fm)), q=max(10, min(100, a.qualidade)))
    a.format = FMTS["lista"][0]
    if a.estrutura:                                        # estrutura de arquivo: simetria e zona de Brillouin
        od = a.outdir or (os.path.splitext(os.path.basename(a.estrutura))[0] + "_estrutura"); os.makedirs(od, exist_ok=True)
        st0 = ler_estrutura(a.estrutura); b0 = os.path.splitext(os.path.basename(a.estrutura))[0]
        bz_relatorio(st0["lat"], b0, a, lambda n: os.path.join(od, f"{b0}_{n}"), st=st0)
        return
    if a.zona_brillouin:                                   # zona de Brillouin direto de uma rede (sem cálculo)
        od = a.outdir or "zona_brillouin"; os.makedirs(od, exist_ok=True)
        bz_relatorio(bz_rede_texto(a.zona_brillouin), a.zona_brillouin, a, lambda n: os.path.join(od, "rede_" + n))
        return
    if a.idioma:
        LANG["v"] = a.idioma
    if a.sobre:
        print(sobre_texto())
        return
    if not a.quiet:
        banner()
    if a.comparar:
        style(a.fontsize)
        compare_report([x.strip() for x in a.comparar.split(",") if x.strip()], a, a.outdir or "comparacao_plots")
        return

    interactive = bool(sys.stdin) and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
    if not a.seed and os.path.isfile("vasprun.xml"):
        a.seed = "."
        print(" VASP: vasprun.xml encontrado na pasta atual")
    if not a.seed:
        sies = sorted({f.rsplit(".", 1)[0] for f in os.listdir(".") if f.endswith((".EIG", ".STRUCT_OUT", ".PDOS"))})
        if sies and not any(f.endswith(".bands") and not is_siesta_bands(f) for f in os.listdir(".")):
            a.seed = sies[0]
            print(f" SIESTA: {a.seed} encontrado na pasta atual")
    if a.seed:
        prepare_inputs(a)
    if not a.seed:
        cands = sorted(f[:-6] for f in os.listdir(".") if f.endswith(".bands")
                       and not re.search(r"_(up|down)$", f[:-6]))
        if not cands:
            sys.exit("ERRO: nenhum .bands na pasta atual. Informe o seedname: "
                     "python3 brumare.py <seed>")
        if len(cands) == 1 or not interactive:
            a.seed = cands[0]
        else:
            for i, c in enumerate(cands, 1):
                print(f"  {i}) {c}")
            r = input("Qual calculo? (numero ou nome) [1]: ").strip() or "1"
            a.seed = cands[int(r) - 1] if r.isdigit() else r
        print(f" Seed detectado: {a.seed}")
        prepare_inputs(a)
        if a.elements is None and interactive:
            a.elements = input("Elementos para PDOS separados por virgula "
                               "(Enter = todos): ").strip() or None
    seed = a.seed[:-6] if a.seed.endswith(".bands") else a.seed
    base = os.path.basename(seed)
    cellf = a.cell or seed + ".cell"
    outdir = a.outdir or base + "_plots"
    os.makedirs(outdir, exist_ok=True)
    out = lambda name: os.path.join(outdir, f"{base}_{name}")
    style(a.fontsize)

    if not _vexists(seed + ".bands"):
        if _vexists(seed + ".cell") or _vexists(seed + ".castep"):
            print(f" Sem {seed}.bands: fazendo so a analise de estrutura, defeito e termodinamica.")
            style(a.fontsize)
            defect_report(seed, a, outdir)
            if a.gerar_referencias:
                generate_references(seed, a, outdir)
            density_report(seed, a, outdir)
            write_citation(outdir, os.path.basename(seed), {CODE["name"]})
            return
        sys.exit(f"ERRO: arquivo nao encontrado: {seed}.bands")
    castep0 = a.castep or seed + ".castep"
    X = read_castep_extra(castep0)

    # ---------------------------- bandas ---------------------------------- #
    B = read_bands(seed + ".bands")
    h = B["hdr"]
    ns = h["ns"]
    GAPCORR.clear()
    GAPCORR.update(correcao_gap(B, a))
    if _vexists(cellf):
        species = read_cell_species(cellf)
    elif X["species"]:
        species = X["species"]
        print(f" AVISO: {cellf} nao encontrado; especies lidas do .castep.")
    elif CODE["name"] != "CASTEP":
        species = []
        print(" AVISO: sem estrutura (STRUCT_OUT/XV ou vasprun): so bandas e DOS total, sem PDOS por elemento.")
    else:
        sys.exit(f"ERRO: preciso do {cellf} (ou do .castep) para saber as especies.")
    lat = h["lattice"] * BOHR2ANG
    if B.get("pre") is not None:                        # SIESTA: caminho e rotulos ja calculados pelo programa
        dist, ticks, labels = B["pre"]; typ = "malha (sem caminho)" if labels and labels[0] == "k1" else f"caminho do {CODE['name']}"
        if a.labels:
            ul = [x.strip() for x in a.labels.split(",")]
            labels = ul if len(ul) == len(labels) else labels
    else:
        dist, ticks, labels, typ = kpath(B["kfrac"], lat, a.labels)
    ef_ha = h["efermi"]
    ef_ev = [x * HA2EV for x in ef_ha]

    if a.fermi_ref == "original":                       # dados relativos a um E_F comum; o eixo mostra E original
        r = float(np.mean(ef_ev))
        ref = [r] * ns
        EIXO.update(orig=True, off=r)
    elif a.fermi_ref == "spin":
        ref = ef_ev
    elif a.fermi_ref == "none":
        ref = [0.0] * ns
    else:
        r = {"up": ef_ev[0], "down": ef_ev[-1], "mean": float(np.mean(ef_ev))}[a.fermi_ref]
        ref = [r] * ns
    shifted = a.fermi_ref != "none"
    E = [B["eig"][s] * HA2EV - ref[s] for s in range(ns)]
    ylab = "E (eV)" if (EIXO["orig"] or not shifted) else r"E $-$ E$_F$ (eV)"

    print("=" * 70)
    print(f" Sistema: {base}   | especies: {', '.join(species)}")
    print(f" k-pontos: {h['nk']}  | spins: {ns}  | bandas: {h['neig']}")
    print(f" Rede: {typ}  | caminho: {' - '.join(labels)}")
    for s in range(ns):
        print(f" E_F spin {SPIN_TAG[s] if ns == 2 else ''}: {ef_ha[s]:.6f} Ha = "
              f"{ef_ev[s]:.4f} eV  (valor do {CODE['name']}, nao recalculado)")
    print(f" Referencia de energia usada: {a.fermi_ref}")
    print("=" * 70)

    if ns == 2 and not a.no_split:
        for fn in write_split_bands(B, base, outdir):
            print(f" -> {fn}")

    tag = (lambda s: "_" + SPIN_TAG[s]) if ns == 2 else (lambda s: "")
    for s in range(ns):
        fn = out(f"bands{tag(s)}.dat")
        write_bands_dat(fn, dist, E[s], ticks, labels, ef_ev[s], shifted, ref[s])
        print(f" -> {fn}")
    with open(out("kticks.dat"), "w", encoding="utf-8") as f:
        f.write("# Pontos de alta simetria (linhas verticais e rotulos do eixo k)\nrotulo\tk(1/A)\n")
        for l, t in zip(labels, ticks):
            f.write(f"{l}\t{t:.6f}\n")

    cu, cd = "#1f4e9c", "#c0392b"
    # bandas: um painel por spin
    for s in range(ns):
        fig, ax = plt.subplots(figsize=(a.width * 0.75, a.height))
        plot_bands(ax, dist, E[s], cu if s == 0 else cd)
        deco_bands(ax, dist, ticks, labels, a.ymin, a.ymax, ylab)
        if ns == 2:
            ax.set_title(f"Spin {SPIN_TAG[s]}")
        fig.savefig(out(f"bands{tag(s)}.{a.format}"), dpi=a.dpi)
        plt.close(fig)
    if ns == 2:
        fig, axs = plt.subplots(1, 2, figsize=(a.width * 1.2, a.height), sharey=True)
        for s in range(2):
            plot_bands(axs[s], dist, E[s], cu if s == 0 else cd)
            deco_bands(axs[s], dist, ticks, labels, a.ymin, a.ymax,
                       ylab if s == 0 else False)
            axs[s].set_title(f"Spin {SPIN_TAG[s]}")
        fig.subplots_adjust(wspace=0.06)
        fig.savefig(out(f"bands_up_down_lado.{a.format}"), dpi=a.dpi)
        plt.close(fig)
        fig, ax = plt.subplots(figsize=(a.width * 0.75, a.height))
        plot_bands(ax, dist, E[0], cu, "-", 1.4, "spin up")
        plot_bands(ax, dist, E[1], cd, "--", 1.1, "spin down")
        deco_bands(ax, dist, ticks, labels, a.ymin, a.ymax, ylab)
        ax.legend(loc="upper right", fontsize=a.fontsize - 2)
        fig.savefig(out(f"bands_up_down_sobrepostas.{a.format}"), dpi=a.dpi)
        plt.close(fig)

    # ------------------------------ DOS ------------------------------------ #
    dseed = a.dos_seed or seed
    if a.dos_seed:
        D = read_bands(dseed + ".bands")
        if D["hdr"]["ns"] != ns:
            sys.exit("ERRO: numero de spins diferente entre bandas e DOS.")
        if GAPCORR.get("delta"):
            aplicar_tesoura(D, GAPCORR["delta"])                     # mesma tesoura na DOS
        # Fermi do calculo de DOS, tambem sem recalcular
        dref = ([x * HA2EV for x in D["hdr"]["efermi"]] if a.fermi_ref == "spin"
                else ref)
    else:
        D, dref = B, ref
    ED = [D["eig"][s] * HA2EV - dref[s] for s in range(ns)]
    ef_dos = [x * HA2EV for x in D["hdr"]["efermi"]]
    efpos = [ef_dos[s] - dref[s] for s in range(ns)]          # posicao de E_F no eixo da DOS
    if D["hdr"]["nk"] < 100 and CODE["name"] != "ORCA":
        print(f" AVISO: a DOS usa apenas {D['hdr']['nk']} k-pontos. Para DOS "
              "quantitativa use uma malha densa (CASTEP: SPECTRAL_TASK DOS;\n        VASP: calculo com malha MP; SIESTA: o .EIG/.PDOS do SCF) e "
              "passe --dos-seed.")

    pdosf = a.pdos or dseed + ".pdos_bin"
    castepf = a.castep or (dseed + ".castep" if _vexists(dseed + ".castep")
                           else seed + ".castep")
    els = [x.strip() for x in a.elements.split(",")] if a.elements else species
    for el in els:
        if el not in species:
            print(f" AVISO: elemento {el} nao esta no .cell; ignorado.")
    els = [el for el in els if el in species]
    orbs = [x.strip() for x in a.orbitals.split(",")]
    sites = [x for x in (a.sites or "").split(",") if x.strip()]
    P, O, groups = None, None, []
    if _vexists(pdosf):
        P = read_pdos_bin(pdosf)
        if P.get("curves") is None and not align_k(D, P):
            print(f" AVISO: os k-pontos de {pdosf} nao batem com {dseed}.bands; PDOS ignorada.")
            P = None
    if P is not None:
        O, msg = build_orbitals(P, species, castepf)
        print(" " + msg)
        groups = make_groups(O, els, orbs, sites)
    elif not _vexists(pdosf):
        if CODE["name"] != "ORCA":
            print(" AVISO: sem projecoes por orbital: somente DOS total (CASTEP: .pdos_bin; VASP: LORBIT = 11; "
                  "SIESTA: bloco ProjectedDensityOfStates; QE: projwfc.x).")
    Mg_ = np.array([g["mask"] for g in groups], float).T if groups else None

    emin = min(np.nanmin(x) for x in ED) - 5 * a.sigma - 1
    emax = max(np.nanmax(x) for x in ED) + 5 * a.sigma + 1
    egrid = np.arange(emin, emax + a.de, a.de)
    dos_tot, dos_g = [], []
    CUR = P.get("curves") if P is not None else None
    if CUR is not None:
        print(f" SIESTA: PDOS calculada pelo proprio SIESTA ({len(CUR['orbs'])} orbitais); E_F do .PDOS = {CUR['ef']:.4f} eV")
    for s in range(ns):
        if CUR is not None:                             # PDOS ja calculada: interpola as curvas no eixo da DOS
            sc = min(s, CUR["ns"] - 1)
            Eabs = egrid + dref[s]
            tot = np.interp(Eabs, CUR["E"], CUR["data"][:, sc, :].sum(axis=0), left=0, right=0)
            gs = [np.interp(Eabs, CUR["E"], (CUR["data"][:, sc, :] * Mg_[:, i][:, None]).sum(axis=0), left=0, right=0)
                  for i in range(Mg_.shape[1])] if groups else []
            dos_tot.append(tot)
            dos_g.append(np.array(gs) if gs else np.zeros((0, len(egrid))))
            continue
        Wg = None
        if groups:
            nb = ED[s].shape[1]
            Wg = P["w"][s][:, :nb, :] @ Mg_          # (nk, nb, ngrupos)
        r = gaussian_dos(ED[s], D["kw"], Wg, egrid, a.sigma)
        dos_tot.append(r[0])
        dos_g.append(r[1:])

    gidx = {(g["cat"], g["name"]): i for i, g in enumerate(groups)}
    sel = lambda *cats: [i for i, g in enumerate(groups) if g["cat"] in cats]

    # ---------- .dat da DOS (um arquivo por nivel de detalhe) ---------- #
    def write_dos(fname, idxs, extra=""):
        fn = out(fname)
        sg = [1, -1 if a.down_negative else 1]
        cols = ["E(eV)"] + [f"TDOS{tag(s)}" for s in range(ns)]
        data = [egrid] + [sg[s] * dos_tot[s] for s in range(ns)]
        for i in idxs:
            for s in range(ns):
                cols.append(f"{groups[i]['name']}{tag(s)}")
                data.append(sg[s] * dos_g[s][i])
        com = [f"DOS/PDOS (estados/eV/celula/spin), gaussiana sigma = {a.sigma} eV",
               "E_F do CASTEP (sem alteracao): " + "; ".join(
                   f"{SPIN_TAG[s] if ns == 2 else ''} {ef_dos[s]:.6f} eV" for s in range(ns)),
               f"Energia: {'E - E_ref' if shifted else 'absoluta'} (eV), referencia = {a.fermi_ref}",
               "Spin down com sinal NEGATIVO" if a.down_negative else "Spin down com valores POSITIVOS"]
        com += [x for x in extra.strip().splitlines() if x] if extra else []
        write_table(fn, [c.lstrip("# ") for c in com], cols, np.column_stack(data))
        print(f" -> {fn}")

    write_dos("dos.dat", sel("el", "l"))
    if groups:
        write_dos("dos_camadas.dat", sel("shell"),
                  "# Separado por camada (n,l) do pseudopotencial, ex: Mg_2p e Mg_3p\n")
        if sel("lm", "eg"):
            write_dos("dos_orbitais_m.dat", sel("lm", "eg"),
                      "# Componentes m nos eixos CARTESIANOS da celula (px,py,pz; "
                      "dz2,dyz,dxz,dx2-y2,dxy).\n# t2g=dxy+dyz+dxz, eg=dz2+dx2-y2 "
                      "so tem sentido fisico se o octaedro estiver alinhado a x,y,z.\n")
        if sel("site", "site_l"):
            write_dos("dos_sitios.dat", sel("site", "site_l"))

    # ----------------------- resumo da analise ---------------------------- #
    if a.zona_brillouin == "":
        try:
            st_zb = read_cell_struct(cellf); st_zb = dict(lat=np.asarray(st_zb["lat"], float), f=np.array(st_zb["f"]) % 1.0, sp=list(st_zb["sp"]))
        except Exception:
            st_zb = None
        bz_relatorio(lat, base, a, out, st=st_zb)
    write_summary(out("resumo.txt"), base, D is not B and dseed or base, B, D, X, species, lat, typ,
                  dist, ticks, labels, ef_ha, ef_ev, egrid, dos_tot, dos_g, groups, efpos,
                  sites, a)

    win = (egrid >= a.ymin) & (egrid <= a.ymax)
    sign = [1, -1]
    efx = 0 if shifted else ef_ev[0]
    elements = [g["el"] for g in groups if g["cat"] == "el"]
    ecolor = {el: COLORS[i % len(COLORS)] for i, el in enumerate(elements)}

    def panel(ax, curves, fill=True):
        """curves: lista de (array_por_spin, label, cor). up +, down -."""
        lim = 0
        for ys, lab, col in curves:
            for s in range(ns):
                sg = sign[s] if ns == 2 else 1
                yy = sg * ys[s][win]
                lim = max(lim, np.abs(yy).max())
                ax.plot(egrid[win], yy, color=col, lw=1.2,
                        label=lab if s == 0 else None)
                if fill and col != "k":
                    ax.fill_between(egrid[win], 0, yy, color=col, alpha=0.13)
        lim = lim * 1.1 if lim > 0 else 1
        ax.set_ylim(-lim if ns == 2 else 0, lim)
        if EIXO["orig"]:
            linha_ef(ax, "x")
        else:
            ax.axvline(efx, color="gray", ls="--", lw=0.9)
        ax.axhline(0, color="k", lw=0.6)
        ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0),
                  fontsize=a.fontsize - 4, ncol=1)

    def gcurve(i, col, lab=None):
        return ([dos_g[s][i] for s in range(ns)], lab or groups[i]["label"], col)

    def dos_figure(fname, panels, title=None):
        """panels: lista de (titulo, [curvas])"""
        if not panels:
            return
        fig, axs = plt.subplots(len(panels), 1, sharex=True,
                                figsize=(a.width, max(a.height * 0.6,
                                                      2.2 * len(panels))))
        axs = np.atleast_1d(axs)
        for ax, (tt, curves) in zip(axs, panels):
            panel(ax, curves)
            ax.set_ylabel("PDOS")
            if tt:
                ax.text(0.01, 0.95, tt, transform=ax.transAxes, va="top",
                        fontsize=a.fontsize - 2, fontweight="bold")
        axs[-1].set_xlim(a.ymin, a.ymax)
        axs[-1].set_xlabel(ylab)
        for _a in axs:
            _a._eixo_e = "x"
        if title:
            axs[0].set_title(title)
        fig.subplots_adjust(hspace=0.08)
        fig.savefig(out(f"{fname}.{a.format}"), dpi=a.dpi)
        plt.close(fig)

    # 1) DOS total + elementos
    tot = ([dos_tot[s] for s in range(ns)], "Total", "k")
    dos_figure("dos_total", [(None, [tot] + [gcurve(gidx[("el", el)], ecolor[el])
                                             for el in elements])])
    # 2) PDOS por elemento resolvida em l
    dos_figure("pdos_elementos", [
        (el, [gcurve(i, ORB_COLORS[groups[i]["name"].split("_")[-1]])
              for i in sel("l") if groups[i]["el"] == el]) for el in elements])
    # 3) PDOS por camada (n,l): ex Mg 2s, 3s, 2p, 3p
    dos_figure("pdos_camadas", [
        (el, [gcurve(i, COLORS[k % len(COLORS)])
              for k, i in enumerate(j for j in sel("shell") if groups[j]["el"] == el)])
        for el in elements])
    # 4) Componentes m: uma figura por elemento, um painel por camada p/d/f
    for el in elements:
        pans = []
        for sh in dict.fromkeys(groups[i]["shell"] for i in sel("lm")
                                if groups[i]["el"] == el):
            ii = [i for i in sel("lm") if groups[i]["el"] == el
                  and groups[i]["shell"] == sh]
            pans.append((f"{el} {sh}", [gcurve(i, M_COLORS[k % 7],
                                               PRETTY.get(groups[i]["m"], groups[i]["m"]))
                                        for k, i in enumerate(ii)]))
        dos_figure(f"pdos_{el}_orbitais_m", pans)
        # t2g / eg
        ii = [i for i in sel("eg") if groups[i]["el"] == el]
        if ii:
            pans = []
            for sh in dict.fromkeys(groups[i]["shell"] for i in ii):
                jj = [i for i in ii if groups[i]["shell"] == sh]
                pans.append((f"{el} {sh}", [gcurve(i, "#d62728" if groups[i]["m"] ==
                                                   "t2g" else "#1f77b4",
                                                   PRETTY[groups[i]["m"]]) for i in jj]))
            dos_figure(f"pdos_{el}_t2g_eg", pans)
    # 5) Sitios individuais
    pans = []
    for st in dict.fromkeys(groups[i]["site"] for i in sel("site")):
        cur = [gcurve(gidx[("site", st)], "k", f"{st} total")]
        cur += [gcurve(i, ORB_COLORS[ORB_NAMES[groups[i]["l"]]])
                for i in sel("site_l") if groups[i]["site"] == st]
        pans.append((st, cur))
    dos_figure("pdos_sitios", pans)

    # 6) Bandas + DOS (painel combinado)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(a.width, a.height), sharey=True,
                                   gridspec_kw={"width_ratios": [2.3, 1]})
    if ns == 2:
        plot_bands(ax1, dist, E[0], cu, "-", 1.3, "up")
        plot_bands(ax1, dist, E[1], cd, "--", 1.0, "down")
        ax1.legend(loc="upper right", fontsize=a.fontsize - 3)
    else:
        plot_bands(ax1, dist, E[0], cu)
    deco_bands(ax1, dist, ticks, labels, a.ymin, a.ymax, ylab)
    lim = 0
    for ys, lab, col in [tot] + [gcurve(gidx[("el", el)], ecolor[el]) for el in elements]:
        for s in range(ns):
            sg = sign[s] if ns == 2 else 1
            xx = sg * ys[s][win]
            lim = max(lim, np.abs(xx).max())
            ax2.plot(xx, egrid[win], color=col, lw=1.2, label=lab if s == 0 else None)
            if col != "k":
                ax2.fill_betweenx(egrid[win], 0, xx, color=col, alpha=0.15)
    linha_ef(ax2, "y", rotulo=False)
    ax2.axvline(0, color="k", lw=0.6)
    ax2.set_xlim(-lim * 1.05 if ns == 2 else 0, lim * 1.05)
    ax2.set_xticks([])
    ax2.set_xlabel("DOS" + ("\n\u2190 down | up \u2192" if ns == 2 else ""))
    ax2.legend(loc="upper right", fontsize=a.fontsize - 4)
    fig.subplots_adjust(wspace=0.04)
    fig.savefig(out(f"bands_dos.{a.format}"), dpi=a.dpi)
    plt.close(fig)

    # ----------------- 7) Bandas projetadas (fat bands) -------------------- #
    PB = None
    if not a.no_fatbands and groups and P is not None and P.get("curves") is not None and not (a.dos_seed and _virt(seed + ".pdos_bin") is not P):
        print(" SIESTA: o .PDOS traz curvas, nao pesos por banda; sem bandas projetadas.")
    elif not a.no_fatbands and groups:
        if not a.dos_seed:
            PB = P
        elif _vexists(seed + ".pdos_bin"):
            PB = read_pdos_bin(seed + ".pdos_bin")
            if PB.get("curves") is not None or not align_k(B, PB):
                PB = None
        if PB is not None and (PB["w"].shape[1] != len(B["kidx"]) or
                               PB["w"].shape[-1] != Mg_.shape[0]):
            print(" AVISO: .pdos_bin nao corresponde ao .bands; sem fat bands.")
            PB = None
    if PB is not None:
        fat_l = sel("l")
        fat_m = sel("lm", "eg")
        fat_m = [i for i in fat_m if groups[i]["l"] >= 2]   # d e f em detalhe
        for s in range(ns):
            nb = E[s].shape[1]
            W = PB["w"][s][:, :nb, :] @ Mg_
            bands = [j for j in range(nb) if np.any((E[s][:, j] > a.ymin - 0.5) &
                                                    (E[s][:, j] < a.ymax + 0.5))]
            # .dat: k, banda, E, pesos
            fn = out(f"fatbands{tag(s)}.dat")
            cols = ["k(1/A)", "banda", "E(eV)"] + [groups[i]["name"] for i in fat_l + fat_m]
            rows = [np.column_stack([dist, np.full(len(dist), j + 1), E[s][:, j]] +
                                    [W[:, j, i] for i in fat_l + fat_m]) for j in bands]
            write_table(fn, [f"Bandas projetadas spin {SPIN_TAG[s] if ns == 2 else ''}; "
                             f"E_F = {ef_ev[s]:.6f} eV (CASTEP); pesos de 0 a 1",
                             "Origin: E vs k como Scatter; use a coluna do orbital em Symbol Size"],
                        cols, np.vstack(rows) if rows else np.zeros((0, len(cols))), fmt="%.5f")
            print(f" -> {fn}")

            def fat_fig(fname, idxs, colors, labs):
                ok = [(i, c, lb) for i, c, lb in zip(idxs, colors, labs)
                      if W[:, bands, i].max() > 0.02] if bands else []
                if not ok:
                    return
                ncol = min(len(ok), 4)
                nrow = int(np.ceil(len(ok) / ncol))
                fig, axs = plt.subplots(nrow, ncol, sharey=True, squeeze=False,
                                        figsize=(a.width * 0.42 * ncol + 1,
                                                 a.height * 0.85 * nrow))
                for ax in axs.ravel()[len(ok):]:
                    ax.axis("off")
                for k, (ax, (i, c, lb)) in enumerate(zip(axs.ravel(), ok)):
                    draw_fat(ax, dist, E[s], W[:, :, i], c, a.fat_scale, bands)
                    deco_bands(ax, dist, ticks, labels, a.ymin, a.ymax,
                               ylab if k % ncol == 0 else False)
                    ax.set_title(lb, fontsize=a.fontsize)
                    ax.tick_params(axis="x", labelsize=a.fontsize - 3)
                if ns == 2:
                    fig.suptitle(f"Spin {SPIN_TAG[s]}", y=0.94)
                fig.subplots_adjust(wspace=0.07, hspace=0.25)
                fig.savefig(out(f"{fname}{tag(s)}.{a.format}"), dpi=a.dpi)
                plt.close(fig)

            fat_fig("fatbands", fat_l,
                    [ORB_COLORS[ORB_NAMES[groups[i]["l"]]] for i in fat_l],
                    [groups[i]["label"] for i in fat_l])
            for el in elements:
                ii = [i for i in fat_m if groups[i]["el"] == el]
                if ii:
                    fat_fig(f"fatbands_{el}_orbitais_m", ii,
                            [M_COLORS[k % 7] if groups[i]["cat"] == "lm" else
                             ("#d62728" if groups[i]["m"] == "t2g" else "#1f77b4")
                             for k, i in enumerate(ii)],
                            [groups[i]["label"] for i in ii])

    if not a.no_defect:
        try:
            defect_report(seed, a, outdir)
        except Exception as e:                    # a analise do defeito nunca derruba o resto
            print(f" AVISO: analise do defeito falhou: {e}")
    if a.gerar_referencias:
        generate_references(seed, a, outdir)
    try:
        density_report(seed, a, outdir)
    except Exception as e:
        print(f" AVISO: analise de densidade falhou: {e}")
    if X.get("mull"):
        USADOS.update(("mulliken1955", "segall1996"))
    orca = (_virt(seed + ".castep", "extra") or {}).get("orca")
    if orca and (orca["mulliken"] or orca["loewdin"]):
        fn = os.path.join(outdir, f"{base}_cargas_orca.dat")
        lw = dict(orca["loewdin"])
        with open(fn, "w", encoding="utf-8") as f:
            f.write("# Cargas atomicas do ORCA (valores do programa, nao recalculados)\natomo\tMulliken(e)\tLoewdin(e)\n")
            for at, q in orca["mulliken"]:
                f.write(f"{at}\t{q:.5f}\t{lw.get(at, float('nan')):.5f}\n")
        print(f" -> {fn}")
    write_citation(outdir, base, {CODE["name"]})
    print(f" Graficos e .dat salvos em: {outdir}/")
    for f in sorted(os.listdir(outdir)):
        print("    ", f)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:          # saida cortada (ex.: brumare --sobre | head)
        pass
