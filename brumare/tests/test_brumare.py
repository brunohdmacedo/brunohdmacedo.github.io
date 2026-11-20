# SPDX-License-Identifier: GPL-3.0-or-later
"""Suíte de testes do BrUMaRe: valores de referência dos cinco programas, correção do gap, formatos,
Bader, citação, idiomas e comparação com ferramentas consolidadas (pymatgen, sumo, sisl, cclib, pybader).
    pytest -q            (os testes de comparação são pulados se a ferramenta não estiver instalada)"""
import os, re, subprocess, sys
import numpy as np
import pytest
from conftest import DADOS, RAIZ, num, GAP, GAP_TOT, EF

# ------------------------------------------------------------------ CASTEP
def test_castep_mgh2_fe(caso):
    t = caso("castep", "mgh2_Fe", "castep_MgH2_Fe")["txt"]
    assert num(GAP_TOT, t) == pytest.approx(1.3940, abs=2e-4)
    assert num(GAP, t, True) == pytest.approx([1.3942, 1.3942], abs=2e-4)
    assert num(EF, t, True)[:2] == pytest.approx([1.8368, 1.8367], abs=2e-4)   # E_F do programa, nunca recalculado

def test_castep_citacao(caso):
    d = caso("castep", "mgh2_Fe", "castep_MgH2_Fe")["dir"]
    bib = open(os.path.join(d, "mgh2_Fe_citacao.bib"), encoding="utf-8").read()
    assert "macedo2026brumare" in bib and "clark2005castep" in bib

# ------------------------------------------------------------------ VASP
def test_vasp_si(caso):
    t = caso("vasp_si", "vasp_Si_bands", None)["txt"]
    assert num(GAP, t) == pytest.approx(0.6143, abs=2e-4) and "(indireto)" in t
    assert num(r"m\* eletron no CBM \([^)]*\)\) = ([\d.]+) m_e", t) == pytest.approx(0.94, abs=0.02)     # exp. 0,92
    assert num(r"m\* buraco no VBM \([^)]*\) = ([\d.]+) m_e", t) == pytest.approx(0.315, abs=0.02)

def test_vasp_fe2o3_magnetico(caso):
    t = caso("vasp_fe2o3", "vasp_Fe2O3_ldau", None)["txt"]
    ne = [int(x) for x in re.findall(r"eletrons = (\d+)", t)][:2]
    assert ne == [56, 36]                                                      # 20 μB: quatro Fe3+ de spin alto
    assert num(GAP, t, True)[:2] == pytest.approx([4.0199, 2.1923], abs=2e-4)

# ------------------------------------------------------------------ SIESTA, QE, ORCA
def test_siesta_srtio3(caso):
    t = caso("siesta", "SrTiO3", "siesta_SrTiO3")["txt"]
    g = num(GAP_TOT, t) or num(GAP, t)
    assert g == pytest.approx(2.2501, abs=2e-3)

def test_qe_si(caso):
    t = caso("qe", "qe_Si", None)["txt"]
    assert num(GAP, t) == pytest.approx(1.3195, abs=2e-4)

def test_orca_molecula(caso):
    r = caso("orca", "dvb_sp.out", "orca")
    assert num(r"Gap HOMO-LUMO = ([\d.]+) eV", r["txt"]) == pytest.approx(5.1849, abs=2e-4)
    assert "AVISO: a DOS usa apenas" not in r["stdout"]                       # sem avisos de cristal para moléculas

# ------------------------------------------------------------------ correção do gap
def test_correcao_gap_modelo_e_tesoura(caso):
    t0 = caso("vasp_si", "vasp_Si_bands", None)["txt"]
    tm = caso("si_mvi", "vasp_Si_bands", None, "--gap-corr", "mvi")["txt"]
    tr = caso("si_ref", "vasp_Si_bands", None, "--gap-corr", "ref", "--gap-ref", "1.17")["txt"]
    assert num(GAP, tm) == pytest.approx(1.358 * 0.6143 + 0.904, abs=5e-4)     # Morales-García et al. (2017)
    assert num(GAP, tr) == pytest.approx(1.17, abs=1e-4)
    m = r"m\* eletron no CBM \([^)]*\)\) = ([\d.]+) m_e"
    assert num(m, tr) == pytest.approx(num(m, t0), abs=1e-3)                   # tesoura rígida: massas inalteradas
    assert num(EF, tr) == pytest.approx(num(EF, t0), abs=1e-6)                 # E_F não muda

# ------------------------------------------------------------------ formatos de figura
def test_formatos_png_jxl_sem_perdas(caso):
    ic = pytest.importorskip("imagecodecs")
    from PIL import Image
    d = caso("formatos", "vasp_Si_bands", None, "--format", "png,jxl,svg")["dir"]
    png = sorted(f for f in os.listdir(d) if f.endswith(".png"))
    assert png and all(os.path.exists(os.path.join(d, f[:-4] + e)) for f in png for e in (".jxl", ".svg"))
    a = np.asarray(Image.open(os.path.join(d, png[0])).convert("RGBA")).astype(int)
    b = ic.jpegxl_decode(open(os.path.join(d, png[0][:-4] + ".jxl"), "rb").read()).astype(int)
    assert np.abs(a - b).max() == 0                                            # JXL sem perdas = PNG pixel a pixel

# ------------------------------------------------------------------ Bader
def _bader_brumare():
    sys.argv = ["x"]
    import brumare as B
    pm = pytest.importorskip("pymatgen.io.vasp")
    fn = os.path.join(DADOS, "bader_MgH2_Fe", "CHGCAR")
    s = pm.Chgcar.from_file(fn).structure
    st = dict(lat=s.lattice.matrix, f=s.frac_coords % 1.0, sp=[str(x.specie) for x in s], label=[str(i) for i in range(len(s))])
    return fn, np.asarray(B.bader_ongrid(B.read_chgcar(fn), st)["q"])

def test_bader_conserva_carga():
    fn, q = _bader_brumare()
    assert q.sum() == pytest.approx(651.0, abs=1e-6)

def test_siesta_bi2se3(caso):
    t = caso("bi2se3", "Bi2Se3", "siesta_Bi2Se3")["txt"]
    assert num(GAP, t) == pytest.approx(0.0418, abs=2e-4)

def test_bader_refinamento_melhora():
    pytest.importorskip("pybader")
    import brumare as B
    from pybader.interface import Bader
    from pybader.io import vasp
    import io, contextlib
    fn, q = _bader_brumare()
    pm = pytest.importorskip("pymatgen.io.vasp"); s = pm.Chgcar.from_file(fn).structure
    st = dict(lat=s.lattice.matrix, f=s.frac_coords % 1.0, sp=[str(x.specie) for x in s], label=[str(i) for i in range(len(s))])
    q0 = np.asarray(B.bader_ongrid(B.read_chgcar(fn), st, refinar=False)["q"])
    with contextlib.redirect_stdout(io.StringIO()):
        bd = Bader(*vasp.read(fn)); bd()
    qp = np.asarray(bd.atoms_charge)
    assert np.mean(np.abs(q - qp)) < 0.002 < np.mean(np.abs(q0 - qp))       # refinado ≈ referência; on-grid não

def test_bader_contra_pybader():
    pytest.importorskip("pybader")
    from pybader.interface import Bader
    from pybader.io import vasp
    fn, q = _bader_brumare()
    bd = Bader(*vasp.read(fn)); bd()
    assert np.mean(np.abs(q - np.asarray(bd.atoms_charge))) < 0.05             # on-grid × refinamento de bordas

# ------------------------------------------------------------------ comparação com ferramentas consolidadas
def test_vasp_si_contra_pymatgen(caso):
    pm = pytest.importorskip("pymatgen.io.vasp")
    d = os.path.join(DADOS, "vasp_Si_bands")
    bs = pm.Vasprun(os.path.join(d, "vasprun.xml"), parse_projected_eigen=False).get_band_structure(
        kpoints_filename=os.path.join(d, "KPOINTS"), line_mode=True)
    assert num(GAP, caso("vasp_si", "vasp_Si_bands", None)["txt"]) == pytest.approx(bs.get_band_gap()["energy"], abs=1e-4)

def test_castep_contra_sumo_contagem_de_eletrons(caso):
    pytest.importorskip("sumo")
    from sumo.io.castep import band_structure
    from pymatgen.electronic_structure.core import Spin
    t = caso("castep", "mgh2_Fe", "castep_MgH2_Fe")["txt"]
    bs = band_structure(os.path.join(DADOS, "castep_MgH2_Fe", "mgh2_Fe.bands"))
    ne = [int(x) for x in re.findall(r"eletrons = (\d+)", t)][:2]
    vb = max(np.max(bs.bands[s][n - 1]) for s, n in zip((Spin.up, Spin.down), ne))
    cb = min(np.min(bs.bands[s][n]) for s, n in zip((Spin.up, Spin.down), ne))
    assert num(GAP_TOT, t) == pytest.approx(cb - vb, abs=2e-4)                 # mesma leitura dos autovalores
    assert bs.efermi == pytest.approx(num(EF, t), abs=1e-4)

def test_orca_contra_cclib(caso):
    cclib = pytest.importorskip("cclib")
    cd = cclib.io.ccread(os.path.join(DADOS, "orca", "dvb_sp.out"))
    h = int(cd.homos[0]); mo = np.asarray(cd.moenergies[0])
    t = caso("orca", "dvb_sp.out", "orca")["txt"]
    assert num(r"HOMO = ([\d.\-]+) eV", t) == pytest.approx(mo[h], abs=1e-3)
    assert num(r"LUMO = ([\d.\-]+) eV", t) == pytest.approx(mo[h + 1], abs=1e-3)

# ------------------------------------------------------------------ interface
@pytest.mark.parametrize("lang,txt", [("en", "show this help message"), ("la", "hoc auxilium ostendit"), ("pt", "mostra autor")])
def test_ajuda_traduzida(lang, txt):
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "brumare.py"), "--idioma", lang, "-h"], capture_output=True, text=True)
    assert r.returncode == 0 and txt in r.stdout

def test_sobre_frase_em_latim():
    for lang in ("pt", "en", "fr"):
        r = subprocess.run([sys.executable, os.path.join(RAIZ, "brumare.py"), "--idioma", lang, "--sobre"], capture_output=True, text=True)
        assert "necessitates suas" in r.stdout                                 # a frase do autor fica sempre em latim

# ------------------------------------------------------------------ zona de Brillouin
def _bz(rede, **kw):
    sys.argv = ["x"]
    import brumare as B
    A, _ = B.bz_ideal(B.bz_rede_texto(rede))
    Z = B.bz_compute(A); C = B.bz_classify(Z); pts, seg = B.bz_path(Z, C)
    return B, Z, C, pts, seg

@pytest.mark.parametrize("rede,tipo,nf,nv", [("fcc 5.431", "FCC", 14, 24), ("bcc 2.8665", "BCC", 12, 14), ("hex 3.209 5.211", "HEX", 8, 12),
                                            ("tet 4.501 3.010", "TET", 6, 8), ("sc 3.359", "CUB", 6, 8), ("orc 10.46 12.87 24.49", "ORC", 6, 8)])
def test_zona_brillouin_redes(rede, tipo, nf, nv):
    B, Z, C, pts, seg = _bz(rede)
    assert C["tipo"] == tipo and len(Z["faces"]) == nf and len(Z["verts"]) == nv
    assert Z["vol"] == pytest.approx((2 * np.pi) ** 3 / abs(Z["V"]), rel=1e-6)        # V_ZB = (2π)³/V

def test_zona_brillouin_fcc_pontos():
    B, Z, C, pts, seg = _bz("fcc 5.431")
    k = {p["L"]: np.linalg.norm(p["k"]) for p in pts}
    a = 5.431
    assert k["X"] == pytest.approx(2 * np.pi / a, rel=1e-9) and k["L"] == pytest.approx(np.sqrt(3) * np.pi / a, rel=1e-9)
    assert k["W"] == pytest.approx(np.sqrt(5) * np.pi / a, rel=1e-9) and k["K"] == pytest.approx(3 * np.sqrt(2) * np.pi / (2 * a), rel=1e-9)

def test_zona_brillouin_triclinica_generica():
    B, Z, C, pts, seg = _bz("4.1 5.3 6.2 78 85 103")
    assert C["tipo"] == "generica" and Z["vol"] == pytest.approx(Z["VBZ"], rel=1e-6)

def test_zona_brillouin_supercelula_mgh2(caso):
    d = caso("zb_mgh2", "mgh2_Fe", "castep_MgH2_Fe", "--zona-brillouin")["dir"]
    t = open(os.path.join(d, "mgh2_Fe_zona_brillouin.txt"), encoding="utf-8").read()
    if "Grupo espacial" in t:                                                  # com moyo: simetria real da supercélula com defeito
        assert "C m m m (n. 65" in t and "(ORCC)" in t
    else:                                                                      # sem moyo: idealização geométrica da rede
        assert "(TET)" in t and "γ: 89.7483 -> 90.0000" in t
    for f in ("kpath_castep.cell", "KPOINTS_bandas", "kpath_qe.in", "kpath_siesta.fdf", "zona_brillouin.json"):
        assert os.path.exists(os.path.join(d, "mgh2_Fe_" + f))

# ------------------------------------------------------------------ estruturas e simetria (moyo)
EST = os.path.join(DADOS, "estruturas")

@pytest.mark.parametrize("nome", ["Si", "NaCl", "TiO2_rutilo", "Mg", "ZnO", "In", "Bi2Se3"])
@pytest.mark.parametrize("ext", ["cif", "vasp"])
def test_estrutura_e_grupo_espacial(nome, ext):
    pytest.importorskip("moyopy")
    import json
    sys.argv = ["x"]
    import brumare as B
    ref = json.load(open(os.path.join(EST, "referencia.json")))[nome]
    st = B.ler_estrutura(os.path.join(EST, f"{nome}.{ext}"))
    assert len(st["sp"]) == ref["nat"]                                         # CIF simetrizado expandido corretamente
    assert B.simetria(st)["numero"] == ref["sg"]

def test_biblioteca_literatura_grupos():
    pytest.importorskip("moyopy")
    import json
    sys.argv = ["x"]
    import brumare as B
    J = json.load(open(os.path.join(RAIZ, "estruturas_literatura.json"), encoding="utf-8"))
    CT = {"P": [[0, 0, 0]], "F": [[0, 0, 0], [0, .5, .5], [.5, 0, .5], [.5, .5, 0]], "I": [[0, 0, 0], [.5, .5, .5]], "R": [[0, 0, 0], [2/3, 1/3, 1/3], [1/3, 2/3, 2/3]]}
    for m in J["materiais"]:
        r = m["rede"]; lat = B.bz_lat_par(r[1], r[1] if r[0] != "orc" else r[2], r[-1] if r[0] != "cub" else r[1], 90, 90, 120 if r[0] == "hex" else 90)
        f, sp = [], []
        for el, p in m["sites"]:
            for t in CT[m["centr"]]:
                x = (np.array(p) + t) % 1.0
                if not any(np.linalg.norm(((x - y) + .5) % 1 - .5) < 1e-4 for y in f):
                    f.append(x); sp.append(el)
        assert B.simetria(dict(lat=lat, f=np.array(f), sp=sp))["numero"] == m["sg"], m["nome"]

@pytest.mark.parametrize("nome,tipo", [("In", "BCT2"), ("Bi2Se3", "RHL1")])
def test_bct_rhl_pontos_na_superficie(nome, tipo):
    pytest.importorskip("moyopy")
    sys.argv = ["x"]
    import brumare as B
    st = B.ler_estrutura(os.path.join(EST, f"{nome}.cif"))
    Z, C, notas, d = B.bz_completo(st["lat"], st)
    assert C["tipo"] == tipo
    G = np.array([f["g"] for f in Z["faces"]])
    for k, v in C["P"].items():
        if k != "Γ":
            assert abs(np.max(G @ v[0] / ((G * G).sum(1) / 2)) - 1) < 1e-6, k   # todo ponto na superfície da zona

def test_cli_estrutura(tmp_path):
    pytest.importorskip("moyopy")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "brumare.py"), "--estrutura", os.path.join(EST, "Bi2Se3.cif"), "--outdir", str(tmp_path)],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-1500:]
    t = open(tmp_path / "Bi2Se3_zona_brillouin.txt", encoding="utf-8").read()
    assert "R -3 m (n. 166" in t and "(RHL1)" in t
    for f in ("celula_primitiva.POSCAR", "celula_primitiva.cif", "celula_convencional.cell", "celula_primitiva.qe.in", "kpath_castep.cell"):
        assert (tmp_path / f"Bi2Se3_{f}").exists()

# ------------------------------------------------------------------ as 14 redes de Bravais (25 casos de Setyawan–Curtarolo)
REDES = {"Si": "FCC", "NaCl": "FCC", "TiO2_rutilo": "TET", "Mg": "HEX", "ZnO": "HEX", "In": "BCT2", "Bi2Se3": "RHL1", "ORCF1": "ORCF1", "ORCF2": "ORCF2",
         "ORCF3": "ORCF3", "ORCI": "ORCI", "MCL": "MCL", "MCLC_a": "MCLC1", "MCLC2": "MCLC2", "MCLC_b": "MCLC3", "MCLC5": "MCLC5", "TRI_a": "TRI1a", "TRI1b": "TRI1b"}

@pytest.mark.parametrize("nome,tipo", list(REDES.items()))
def test_redes_bravais_tipo_e_superficie(nome, tipo):
    pytest.importorskip("moyopy")
    sys.argv = ["x"]
    import brumare as B
    st = B.ler_estrutura(os.path.join(EST, f"{nome}.cif"))
    Z, C, notas, d = B.bz_completo(st["lat"], st)
    assert C["tipo"] == tipo
    G = np.array([f["g"] for f in Z["faces"]])
    for k, v in C["P"].items():
        if k != "Γ":
            assert abs(np.max(G @ v[0] / ((G * G).sum(1) / 2)) - 1) < 1e-6, k

@pytest.mark.parametrize("nome", [n for n, t in REDES.items() if t not in ("ORCF3", "TRI1a", "TRI1b")])
def test_redes_contra_pymatgen(nome):
    """|k| de cada ponto igual ao do pymatgen (KPathSetyawanCurtarolo); ORCF3 (fronteira) e TRI (base reduzida não única) ficam de fora."""
    pytest.importorskip("moyopy"); pytest.importorskip("pymatgen")
    from pymatgen.core import Structure, Lattice
    from pymatgen.symmetry.kpath import KPathSetyawanCurtarolo
    sys.argv = ["x"]
    import brumare as B
    st = B.ler_estrutura(os.path.join(EST, f"{nome}.cif")); Z, C, notas, d = B.bz_completo(st["lat"], st)
    kp = KPathSetyawanCurtarolo(Structure(Lattice(st["lat"]), st["sp"], st["f"]), symprec=0.01); Bp = kp.prim_rec.matrix
    pm = {L.replace("\\Gamma", "Γ").replace("\\Sigma", "Σ").replace("_", ""): np.linalg.norm(np.array(v) @ Bp) for L, v in kp.kpath["kpoints"].items()}
    for L, v in C["P"].items():
        assert L in pm and np.linalg.norm(v[0]) == pytest.approx(pm[L], abs=1e-8), L
