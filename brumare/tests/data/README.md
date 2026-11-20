# Dados de teste do BrUMaRe

Saídas reais usadas pelos testes automatizados (`tests/`) e pela comparação com outras ferramentas (`tools/comparar_ferramentas.py`).

| Pasta | Programa | Sistema | Origem | Licença |
|---|---|---|---|---|
| `castep_MgH2_Fe/` | CASTEP | MgH₂ com Fe substitucional (162 átomos, spin) | cálculos do autor | GPL-3.0-or-later (como o BrUMaRe) |
| `vasp_Si_bands/` | VASP | Si, bandas em linha (PBE) | arquivos de teste do pymatgen | MIT |
| `vasp_Fe2O3_ldau/` | VASP | Fe₂O₃ ferromagnético (LDA+U) | arquivos de teste do pymatgen | MIT |
| `siesta_SrTiO3/` | SIESTA | SrTiO₃ polarizado (LDA) | arquivos de teste do sisl (sisl-files) | MPL-2.0 |
| `qe_Si/` | Quantum ESPRESSO | Si, saída de referência | suíte de testes do Quantum ESPRESSO | GPL-2.0-or-later |
| `orca/` | ORCA | divinilbenzeno | dados de teste do cclib | BSD-3-Clause |
| `bader_MgH2_Fe/` | densidade (CHGCAR) | MgH₂ com Fe | cálculos do autor | GPL-3.0-or-later |

Confira as licenças de cada projeto de origem antes de redistribuir separadamente.
