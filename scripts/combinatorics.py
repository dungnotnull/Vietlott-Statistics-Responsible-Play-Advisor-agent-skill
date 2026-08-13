#!/usr/bin/env python3
"""
Combinatorics & odds calculation for Vietlott jackpot-format games.

Implements:
  - Single-pool odds (Mega 6/45): match-k probability via C(r,k)*C(n-r,r-k)/C(n,r)
  - Bonus-ball odds (Power 6/55): 6 main from 55, 1 bonus from remaining 49
  - Generic nCr helper with validation

This is the executable backend behind the `calculate_odds` tool schema in
SKILL.md. It is import-safe (no side effects on import) and CLI-runnable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Dict, List, Optional


def ncr(n: int, r: int) -> int:
    """Binomial coefficient C(n, r) with input validation."""
    if n < 0 or r < 0:
        raise ValueError("n and r must be non-negative")
    if r > n:
        return 0
    return comb(n, r)


@dataclass(frozen=True)
class SinglePoolOdds:
    pool_size: int
    numbers_drawn: int
    match: int
    sample_space: int
    favorable: int
    probability: float
    odds: float

    @property
    def odds_label(self) -> str:
        return f"1 in {int(round(self.odds)):,}"


def single_pool_match_odds(pool_size: int, numbers_drawn: int, match: int) -> SinglePoolOdds:
    """Odds of matching exactly `match` of the drawn numbers in a single-pool draw.

    Used for Mega 6/45 and the main-number portion of Power 6/55.
    """
    if numbers_drawn > pool_size:
        raise ValueError("numbers_drawn cannot exceed pool_size")
    if match < 0 or match > numbers_drawn:
        raise ValueError("match must be in 0..numbers_drawn")
    sample_space = ncr(pool_size, numbers_drawn)
    favorable = ncr(numbers_drawn, match) * ncr(pool_size - numbers_drawn, numbers_drawn - match)
    probability = favorable / sample_space
    odds = sample_space / favorable if favorable else float("inf")
    return SinglePoolOdds(
        pool_size=pool_size,
        numbers_drawn=numbers_drawn,
        match=match,
        sample_space=sample_space,
        favorable=favorable,
        probability=probability,
        odds=odds,
    )


@dataclass(frozen=True)
class BonusOdds:
    main_match: int
    bonus_match: bool
    favorable: int
    probability: float
    odds: float

    @property
    def odds_label(self) -> str:
        return f"1 in {int(round(self.odds)):,}"


def bonus_pool_match_odds(pool_size: int, numbers_drawn: int, main_match: int, bonus_match: bool) -> BonusOdds:
    """Ods for a Power 6/55-style bonus draw.

    The draw selects `numbers_drawn` main numbers from `pool_size`, then 1 bonus
    ball from the remaining (pool_size - numbers_drawn) balls. A ticket holds
    `numbers_drawn` numbers. `main_match` is how many of the ticket's numbers
    equal a main winner; `bonus_match` indicates whether the bonus equals one
    of the ticket's non-matching numbers.
    """
    if numbers_drawn > pool_size:
        raise ValueError("numbers_drawn cannot exceed pool_size")
    if main_match < 0 or main_match > numbers_drawn:
        raise ValueError("main_match must be in 0..numbers_drawn")
    bonus_pool = pool_size - numbers_drawn
    non_matching = numbers_drawn - main_match
    if bonus_match and non_matching == 0:
        # Cannot match the bonus if every ticket number is already a main winner.
        return BonusOdds(main_match, bonus_match, favorable=0, probability=0.0, odds=float("inf"))

    main_favorable = ncr(numbers_drawn, main_match) * ncr(bonus_pool, numbers_drawn - main_match)
    bonus_factor = non_matching if bonus_match else (bonus_pool - non_matching)
    sample_space = ncr(pool_size, numbers_drawn) * bonus_pool
    favorable = main_favorable * bonus_factor
    probability = favorable / sample_space
    odds = sample_space / favorable if favorable else float("inf")
    return BonusOdds(
        main_match=main_match,
        bonus_match=bonus_match,
        favorable=favorable,
        probability=probability,
        odds=odds,
    )


def mega_6_45_table() -> List[Dict[str, object]]:
    """Full match-tier odds table for Mega 6/45 (VND prizes illustrative/fixed)."""
    prizes = {6: 12_000_000_000, 5: 10_000_000, 4: 300_000, 3: 30_000}
    pari_mutuel = {6: True, 5: True, 4: False, 3: False}
    rows = []
    for match in (6, 5, 4, 3):
        o = single_pool_match_odds(45, 6, match)
        rows.append(
            {
                "match": match,
                "prize_name": {6: "Jackpot", 5: "Giai Nhi", 4: "Giai Ba", 3: "Giai Tu"}[match],
                "prize_vnd": prizes[match],
                "pari_mutuel": pari_mutuel[match],
                "favorable": o.favorable,
                "probability": o.probability,
                "odds_1_in": round(o.odds, 4),
            }
        )
    return rows


def power_6_55_table() -> List[Dict[str, object]]:
    """Full match-tier odds table for Power 6/55 (bonus-ball format).

    Prize amounts are illustrative representative values; pari-mutuel tiers
    (Jackpot, Giai Nhat) vary draw to draw. Odds are exact combinatorial values.
    """
    # (main_match, bonus_match, prize_vnd, prize_name, pari_mutuel)
    tiers = [
        (6, False, 30_000_000_000, "Giai Dac biet (Jackpot)", True),
        (5, True, 40_000_000, "Giai Nhat (5+bonus)", True),
        (5, False, 1_000_000, "Giai Nhi (5)", False),
        (4, True, 100_000, "Giai Ba (4+bonus)", False),
        (4, False, 100_000, "Giai Tu (4)", False),
        (3, True, 30_000, "Giai Nam (3+bonus)", False),
        (3, False, 30_000, "Giai Luc (3)", False),
        (2, True, 20_000, "Giai Bay (2+bonus)", False),
    ]
    rows = []
    for main_match, bonus_match, prize, name, pm in tiers:
        o = bonus_pool_match_odds(55, 6, main_match, bonus_match)
        rows.append(
            {
                "match": f"{main_match}+{1 if bonus_match else 0}",
                "prize_name": name,
                "prize_vnd": prize,
                "pari_mutuel": pm,
                "favorable": o.favorable,
                "probability": o.probability,
                "odds_1_in": round(o.odds, 4),
            }
        )
    return rows


def format_odds(result: SinglePoolOdds) -> str:
    return (
        f"Match {result.match} of {result.numbers_drawn} from {result.pool_size}: "
        f"odds {result.odds_label} | P={result.probability:.6f}"
    )


def main() -> None:
    print("Mega 6/45 odds")
    print("=" * 60)
    for row in mega_6_45_table():
        print(f"  match {row['match']}: 1 in {row['odds_1_in']:,}  ({row['prize_name']})")

    print("\nPower 6/55 odds (bonus-ball format, combinatorially derived)")
    print("=" * 60)
    for row in power_6_55_table():
        print(f"  {row['match']:>4}: 1 in {row['odds_1_in']:>14,}  ({row['prize_name']})")

    print("\nAny-prize probability Power 6/55:")
    any_prize = sum(r["probability"] for r in power_6_55_table())
    print(f"  P(any prize) = {any_prize:.6f}  -> 1 in {1/any_prize:,.1f}")

    print("\nAny-prize probability Mega 6/45:")
    any_prize_mega = sum(r["probability"] for r in mega_6_45_table())
    print(f"  P(any prize) = {any_prize_mega:.6f}  -> 1 in {1/any_prize_mega:,.1f}")


if __name__ == "__main__":
    main()
