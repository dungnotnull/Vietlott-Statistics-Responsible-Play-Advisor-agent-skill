#!/usr/bin/env python3
"""
Keno hypergeometric probability and expected-value calculator (Vietlott).

Vietlott Keno: player selects s numbers (1..10) from a pool of 80; the draw
selects 20 numbers. The number of player matches follows the hypergeometric
distribution:

    P(match m | select s) = C(s,m) * C(80-s, 20-m) / C(80,20)

This module computes exact probabilities, odds, and expected value per ticket
for the published Vietlott "Keno Co ban" (basic) prize table.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Dict, List


POOL_SIZE = 80
DRAWN = 20


@dataclass(frozen=True)
class PrizeTier:
    select: int
    match: int
    prize_vnd: int

    @property
    def probability(self) -> float:
        s = self.select
        m = self.match
        if m > s or (DRAWN - m) > (POOL_SIZE - s) or m < 0:
            return 0.0
        favorable = comb(s, m) * comb(POOL_SIZE - s, DRAWN - m)
        total = comb(POOL_SIZE, DRAWN)
        return favorable / total

    @property
    def odds(self) -> float:
        p = self.probability
        return float("inf") if p == 0 else 1.0 / p


# Published Vietlott "Keno Co ban" (basic) prize table (VND per 10,000 VND ticket).
# Only winning tiers are listed; non-listed match counts pay 0 VND.
def published_prize_table() -> List[PrizeTier]:
    return [
        PrizeTier(1, 1, 20000),
        PrizeTier(2, 2, 90000),
        PrizeTier(3, 3, 180000),
        PrizeTier(3, 2, 20000),
        PrizeTier(4, 4, 400000),
        PrizeTier(4, 3, 20000),
        PrizeTier(4, 2, 20000),
        PrizeTier(5, 5, 4400000),
        PrizeTier(5, 4, 100000),
        PrizeTier(5, 3, 20000),
        PrizeTier(6, 6, 12000000),
        PrizeTier(6, 5, 300000),
        PrizeTier(6, 4, 30000),
        PrizeTier(6, 3, 20000),
        PrizeTier(7, 7, 47000000),
        PrizeTier(7, 6, 1000000),
        PrizeTier(7, 5, 100000),
        PrizeTier(7, 4, 30000),
        PrizeTier(7, 3, 20000),
        PrizeTier(8, 8, 200000000),
        PrizeTier(8, 7, 4000000),
        PrizeTier(8, 6, 200000),
        PrizeTier(8, 5, 50000),
        PrizeTier(8, 0, 20000),
        PrizeTier(9, 9, 600000000),
        PrizeTier(9, 8, 20000000),
        PrizeTier(9, 7, 1000000),
        PrizeTier(9, 6, 100000),
        PrizeTier(9, 5, 30000),
        PrizeTier(9, 4, 20000),
        PrizeTier(10, 10, 2000000000),
        PrizeTier(10, 9, 100000000),
        PrizeTier(10, 8, 5000000),
        PrizeTier(10, 7, 200000),
        PrizeTier(10, 6, 50000),
        PrizeTier(10, 5, 30000),
        PrizeTier(10, 0, 20000),
    ]


def keno_probability(select: int, match: int) -> float:
    """Exact hypergeometric P(match m | select s)."""
    if select < 1 or select > 10:
        raise ValueError("select must be in 1..10")
    if match < 0 or match > select:
        raise ValueError("match must be in 0..select")
    favorable = comb(select, match) * comb(POOL_SIZE - select, DRAWN - match)
    total = comb(POOL_SIZE, DRAWN)
    return favorable / total


def keno_odds(select: int, match: int) -> float:
    """Odds 1-in-N for selecting s and matching m."""
    p = keno_probability(select, match)
    return float("inf") if p == 0 else 1.0 / p


def expected_value_select(select: int, ticket_cost_vnd: int = 10000) -> Dict[str, float]:
    """EV for one Keno Co ban ticket of `select` numbers."""
    tiers = [t for t in published_prize_table() if t.select == select]
    expected_winnings = sum(t.prize_vnd * t.probability for t in tiers)
    ev = expected_winnings - ticket_cost_vnd
    house_edge = (ticket_cost_vnd - expected_winnings) / ticket_cost_vnd * 100.0
    return {
        "select": select,
        "expected_winnings_vnd": expected_winnings,
        "expected_value_vnd": ev,
        "house_edge_percent": house_edge,
        "expected_loss_vnd": ticket_cost_vnd - expected_winnings,
    }


def full_table() -> List[Dict[str, object]]:
    rows = []
    for tier in published_prize_table():
        rows.append(
            {
                "select": tier.select,
                "match": tier.match,
                "prize_vnd": tier.prize_vnd,
                "probability": tier.probability,
                "odds_1_in": round(tier.odds, 2) if tier.odds != float("inf") else None,
            }
        )
    return rows


def validate_distribution(select: int) -> Dict[str, object]:
    """Sanity check: probabilities across all match counts sum to 1."""
    probs = [keno_probability(select, m) for m in range(select + 1)]
    return {"select": select, "sum_probability": sum(probs), "ok": abs(sum(probs) - 1.0) < 1e-9}


def main() -> None:
    print("Vietlott Keno Co ban - exact odds (computed, not rounded marketing figures)")
    print("=" * 80)
    for tier in published_prize_table():
        print(
            f"select {tier.select:>2} | match {tier.match:>2} | prize {tier.prize_vnd:>12,} VND | "
            f"P={tier.probability:.6f} | odds 1 in {tier.odds:,.2f}"
        )

    print("\nDistribution sanity checks (must sum to 1.0):")
    for s in range(1, 11):
        v = validate_distribution(s)
        print(f"  select {s:>2}: sum={v['sum_probability']:.10f}  ok={v['ok']}")

    print("\nExpected value per 10,000 VND ticket, by select:")
    for s in range(1, 11):
        ev = expected_value_select(s)
        print(
            f"  select {s:>2}: EV={ev['expected_value_vnd']:>10,.0f} VND | "
            f"house edge={ev['house_edge_percent']:5.1f}% | "
            f"win rate -> {ev['expected_winnings_vnd']:>10,.0f} VND"
        )


if __name__ == "__main__":
    main()
