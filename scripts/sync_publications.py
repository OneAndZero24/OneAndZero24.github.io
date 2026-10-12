#!/usr/bin/env python3
"""Synchronize publications from Google Scholar and merge manual overrides.

Pipeline
--------
1. Fetch the publication list from Google Scholar (author ``bTL7lzgAAAAJ``)
   either through SerpAPI (if ``SERPAPI_API_KEY`` is set) or through the
   ``scholarly`` package. The raw response is cached in
   ``data/scholar_cache.yaml``.
2. Merge the fetched list with the human-editable file
   ``data/publications_manual.yaml`` (overrides by Scholar id or title,
   plus manual-only entries).
3. Write ``data/publications.yaml``, which is consumed by the Hugo website
   (publications page and homepage) and by ``scripts/generate_cv.py``.

Usage
-----
    python3 scripts/sync_publications.py             # fetch + merge
    python3 scripts/sync_publications.py --offline   # merge from cache only
    python3 scripts/sync_publications.py --strict    # fail if the fetch fails

The script never deletes manual data: if Scholar is unreachable it falls back
to the committed cache, and if the cache is missing it still produces a file
from the manual entries.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MANUAL_PATH = DATA_DIR / "publications_manual.yaml"
CACHE_PATH = DATA_DIR / "scholar_cache.yaml"
OUTPUT_PATH = DATA_DIR / "publications.yaml"

ME = "Jan Miksa"
DEFAULT_SCHOLAR_ID = "bTL7lzgAAAAJ"

STATUS_LABELS = {
    "published": "Published",
    "accepted": "Accepted",
    "preprint": "Preprint",
    "under_review": "Under review",
    "thesis": "Thesis",
    "unpublished": "Unpublished",
}

ARXIV_RE = re.compile(r"arxiv[:\s]*preprint[:\s]*arxiv[:\s]*([0-9]{4}\.[0-9]{4,5})", re.I)
ARXIV_ID_RE = re.compile(r"([0-9]{4}\.[0-9]{4,5})")
YEAR_RE = re.compile(r"((?:19|20)[0-9]{2})\s*$")


def log(message: str) -> None:
    print(f"[sync] {message}")


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch_via_serpapi(scholar_id: str, api_key: str) -> list[dict]:
    params = {
        "engine": "google_scholar_author",
        "author_id": scholar_id,
        "num": "100",
        "api_key": api_key,
    }
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.load(response)

    items = []
    for article in payload.get("articles", []):
        items.append(
            {
                "scholar_id": article.get("citation_id", ""),
                "title": article.get("title", "").strip(),
                "authors_raw": article.get("authors", "").strip(),
                "venue_raw": article.get("publication", "").strip(),
                "year": to_int(article.get("year")),
                "num_citations": to_int((article.get("cited_by") or {}).get("value")),
                "pub_url": article.get("link", "") or "",
                "eprint_url": "",
            }
        )
    return items


def fetch_via_scholarly(scholar_id: str) -> list[dict]:
    # Imported dynamically: the package is only needed for online sync, so the
    # merge step still works with --offline when it is not installed.
    import importlib

    try:
        scholarly = importlib.import_module("scholarly")
    except ImportError as error:
        raise RuntimeError(
            "the 'scholarly' package is required for online sync; "
            "install scripts/requirements.txt or run with --offline"
        ) from error

    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["publications"])

    items = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        items.append(
            {
                "scholar_id": pub.get("author_pub_id", ""),
                "title": str(bib.get("title", "")).strip(),
                "authors_raw": str(bib.get("author", "")).strip(),
                "venue_raw": str(bib.get("venue", "")).strip(),
                "year": to_int(bib.get("pub_year")),
                "num_citations": to_int(pub.get("num_citations")),
                "pub_url": pub.get("pub_url", "") or "",
                "eprint_url": pub.get("eprint_url", "") or "",
            }
        )
    return items


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def to_int(value) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def slugify(title: str, max_words: int = 6) -> str:
    words = re.findall(r"[a-z0-9]+", title.lower())
    return "-".join(words[:max_words]) or "publication"


def normalize_author(name: str) -> str:
    name = name.strip().strip(",").strip()
    if name in {"...", "…", "others", "and others"}:
        return "et al."
    if re.fullmatch(r"J\.?\s*Miksa", name) or name == ME:
        return ME
    initials = re.fullmatch(r"([A-Z]{1,3})\s+(.*)", name)
    if initials:
        spaced = ". ".join(initials.group(1)) + ". " + initials.group(2)
        return spaced
    return name


def split_authors(authors_raw: str) -> list[str]:
    if not authors_raw:
        return []
    if " and " in authors_raw:
        parts = re.split(r"\s+and\s+", authors_raw)
    else:
        parts = authors_raw.split(",")
    authors = []
    for part in parts:
        name = normalize_author(part)
        if name and name not in authors:
            authors.append(name)
    return authors


def normalize_scholar_item(raw: dict) -> dict:
    title = raw.get("title", "").strip()
    venue_raw = raw.get("venue_raw", "").strip()
    year = to_int(raw.get("year"))
    status = "published"
    venue = venue_raw
    links = {}

    arxiv_match = ARXIV_RE.search(venue_raw)
    if arxiv_match:
        status = "preprint"
        venue = "arXiv preprint"
        links["paper"] = f"https://arxiv.org/abs/{arxiv_match.group(1)}"
    elif not venue_raw:
        status = "unpublished"
        venue = ""
    else:
        year_match = YEAR_RE.search(venue_raw)
        if year_match:
            venue = venue_raw[: year_match.start()].rstrip(", ").strip()
        if not year:
            year = to_int(year_match.group(1)) if year_match else 0

    if not links.get("paper"):
        paper_url = raw.get("eprint_url") or raw.get("pub_url")
        if paper_url:
            links["paper"] = paper_url

    item = {
        "id": slugify(title),
        "title": title,
        "authors": split_authors(raw.get("authors_raw", "")),
        "venue": venue,
        "status": status,
        "year": year,
        "citations": to_int(raw.get("num_citations")),
        "scholar_id": raw.get("scholar_id", ""),
        "links": links,
    }
    return item


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def merge(scholar_items: list[dict], manual: dict) -> list[dict]:
    overrides = manual.get("overrides") or []
    entries = manual.get("entries") or []

    by_scholar_id = {item["scholar_id"]: item for item in scholar_items if item.get("scholar_id")}
    by_title = {normalize_title(item["title"]): item for item in scholar_items}
    used_scholar_ids: set[str] = set()
    used_titles: set[str] = set()

    merged: list[dict] = []

    for override in overrides:
        base = None
        scholar_id = override.get("scholar_id")
        title_key = normalize_title(override["title"]) if override.get("title") else None
        if scholar_id and scholar_id in by_scholar_id:
            base = by_scholar_id[scholar_id]
        elif title_key and title_key in by_title:
            base = by_title[title_key]

        if base is not None:
            if base.get("scholar_id"):
                used_scholar_ids.add(base["scholar_id"])
            used_titles.add(normalize_title(base["title"]))

        item = dict(base) if base else {}
        for key, value in override.items():
            if value is not None:
                item[key] = value
        if not item.get("id"):
            item["id"] = slugify(item.get("title", "publication"))
        merged.append(item)

    for entry in entries:
        item = dict(entry)
        if not item.get("id"):
            item["id"] = slugify(item.get("title", "publication"))
        merged.append(item)

    for item in scholar_items:
        if item.get("scholar_id") in used_scholar_ids:
            continue
        if normalize_title(item["title"]) in used_titles:
            continue
        merged.append(item)

    # Finalize and deduplicate (a manual entry wins over a Scholar duplicate).
    finalized: list[dict] = []
    seen_titles: set[str] = set()
    for item in merged:
        if item.get("hidden"):
            continue
        title_key = normalize_title(item.get("title", ""))
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        item.setdefault("status_label", STATUS_LABELS.get(item.get("status", ""), ""))
        item["citations"] = to_int(item.get("citations"))
        item["year"] = to_int(item.get("year"))
        item.setdefault("links", {})
        finalized.append(item)

    def sort_key(item: dict):
        order = item.get("order")
        has_order = order is not None
        return (
            0 if has_order else 1,
            to_int(order) if has_order else 0,
            -to_int(item.get("year")),
            item.get("title", ""),
        )

    return sorted(finalized, key=sort_key)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--offline", action="store_true", help="do not fetch; merge from the cache")
    parser.add_argument("--strict", action="store_true", help="exit non-zero if the fetch fails")
    parser.add_argument("--scholar-id", default=None, help="Google Scholar author id (default: from manual file)")
    parser.add_argument("--manual", type=Path, default=MANUAL_PATH, help="path to the manual override file")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="path of the merged output file")
    args = parser.parse_args()

    manual = load_yaml(args.manual)
    scholar_id = args.scholar_id or os.environ.get("SCHOLAR_ID") or manual.get("scholar_id") or DEFAULT_SCHOLAR_ID

    cache = load_yaml(CACHE_PATH)
    cache_items_raw = cache.get("items") or []
    cache_fetched_at = cache.get("fetched_at") or ""

    fetched_items_raw: list[dict] | None = None
    fetch_source = ""
    fetch_error = ""

    if not args.offline:
        api_key = os.environ.get("SERPAPI_API_KEY", "").strip()
        try:
            if api_key:
                log("fetching publications from Google Scholar via SerpAPI")
                fetched_items_raw = fetch_via_serpapi(scholar_id, api_key)
                fetch_source = "serpapi"
            else:
                log("fetching publications from Google Scholar via scholarly")
                fetched_items_raw = fetch_via_scholarly(scholar_id)
                fetch_source = "scholarly"
            log(f"fetched {len(fetched_items_raw)} entries")
        except Exception as error:  # noqa: BLE001 - report and fall back to cache
            fetch_error = f"{type(error).__name__}: {error}"
            log(f"fetch failed: {fetch_error}")
            fetched_items_raw = None

    if fetched_items_raw is not None:
        cache_payload = {
            "fetched_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": fetch_source,
            "scholar_id": scholar_id,
            "items": fetched_items_raw,
        }
        with CACHE_PATH.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(cache_payload, handle, allow_unicode=True, sort_keys=False)
        log(f"wrote cache to {CACHE_PATH.relative_to(ROOT)}")
        raw_items = fetched_items_raw
        synced_at = cache_payload["fetched_at"]
    else:
        if args.strict:
            log("strict mode: refusing to continue without a fresh fetch")
            return 1
        if not cache_items_raw:
            log("no cache available; building the list from manual entries only")
        else:
            log(f"using cached Scholar data from {cache_fetched_at or 'unknown date'}")
        raw_items = cache_items_raw
        synced_at = cache_fetched_at

    scholar_items = [normalize_scholar_item(item) for item in raw_items if item.get("title")]
    items = merge(scholar_items, manual)

    output = {
        "scholar_id": scholar_id,
        "scholar_url": f"https://scholar.google.com/citations?user={scholar_id}",
        "scholar_synced_at": synced_at,
        "last_updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fetch_error": fetch_error,
        "items": items,
    }

    # Only rewrite the output when the actual content changed, so that
    # scheduled syncs do not create noise commits (and the "last updated"
    # date always reflects a real change).
    volatile_keys = ("scholar_synced_at", "last_updated", "fetch_error")
    existing = load_yaml(args.output)
    existing_content = {k: v for k, v in existing.items() if k not in volatile_keys}
    new_content = {k: v for k, v in output.items() if k not in volatile_keys}
    if existing_content and existing_content == new_content:
        log("no publication changes detected; output left untouched")
        return 0

    with args.output.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(output, handle, allow_unicode=True, sort_keys=False)

    log(f"wrote {len(items)} publications to {args.output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
