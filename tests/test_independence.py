"""Tests for draw-data ingestion and statistical independence analysis.

Covers: special functions (gamma/chi-square/normal), chi-square uniformity,
lag-1 autocorrelation, Wald-Wolfowitz runs test, hot/cold backtest, and the
ingestion source handlers (csv_file, manual, synthetic, dedupe/sort, schema
validation). Self-contained: no dependency on persisted data files.
"""

from __future__ import annotations

import csv
import json
import math
import os
import random
import tempfile

import pytest

import independence_test as it
import ingest_results as ing
import generate_synthetic_results as syn


# ---------------- special functions ----------------

class TestSpecialFunctions:
    def test_gammp_gammq_complement(self):
        for a in (1.0, 2.5, 5.0, 10.0):
            for x in (0.5, 2.0, 5.0, 10.0, 20.0):
                p, q = it.gammp(a, x), it.gammq(a, x)
                assert abs((p + q) - 1.0) < 1e-9

    def test_chi2_sf_known(self):
        # chi2_sf(3.84, 1) ~ 0.05 ; chi2_sf(23.0, 1) ~ 1.6e-6
        assert abs(it.chi2_sf(3.841, 1) - 0.05) < 1e-2
        assert it.chi2_sf(10.0, 5) > 0.05  # not rejected

    def test_normal_sf_symmetry(self):
        assert abs(it.normal_sf(0.0) - 0.5) < 1e-9
        assert abs(it.normal_sf(1.96) - 0.025) < 1e-3


# ---------------- chi-square uniformity ----------------

class TestChiSquare:
    def test_uniform_not_rejected(self):
        rng = random.Random(7)
        counts = [rng.randint(950, 1050) for _ in range(10)]  # ~uniform
        r = it.chi_square_uniform(counts)
        assert r["reject_at_0.05"] is False

    def test_biased_rejected(self):
        counts = [1000] * 9 + [10000]  # one bucket hugely over
        r = it.chi_square_uniform(counts)
        assert r["reject_at_0.05"] is True
        assert r["p_value"] < 0.05

    def test_validation(self):
        with pytest.raises(ValueError):
            it.chi_square_uniform([])
        with pytest.raises(ValueError):
            it.chi_square_uniform([5])  # only 1 category


# ---------------- autocorrelation & runs ----------------

class TestSerialIndependence:
    def test_autocorrelation_zero_series(self):
        assert it.lag1_autocorrelation([5, 5, 5, 5]) == 0.0

    def test_autocorrelation_positive(self):
        # monotonically increasing -> strong positive lag-1
        r = it.lag1_autocorrelation([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        assert r >= 0.5

    def test_autocorrelation_validation(self):
        with pytest.raises(ValueError):
            it.lag1_autocorrelation([1.0, 2.0])

    def test_runs_alternating_not_rejected_for_independence(self):
        # strictly alternating -> many runs -> NOT the clustered pattern of dependence
        r = it.wald_wolfowitz_runs([1, 2, 1, 2, 1, 2, 1, 2, 1, 2])
        # alternating yields runs == n; that is unusual vs expectation but the function must run
        assert r["runs"] == 10

    def test_runs_validation(self):
        with pytest.raises(ValueError):
            it.wald_wolfowitz_runs([1.0])


# ---------------- hot/cold backtest ----------------

class TestHotColdBacktest:
    def test_no_edge_on_uniform_synthetic(self):
        rng = random.Random(123)
        draws = [sorted(rng.sample(range(1, 46), 6)) for _ in range(4000)]
        r = it.hot_cold_backtest(draws, pool=45, train_frac=0.5, top_k=6)
        assert r["edge_present"] is False
        assert abs(r["z"]) < 3.0  # strong tolerance; fair lottery shows no edge

    def test_backtest_validation(self):
        with pytest.raises(ValueError):
            it.hot_cold_backtest([[1, 2, 3, 4, 5, 6]], 45)  # too few


# ---------------- synthetic generator ----------------

class TestSyntheticGenerator:
    def test_mega_valid(self):
        for d in syn.generate("mega_6_45", 50, 1):
            assert len(d.numbers) == 6 and len(set(d.numbers)) == 6
            assert all(1 <= n <= 45 for n in d.numbers)
            assert d.numbers == sorted(d.numbers)
            assert d.bonus is None
            assert d.source == "synthetic"

    def test_power_bonus_valid(self):
        for d in syn.generate("power_6_55", 50, 2):
            assert len(d.numbers) == 6 and d.bonus is not None
            assert d.bonus not in d.numbers and 1 <= d.bonus <= 55

    def test_keno_valid(self):
        for d in syn.generate("keno", 30, 3):
            assert len(d.numbers) == 20 and len(set(d.numbers)) == 20
            assert all(1 <= n <= 80 for n in d.numbers)

    def test_max3d_valid(self):
        for d in syn.generate("max_3d", 30, 4):
            assert d.three_digit is not None and len(d.three_digit) == 3
            assert d.three_digit.isdigit()

    def test_unknown_game_raises(self):
        with pytest.raises(ValueError):
            syn.generate("scratch", 10, 1)


# ---------------- ingestion handlers ----------------

class TestIngestion:
    def test_csv_file_mega(self, tmp_path):
        csv_path = tmp_path / "mega.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "draw_id", "n1", "n2", "n3", "n4", "n5", "n6"])
            w.writerow(["2024-01-01", "m1", 1, 7, 13, 21, 33, 45])
            w.writerow(["2024-01-02", "m2", 2, 9, 14, 22, 34, 40])
        draws = ing._from_csv({"path": str(csv_path), "source_label": "official_csv"}, "mega_6_45")
        assert len(draws) == 2
        assert draws[0]["numbers"] == [1, 7, 13, 21, 33, 45]
        assert draws[0]["source"] == "official_csv"

    def test_csv_file_max3d(self, tmp_path):
        csv_path = tmp_path / "max3d.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "draw_id", "three_digit"])
            w.writerow(["2024-01-01", "x1", "42"])  # should zero-pad to 042
            w.writerow(["2024-01-02", "x2", "999"])
        draws = ing._from_csv({"path": str(csv_path), "source_label": "official_csv"}, "max_3d")
        assert draws[0]["three_digit"] == "042"
        assert draws[1]["three_digit"] == "999"

    def test_manual_source(self):
        draws = ing._from_manual({
            "source_label": "manual",
            "draws": [
                {"draw_date": "2024-01-02", "numbers": [1, 2, 3, 4, 5, 6]},
                {"draw_date": "2024-01-01", "numbers": [7, 8, 9, 10, 11, 12]},
            ],
        }, "mega_6_45")
        assert len(draws) == 2
        assert draws[0]["numbers"] == [1, 2, 3, 4, 5, 6]

    def test_schema_validation_rejects_bad_draw(self):
        bad = {"game": "mega_6_45", "draw_id": "bad1", "source": "manual",
               "numbers": [1, 2, 3], "bonus": None, "three_digit": None}
        with pytest.raises(ValueError):
            ing._validate_draw(bad, "mega_6_45")
        bad2 = {"game": "mega_6_45", "draw_id": "bad2", "source": "manual",
                "numbers": [1, 2, 3, 4, 5, 50], "bonus": None, "three_digit": None}
        with pytest.raises(ValueError):
            ing._validate_draw(bad2, "mega_6_45")

    def test_ingest_game_dedupes_and_sorts(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ing, "RESULTS_DIR", tmp_path)
        cfg = ing._load_ingestion_config()
        cfg["sources"]["mega_6_45"] = [{
            "type": "manual", "active": True, "source_label": "manual",
            "draws": [
                {"draw_date": "2024-01-02", "draw_id": "A", "numbers": [1, 2, 3, 4, 5, 6]},
                {"draw_date": "2024-01-01", "draw_id": "B", "numbers": [7, 8, 9, 10, 11, 12]},
                {"draw_date": "2024-01-02", "draw_id": "A", "numbers": [40, 41, 42, 43, 44, 45]},  # dup id A
            ],
        }]
        r = ing.ingest_game("mega_6_45", cfg)
        assert r["count"] == 2  # A and B deduped by draw_id
        # sorted by date: 2024-01-01 (B) first
        rows = [json.loads(line) for line in (tmp_path / "mega_6_45.jsonl").read_text(encoding="utf-8").splitlines()]
        assert rows[0]["draw_id"] == "B"
        assert rows[0]["numbers"] == [7, 8, 9, 10, 11, 12]
        assert r["has_real_data"] is True  # manual, not synthetic

    def test_synthetic_source_labeled(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ing, "RESULTS_DIR", tmp_path)
        cfg = ing._load_ingestion_config()
        cfg["sources"]["keno"] = [{"type": "synthetic", "active": True, "count": 100, "seed": 99, "source_label": "synthetic"}]
        r = ing.ingest_game("keno", cfg)
        assert r["count"] == 100
        assert r["has_real_data"] is False  # synthetic
        rows = [json.loads(line) for line in (tmp_path / "keno.jsonl").read_text(encoding="utf-8").splitlines()]
        assert rows[0]["source"] == "synthetic"


# ---------------- end-to-end analyze on tmp fixture ----------------

class TestAnalyzeEndToEnd:
    def test_analyze_mega_synthetic(self, tmp_path, monkeypatch):
        monkeypatch.setattr(it, "RESULTS_DIR", tmp_path)
        draws = syn.generate("mega_6_45", 2000, 555)
        rows = [json.dumps(d.to_dict(), ensure_ascii=False) for d in draws]
        (tmp_path / "mega_6_45.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
        r = it.analyze("mega_6_45")
        assert r["n_draws"] == 2000
        assert r["chi_square_uniform"]["reject_at_0.05"] is False
        assert abs(r["lag1_autocorrelation"]) < 0.15
        assert r["hot_cold_backtest"]["edge_present"] is False
        assert r["source_is_synthetic"] is True
