#!/usr/bin/env python3
"""
Faithful synthetic Vietlott draw generator (offline/CI fixture).

Generates draws sampled from the EXACT Vietlott probability distributions:
  - Mega 6/45: 6 distinct numbers from 1..45 (uniform without replacement)
  - Power 6/55: 6 distinct from 1..55 + 1 bonus from the remaining 49
  - Keno: 20 distinct from 1..80
  - Max 3D: one 3-digit outcome 000..999 (uniform)

Every generated draw is labeled source="synthetic" so it is NEVER mistaken for
real Vietlott history. This fixture exists ONLY so the ingestion + independence
analysis pipeline is runnable in CI without network access. Real ingested data
(config/ingestion.json active csv_file/http_json sources) always takes precedence.

Backend for the synthetic source type in scripts/ingest_results.py.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional


GAME_PARAMS = {
    "mega_6_45": {"pool": 45, "draw": 6, "bonus": False, "keno20": False, "max3d": False},
    "power_6_55": {"pool": 55, "draw": 6, "bonus": True, "bonus_pool": 49, "keno20": False, "max3d": False},
    "keno": {"pool": 80, "draw": 20, "bonus": False, "keno20": True, "max3d": False},
    "max_3d": {"pool": 1000, "draw": 0, "bonus": False, "keno20": False, "max3d": True},
}


@dataclass(frozen=True)
class SyntheticDraw:
    game: str
    draw_id: str
    source: str
    numbers: List[int]
    bonus: Optional[int]
    three_digit: Optional[str]
    draw_date: Optional[str]

    def to_dict(self) -> Dict:
        return {
            "game": self.game,
            "draw_id": self.draw_id,
            "source": self.source,
            "draw_date": self.draw_date,
            "numbers": self.numbers,
            "bonus": self.bonus,
            "three_digit": self.three_digit,
            "extra": {"synthetic": True, "generator": "generate_synthetic_results"},
        }


def generate_one(game: str, rng: random.Random, index: int) -> SyntheticDraw:
    p = GAME_PARAMS[game]
    draw_id = f"synthetic-{game}-{index:06d}"
    if p["max3d"]:
        val = rng.randrange(1000)
        return SyntheticDraw(game, draw_id, "synthetic", [], None, f"{val:03d}", None)
    numbers = sorted(rng.sample(range(1, p["pool"] + 1), p["draw"]))
    bonus = None
    if p["bonus"]:
        remaining = [n for n in range(1, p["pool"] + 1) if n not in numbers]
        bonus = rng.choice(remaining)
    return SyntheticDraw(game, draw_id, "synthetic", numbers, bonus, None, None)


def generate(game: str, count: int, seed: int) -> List[SyntheticDraw]:
    if game not in GAME_PARAMS:
        raise ValueError(f"unknown game: {game}; known: {list(GAME_PARAMS)}")
    if count <= 0:
        raise ValueError("count must be positive")
    rng = random.Random(seed)
    return [generate_one(game, rng, i) for i in range(count)]


def main() -> None:
    import json
    import sys
    game = sys.argv[1] if len(sys.argv) > 1 else "mega_6_45"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20260810
    draws = generate(game, count, seed)
    for d in draws:
        print(json.dumps(d.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
