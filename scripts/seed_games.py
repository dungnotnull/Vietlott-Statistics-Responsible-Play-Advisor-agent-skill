#!/usr/bin/env python3
"""
Database/config seeding for the Vietlott skill.

Regenerates config/games.json so that every odds figure is computed from
first principles (no hand-typed probabilities). Run after editing any
prize-amount assumption to keep the config internally consistent:

    python scripts/seed_games.py

Prize AMOUNTS remain human-authored representative values (clearly labelled in
the output); all PROBABILITIES/ODDS are derived.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import combinatorics as c
import keno_calculator as k
import max3d_calculator as m


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def _mega_section() -> Dict:
    rows = c.mega_6_45_table()
    tiers = []
    for r in rows:
        tiers.append(
            {
                "match": r["match"],
                "prize_name": r["prize_name"],
                "prize_vnd": r["prize_vnd"],
                "pari_mutuel": r["pari_mutuel"],
                "favorable_outcomes": r["favorable"],
                "probability": r["probability"],
                "odds_1_in": r["odds_1_in"],
            }
        )
    return {
        "name": "Mega 6/45",
        "vietnamese_name": "Mega 6/45",
        "description": "Chon 6 so tu 1-45. Quay 1 lan/ngay. Jackpot pari-mutuel.",
        "format": "single_pool",
        "pool_size": 45,
        "numbers_drawn": 6,
        "bonus_ball": False,
        "ticket_cost_vnd": 10000,
        "draw_frequency": "daily",
        "total_combinations": 8145060,
        "calculation": "C(45,6) = 8,145,060",
        "prize_tiers": tiers,
        "expected_value_note": "Jackpot is pari-mutuel and accumulates; EV stays negative even at large jackpots because the prize is shared and grows slower than ticket sales.",
    }


def _power_section() -> Dict:
    rows = c.power_6_55_table()
    tiers = []
    for r in rows:
        tiers.append(
            {
                "match": r["match"],
                "prize_name": r["prize_name"],
                "prize_vnd": r["prize_vnd"],
                "pari_mutuel": r["pari_mutuel"],
                "favorable_outcomes": r["favorable"],
                "probability": r["probability"],
                "odds_1_in": r["odds_1_in"],
            }
        )
    return {
        "name": "Power 6/55",
        "vietnamese_name": "Power 6/55",
        "description": "Chon 6 so tu 1-55; 1 so bo sung duoc quay tu 49 con lai.",
        "format": "single_pool_with_bonus",
        "pool_size": 55,
        "numbers_drawn": 6,
        "bonus_ball": True,
        "bonus_ball_name": "So bo sung",
        "bonus_ball_pool": 49,
        "ticket_cost_vnd": 10000,
        "draw_frequency": "daily",
        "total_combinations": 28989675,
        "calculation": "C(55,6) = 28,989,675 main; bonus drawn from remaining 49",
        "prize_tiers": tiers,
        "odds_derivation_note": "Mid-tier odds are combinatorially derived (6 main + 1 bonus from remaining 49). Published Vietlott marketing tables may round differently; verify current official odds at https://vietlott.vn.",
    }


def _keno_section() -> Dict:
    table = k.published_prize_table()
    by_select: Dict[int, List[Dict]] = {}
    for tier in table:
        by_select.setdefault(tier.select, []).append(
            {
                "match": tier.match,
                "prize_vnd": tier.prize_vnd,
                "probability": tier.probability,
                "odds_1_in": round(tier.odds, 4) if tier.odds != float("inf") else None,
            }
        )
    ev_rows = []
    for s in range(1, 11):
        ev = k.expected_value_select(s)
        ev_rows.append(
            {
                "select": ev["select"],
                "expected_winnings_vnd": round(ev["expected_winnings_vnd"], 2),
                "expected_value_vnd": round(ev["expected_value_vnd"], 2),
                "house_edge_percent": round(ev["house_edge_percent"], 2),
            }
        )
    return {
        "name": "Keno",
        "vietnamese_name": "Keno",
        "description": "Tro choi quay nhanh: nguoi choi chon 1-10 so tu 1-80; 20 so duoc quay moi ~10 phut.",
        "format": "rapid_draw_hypergeometric",
        "pool_size": 80,
        "numbers_drawn": 20,
        "player_selects_range": [1, 10],
        "ticket_cost_vnd": 10000,
        "draw_frequency": "every_10_minutes",
        "co_ban_prize_tables": {f"select_{s}": by_select[s] for s in sorted(by_select)},
        "expected_value_per_select": ev_rows,
        "house_edge_note": "Keno's per-draw house edge (22-54%) is lower than jackpot games, but the ~10-minute draw cadence is the dominant financial risk factor: more draws per day means more opportunities to lose expected value.",
        "play_modes": {
            "co_ban": "Payout by match count (tables above).",
            "trung_lon": "Select 10-12 numbers; only top tiers pay; higher volatility, same negative EV.",
            "lon_nho": "Bet >13 of 20 drawn numbers are >40 (Lon) or <=40 (Nho); near even-money minus house edge.",
        },
    }


def _max3d_section() -> Dict:
    single = m.max_3d_single_table()
    plus = m.max_3d_plus_table()
    pro = m.max_3d_pro_table()

    def to_dicts(tiers):
        return [
            {
                "matches": t.matches,
                "prize_vnd": t.prize_vnd,
                "probability": t.probability,
                "odds_1_in": round(t.odds, 4) if t.odds != float("inf") else None,
            }
            for t in tiers
        ]

    return {
        "name": "Max 3D",
        "vietnamese_name": "Max 3D",
        "description": "Tro choi co dinh 3 chu so (000-999). Nhieu che do: 1 so, 2 so (Max 3D+), 3 so (Max 3D Pro).",
        "format": "fixed_odds_digits",
        "pool_size": 1000,
        "ticket_cost_vnd": 10000,
        "draw_frequency": "daily",
        "per_number_odds": 1000,
        "play_modes": {
            "max_3d_single": {
                "name": "Max 3D (1 so)",
                "description": "Chon 1 so 3 chu so; trung chinh xac de thang.",
                "prize_tiers": to_dicts(single),
            },
            "max_3d_plus": {
                "name": "Max 3D+ (2 so)",
                "description": "Chon 2 so 3 chu so; giai thuong theo so luong trung.",
                "prize_tiers": to_dicts(plus),
            },
            "max_3d_pro": {
                "name": "Max 3D Pro (3 so)",
                "description": "Chon 3 so 3 chu so; giai thuong theo so luong trung.",
                "prize_tiers": to_dicts(pro),
            },
        },
        "house_edge_note": "House edge depends on the current official prize amounts (verify at https://vietlott.vn). With representative prizes the per-ticket EV is strongly negative; fixed-odds means payouts do NOT vary with how many players win, unlike pari-mutuel jackpot tiers.",
    }


def build_games() -> Dict:
    return {
        "vietlott_games": {
            "mega_6_45": _mega_section(),
            "power_6_55": _power_section(),
            "keno": _keno_section(),
            "max_3d": _max3d_section(),
        },
        "metadata": {
            "version": "1.0.0",
            "last_updated": "2026-08-10",
            "currency": "VND",
            "source_note": "All probabilities/odds are combinatorially derived by scripts/seed_games.py from the draw mechanisms documented in references/. Prize AMOUNTS are representative human-authored values (pari-mutuel tiers vary draw to draw). Always verify current official structures at https://vietlott.vn.",
            "generation": "Run `python scripts/seed_games.py` to regenerate after editing prize assumptions.",
        },
    }


def main() -> None:
    games = build_games()
    out = CONFIG_DIR / "games.json"
    out.write_text(json.dumps(games, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")

    # Quick consistency report
    mega = games["vietlott_games"]["mega_6_45"]
    power = games["vietlott_games"]["power_6_55"]
    print("\nConsistency report:")
    print(f"  Mega 6/45 jackpot odds : 1 in {mega['prize_tiers'][0]['odds_1_in']:,.0f}")
    print(f"  Power 6/55 jackpot odds : 1 in {power['prize_tiers'][0]['odds_1_in']:,.0f}")
    print(f"  Keno select tiers       : {sum(len(v) for v in games['vietlott_games']['keno']['co_ban_prize_tables'].values())} rows")
    print(f"  Max 3D modes            : {len(games['vietlott_games']['max_3d']['play_modes'])}")


if __name__ == "__main__":
    main()
