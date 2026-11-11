#!/usr/bin/env python3
"""Atualiza data/citacoes.json com as citações de Bruno H. D. Macedo.

Fontes:
  * OpenAlex (gratuito, aberto), pelo ORCID 0000-0002-8152-0950;
  * Google Acadêmico pelo SerpApi (API oficial para dados do Scholar), se a
    variável de ambiente SERPAPI_KEY existir (secret do repositório).
O Google Acadêmico proíbe raspagem direta; por isso não há scraping aqui.
Se uma fonte falhar, os valores anteriores dessa fonte são mantidos.
Roda no GitHub Actions (.github/workflows/citacoes.yml) ou localmente:
    SERPAPI_KEY=... python3 scripts/atualizar_citacoes.py
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

ORCID = "0000-0002-8152-0950"
SCHOLAR_ID = "zl-LdTMAAAAJ"
MAILTO = "brunohdmacedo@gmail.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "citacoes.json")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"brunohdmacedo.tech citacoes (mailto:{MAILTO})"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def openalex():
    a = get(f"https://api.openalex.org/authors/orcid:{ORCID}?mailto={MAILTO}")
    w = get(f"https://api.openalex.org/works?filter=author.orcid:{ORCID}&per-page=200"
            f"&select=display_name,doi,cited_by_count,publication_year&mailto={MAILTO}")
    s = a.get("summary_stats") or {}
    return {"citacoes": a.get("cited_by_count"), "h": s.get("h_index"), "i10": s.get("i10_index"),
            "por_ano": {str(x["year"]): x["cited_by_count"] for x in a.get("counts_by_year", [])},
            "trabalhos": [{"titulo": x.get("display_name"), "doi": x.get("doi"), "citacoes": x.get("cited_by_count"),
                           "ano": x.get("publication_year")} for x in w.get("results", [])]}


def scholar(key):
    q = urllib.parse.urlencode({"engine": "google_scholar_author", "author_id": SCHOLAR_ID, "hl": "pt-BR",
                                "num": 100, "api_key": key})
    d = get(f"https://serpapi.com/search.json?{q}")
    if d.get("error"):
        raise RuntimeError(d["error"])
    tab = {}
    for row in (d.get("cited_by") or {}).get("table", []):
        for k, v in row.items():
            tab[k] = v.get("all") if isinstance(v, dict) else v
    return {"citacoes": tab.get("citations"), "h": tab.get("h_index"), "i10": tab.get("i10_index"),
            "por_ano": {str(g["year"]): g["citations"] for g in (d.get("cited_by") or {}).get("graph", [])},
            "artigos": [{"titulo": x.get("title"), "citacoes": (x.get("cited_by") or {}).get("value") or 0,
                         "ano": x.get("year"), "link": x.get("link")} for x in d.get("articles", [])]}


def main():
    old = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
        except ValueError:
            old = {}
    new = {"atualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "orcid": ORCID, "scholar_id": SCHOLAR_ID,
           "openalex": old.get("openalex"), "scholar": old.get("scholar"), "avisos": []}
    try:
        new["openalex"] = openalex()
        print(f"OpenAlex: {new['openalex']['citacoes']} citações, h = {new['openalex']['h']}")
    except Exception as e:
        new["avisos"].append(f"OpenAlex indisponível: {e}"); print("AVISO OpenAlex:", e, file=sys.stderr)
    key = os.environ.get("SERPAPI_KEY", "").strip()
    if key:
        try:
            new["scholar"] = scholar(key)
            print(f"Google Acadêmico: {new['scholar']['citacoes']} citações, h = {new['scholar']['h']}")
        except Exception as e:
            new["avisos"].append(f"Google Acadêmico (SerpApi) indisponível: {e}"); print("AVISO Scholar:", e, file=sys.stderr)
    else:
        new["avisos"].append("SERPAPI_KEY não configurada: só OpenAlex.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
    print("->", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
