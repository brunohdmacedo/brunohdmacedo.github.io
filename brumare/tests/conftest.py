# SPDX-License-Identifier: GPL-3.0-or-later
"""Funções comuns da suíte de testes: roda a linha de comando do BrUMaRe uma vez por caso e lê o resumo."""
import os, re, subprocess, sys
import pytest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "tests", "data")
sys.path.insert(0, RAIZ)
_CACHE = {}


def rodar(alvo, cwd, *extra, outdir):
    cmd = [sys.executable, os.path.join(RAIZ, "brumare.py"), alvo, "--outdir", str(outdir), "--quiet", "--no-fatbands", "--no-defect", *extra]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900)
    assert r.returncode == 0, r.stderr[-2000:]
    res = [f for f in os.listdir(outdir) if f.endswith("_resumo.txt")]
    return dict(txt=open(os.path.join(outdir, res[0]), encoding="utf-8").read() if res else "", stdout=r.stdout, dir=str(outdir))


@pytest.fixture(scope="session")
def caso(tmp_path_factory):
    """caso(nome, alvo, pasta, *opções) -> dict com o resumo; cada combinação roda uma vez por sessão."""
    def _f(nome, alvo, pasta, *extra):
        k = (nome, alvo, pasta, extra)
        if k not in _CACHE:
            _CACHE[k] = rodar(alvo, os.path.join(DADOS, pasta) if pasta else DADOS, *extra, outdir=tmp_path_factory.mktemp(nome))
        return _CACHE[k]
    return _f


def num(pad, txt, todos=False):
    v = [float(x) for x in re.findall(pad, txt)]
    return v if todos else (v[0] if v else None)


GAP = r"Gap banda N -> N\+1 no caminho = ([\d.]+) eV"
GAP_TOT = r"Gap considerando os dois spins = ([\d.]+) eV"
EF = r"E_F = [\d.\-]+ Ha = ([\d.\-]+) eV"
