#!/usr/bin/env python3
"""
Wheeling / covering-system analyzer for Vietlott jackpot formats (Mega 6/45, Power 6/55).

Analyzes what wheeling systems can and cannot achieve. Backend for the
`analyze_wheeling_system` tool schema in SKILL.md.

Key teaching: wheeling redistributes risk; it does NOT improve expected value
per VND spent.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Dict, List, Optional


@dataclass(frozen=True)
class WheelingResult:
    chosen_count: int
    guarantee_match: int
    ticket_count: int
    pool_size: int
    draw_size: int
    full_wheel_tickets: int
    coverage_percent: float
    cost_factor: float
    odds_if_chosen_contain_all_winners: float
    base_jackpot_odds: float
    what_it_does: str
    what_it_does_not_do: str


def analyze_wheeling(
    chosen_count: int,
    guarantee_match: int,
    ticket_count: int,
    pool_size: int = 45,
    draw_size: int = 6,
) -> WheelingResult:
    """Analyze a wheel covering `chosen_count` numbers with a `guarantee_match` guarantee."""
    if chosen_count < draw_size or chosen_count > pool_size:
        raise ValueError(f"chosen_count must be in {draw_size}..{pool_size}")
    if guarantee_match < 1 or guarantee_match > draw_size:
        raise ValueError("guarantee_match must be in 1..draw_size")
    if ticket_count < 1:
        raise ValueError("ticket_count must be >= 1")

    full_wheel = comb(chosen_count, draw_size)
    coverage = (ticket_count / full_wheel) * 100.0 if full_wheel else 0.0
    base_odds = comb(pool_size, draw_size)
    odds_if_all_in = base_odds / comb(chosen_count, draw_size) if comb(chosen_count, draw_size) else float("inf")

    return WheelingResult(
        chosen_count=chosen_count,
        guarantee_match=guarantee_match,
        ticket_count=ticket_count,
        pool_size=pool_size,
        draw_size=draw_size,
        full_wheel_tickets=full_wheel,
        coverage_percent=coverage,
        cost_factor=ticket_count,
        odds_if_chosen_contain_all_winners=odds_if_all_in,
        base_jackpot_odds=base_odds,
        what_it_does=(
            f"Guarantees at least a {guarantee_match}-number match IF "
            f"{guarantee_match}+ of your {chosen_count} chosen numbers are among the {draw_size} drawn."
        ),
        what_it_does_not_do=(
            "Does NOT improve expected value per VND spent. House edge is unchanged. "
            "Does NOT predict which numbers to wheel."
        ),
    )


def compare_wheeling_vs_random(wheeling_cost_vnd: int, random_cost_vnd: int, house_edge: float = 0.50) -> Dict[str, object]:
    """Show that EV per VND is identical for wheeling vs random play."""
    if not 0.0 <= house_edge <= 1.0:
        raise ValueError("house_edge must be in [0,1]")
    return {
        "wheeling_cost_vnd": wheeling_cost_vnd,
        "random_cost_vnd": random_cost_vnd,
        "house_edge": house_edge,
        "wheeling_expected_loss_vnd": -wheeling_cost_vnd * house_edge,
        "random_expected_loss_vnd": -random_cost_vnd * house_edge,
        "conclusion": "Expected value per VND is identical. Wheeling redistributes risk; it does not beat the house edge.",
    }


def evaluate_claim(claim: str, chosen_count: int, ticket_count: int, draw_size: int = 6) -> Dict[str, object]:
    """Evaluate a marketing claim about a wheeling system."""
    full = comb(chosen_count, draw_size)
    is_partial = ticket_count < full
    conditional = any(w in claim.lower() for w in ("guarantee", "if", "neu", "dam bao"))
    return {
        "claim": claim,
        "is_partial_wheel": is_partial,
        "is_conditional_guarantee": conditional,
        "full_wheel_would_require": full,
        "this_system_requires": ticket_count,
        "cost_reduction_vs_full": full - ticket_count if is_partial else 0,
        "likely_reality": (
            "Conditional guarantee - only if conditions are met" if conditional
            else "Unconditional guarantee (verify independently)"
        ),
        "expected_value_impact": "None - EV per VND unchanged",
    }


def main() -> None:
    print("Wheeling analysis: Mega 6/45, 10-number wheel, guarantee 4-match, 50 tickets")
    print("=" * 70)
    r = analyze_wheeling(10, 4, 50, pool_size=45, draw_size=6)
    print(f"  Full wheel would need : {r.full_wheel_tickets:,} tickets")
    print(f"  This wheel uses       : {r.ticket_count} tickets ({r.coverage_percent:.1f}% coverage)")
    print(f"  Cost factor vs 1 tick : {r.cost_factor}x")
    print(f"  Base jackpot odds     : 1 in {r.base_jackpot_odds:,}")
    print(f"  If all 6 winners in 10: 1 in {r.odds_if_chosen_contain_all_winners:,.0f}")
    print(f"  Does  : {r.what_it_does}")
    print(f"  Doesn't: {r.what_it_does_not_do}")

    print("\nWheeling vs random (2,100,000 VND each, 50% house edge):")
    print(compare_wheeling_vs_random(2_100_000, 2_100_000, 0.50))

    print("\nClaim evaluation:")
    print(evaluate_claim("Dam bao trung 4 so neu 5/10 so cua ban trung!", 10, 50))


if __name__ == "__main__":
    main()
