"""Executable test suite for the Vietlott skill.

Run with:  python -m pytest tests/ -q

These tests assert the numeric regressions documented in tests/test_cases.md
plus guardrail and risk-screener behaviour. They use only the standard library
plus the project's own scripts; no third-party deps beyond pytest itself.
"""

from __future__ import annotations

import math
from typing import List

import pytest

import combinatorics as c
import keno_calculator as k
import max3d_calculator as m
import expected_value as ev
import wheeling_analyzer as w
import risk_screener as r
import config_loader as cfg

TOL = 1e-6  # relative/absolute tolerance for float comparisons


# ---------------------------------------------------------------------------
# Methodology 1: combinatorial odds (Mega 6/45, Power 6/55)
# ---------------------------------------------------------------------------

class TestMegaOdds:
    def test_jackpot_odds(self):
        o = c.single_pool_match_odds(45, 6, 6)
        assert o.sample_space == 8_145_060
        assert o.favorable == 1
        assert abs(o.odds - 8_145_060.0) < TOL

    @pytest.mark.parametrize("match,expected_odds", [(6, 8145060.0), (5, 34807.95), (4, 732.80), (3, 44.56)])
    def test_tier_odds(self, match, expected_odds):
        o = c.single_pool_match_odds(45, 6, match)
        assert abs(o.odds - expected_odds) < 1.0  # rounded reference values

    def test_any_prize_probability(self):
        rows = c.mega_6_45_table()
        p_any = sum(row["probability"] for row in rows)
        assert 0.02 < p_any < 0.03  # ~1 in 42

    def test_validation_errors(self):
        with pytest.raises(ValueError):
            c.single_pool_match_odds(45, 50, 6)  # numbers_drawn > pool_size
        with pytest.raises(ValueError):
            c.single_pool_match_odds(45, 6, 7)  # match > numbers_drawn
        with pytest.raises(ValueError):
            c.single_pool_match_odds(-1, 6, 6)  # negative pool


class TestPowerOdds:
    def test_jackpot_odds(self):
        o = c.bonus_pool_match_odds(55, 6, 6, False)
        assert abs(o.odds - 28_989_675.0) < TOL

    def test_five_plus_bonus(self):
        o = c.bonus_pool_match_odds(55, 6, 5, True)
        assert abs(o.odds - 4_831_612.5) < TOL

    def test_five_no_bonus(self):
        o = c.bonus_pool_match_odds(55, 6, 5, False)
        assert abs(o.odds - 100_658.59) < 0.01

    def test_three_no_bonus_close_to_published_85(self):
        o = c.bonus_pool_match_odds(55, 6, 3, False)
        # published ~1 in 85; derived ~1 in 84 (rounding reconciliation)
        assert 80 < o.odds < 90

    def test_cannot_match_bonus_when_all_main_match(self):
        o = c.bonus_pool_match_odds(55, 6, 6, True)
        assert o.favorable == 0
        assert math.isinf(o.odds)

    def test_any_prize_probability(self):
        rows = c.power_6_55_table()
        p_any = sum(row["probability"] for row in rows)
        assert 0.02 < p_any < 0.025  # ~1 in 45


# ---------------------------------------------------------------------------
# Methodology: Keno hypergeometric
# ---------------------------------------------------------------------------

class TestKeno:
    @pytest.mark.parametrize("s", range(1, 11))
    def test_distribution_sums_to_one(self, s):
        probs = [k.keno_probability(s, mm) for mm in range(s + 1)]
        assert abs(sum(probs) - 1.0) < 1e-9

    def test_select1_match1(self):
        assert abs(k.keno_odds(1, 1) - 4.0) < TOL

    def test_select10_match10_top_prize(self):
        assert abs(k.keno_odds(10, 10) - 8_911_711.18) < 1.0

    @pytest.mark.parametrize("s", range(1, 11))
    def test_all_select_evs_negative(self, s):
        result = k.expected_value_select(s)
        assert result["expected_value_vnd"] < 0, f"select {s} EV must be negative"

    def test_select7_lowest_house_edge(self):
        edges = {s: k.expected_value_select(s)["house_edge_percent"] for s in range(1, 11)}
        assert min(edges, key=edges.get) == 7

    def test_validation_errors(self):
        with pytest.raises(ValueError):
            k.keno_probability(0, 0)
        with pytest.raises(ValueError):
            k.keno_probability(11, 1)
        with pytest.raises(ValueError):
            k.keno_probability(3, 4)


# ---------------------------------------------------------------------------
# Methodology: Max 3D fixed-odds
# ---------------------------------------------------------------------------

class TestMax3D:
    def test_single_odds(self):
        single = m.max_3d_single_table()
        assert abs(single[0].odds - 1000.0) < TOL
        assert single[0].prize_vnd == 500_000

    def test_pro_three_match_astronomical(self):
        pro = m.max_3d_pro_table()
        three = [t for t in pro if t.matches == 3][0]
        assert abs(three.odds - 1_000_000_000.0) < TOL

    def test_binomial_match_distribution_sums_to_one(self):
        for chosen in (2, 3):
            probs = [m.binomial_match_prob(chosen, mm) for mm in range(chosen + 1)]
            assert abs(sum(probs) - 1.0) < 1e-6

    @pytest.mark.parametrize("mode", ["max_3d_single", "max_3d_plus", "max_3d_pro"])
    def test_all_mode_evs_negative(self, mode):
        result = m.expected_value(mode)
        assert result["expected_value_vnd"] < 0

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            m.expected_value("nonsense")


# ---------------------------------------------------------------------------
# Methodology 3: expected value & long-term projection
# ---------------------------------------------------------------------------

class TestExpectedValue:
    @pytest.mark.parametrize("game,kw", [
        ("mega", {}),
        ("power", {}),
        ("keno", {"keno_select": 7}),
        ("max3d", {"max3d_mode": "max_3d_single"}),
    ])
    def test_ev_always_negative(self, game, kw):
        result = ev.calculate_expected_value(game, **kw)
        assert result.expected_value_vnd < 0
        assert 0 < result.house_edge_percent <= 100
        assert 0 < result.any_prize_probability <= 1

    def test_long_term_projection(self):
        proj = ev.long_term_projection(200_000, 0.50, 10)
        assert abs(proj.weekly_expected_loss_vnd - 100_000) < TOL
        assert abs(proj.annual_expected_loss_vnd - 5_200_000) < TOL
        assert abs(proj.total_expected_loss_vnd - 52_000_000) < TOL
        assert proj.investment_alternative_vnd > proj.total_expected_loss_vnd

    def test_projection_validation(self):
        with pytest.raises(ValueError):
            ev.long_term_projection(100, 1.5)
        with pytest.raises(ValueError):
            ev.long_term_projection(100, 0.5, 0)

    def test_unknown_game_raises(self):
        with pytest.raises(ValueError):
            ev.calculate_expected_value("scratch_off")
        with pytest.raises(ValueError):
            ev.calculate_expected_value("keno")  # missing select
        with pytest.raises(ValueError):
            ev.calculate_expected_value("max3d")  # missing mode


# ---------------------------------------------------------------------------
# Methodology: wheeling systems
# ---------------------------------------------------------------------------

class TestWheeling:
    def test_full_wheel_size(self):
        res = w.analyze_wheeling(10, 4, 50, pool_size=45, draw_size=6)
        assert res.full_wheel_tickets == math.comb(10, 6) == 210
        assert res.cost_factor == 50

    def test_ev_identical_wheeling_vs_random(self):
        cmp = w.compare_wheeling_vs_random(2_100_000, 2_100_000, 0.50)
        assert cmp["wheeling_expected_loss_vnd"] == cmp["random_expected_loss_vnd"]
        assert "redistributes risk" in cmp["conclusion"].lower()

    def test_conditional_claim_detected(self):
        ev = w.evaluate_claim("Dam bao trung 4 so neu 5/10 so cua ban trung!", 10, 50)
        assert ev["is_conditional_guarantee"] is True
        assert ev["expected_value_impact"].lower().startswith("none")

    def test_validation_errors(self):
        with pytest.raises(ValueError):
            w.analyze_wheeling(3, 4, 50)  # chosen_count < draw_size
        with pytest.raises(ValueError):
            w.analyze_wheeling(10, 7, 50)  # guarantee > draw_size


# ---------------------------------------------------------------------------
# Methodology 5: responsible-gambling risk screening
# ---------------------------------------------------------------------------

class TestRiskScreener:
    def setup_method(self):
        self.s = r.RiskScreener()

    def test_ncpg_low_risk(self):
        res = self.s.screen_ncpg([False] * 7)
        assert res.risk_level == "Low risk"
        assert res.score == 0

    def test_ncpg_moderate_risk(self):
        res = self.s.screen_ncpg([False, False, True, False, True, False, False])
        assert res.risk_level == "Moderate risk"
        assert res.score == 2

    def test_ncpg_high_risk(self):
        res = self.s.screen_ncpg([True, True, True, True, False, False, False])
        assert res.risk_level == "High risk"
        assert res.score == 4

    def test_ncpg_wrong_length_raises(self):
        with pytest.raises(ValueError):
            self.s.screen_ncpg([True, False])

    def test_pgsi_thresholds(self):
        assert self.s.screen_pgsi([0] * 9).risk_level == "Non-problem gambler"
        assert self.s.screen_pgsi([1, 1, 0, 0, 0, 0, 0, 0, 0]).risk_level == "Low-risk gambler"
        assert self.s.screen_pgsi([2, 2, 2, 0, 0, 0, 0, 0, 0]).risk_level == "Moderate-risk gambler"
        assert self.s.screen_pgsi([3, 3, 3, 3, 0, 0, 0, 0, 0]).risk_level == "Problem gambler"

    def test_pgsi_validation(self):
        with pytest.raises(ValueError):
            self.s.screen_pgsi([0, 1, 2])
        with pytest.raises(ValueError):
            self.s.screen_pgsi([4, 0, 0, 0, 0, 0, 0, 0, 0])  # out of 0-3 range

    def test_text_scan_diacritic_insensitive_vietnamese(self):
        # ASCII/no-tone Vietnamese should still match diacritic-bearing keywords.
        res = self.s.detect_risk_in_text("Toi muon go lai so tien da thua, co nen vay tien choi them khong?")
        assert res.risk_level == "High risk"
        assert res.score >= 2
        assert any("go" in r._strip_diacritics(kw) for kw in res.indicators_present)

    def test_text_scan_clean_text(self):
        res = self.s.detect_risk_in_text("Toi muon hieu xac suat Mega 6/45.")
        assert res.risk_level == "No indicators present"
        assert res.score == 0

    def test_indicator_screening_counts(self):
        res = self.s.screen_indicators([
            "Chasing losses or gambling to recover money",
            "Exceeding predetermined gambling budget",
            "Feeling guilt or shame about gambling",
        ])
        assert res.risk_level == "Moderate risk"
        assert res.extra["behavioral"] == 1
        assert res.extra["financial"] == 1
        assert res.extra["psychological"] == 1

    def test_unknown_indicator_raises(self):
        with pytest.raises(ValueError):
            self.s.screen_indicators(["something not in the list"])

    def test_vietnam_resources_present(self):
        res = self.s.screen_ncpg([True] * 7)
        assert "vietnam" in res.support_resources
        assert "crisis" in res.support_resources


# ---------------------------------------------------------------------------
# Guardrail: hard refusal of predictions is encoded in config
# ---------------------------------------------------------------------------

class TestGuardrails:
    def test_never_generate_predictions_flag(self):
        assert cfg.is_feature_enabled("never_generate_predictions") is True

    def test_disclaimer_flag(self):
        assert cfg.is_feature_enabled("always_include_disclaimer") is True

    def test_investment_alternative_feature_enabled(self):
        assert cfg.is_feature_enabled("enable_investment_alternative_comparison") is True

    def test_guardrails_in_settings(self):
        guardrails = cfg.load_settings()["skill_settings"]["guardrails"]
        assert guardrails["no_investment_framing"] is True
        assert guardrails["no_guarantees_of_winning"] is True
        assert guardrails["no_encouragement_of_increased_spending"] is True

    def test_unknown_flag_raises(self):
        with pytest.raises(KeyError):
            cfg.is_feature_enabled("nonexistent_flag")

    def test_required_configs_validate(self):
        cfg.validate_required_configs()  # raises if any missing/invalid

    def test_games_json_has_four_formats(self):
        games = cfg.load_games()["vietlott_games"]
        assert set(games.keys()) == {"mega_6_45", "power_6_55", "keno", "max_3d"}

    def test_all_configured_odds_positive(self):
        games = cfg.load_games()["vietlott_games"]
        for game in ("mega_6_45", "power_6_55"):
            for tier in games[game]["prize_tiers"]:
                assert tier["odds_1_in"] > 1
                assert 0 < tier["probability"] <= 1

    def test_keno_distribution_integrity_in_config(self):
        # Every select's tier probabilities must sum to <= 1 (winning tiers only; remainder is losing).
        keno = cfg.load_games()["vietlott_games"]["keno"]["co_ban_prize_tables"]
        for key, tiers in keno.items():
            total = sum(t["probability"] for t in tiers)
            assert 0 < total <= 1.0 + 1e-9, f"{key} winning-tier probs exceed 1: {total}"


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
