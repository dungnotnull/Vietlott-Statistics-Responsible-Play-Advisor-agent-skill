#!/usr/bin/env python3
"""
Real draw-result ingestion for the Vietlott skill.

Reads the active source(s) for each game from config/ingestion.json, fetches/reads
the raw draws, normalizes them to the schema in data/results.schema.json, validates
per-game invariants, dedupes by draw_id, sorts by draw_date, and writes
data/results/<game>.jsonl.

Supported source types:
  - synthetic   : faithful simulator (scripts/generate_synthetic_results.py) - CI fixture
  - csv_file    : real CSV at data/raw/<game>.csv (operator-supplied from official results)
  - jsonl_file  : real JSONL at data/raw/<game>.jsonl
  - http_json   : real HTTP JSON endpoint ({draws:[{date,numbers:[...],bonus?}]})
  - manual      : a literal list embedded in config (for small ad-hoc real datasets)

Real data (csv_file/jsonl_file/http_json/manual) ALWAYS takes precedence over the
synthetic fixture when active. The synthetic source is labeled source="synthetic"
and is never presented as real history.

Usage:
    python scripts/ingest_results.py                 # ingest all games (active sources)
    python scripts/ingest_results.py mega_6_45       # one game
    python scripts/ingest_results.py --list          # show configured sources
"""

from __future__ import annotations

import csv
import json
import os
import ssl
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

import generate_synthetic_results as syn

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RESULTS_DIR = DATA_DIR / "results"


def _load_ingestion_config() -> Dict:
    return json.loads((CONFIG_DIR / "ingestion.json").read_text(encoding="utf-8-sig"))


# ----------------------------- per-game validation -----------------------------

def _validate_draw(d: Dict, game: str) -> None:
    if d.get("game") != game:
        raise ValueError(f"draw {d.get('draw_id')}: game={d.get('game')} != {game}")
    if not d.get("draw_id"):
        raise ValueError("draw missing draw_id")
    src = d.get("source")
    if src not in ("synthetic", "official_csv", "http_json", "jsonl_file", "manual"):
        raise ValueError(f"draw {d['draw_id']}: bad source {src!r}")
    nums = d.get("numbers") or []
    bonus = d.get("bonus")
    three = d.get("three_digit")

    if game == "mega_6_45":
        if not (len(nums) == 6 and len(set(nums)) == 6 and all(1 <= n <= 45 for n in nums)):
            raise ValueError(f"draw {d['draw_id']}: mega numbers invalid: {nums}")
        if nums != sorted(nums):
            raise ValueError(f"draw {d['draw_id']}: mega numbers not sorted")
        if bonus is not None:
            raise ValueError(f"draw {d['draw_id']}: mega must have bonus null")
    elif game == "power_6_55":
        if not (len(nums) == 6 and len(set(nums)) == 6 and all(1 <= n <= 55 for n in nums)):
            raise ValueError(f"draw {d['draw_id']}: power numbers invalid: {nums}")
        if nums != sorted(nums):
            raise ValueError(f"draw {d['draw_id']}: power numbers not sorted")
        if bonus is None or not (1 <= bonus <= 55) or bonus in nums:
            raise ValueError(f"draw {d['draw_id']}: power bonus invalid: {bonus}")
    elif game == "keno":
        if not (len(nums) == 20 and len(set(nums)) == 20 and all(1 <= n <= 80 for n in nums)):
            raise ValueError(f"draw {d['draw_id']}: keno numbers invalid")
        if nums != sorted(nums):
            raise ValueError(f"draw {d['draw_id']}: keno numbers not sorted")
        if bonus is not None:
            raise ValueError(f"draw {d['draw_id']}: keno must have bonus null")
    elif game == "max_3d":
        if nums != []:
            raise ValueError(f"draw {d['draw_id']}: max3d numbers must be empty")
        if not (isinstance(three, str) and len(three) == 3 and three.isdigit()):
            raise ValueError(f"draw {d['draw_id']}: max3d three_digit invalid: {three!r}")
        if bonus is not None:
            raise ValueError(f"draw {d['draw_id']}: max3d must have bonus null")


def _norm(game: str, draw_id: str, source: str, numbers, bonus=None, three_digit=None, draw_date=None) -> Dict:
    d = {
        "game": game,
        "draw_id": draw_id,
        "source": source,
        "draw_date": draw_date,
        "numbers": sorted(numbers) if numbers else [],
        "bonus": bonus,
        "three_digit": three_digit,
        "extra": {},
    }
    _validate_draw(d, game)
    return d


# ----------------------------- source handlers -----------------------------

def _from_synthetic(spec: Dict, game: str) -> List[Dict]:
    count = int(spec.get("count", 1000))
    seed = int(spec.get("seed", 20260810))
    label = spec.get("source_label", "synthetic")
    draws = syn.generate(game, count, seed)
    out = []
    for d in draws:
        nd = d.to_dict()
        nd["source"] = label
        _validate_draw(nd, game)
        out.append(nd)
    return out


def _from_csv(spec: Dict, game: str) -> List[Dict]:
    path = ROOT / spec["path"]
    if not path.exists():
        raise FileNotFoundError(f"csv_file source missing: {path}")
    label = spec.get("source_label", "official_csv")
    out = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            date = (row.get("date") or "").strip() or None
            did = (row.get("draw_id") or f"{game}-csv-{i:06d}").strip()
            if game == "max_3d":
                three = (row.get("three_digit") or "").strip().zfill(3)
                out.append(_norm(game, did, label, [], None, three, date))
            else:
                nfields = [row[k] for k in sorted(k for k in row if k.startswith("n") and k[1:].isdigit())]
                nums = [int(x) for x in nfields if str(x).strip() != ""]
                bonus = None
                if "bonus" in row and row["bonus"].strip() != "":
                    bonus = int(row["bonus"])
                out.append(_norm(game, did, label, nums, bonus, None, date))
    return out


def _from_jsonl(spec: Dict, game: str) -> List[Dict]:
    path = ROOT / spec["path"]
    if not path.exists():
        raise FileNotFoundError(f"jsonl_file source missing: {path}")
    label = spec.get("source_label", "jsonl_file")
    out = []
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            d["source"] = label
            _validate_draw(d, game)
            out.append(d)
    return out


def _from_manual(spec: Dict, game: str) -> List[Dict]:
    label = spec.get("source_label", "manual")
    out = []
    for i, raw in enumerate(spec.get("draws", []), 1):
        d = _norm(
            game,
            raw.get("draw_id", f"{game}-manual-{i:06d}"),
            label,
            raw.get("numbers", []),
            raw.get("bonus"),
            raw.get("three_digit"),
            raw.get("draw_date"),
        )
        out.append(d)
    return out


def _http_get_json(url: str, timeout: int, retries: int, backoff_base: int) -> Dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    last = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "vietlott-skill-ingest/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < retries:
                time.sleep((backoff_base * (2 ** (attempt - 1))) / 1000.0)
    raise RuntimeError(f"HTTP fetch failed after {retries} attempts: {url} -> {last}")


def _from_http_json(spec: Dict, game: str, defaults: Dict) -> List[Dict]:
    url = spec["url"]
    label = spec.get("source_label", "http_json")
    timeout = int(spec.get("timeout", defaults.get("request_timeout_seconds", 15)))
    retries = int(spec.get("max_retries", defaults.get("max_retries", 3)))
    backoff = int(spec.get("backoff_base_ms", defaults.get("backoff_base_ms", 500)))
    data = _http_get_json(url, timeout, retries, backoff)
    items = data.get("draws", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError(f"http_json {url}: expected a list or {{draws:[...]}}, got {type(items)}")
    out = []
    for i, raw in enumerate(items, 1):
        nums = raw.get("numbers", [])
        bonus = raw.get("bonus")
        three = raw.get("three_digit")
        if game == "max_3d" and three is None and "three_digit" not in raw and "value" in raw:
            three = str(raw["value"]).zfill(3)
        d = _norm(
            game,
            raw.get("draw_id", f"{game}-http-{i:06d}"),
            label,
            nums,
            bonus,
            three,
            raw.get("draw_date") or raw.get("date"),
        )
        out.append(d)
    return out


_HANDLERS = {
    "synthetic": _from_synthetic,
    "csv_file": _from_csv,
    "jsonl_file": _from_jsonl,
    "manual": _from_manual,
    "http_json": _from_http_json,
}


# ----------------------------- orchestration -----------------------------

def ingest_game(game: str, config: Optional[Dict] = None) -> Dict:
    config = config or _load_ingestion_config()
    sources = config["sources"].get(game)
    if not sources:
        raise ValueError(f"no sources configured for game {game}")
    active = [s for s in sources if s.get("active")]
    if not active:
        raise ValueError(f"no active source for game {game}; set active:true in config/ingestion.json")
    defaults = config.get("defaults", {})

    all_draws: List[Dict] = []
    used_sources: List[str] = []
    for spec in active:
        handler = _HANDLERS.get(spec["type"])
        if not handler:
            raise ValueError(f"unknown source type: {spec['type']}")
        if spec["type"] == "http_json":
            draws = handler(spec, game, defaults)
        else:
            draws = handler(spec, game)
        all_draws.extend(draws)
        used_sources.append(f"{spec['type']}({len(draws)})")

    # Dedupe by draw_id (last wins), preserve order, then sort by date (nulls last/stable).
    by_id: Dict[str, Dict] = {}
    for d in all_draws:
        by_id[d["draw_id"]] = d
    deduped = list(by_id.values())
    deduped.sort(key=lambda d: (d.get("draw_date") is None, d.get("draw_date") or ""))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"{game}.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for d in deduped:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    # Provenance report.
    provenance = {}
    for d in deduped:
        provenance[d["source"]] = provenance.get(d["source"], 0) + 1
    return {
        "game": game,
        "out_path": str(out_path),
        "count": len(deduped),
        "sources_used": used_sources,
        "provenance": provenance,
        "has_real_data": any(k != "synthetic" for k in provenance),
    }


def ingest_all(config: Optional[Dict] = None) -> List[Dict]:
    config = config or _load_ingestion_config()
    return [ingest_game(g, config) for g in config["sources"].keys()]


def list_sources(config: Optional[Dict] = None) -> None:
    config = config or _load_ingestion_config()
    for game, sources in config["sources"].items():
        print(f"\n{game}:")
        for s in sources:
            mark = "ACTIVE" if s.get("active") else "       "
            extra = s.get("path") or s.get("url") or f"count={s.get('count')}"
            print(f"  [{mark}] {s['type']:<10} {extra}  label={s.get('source_label')}")


def main() -> None:
    args = sys.argv[1:]
    if "--list" in args:
        list_sources()
        return
    games = [a for a in args if not a.startswith("-")]
    reports = []
    for g in (games or [None]):
        if g is None:
            reports.extend(ingest_all())
        else:
            reports.append(ingest_game(g))
    print("Ingestion complete:")
    for r in reports:
        flag = "REAL" if r["has_real_data"] else "synthetic-fixture"
        print(f"  {r['game']:<11} {r['count']:>5} draws -> {r['out_path']}  [{flag}]  sources={r['sources_used']}")


if __name__ == "__main__":
    main()
