#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo
"""Compara o BrUMaRe com ferramentas de referência nos MESMOS arquivos de saída.

Referências: pymatgen (VASP: gap, bordas, elétrons por spin), sumo (CASTEP: gap; VASP: massa efetiva),
sisl (SIESTA: autovalores e gap), cclib (ORCA: HOMO, LUMO) e pybader (cargas de Bader, Henkelman).

    pip install pymatgen sumo sisl cclib pybader
    python3 tools/comparar_ferramentas.py --dados tests/data --saida docs/comparacao
Gera comparacao.md, comparacao.tex (tabela do artigo) e resultados.json.
"""
import argparse, json, os, re, subprocess, sys, tempfile, time, warnings
import numpy as np
warnings.filterwarnings("ignore")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.argv = sys.argv[:1] + [x for x in sys.argv[1:]]


TEMPOS = []


def rodar_brumare(alvo, cwd, extra=()):
    """Roda a linha de comando do BrUMaRe e devolve o texto do resumo (e guarda o tempo de execução)."""
    out = tempfile.mkdtemp(prefix="bmr_"); t0 = time.time()
    subprocess.run([sys.executable, os.path.join(RAIZ, "brumare.py"), alvo, "--outdir", out, "--quiet",
                    "--no-fatbands", "--no-defect", "--fermi-ref", "spin", *extra],
                   cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, timeout=900)
    TEMPOS.append((os.path.basename(os.path.normpath(os.path.join(cwd, alvo))), time.time() - t0))
    r = [f for f in os.listdir(out) if f.endswith("_resumo.txt")]
    return open(os.path.join(out, r[0]), encoding="utf-8").read() if r else ""


def gaps_spin(txt):
    return [float(x) for x in re.findall(r"Gap banda N -> N\+1 no caminho = ([\d.]+) eV", txt)]


def num(pad, txt, conv=float):
    m = re.search(pad, txt)
    return conv(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default=os.path.join(RAIZ, "tests", "data"))
    ap.add_argument("--saida", default=os.path.join(RAIZ, "docs", "comparacao"))
    a = ap.parse_args()
    D = a.dados
    os.makedirs(a.saida, exist_ok=True)
    linhas = []                                    # (código, sistema, grandeza, BrUMaRe, referência, ferramenta, |Δ|)

    def add(cod, sis, gr, b, r, ferr, un=""):
        d = None if (b is None or r is None) else abs(b - r)
        linhas.append(dict(codigo=cod, sistema=sis, grandeza=gr, brumare=b, referencia=r, ferramenta=ferr, unidade=un, delta=d))
        print(f"  {cod:<7} {sis:<16} {gr:<28} BrUMaRe={b if b is None else round(b, 4)!s:<10} {ferr}={r if r is None else round(r, 4)!s:<10} |Δ|={d if d is None else f'{d:.2e}'}")

    # ---------------- VASP: Si (bandas em linha) — pymatgen e sumo ----------------
    print("VASP Si")
    from pymatgen.io.vasp import Vasprun
    from pymatgen.electronic_structure.core import Spin
    si = os.path.join(D, "vasp_Si_bands")
    txt = rodar_brumare(si, D)
    vr = Vasprun(os.path.join(si, "vasprun.xml"), parse_projected_eigen=False)
    bs = vr.get_band_structure(kpoints_filename=os.path.join(si, "KPOINTS"), line_mode=True)
    g = bs.get_band_gap()
    add("VASP", "Si (PBE)", "gap (eV)", gaps_spin(txt)[0], g["energy"], "pymatgen", "eV")
    add("VASP", "Si (PBE)", "E_F (eV)", num(r"E_F = [\d.\-]+ Ha = ([\d.\-]+) eV", txt), vr.efermi, "pymatgen", "eV")
    cbm, vbm = bs.get_cbm(), bs.get_vbm()
    add("VASP", "Si (PBE)", "CBM − VBM (eV)", gaps_spin(txt)[0], cbm["energy"] - vbm["energy"], "pymatgen", "eV")
    try:
        from sumo.electronic_structure.effective_mass import get_fitting_data, fit_effective_mass
        m_b = num(r"m\* eletron no CBM \([^)]*\)\) = ([\d.]+) m_e", txt)
        lados = [abs(fit_effective_mass(fd["distances"], fd["energies"], parabolic=True))
                 for fd in get_fitting_data(bs, Spin.up, cbm["band_index"][Spin.up][0], cbm["kpoint_index"][0], num_sample_points=2)]
        for i, m in enumerate(lados):
            add("VASP", "Si (PBE)", f"m* elétron, lado {i + 1} (m_e)", m_b, m, "sumo", "m_e")
        add("VASP", "Si (PBE)", "m* elétron (exp. 0,92 m_e)", m_b, 0.92, "experimento", "m_e")
    except Exception as e:
        print("   sumo (massa efetiva) indisponível:", e)

    # ---------------- VASP: Fe2O3 FM LDA+U — pymatgen ----------------
    print("VASP Fe2O3")
    fe = os.path.join(D, "vasp_Fe2O3_ldau")
    txt = rodar_brumare(fe, D)
    vr = Vasprun(os.path.join(fe, "vasprun.xml"), parse_projected_eigen=False)
    occ = {s: sum(float(np.sum(vr.eigenvalues[s][k][:, 1]) * w) for k, w in enumerate(vr.actual_kpoints_weights)) for s in vr.eigenvalues}
    nb = re.findall(r"eletrons = (\d+)", txt)
    add("VASP", "Fe2O3 (LDA+U)", "momento (μB)", float(int(nb[0]) - int(nb[1])) if len(nb) >= 2 else None, occ[Spin.up] - occ[Spin.down], "pymatgen", "μB")
    bsf = vr.get_band_structure()
    for i, s in enumerate((Spin.up, Spin.down)):
        e = vr.eigenvalues[s]; nocc = int(round(occ[s]))
        gs = float(np.min(e[:, nocc, 0]) - np.max(e[:, nocc - 1, 0]))
        add("VASP", "Fe2O3 (LDA+U)", f"gap spin {'↑' if i == 0 else '↓'} (eV)", gaps_spin(txt)[i] if len(gaps_spin(txt)) > i else None, gs, "pymatgen", "eV")

    # ---------------- CASTEP: MgH2:Fe — sumo ----------------
    print("CASTEP MgH2:Fe")
    try:
        from sumo.io.castep import band_structure
        cdir = os.path.join(D, "castep_MgH2_Fe")
        txt = rodar_brumare("mgh2_Fe", cdir)
        bsc = band_structure(os.path.join(cdir, "mgh2_Fe.bands"))
        add("CASTEP", "MgH2:Fe (162 at.)", "gap total (eV)", num(r"Gap considerando os dois spins = ([\d.]+) eV", txt), bsc.get_band_gap()["energy"], "sumo", "eV")
        add("CASTEP", "MgH2:Fe (162 at.)", "E_F (eV)", num(r"E_F = [\d.\-]+ Ha = ([\d.\-]+) eV", txt), bsc.efermi, "sumo", "eV")
        # mesma contagem de elétrons aplicada aos autovalores lidos pelo sumo: mostra que a diferença é de critério
        from pymatgen.electronic_structure.core import Spin as _S
        ne = [int(x) for x in re.findall(r"eletrons = (\d+)", txt)][:2]
        vb = max(float(np.max(bsc.bands[s_][n - 1])) for s_, n in zip((_S.up, _S.down), ne))
        cb = min(float(np.min(bsc.bands[s_][n])) for s_, n in zip((_S.up, _S.down), ne))
        add("CASTEP", "MgH2:Fe (162 at.)", "gap, contagem de elétrons nos autovalores do sumo (eV)", num(r"Gap considerando os dois spins = ([\d.]+) eV", txt), cb - vb, "sumo", "eV")
    except BaseException as e:                     # o sumo chama sys.exit em alguns erros de leitura
        print("   sumo (CASTEP) indisponível:", repr(e)[:120])

    # ---------------- SIESTA: SrTiO3 — sisl ----------------
    print("SIESTA SrTiO3")
    try:
        import sisl
        sdir = os.path.join(D, "siesta_SrTiO3")
        txt = rodar_brumare("SrTiO3", sdir)
        eig = np.asarray(sisl.get_sile(os.path.join(sdir, "SrTiO3.bands")).read_data()[-1])   # (spin, k, banda), já relativos a E_F
        eig = eig.reshape(-1, eig.shape[-2], eig.shape[-1]) if eig.ndim == 3 else eig[None]
        n = 20                                                       # 40 elétrons de valência, 20 por spin
        gs = [float(np.min(e[:, n]) - np.max(e[:, n - 1])) for e in eig]
        tot = float(min(np.min(e[:, n]) for e in eig) - max(np.max(e[:, n - 1]) for e in eig))
        add("SIESTA", "SrTiO3 (LDA)", "gap total (eV)", num(r"Gap considerando os dois spins = ([\d.]+) eV", txt) or gaps_spin(txt)[0], tot, "sisl", "eV")
        bdir = os.path.join(D, "siesta_Bi2Se3")
        txt = rodar_brumare("Bi2Se3", bdir)
        e = np.asarray(sisl.get_sile(os.path.join(bdir, "Bi2Se3.bands")).read_data()[-1])
        e = e.reshape(-1, e.shape[-2], e.shape[-1]) if e.ndim == 3 else e[None]
        nb = int(re.findall(r"eletrons = (\d+)", txt)[0]) // 2
        add("SIESTA", "Bi2Se3", "gap (eV)", gaps_spin(txt)[0], float(np.min(e[0][:, nb]) - np.max(e[0][:, nb - 1])), "sisl", "eV")
    except Exception as e:
        print("   sisl indisponível:", e)

    # ---------------- ORCA: divinilbenzeno — cclib ----------------
    print("ORCA divinilbenzeno")
    try:
        import cclib
        odir = os.path.join(D, "orca")
        txt = rodar_brumare("dvb_sp.out", odir)
        cd = cclib.io.ccread(os.path.join(odir, "dvb_sp.out"))
        h = int(cd.homos[0]); mo = np.asarray(cd.moenergies[0])
        add("ORCA", "divinylbenzene", "HOMO (eV)", num(r"HOMO = ([\d.\-]+) eV", txt), float(mo[h]), "cclib", "eV")
        add("ORCA", "divinylbenzene", "LUMO (eV)", num(r"LUMO = ([\d.\-]+) eV", txt), float(mo[h + 1]), "cclib", "eV")
        add("ORCA", "divinylbenzene", "gap HOMO–LUMO (eV)", num(r"Gap HOMO-LUMO = ([\d.]+) eV", txt), float(mo[h + 1] - mo[h]), "cclib", "eV")
    except Exception as e:
        print("   cclib indisponível:", e)

    # ---------------- Bader: Fe3O4 (CHGCAR com spin) — pybader ----------------
    print("Bader MgH2:Fe")
    try:
        import brumare as B
        from pybader.interface import Bader
        from pybader.io import vasp as pbv
        from pymatgen.io.vasp import Chgcar
        fn = os.path.join(D, "bader_MgH2_Fe", "CHGCAR")
        ch = Chgcar.from_file(fn); s = ch.structure
        st = dict(lat=s.lattice.matrix, f=s.frac_coords % 1.0, sp=[str(x.specie) for x in s], label=[f"{x.specie}{i + 1}" for i, x in enumerate(s)])
        G = B.read_chgcar(fn)
        t0 = time.time(); r0 = B.bader_ongrid(G, st, refinar=False); t_b0 = time.time() - t0
        t0 = time.time(); r = B.bader_ongrid(G, st); t_b = time.time() - t0
        t0 = time.time(); bd = Bader(*pbv.read(fn)); bd.bader_volume_tol = 1e-3
        bd(); t_p = time.time() - t0
        qb, qp = np.asarray(r["q"]), np.asarray(bd.atoms_charge)
        q0 = np.asarray(r0["q"])
        add("CHGCAR", f"MgH2:Fe CHGCAR ({len(st['sp'])} at.)", "Bader on-grid: |Δq| médio (e)", 0.0, float(np.mean(np.abs(q0 - qp))), "pybader", "e")
        add("CHGCAR", f"MgH2:Fe CHGCAR ({len(st[chr(115)+chr(112)])} at.)", "Bader: |Δq| médio (e)", 0.0, float(np.mean(np.abs(qb - qp))), "pybader", "e")
        add("CHGCAR", f"MgH2:Fe CHGCAR ({len(st[chr(115)+chr(112)])} at.)", "Bader: Σq (e)", float(qb.sum()), float(qp.sum()), "pybader", "e")
        add("CHGCAR", f"MgH2:Fe CHGCAR ({len(st[chr(115)+chr(112)])} at.)", "Bader: |Δq| máximo (e)", 0.0, float(np.max(np.abs(qb - qp))), "pybader", "e")
        print(f"   tempos: BrUMaRe on-grid {t_b0:.2f} s, refinado {t_b:.2f} s, pybader {t_p:.2f} s")
        TEMPOS.append(("Bader on-grid (BrUMaRe)", t_b0)); TEMPOS.append(("Bader refinado (BrUMaRe)", t_b)); TEMPOS.append(("Bader (pybader)", t_p))
    except Exception as e:
        print("   pybader indisponível:", e)

    # ---------------- saídas ----------------
    json.dump(linhas, open(os.path.join(a.saida, "resultados.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# BrUMaRe × ferramentas de referência (mesmos arquivos)", "", "| Código | Sistema | Grandeza | BrUMaRe | Referência | Ferramenta | |Δ| |", "|---|---|---|---|---|---|---|"]
    for l in linhas:
        f = lambda v: "—" if v is None else f"{v:.4f}"
        md.append(f"| {l['codigo']} | {l['sistema']} | {l['grandeza']} | {f(l['brumare'])} | {f(l['referencia'])} | {l['ferramenta']} | {'—' if l['delta'] is None else f'{l[chr(100)+chr(101)+chr(108)+chr(116)+chr(97)]:.1e}'} |")
    md += ["", "## Tempos de execução", "", "| Caso | Tempo (s) |", "|---|---|"] + [f"| {n} | {t:.2f} |" for n, t in TEMPOS]
    open(os.path.join(a.saida, "comparacao.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    json.dump(dict(comparacoes=linhas, tempos=TEMPOS), open(os.path.join(a.saida, "resultados.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tex = [r"\begin{table}[t]\centering\small", r"\caption{Cross-validation of \BMR\ against established tools on the same output files. $|\Delta|$ is the absolute difference.}\label{tab:bench}",
           r"\resizebox{\linewidth}{!}{\begin{tabular}{@{}lllrrlr@{}}\toprule", r"Code & System & Quantity & \BMR & Reference & Tool & $|\Delta|$ \\\midrule"]
    tr = {"gap (eV)": "gap (eV)", "E_F (eV)": "$E_\\mathrm{F}$ (eV)", "CBM − VBM (eV)": "CBM$-$VBM (eV)", "m* elétron (m_e)": "$m^*_e$ ($m_e$)",
          "momento (μB)": "moment ($\\mu_\\mathrm{B}$)", "gap spin ↑ (eV)": "gap $\\uparrow$ (eV)", "gap spin ↓ (eV)": "gap $\\downarrow$ (eV)",
          "gap total (eV)": "total gap (eV)", "HOMO (eV)": "HOMO (eV)", "LUMO (eV)": "LUMO (eV)", "gap HOMO–LUMO (eV)": "HOMO--LUMO gap (eV)",
          "Bader: |Δq| médio (e)": "Bader (refined) mean $|\\Delta q|$ (e)", "Bader on-grid: |Δq| médio (e)": "Bader (on-grid) mean $|\\Delta q|$ (e)", "Bader: |Δq| máximo (e)": "Bader (refined) max.\\ $|\\Delta q|$ (e)", "gap, contagem de elétrons nos autovalores do sumo (eV)": "gap, electron counting on sumo eigenvalues (eV)", "m* elétron, lado 1 (m_e)": "$m^*_e$, side 1 ($m_e$)", "m* elétron, lado 2 (m_e)": "$m^*_e$, side 2 ($m_e$)", "m* elétron (exp. 0,92 m_e)": "$m^*_e$ vs experiment ($m_e$)", "Bader: Σq (e)": "Bader $\\sum q$ (e)"}
    for l in linhas:
        g = tr.get(l["grandeza"], l["grandeza"].replace("Bader: q médio", "Bader mean $q$").replace("(e)", "(e)"))
        f = lambda v: "--" if v is None else f"{v:.4f}"
        sis = l["sistema"].replace("MgH2", "MgH$_2$").replace("Fe2O3", "Fe$_2$O$_3$").replace("Fe3O4", "Fe$_3$O$_4$").replace("SrTiO3", "SrTiO$_3$").replace("Bi2Se3", "Bi$_2$Se$_3$")
        tex.append(f"{l['codigo']} & {sis} & {g} & {f(l['brumare'])} & {f(l['referencia'])} & {l['ferramenta'].replace('experimento', 'experiment')} & {'--' if l['delta'] is None else f'{l[chr(100)+chr(101)+chr(108)+chr(116)+chr(97)]:.1e}'} \\\\")
    tex += [r"\bottomrule\end{tabular}}", r"\end{table}"]
    open(os.path.join(a.saida, "comparacao.tex"), "w", encoding="utf-8").write("\n".join(tex) + "\n")
    print(f"\n{len(linhas)} comparações -> {a.saida}/comparacao.md, comparacao.tex, resultados.json")


if __name__ == "__main__":
    main()
