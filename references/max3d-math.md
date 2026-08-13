# Max 3D Mathematics (Vietlott) — fixed-odds digit game

## Foundation

- Feller, W. (1968). *An Introduction to Probability Theory*. (independent Bernoulli trials, binomial aggregation)
- Vietlott published Max 3D / Max 3D+ / Max 3D Pro rules.

This reference covers Max 3D's fixed-odds 3-digit structure. All odds here are produced by `scripts/max3d_calculator.py` and baked into `config/games.json` via `scripts/seed_games.py`.

## Why Max 3D is structurally different from Mega/Power

Mega and Power are **pari-mutuel jackpot** games: prize pools depend on sales and are split among winners. Max 3D is **fixed-odds**: each 3-digit outcome (000-999) is equally likely (1 in 1,000), and payouts are fixed regardless of how many players win the same number.

**Implication:** unlike Mega/Power, Max 3D has no "shared prize" risk and no accumulating jackpot. The per-ticket EV is a simple function of `prize / odds - cost`.

## Per-number exact match

A single 3-digit number has a 1/1,000 chance of matching the drawn number exactly. The lottery draws ONE 3-digit number; each chosen number is an independent Bernoulli(1/1000) trial against that drawn number.

## Modes and odds (per 10,000 VND ticket)

Prize amounts are representative (verify current official figures at https://vietlott.vn); odds are exact.

### Max 3D (single — 1 chosen number)

| matches | prize (VND) | odds (1 in) |
|--------:|-----------:|------------:|
| 1 (exact) | 500,000 | 1,000 |

EV = 500,000/1,000 - 10,000 = 500 - 10,000 = **-9,500 VND**. House edge = 95.0% (at representative prize).

### Max 3D+ (two chosen numbers)

The count of matches across 2 independent numbers is Binomial(2, 1/1000).

| matches | prize (VND) | probability | odds (1 in) |
|--------:|-----------:|------------:|------------:|
| 2 (both exact) | 1,000,000 | 1.00e-6 | 1,000,000 |
| 1 (one exact) | 500,000 | 1.998e-3 | 500.5 |

EV = 1,000,000/1,000,000 + 500,000/500.5 - 10,000 = 1 + 998 - 10,000 = **-9,001 VND**. House edge = 90.0%.

### Max 3D Pro (three chosen numbers)

The count of matches across 3 independent numbers is Binomial(3, 1/1000).

| matches | prize (VND) | probability | odds (1 in) |
|--------:|-----------:|------------:|------------:|
| 3 (all exact) | 1,500,000 | 1.00e-9 | 1,000,000,000 |
| 2 (two exact) | 1,000,000 | 2.997e-6 | 333,667 |
| 1 (one exact) | 500,000 | 2.994e-3 | 334.0 |

EV = 1,500,000/1e9 + 1,000,000/333,667 + 500,000/334 - 10,000 = 0.0015 + 2.997 + 1,497.0 - 10,000 = **-8,500 VND**. House edge = 85.0%.

## Teaching points

1. **Fixed-odds vs pari-mutuel:** Max 3D payouts do not change with how many people win. This is the opposite of Mega/Power jackpots, which are shared. Both still have negative EV.

2. **The "easy odds" illusion:** 1 in 1,000 *sounds* easy compared to 1 in 8 million, but the prize is priced so that the expected loss per 10,000 VND is even *larger* than Mega's at a representative jackpot. "Easier to win" is fully offset by "pays much less relative to odds."

3. **Multiple numbers don't help:** adding numbers (Plus/Pro) raises win frequency slightly but the EV stays strongly negative because the top-tier prizes are astronomically unlikely (1 in 1,000,000 / 1,000,000,000).

4. **House edge depends on the current prize:** if Max 3D single pays more than 500,000 VND (verify official), the edge is lower; if less, higher. Compute with `scripts/max3d_calculator.py expected_value(mode)`.

## Common misconceptions

### "1 in 1,000 la de trung, nen Max 3D la lua chon tot nhat" (1-in-1000 is easy, so Max 3D is best)

Reality: per-ticket odds are the easiest, but the EV is the most negative because the prize is small relative to the odds. "Easy to win" and "good value" are different things. Always compare EV, not raw odds.

### "Chon them so (Plus/Pro) se tang co hoi" (more numbers = better odds)

Reality: more numbers raise the chance of *some* match but the prize tiers are tuned so EV stays negative. The top tier (all exact) is so rare it contributes near zero to EV.

## Independence

Each Max 3D draw is independent. A number that "hit" yesterday has exactly 1/1,000 again today. See `cognitive-biases.md` for the gambler's-fallacy application to digit games.

## Calculation verification

Run `python scripts/max3d_calculator.py` to reproduce every figure above. `python scripts/seed_games.py` regenerates `config/games.json` from this calculator.

## Related Reference Files

- `combinatorics.md` — general Vietlott odds framework
- `expected-value.md` — EV methodology
- `keno-math.md` — the other non-jackpot format
- `cognitive-biases.md` — digit-game fallacies
