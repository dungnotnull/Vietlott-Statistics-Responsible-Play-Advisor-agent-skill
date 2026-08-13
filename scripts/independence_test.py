#!/usr/bin/env python3
"""
Statistical independence testing for Vietlott draw histories.

Reads ingested draws from data/results/<game>.jsonl and runs REAL statistical
tests that *demonstrate* (not merely assert) that historical draw-frequency
analysis does not improve future-draw prediction for a fair lottery:

  1. Chi-square goodness-of-fit per number (uniformity across the pool)
  2. Lag-1 autocorrelation of the per-draw sum series (serial independence)
  3. Wald-Wolfowitz runs test on above/below-median of the sum series
  4. Hot/cold backtest: do "hot" numbers (frequent in train) outperform random
     in held-out test draws? (Expected: no edge.)

Pure standard library (math/statistics). Backend for the `run_independence_test`
tool in SKILL.md. Works on real ingested data OR the synthetic fixture; the
report always echoes the dataset's source provenance so output never
misrepresents real vs synthetic data.

Usage:
    python scripts/independence_test.py            # all ingested games
    python scripts/independence_test.py mega_6_45
    python scripts/independence_test.py mega_6_45 --json
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "data" / "results"

GAME_META = {
    "mega_6_45": {"pool": 45, "draw": 6, "number_game": True},
    "power_6_55": {"pool": 55, "draw": 6, "number_game": True, "has_bonus": True},
    "keno": {"pool": 80, "draw": 20, "number_game": True},
    "max_3d": {"pool": 1000, "draw": 1, "number_game": False, "digit_game": True},
}


# --------------------------- special functions (stdlib only) ---------------------------

def _gammp_series(a: float, x: float) -> float:
    """Regularized LOWER incomplete gamma P(a,x) via series (x < a+1)."""
    gln = math.lgamma(a)
    ap = a
    summ = 1.0 / a
    delta = summ
    for _ in range(1000):
        ap += 1.0
        delta *= x / ap
        summ += delta
        if abs(delta) < abs(summ) * 1e-14:
            break
    return summ * math.exp(-x + a * math.log(x) - gln)


def _gammq_cf(a: float, x: float) -> float:
    """Regularized UPPER incomplete gamma Q(a,x) via continued fraction (x >= a+1)."""
    gln = math.lgamma(a)
    b = x + 1.0 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def gammp(a: float, x: float) -> float:
    if x < 0 or a <= 0:
        raise ValueError("a>0 and x>=0 required")
    if x == 0:
        return 0.0
    if x < a + 1.0:
        return _gammp_series(a, x)
    return 1.0 - _gammq_cf(a, x)


def gammq(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a,x) = 1 - P(a,x)."""
    if x < 0 or a <= 0:
        raise ValueError("a>0 and x>=0 required")
    if x == 0:
        return 1.0
    if x < a + 1.0:
        return 1.0 - _gammp_series(a, x)
    return _gammq_cf(a, x)


def chi2_sf(stat: float, df: int) -> float:
    """Chi-square survival function (upper-tail p-value)."""
    return gammq(df / 2.0, stat / 2.0)


def normal_sf(z: float) -> float:
    """Standard normal survival function (two-tailed = 2*this)."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


# --------------------------- tests ---------------------------

def chi_square_uniform(counts: List[int]) -> Dict:
    """Goodness-of-fit to uniform. counts[i] = observed frequency for category i."""
    n = sum(counts)
    k = len(counts)
    if n == 0 or k < 2:
        raise ValueError("need non-empty counts with >=2 categories")
    expected = n / k
    stat = sum((c - expected) ** 2 / expected for c in counts)
    df = k - 1
    p = chi2_sf(stat, df)
    return {"statistic": stat, "df": df, "p_value": p, "expected_per_category": expected, "reject_at_0.05": p < 0.05}


def lag1_autocorrelation(series: List[float]) -> float:
    n = len(series)
    if n < 3:
        raise ValueError("need >=3 observations")
    mean = statistics.fmean(series)
    num = sum((series[i] - mean) * (series[i - 1] - mean) for i in range(1, n))
    den = sum((x - mean) ** 2 for x in series)
    if den == 0:
        return 0.0
    return num / den


def wald_wolfowitz_runs(series: List[float]) -> Dict:
    """Runs test on above/below median (serial independence)."""
    n = len(series)
    if n < 2:
        raise ValueError("need >=2 observations")
    median = statistics.median(series)
    bits = [1 if x > median else 0 for x in series]
    n1 = sum(bits)
    n2 = n - n1
    if n1 == 0 or n2 == 0:
        return {"runs": 0, "n1": n1, "n2": n2, "z": 0.0, "p_value": 1.0, "reject_at_0.05": False}
    runs = 1 + sum(1 for i in range(1, n) if bits[i] != bits[i - 1])
    mu = (2.0 * n1 * n2) / n + 1.0
    sigma = math.sqrt((2.0 * n1 * n2 * (2.0 * n1 * n2 - n)) / (n * n * (n - 1)))
    z = (runs - mu) / sigma if sigma > 0 else 0.0
    p = 2.0 * normal_sf(abs(z))
    return {"runs": runs, "expected_runs": mu, "z": z, "p_value": p, "reject_at_0.05": p < 0.05}


def hot_cold_backtest(draws: List[List[int]], pool: int, train_frac: float = 0.5, top_k: int = 6) -> Dict:
    """Train on first fraction; bet the `top_k` hottest numbers in the held-out test.

    For a fair lottery, the test-draw hit rate of the 'hot' set should equal the
    random expectation (top_k/pool per draw). Returns observed vs expected and a z-test.
    """
    n = len(draws)
    if n < 20:
        raise ValueError("need >=20 draws for a backtest")
    split = int(n * train_frac)
    train, test = draws[:split], draws[split:]
    counts = [0] * (pool + 1)
    for d in train:
        for x in d:
            counts[x] += 1
    hot = sorted(range(1, pool + 1), key=lambda i: counts[i], reverse=True)[:top_k]
    hot_set = set(hot)
    hits = sum(sum(1 for x in d if x in hot_set) for d in test)
    draws_test = len(test)
    per_draw_expected = top_k / pool * len(draws[0]) if draws else 0
    total_expected = per_draw_expected * draws_test
    var = draws_test * (len(draws[0]) * top_k / pool) * (1 - top_k / pool)  # binomial-ish per draw
    z = (hits - total_expected) / math.sqrt(var) if var > 0 else 0.0
    p = 2.0 * normal_sf(abs(z))
    return {
        "train_draws": len(train),
        "test_draws": draws_test,
        "top_k": top_k,
        "hot_numbers": hot,
        "observed_hits": hits,
        "expected_hits": total_expected,
        "z": z,
        "p_value": p,
        "edge_present": abs(z) >= 1.96,
        "conclusion": "No predictive edge (consistent with independence)" if not (abs(z) >= 1.96) else "Apparent deviation (check sample size / multiple-testing)",
    }


# --------------------------- orchestration ---------------------------

def _load_draws(game: str) -> Tuple[List[Dict], List[str]]:
    path = RESULTS_DIR / f"{game}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"no ingested data for {game}; run: python scripts/ingest_results.py {game}")
    draws = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                draws.append(json.loads(line))
    provenance = {}
    for d in draws:
        provenance[d.get("source", "?")] = provenance.get(d.get("source", "?"), 0) + 1
    return draws, [f"{k}:{v}" for k, v in provenance.items()]


def analyze(game: str) -> Dict:
    meta = GAME_META[game]
    draws, provenance = _load_draws(game)
    n = len(draws)
    report: Dict = {"game": game, "n_draws": n, "provenance": provenance, "source_is_synthetic": all("synthetic" in p for p in provenance)}

    if meta.get("digit_game"):
        vals = [int(d["three_digit"]) for d in draws]
        counts = [0] * 1000
        for v in vals:
            counts[v] += 1
        full = chi_square_uniform(counts)
        sparse = full["expected_per_category"] < 5
        report["chi_square_uniform_1000"] = {**full, "reliable": not sparse,
            "warning": "sparse bins (expected<5); use per-digit test below for a valid uniformity check" if sparse else None}
        # Per-digit uniformity (hundreds / tens / units) - the meaningful test for Max 3D.
        digit_tests = {}
        for pos, shift in (("hundreds", 100), ("tens", 10), ("units", 1)):
            buckets = [0] * 10
            for v in vals:
                buckets[(v // shift) % 10] += 1
            digit_tests[pos] = chi_square_uniform(buckets)
        report["chi_square_per_digit"] = digit_tests
        report["lag1_autocorrelation"] = lag1_autocorrelation([float(v) for v in vals])
        report["wald_wolfowitz"] = wald_wolfowitz_runs([float(v) for v in vals])
        report["interpretation"] = _interpret(report)
        return report

    pool = meta["pool"]
    draw_size = meta["draw"]
    num_draws = [d["numbers"] for d in draws]
    counts = [0] * (pool + 1)
    for d in num_draws:
        for x in d:
            counts[x] += 1
    report["chi_square_uniform"] = chi_square_uniform(counts[1:])  # drop index 0
    sums = [float(sum(d)) for d in num_draws]
    report["lag1_autocorrelation"] = lag1_autocorrelation(sums)
    report["wald_wolfowitz"] = wald_wolfowitz_runs(sums)
    report["hot_cold_backtest"] = hot_cold_backtest(num_draws, pool, train_frac=0.5, top_k=meta["draw"])
    report["interpretation"] = _interpret(report)
    return report


def _interpret(report: Dict) -> str:
    parts = []
    chi = report.get("chi_square_uniform") or report.get("chi_square_uniform_1000")
    if chi:
        parts.append(f"chi-square p={chi['p_value']:.3f} ({'reject uniformity' if chi['reject_at_0.05'] else 'consistent with uniform'})")
    acf = report.get("lag1_autocorrelation")
    if acf is not None:
        parts.append(f"lag-1 autocorr={acf:+.4f} ({'serially independent' if abs(acf) < 0.1 else 'possible autocorrelation'})")
    ww = report.get("wald_wolfowitz")
    if ww:
        parts.append(f"runs-test p={ww['p_value']:.3f} ({'serially independent' if not ww['reject_at_0.05'] else 'reject independence'})")
    hc = report.get("hot_cold_backtest")
    if hc:
        parts.append(f"hot/cold edge z={hc['z']:+.3f} ({hc['conclusion']})")
    pd = report.get("chi_square_per_digit")
    if pd:
        digit_ps = {k: f"{v['p_value']:.3f}" for k, v in pd.items()}
        parts.append(f"per-digit chi-square p={digit_ps}")
    if report.get("chi_square_uniform_1000", {}).get("warning"):
        parts.append("note: 1000-bucket chi-square sparse/unreliable")
    synth = " [SYNTHETIC FIXTURE - not real Vietlott history]" if report.get("source_is_synthetic") else " [REAL INGESTED DATA]"
    return "; ".join(parts) + synth


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    as_json = "--json" in sys.argv[1:]
    games = args or list(GAME_META.keys())
    reports = []
    for g in games:
        try:
            reports.append(analyze(g))
        except FileNotFoundError as e:
            print(f"{g}: {e}", file=sys.stderr)
    if as_json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
        return
    for r in reports:
        print(f"\n=== Independence analysis: {r['game']} (n={r['n_draws']}) ===")
        print(f"  provenance: {', '.join(r['provenance'])}")
        for k, v in r.items():
            if k in ("game", "n_draws", "provenance", "source_is_synthetic", "interpretation"):
                continue
            print(f"  {k}: {json.dumps(v, ensure_ascii=False)}")
        print(f"  -> {r['interpretation']}")


if __name__ == "__main__":
    main()
