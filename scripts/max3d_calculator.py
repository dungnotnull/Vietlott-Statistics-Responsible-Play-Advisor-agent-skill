#!/usr/bin/env python3
"""
Max 3D fixed-odds calculator (Vietlott).

Max 3D is a fixed-odds 3-digit game (000-999). One 3-digit number is drawn.
Modes:
  - Max 3D (single):    one chosen 3-digit number; exact match wins.
  - Max 3D+ (two):      two chosen numbers; tiers by how many match the draw.
  - Max 3D Pro (three): three chosen numbers; tiers by how many match.

Per-number exact-match probability is 1/1000. Because each chosen number is
an independent Bernoulli(1/1000) trial against the single drawn number, the
count of matches across k chosen numbers follows Binomial(k, 1/1000).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Dict, List


PER_NUMBER_ODDS = 1000
PER_NUMBER_PROB = 1.0 / PER_NUMBER_ODDS
TICKET_COST_VND = 10_000


@dataclass(frozen=True)
class Max3DTier:
    mode: str
    matches: int
    prize_vnd: int
    probability: float
    odds: float

    @property
    def odds_label(self) -> str:
        return f"1 in {int(round(self.odds)):,}"


def binomial_match_prob(chosen: int, matches: int) -> float:
    """P(exactly `matches` of `chosen` independent numbers equal the drawn number)."""
    if matches < 0 or matches > chosen:
        raise ValueError("matches must be in 0..chosen")
    p = PER_NUMBER_PROB
    return comb(chosen, matches) * (p ** matches) * ((1 - p) ** (chosen - matches))


def max_3d_single_table() -> List[Max3DTier]:
    return [Max3DTier("max_3d_single", 1, 500_000, PER_NUMBER_PROB, PER_NUMBER_ODDS)]


def max_3d_plus_table() -> List[Max3DTier]:
    """Max 3D+: two chosen numbers. Two tiers: both match, exactly one matches."""
    p2 = binomial_match_prob(2, 2)
    p1 = binomial_match_prob(2, 1)
    return [
        Max3DTier("max_3d_plus", 2, 1_000_000, p2, 1.0 / p2),
        Max3DTier("max_3d_plus", 1, 500_000, p1, 1.0 / p1),
    ]


def max_3d_pro_table() -> List[Max3DTier]:
    """Max 3D Pro: three chosen numbers. Three tiers: three/two/one match."""
    p3 = binomial_match_prob(3, 3)
    p2 = binomial_match_prob(3, 2)
    p1 = binomial_match_prob(3, 1)
    return [
        Max3DTier("max_3d_pro", 3, 1_500_000, p3, 1.0 / p3),
        Max3DTier("max_3d_pro", 2, 1_000_000, p2, 1.0 / p2),
        Max3DTier("max_3d_pro", 1, 500_000, p1, 1.0 / p1),
    ]


def expected_value(mode: str, ticket_cost_vnd: int = TICKET_COST_VND) -> Dict[str, float]:
    tables = {
        "max_3d_single": max_3d_single_table(),
        "max_3d_plus": max_3d_plus_table(),
        "max_3d_pro": max_3d_pro_table(),
    }
    if mode not in tables:
        raise ValueError(f"unknown mode: {mode}")
    tiers = tables[mode]
    expected_winnings = sum(t.prize_vnd * t.probability for t in tiers)
    return {
        "mode": mode,
        "expected_winnings_vnd": expected_winnings,
        "expected_value_vnd": expected_winnings - ticket_cost_vnd,
        "house_edge_percent": (ticket_cost_vnd - expected_winnings) / ticket_cost_vnd * 100.0,
    }


def main() -> None:
    print("Max 3D fixed-odds tables (per 10,000 VND ticket)")
    print("=" * 60)
    for tier in max_3d_single_table():
        print(f"  single  match {tier.matches}: {tier.prize_vnd:>10,} VND  | {tier.odds_label}")
    for tier in max_3d_plus_table():
        print(f"  plus    match {tier.matches}: {tier.prize_vnd:>10,} VND  | P={tier.probability:.6e} | 1 in {tier.odds:,.2f}")
    for tier in max_3d_pro_table():
        print(f"  pro     match {tier.matches}: {tier.prize_vnd:>10,} VND  | P={tier.probability:.6e} | 1 in {tier.odds:,.2f}")

    print("\nExpected value per 10,000 VND ticket:")
    for mode in ("max_3d_single", "max_3d_plus", "max_3d_pro"):
        ev = expected_value(mode)
        print(
            f"  {mode:>14}: EV={ev['expected_value_vnd']:>8,.0f} VND | "
            f"house edge={ev['house_edge_percent']:5.1f}%"
        )


if __name__ == "__main__":
    main()
