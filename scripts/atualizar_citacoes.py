#!/usr/bin/env python3
"""Atualiza métricas bibliométricas via OpenAlex e, opcionalmente, Google Scholar/SerpApi."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "citacoes.json"
ORCID = os.getenv("ORCID", "0000-0002-8152-0950")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()
SERPAPI_AUTHOR_ID = os.getenv("SERPAPI_AUTHOR_ID", "").strip()
OPENALEX_MAILTO = os.getenv("OPENALEX_MAILTO", "").strip()

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "PortfolioCitationUpdater/1.0 (academic portfolio; mailto: "
                  + (OPENALEX_MAILTO or "not-provided") + ")"
})


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_doi(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value)
    return value.strip()


def normalize_title(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def load_previous() -> dict[str, Any]:
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema_version": 1,
        "orcid": ORCID,
        "updated_at": None,
        "sources": {},
        "metrics": {},
        "publications": [],
        "warnings": [],
    }


def get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = SESSION.get(url, params=params, timeout=45)
    response.raise_for_status()
    return response.json()


def fetch_openalex() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Obtém os trabalhos associados ao ORCID usando a API pública do OpenAlex."""
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"authorships.author.orcid:https://orcid.org/{ORCID}",
        "per-page": 200,
        "sort": "publication_date:desc",
    }
    if OPENALEX_MAILTO:
        params["mailto"] = OPENALEX_MAILTO

    works: list[dict[str, Any]] = []
    cursor = "*"
    while cursor:
        page_params = dict(params)
        page_params["cursor"] = cursor
        payload = get_json(url, page_params)
        results = payload.get("results", [])
        works.extend(results)
        cursor = payload.get("meta", {}).get("next_cursor")
        if not results or len(works) >= 2000:
            break

    publications = []
    for work in works:
        doi = normalize_doi(work.get("doi"))
        title = work.get("title") or ""
        if not title:
            continue
        publications.append({
            "openalex_id": work.get("id"),
            "doi": doi or None,
            "title": title,
            "year": work.get("publication_year"),
            "type": work.get("type"),
            "url": work.get("doi") or work.get("id"),
            "cited_by_count": int(work.get("cited_by_count") or 0),
        })

    author_info = {
        "works_found": len(publications),
        "orcid": ORCID,
        "status": "ok",
    }
    return publications, author_info


def fetch_scholar() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Consulta perfil público do Google Scholar via SerpApi, se configurado."""
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY não configurada; fonte opcional ignorada.")
    if not SERPAPI_AUTHOR_ID:
        raise RuntimeError(
            "SERPAPI_AUTHOR_ID não configurado. Informe o ID do perfil público do Google Acadêmico."
        )

    payload = get_json("https://serpapi.com/search.json", {
        "engine": "google_scholar_author",
        "author_id": SERPAPI_AUTHOR_ID,
        "api_key": SERPAPI_KEY,
        "hl": "pt-br",
    })
    articles = payload.get("articles", [])
    publications = []
    for article in articles:
        cited = article.get("cited_by") or {}
        publications.append({
            "title": article.get("title") or "",
            "year": article.get("year"),
            "cited_by_count": int(cited.get("value") or 0),
            "scholar_url": cited.get("link"),
        })
    if not publications:
        raise RuntimeError("SerpApi não retornou artigos para o perfil informado.")
    return publications, {"status": "ok", "works_found": len(publications)}


def match_scholar(openalex_items: list[dict[str, Any]],
                  scholar_items: list[dict[str, Any]]) -> dict[str, int]:
    """Associa os registros pelo título normalizado; não inventa correspondências."""
    index = {normalize_title(item["title"]): item for item in scholar_items if item.get("title")}
    matched: dict[str, int] = {}
    for item in openalex_items:
        key = normalize_title(item.get("title"))
        candidate = index.get(key)
        if candidate:
            matched[key] = int(candidate.get("cited_by_count") or 0)
    return matched


def h_index(values: list[int]) -> int:
    ordered = sorted((max(0, int(v)) for v in values), reverse=True)
    return sum(1 for position, citations in enumerate(ordered, start=1)
               if citations >= position)


def main() -> int:
    previous = load_previous()
    warnings: list[str] = []
    publications = previous.get("publications", [])
    sources = previous.get("sources", {})

    # OpenAlex: mantém os dados anteriores caso a consulta falhe.
    try:
        openalex_items, openalex_status = fetch_openalex()
        publications = openalex_items
        sources["openalex"] = {
            **openalex_status,
            "updated_at": now_iso(),
            "total_citations": sum(p["cited_by_count"] for p in publications),
            "h_index": h_index([p["cited_by_count"] for p in publications]),
        }
    except Exception as exc:
        warnings.append(f"OpenAlex: {exc}")
        sources.setdefault("openalex", {"status": "stale"})
        sources["openalex"]["status"] = "stale"

    # Scholar: opcional; se indisponível, mantém os valores anteriores.
    scholar_map: dict[str, int] = {}
    try:
        if SERPAPI_KEY and SERPAPI_AUTHOR_ID:
            scholar_items, scholar_status = fetch_scholar()
            scholar_map = match_scholar(publications, scholar_items)
            sources["google_scholar"] = {
                **scholar_status,
                "updated_at": now_iso(),
                "matched_publications": len(scholar_map),
                "total_citations_matched": sum(scholar_map.values()),
                "h_index_matched": h_index(list(scholar_map.values())),
            }
        elif SERPAPI_KEY or SERPAPI_AUTHOR_ID:
            raise RuntimeError("Configure SERPAPI_KEY e SERPAPI_AUTHOR_ID juntos.")
        else:
            sources.setdefault("google_scholar", {"status": "not_configured"})
    except Exception as exc:
        warnings.append(f"Google Acadêmico/SerpApi: {exc}")
        sources.setdefault("google_scholar", {"status": "stale"})
        sources["google_scholar"]["status"] = "stale"

    # Preserva contagens Scholar anteriores por DOI/título se a fonte falhar.
    old_by_key = {}
    for item in previous.get("publications", []):
        old_by_key[normalize_doi(item.get("doi")) or normalize_title(item.get("title"))] = item

    for item in publications:
        key = normalize_doi(item.get("doi")) or normalize_title(item.get("title"))
        old = old_by_key.get(key, {})
        title_key = normalize_title(item.get("title"))
        item["citations"] = {
            "openalex": int(item.get("cited_by_count") or 0),
            "google_scholar": scholar_map.get(
                title_key, (old.get("citations") or {}).get("google_scholar")
            ),
        }

    openalex_values = [int(p.get("citations", {}).get("openalex") or 0)
                       for p in publications]
    scholar_values = [p["citations"]["google_scholar"]
                      for p in publications
                      if p.get("citations", {}).get("google_scholar") is not None]

    output = {
        "schema_version": 1,
        "orcid": ORCID,
        "updated_at": now_iso(),
        "sources": sources,
        "metrics": {
            "publications": len(publications),
            "openalex": {
                "total_citations": sum(openalex_values),
                "h_index": h_index(openalex_values),
            },
            "google_scholar": {
                "matched_publications": len(scholar_values),
                "total_citations": sum(scholar_values) if scholar_values else None,
                "h_index": h_index(scholar_values) if scholar_values else None,
            },
        },
        "publications": publications,
        "warnings": warnings,
    }

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    print(f"Arquivo atualizado: {DATA_FILE}")
    print(f"Publicações: {len(publications)}")
    print(f"Citações OpenAlex: {sum(openalex_values)} | índice h: {h_index(openalex_values)}")
    if warnings:
        print("Avisos:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
