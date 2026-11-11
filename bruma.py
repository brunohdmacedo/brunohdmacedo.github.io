#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##############################################################################
#  Bruma 1.0.0  -  bandas, DOS, PDOS, densidade de carga, defeitos e        #
#                  termodinamica a partir de calculos CASTEP                 #
#                                                                            #
#  Autor: Bruno Henrique Dourado Macedo (UNILA, PPGFISA)                     #
#         https://brunohdmacedo.tech  ·  ORCID 0000-0002-8152-0950           #
#  Site e tutorial: https://brunohdmacedo.tech/bruma/                        #
#  Codigo-fonte:    https://github.com/brunohdmacedo/bruma-dft               #
#                                                                            #
#  * Spin up e down separados; a energia de Fermi e EXATAMENTE a do .bands   #
#  * PDOS por elemento, l, camada, m, t2g/eg e atomo; bandas projetadas      #
#  * Defeitos, distorcao, termodinamica; densidade total e polarizada,       #
#    planos (h k l), diferenca puro x defeito, cargas por atomo              #
#  * .dat para o Origin, CHGCAR/XSF para o VESTA, figuras PNG/SVG            #
#  * Dependencias: apenas numpy e matplotlib (roda em cluster, sem display)  #
#                                                                            #
#  Uso:  python3 bruma.py                  (detecta o seed e pergunta)       #
#        python3 bruma.py mgh2_Fe -e Mg,H,Fe --sites Fe1                     #
#        python3 bruma.py --sobre          (autor, links e como citar)       #
#        python3 bruma.py -h               (todas as opcoes)                 #
#  Interface grafica: python3 bruma_gui.py                                   #
#                                                                            #
#  Baseado em plot_all_dos_bands.sh (B. H. D. Macedo) e separar_up_down.py   #
#  (Luiz Claudio), 07/2025.                                                  #
##############################################################################
import argparse
import os
import re
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
NOME = "Bruma"
VERSAO = "1.0.0"
DESCRICAO = "bandas, DOS, PDOS, densidade de carga, defeitos e termodinâmica a partir de cálculos CASTEP"
AUTOR = "Bruno Henrique Dourado Macedo"
AFILIACAO = "Engenheiro Físico (UNILA) e mestrando em Física Aplicada (PPGFISA/UNILA), bolsista CNPq"
FOTO_URL = "https://wwws.cnpq.br/cvlattesweb/pkg_util_img.show_foto?v_cod=K4494050P3"
LINKS = [("Site", "https://brunohdmacedo.tech/"), ("Bruma", "https://brunohdmacedo.tech/bruma/"),
         ("Codigo-fonte", "https://github.com/brunohdmacedo/bruma-dft"), ("Lattes", "http://lattes.cnpq.br/7842985016416991"),
         ("ORCID", "https://orcid.org/0000-0002-8152-0950"), ("Google Academico", "https://scholar.google.com/citations?user=zl-LdTMAAAAJ&hl=pt-BR"),
         ("LinkedIn", "https://bit.ly/3VlPBAE"), ("GitHub", "https://bit.ly/47dlUt0"), ("YouTube", "https://bit.ly/3HGUTDW"),
         ("Instagram", "https://bit.ly/465SETR"), ("E-mail", "mailto:brunohdmacedo@gmail.com")]
CITACAO_ABNT = ("MACEDO, B. H. D. Bruma: análise de estrutura de bandas, DOS, PDOS, densidade de carga, defeitos e "
                "termodinâmica a partir de cálculos CASTEP. Versão " + VERSAO + ". Foz do Iguaçu, 2026. Software. "
                "Disponível em: https://brunohdmacedo.tech/bruma/.")
CITACAO_BIBTEX = """@misc{macedo2026bruma,
  author       = {Macedo, Bruno Henrique Dourado},
  title        = {Bruma: análise de estrutura de bandas, {DOS}, {PDOS}, densidade de carga, defeitos e termodinâmica a partir de cálculos {CASTEP}},
  year         = {2026},
  version      = {""" + VERSAO + """},
  howpublished = {\\url{https://brunohdmacedo.tech/bruma/}},
  note         = {Código-fonte: \\url{https://github.com/brunohdmacedo/bruma-dft}}
}"""
CITACAO_CASTEP = "S. J. Clark et al., Z. Kristallogr. 220, 567-570 (2005), doi:10.1524/zkri.220.5.567.65075"


def banner():
    print(f" {NOME} {VERSAO}  ·  {DESCRICAO}")
    print(f" {AUTOR}  ·  brunohdmacedo.tech/bruma  ·  como citar: {os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else 'bruma'} --sobre")


def sobre_texto():
    L = [f"{NOME} {VERSAO}", "=" * 72, DESCRICAO, "",
         f"Autor: {AUTOR}", f"       {AFILIACAO}", "",
         "Links:"] + [f"  {n:<17}{u}" for n, u in LINKS] + ["",
         "Como citar (ABNT):", "  " + CITACAO_ABNT, "", "BibTeX:", CITACAO_BIBTEX, "",
         "Cite tambem o CASTEP:", "  " + CITACAO_CASTEP]
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
    if not fname or not os.path.isfile(fname):
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
    return dict(vbm=vbm, cbm=cbm, vb=vb, cb=cb, gap=cbm - vbm, vkl=lab(vk), ckl=lab(ck),
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


def deco_bands(ax, dist, ticks, labels, ymin, ymax, ylabel=True):
    for t in ticks[1:-1]:
        ax.axvline(t, color="k", lw=0.8)
    ax.axhline(0, color="gray", ls="--", lw=0.9)
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
    if not fname or not os.path.isfile(fname):
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
    ref, mlab = read_castep_orbitals(castepf)
    norb = len(P["am"])
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
MASS = dict(H=1.008, Li=6.94, Be=9.0122, B=10.81, C=12.011, N=14.007, O=15.999, F=18.998, Na=22.99,
            Mg=24.305, Al=26.982, Si=28.085, P=30.974, S=32.06, Cl=35.45, K=39.098, Ca=40.078,
            Sc=44.956, Ti=47.867, V=50.942, Cr=51.996, Mn=54.938, Fe=55.845, Co=58.933, Ni=58.693,
            Cu=63.546, Zn=65.38, Ga=69.723, Ge=72.63, Y=88.906, Zr=91.224, Nb=92.906, Mo=95.95,
            Ru=101.07, Rh=102.91, Pd=106.42, Ag=107.87, Cd=112.41, In=114.82, Sn=118.71, La=138.91,
            Ce=140.12, Hf=178.49, Ta=180.95, W=183.84, Pt=195.08, Au=196.97, Pb=207.2)


def read_cell_struct(fname):
    """Rede (A), posicoes fracionarias e massas de um .cell."""
    if not fname or not os.path.isfile(fname):
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
    if not fname or not os.path.isfile(fname):
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
    if os.path.isfile(seed + ".cell"):
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
    if os.path.isfile(seed + ".castep"):
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
        f.write(f"! {title}\n! Gerado pelo bruma.py (Bruma)\n" + "".join(f"! {n}\n" for n in notes))
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
        f.write("Depois de rodar:\n  python3 bruma.py " + base + f" --ref {base}_puro --mu \"" +
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


def write_chgcar(fn, st, G, arr, arr2=None, title="Bruma"):
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
    """.den_fmt (CASTEP), .cube ou CHGCAR -> dict(lat, n, rho (e/A^3), spin, V, Nel)."""
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
    fn = a.density or next((seed + e for e in (".den_fmt", ".cube") if os.path.isfile(seed + e)), None)
    if not fn or not os.path.isfile(fn):
        print(f" Sem {seed}.den_fmt: analise de densidade ignorada (no .param: WRITE_FORMATTED_DENSITY : true).")
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
    print(f" Densidade {fn}: grade {G['n']}, eletrons integrados {G['Nel']:.3f}" + (f", spin {G['Sint']:.4f} / |spin| {G['Sabs']:.4f}" if G.get("Sint") is not None else ""))
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
        write_chgcar(nm, st, G, arr, two, f"{base} {dict(rho='densidade de carga', spin='densidade de spin', diff='diferenca de densidade')[field]} (Bruma)")
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
    if os.path.isfile(seed + ".castep"):
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
        fn = out(f"{names[k]}_CHGCAR.vasp"); write_chgcar(fn, st, G, A, None, f"{base} {names[k]} (Bruma)"); log.append(fn)
        if refs:
            try:
                D = A.copy()
                for H in refs:
                    D = D - on_grid(G, H, density_component(H, k))
            except ValueError:
                continue
            D = sgn * D
            fn = out(f"delta_{names[k]}_{tag}_CHGCAR.vasp")
            write_chgcar(fn, st, G, D, None, f"{base} delta {names[k]} {tag.replace('_', ' ')} (Bruma)")
            log.append(f"{fn}  (faixa {D.min():.4g} a {D.max():.4g} e/A^3)")
    with open(out("LEIAME_VESTA.txt"), "w", encoding="utf-8") as fh:
        fh.write("VISUALIZACAO NO VESTA (Bruma)\nArquivos CHGCAR em formato VASP 5 (com elementos), valores rho*V.\n"
                 f"Diferencas: {'rho(puro) - rho(defeito)' if sgn < 0 else 'rho(defeito) - rho(puro)'}; referencia reamostrada se a grade for diferente.\n\n"
                 + "\n".join("  " + x for x in log) +
                 "\n\nNo VESTA: File > Open; Properties > Isosurfaces com dois niveis (+0.01 e -0.01) para as diferencas e o spin;\n"
                 "Edit > Lattice Planes (1 1 0), (-1 1 0)... e Utilities > 2D Data Display para os cortes.\n")
    print(f" -> {len(log)} CHGCARs para o VESTA + {out('LEIAME_VESTA.txt')}")


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
        w(f"  Gap banda N -> N+1 no caminho = {e['gap']:.4f} eV "
          f"({'direto' if e['direct'] else 'indireto'})")
        w("  E_F dentro de banda: " + ("; ".join(f"sim, banda {b + 1} (largura {wd:.1f} meV)"
                                                for b, wd in e["inside"]) or "nao"))
        w(f"  N(E_F) = {dos_tot[s][i0]:.4f} estados/eV")
    if ns == 2:
        vb = max(e["vbm"] - ef_ev[s] for s, e in enumerate(edges))
        cb = min(e["cbm"] - ef_ev[s] for s, e in enumerate(edges))
        nu, nd = [dos_tot[s][int(np.argmin(np.abs(egrid - efpos[s])))] for s in (0, 1)]
        w(f"Gap considerando os dois spins = {cb - vb:.4f} eV")
        w(f"Polarizacao de spin em E_F = {100 * (nu - nd) / (nu + nd) if nu + nd > 1e-8 else 0:.2f} %")
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
    if D["hdr"]["nk"] < 100:
        w("")
        w(f"AVISO: a DOS usa {D['hdr']['nk']} k-pontos. Para valores quantitativos rode "
          "SPECTRAL_TASK : DOS com malha MP densa e use --dos-seed.")
    with open(fn, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f" -> {fn}")
    for l in L[L.index(next(x for x in L if x.startswith("ENERGIA"))):]:
        if l.startswith(("Spin", "  E_F", "  Gap", "  E_F dentro", "Gap", "Polariz", "Spin integ")):
            print(" " + l)


def main(argv=None):
    for _s in (sys.stdout, sys.stderr):           # console do Windows: nunca quebrar por acento
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass
    p = argparse.ArgumentParser(
        prog="bruma", description=f"{NOME} {VERSAO}: {DESCRICAO}. Autor: {AUTOR}.",
        epilog="Como citar: bruma --sobre  ·  tutorial: https://brunohdmacedo.tech/bruma/tutorial.html",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("seed", nargs="?", help="seedname (ex: mgh2_Fe) ou o arquivo .bands. "
                   "Se omitido, procura um .bands na pasta atual")
    p.add_argument("--sobre", action="store_true", help="mostra autor, links e como citar o Bruma, e sai")
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
    p.add_argument("--fermi-ref", choices=["spin", "up", "down", "mean", "none"],
                   default="spin",
                   help="referencia de energia: 'spin' = cada canal com o SEU E_F "
                   "do .bands; 'up'/'down'/'mean' = um E_F comum; "
                   "'none' = energias absolutas")
    p.add_argument("--labels", help="rotulos dos pontos k, ex: G,X,M,G,Z,R,A,Z")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--width", type=float, default=8.0)
    p.add_argument("--height", type=float, default=6.0)
    p.add_argument("--fontsize", type=int, default=13)
    p.add_argument("--format", default="png", help="png, pdf, svg, eps...")
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
    d.add_argument("--diff-sign", choices=["defeito-puro", "puro-defeito"], default="defeito-puro",
                   help="sentido das diferencas (--field diff e --vesta)")
    d.add_argument("--chgcar-spin", action="store_true", help="com --chgcar e --field rho: inclui a densidade de spin como 2o bloco")
    g.add_argument("--dS", type=float, default=130.7, help="entropia de dessorcao (J/mol K) para T_d = dH/dS")
    g.add_argument("--h-less", help="seed da estrutura com H a menos (energia de remocao de H)")
    g.add_argument("--no-defect", action="store_true", help="nao fazer a analise de defeito")
    p.add_argument("--no-split", action="store_true",
                   help="nao escrever <seed>_up.bands / <seed>_down.bands")
    a = p.parse_args(argv)
    if a.sobre:
        print(sobre_texto())
        return
    if not a.quiet:
        banner()

    interactive = bool(sys.stdin) and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
    if not a.seed:
        cands = sorted(f[:-6] for f in os.listdir(".") if f.endswith(".bands")
                       and not re.search(r"_(up|down)$", f[:-6]))
        if not cands:
            sys.exit("ERRO: nenhum .bands na pasta atual. Informe o seedname: "
                     "python3 bruma.py <seed>")
        if len(cands) == 1 or not interactive:
            a.seed = cands[0]
        else:
            for i, c in enumerate(cands, 1):
                print(f"  {i}) {c}")
            r = input("Qual calculo? (numero ou nome) [1]: ").strip() or "1"
            a.seed = cands[int(r) - 1] if r.isdigit() else r
        print(f" Seed detectado: {a.seed}")
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

    if not os.path.isfile(seed + ".bands"):
        if os.path.isfile(seed + ".cell") or os.path.isfile(seed + ".castep"):
            print(f" Sem {seed}.bands: fazendo so a analise de estrutura, defeito e termodinamica.")
            style(a.fontsize)
            defect_report(seed, a, outdir)
            if a.gerar_referencias:
                generate_references(seed, a, outdir)
            density_report(seed, a, outdir)
            return
        sys.exit(f"ERRO: arquivo nao encontrado: {seed}.bands")
    castep0 = a.castep or seed + ".castep"
    X = read_castep_extra(castep0)

    # ---------------------------- bandas ---------------------------------- #
    B = read_bands(seed + ".bands")
    h = B["hdr"]
    ns = h["ns"]
    if os.path.isfile(cellf):
        species = read_cell_species(cellf)
    elif X["species"]:
        species = X["species"]
        print(f" AVISO: {cellf} nao encontrado; especies lidas do .castep.")
    else:
        sys.exit(f"ERRO: preciso do {cellf} (ou do .castep) para saber as especies.")
    lat = h["lattice"] * BOHR2ANG
    dist, ticks, labels, typ = kpath(B["kfrac"], lat, a.labels)
    ef_ha = h["efermi"]
    ef_ev = [x * HA2EV for x in ef_ha]

    if a.fermi_ref == "spin":
        ref = ef_ev
    elif a.fermi_ref == "none":
        ref = [0.0] * ns
    else:
        r = {"up": ef_ev[0], "down": ef_ev[-1], "mean": float(np.mean(ef_ev))}[a.fermi_ref]
        ref = [r] * ns
    shifted = a.fermi_ref != "none"
    E = [B["eig"][s] * HA2EV - ref[s] for s in range(ns)]
    ylab = r"E $-$ E$_F$ (eV)" if shifted else "E (eV)"

    print("=" * 70)
    print(f" Sistema: {base}   | especies: {', '.join(species)}")
    print(f" k-pontos: {h['nk']}  | spins: {ns}  | bandas: {h['neig']}")
    print(f" Rede: {typ}  | caminho: {' - '.join(labels)}")
    for s in range(ns):
        print(f" E_F spin {SPIN_TAG[s] if ns == 2 else ''}: {ef_ha[s]:.6f} Ha = "
              f"{ef_ev[s]:.4f} eV  (valor do CASTEP, nao recalculado)")
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
        # Fermi do calculo de DOS, tambem sem recalcular
        dref = ([x * HA2EV for x in D["hdr"]["efermi"]] if a.fermi_ref == "spin"
                else ref)
    else:
        D, dref = B, ref
    ED = [D["eig"][s] * HA2EV - dref[s] for s in range(ns)]
    ef_dos = [x * HA2EV for x in D["hdr"]["efermi"]]
    efpos = [ef_dos[s] - dref[s] for s in range(ns)]          # posicao de E_F no eixo da DOS
    if D["hdr"]["nk"] < 100:
        print(f" AVISO: a DOS usa apenas {D['hdr']['nk']} k-pontos. Para DOS "
              "quantitativa rode SPECTRAL_TASK: DOS\n        com malha MP densa e "
              "passe --dos-seed.")

    pdosf = a.pdos or dseed + ".pdos_bin"
    castepf = a.castep or (dseed + ".castep" if os.path.isfile(dseed + ".castep")
                           else seed + ".castep")
    els = [x.strip() for x in a.elements.split(",")] if a.elements else species
    for el in els:
        if el not in species:
            print(f" AVISO: elemento {el} nao esta no .cell; ignorado.")
    els = [el for el in els if el in species]
    orbs = [x.strip() for x in a.orbitals.split(",")]
    sites = [x for x in (a.sites or "").split(",") if x.strip()]
    P, O, groups = None, None, []
    if os.path.isfile(pdosf):
        P = read_pdos_bin(pdosf)
        if not align_k(D, P):
            print(f" AVISO: os k-pontos de {pdosf} nao batem com {dseed}.bands; PDOS ignorada.")
            P = None
    if P is not None:
        O, msg = build_orbitals(P, species, castepf)
        print(" " + msg)
        groups = make_groups(O, els, orbs, sites)
    elif not os.path.isfile(pdosf):
        print(f" AVISO: {pdosf} nao encontrado: somente DOS total.")
    Mg_ = np.array([g["mask"] for g in groups], float).T if groups else None

    emin = min(np.nanmin(x) for x in ED) - 5 * a.sigma - 1
    emax = max(np.nanmax(x) for x in ED) + 5 * a.sigma + 1
    egrid = np.arange(emin, emax + a.de, a.de)
    dos_tot, dos_g = [], []
    for s in range(ns):
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
    ax2.axhline(0, color="gray", ls="--", lw=0.9)
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
    if not a.no_fatbands and groups:
        if not a.dos_seed:
            PB = P
        elif os.path.isfile(seed + ".pdos_bin"):
            PB = read_pdos_bin(seed + ".pdos_bin")
            if not align_k(B, PB):
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
    print(f" Graficos e .dat salvos em: {outdir}/")
    for f in sorted(os.listdir(outdir)):
        print("    ", f)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:          # saida cortada (ex.: bruma --sobre | head)
        pass
