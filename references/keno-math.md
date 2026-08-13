# Keno Mathematics (Vietlott) — rapid-draw hypergeometric

## Foundation

- Feller, W. (1968). *An Introduction to Probability Theory and Its Applications*. (hypergeometric distribution)
- Croson, R., & Sundali, J. (2005). *The Gambler's Fallacy and the Hot Hand: Empirical Data from Casinos*. Journal of Risk and Uncertainty. (rapid-draw fallacy research)
- Vietlott published Keno rules (Co ban / Trung lon / Lon-Nho modes).

This reference covers Keno's distinctive structure: a rapid-draw, hypergeometric match-count game. All odds here are produced by `scripts/keno_calculator.py` and baked into `config/games.json` via `scripts/seed_games.py`.

## Why Keno is structurally different from Mega/Power

Mega 6/45 and Power 6/55 are **single-combination jackpot** games: one ticket = one combination, drawn once/day. Keno is a **rapid-draw hypergeometric** game:

- Pool = 80 numbers; draw = 20 numbers; draw every ~10 minutes (~144 draws/day).
- Player selects s in 1..10 numbers.
- Match count m follows the hypergeometric distribution:

```
P(match m | select s) = C(s,m) * C(80-s, 20-m) / C(80,20)
```

- Prizes are paid per match tier (multiple winning tiers per ticket), not a single jackpot.
- Distribution sanity check: for every s, sum over m of P(match m) = 1.0 (verified by `scripts/keno_calculator.py validate_distribution`).

## Co ban prize table + exact odds (per 10,000 VND ticket)

Only winning tiers are shown; non-listed match counts pay 0 VND. Odds are exact (computed), prize amounts are the published representative values (verify at https://vietlott.vn).

| select | match | prize (VND) | odds (1 in) |
|-------:|------:|------------:|------------:|
| 1 | 1 | 20,000 | 4.00 |
| 2 | 2 | 90,000 | 16.63 |
| 3 | 3 | 180,000 | 72.07 |
| 3 | 2 | 20,000 | 7.21 |
| 4 | 4 | 400,000 | 326.44 |
| 4 | 3 | 20,000 | 23.12 |
| 4 | 2 | 20,000 | 4.70 |
| 5 | 5 | 4,400,000 | 1,550.57 |
| 5 | 4 | 100,000 | 82.70 |
| 5 | 3 | 20,000 | 11.91 |
| 6 | 6 | 12,000,000 | 7,752.84 |
| 6 | 5 | 300,000 | 323.04 |
| 6 | 4 | 30,000 | 35.04 |
| 6 | 3 | 20,000 | 7.70 |
| 7 | 7 | 47,000,000 | 40,979.31 |
| 7 | 6 | 1,000,000 | 1,365.98 |
| 7 | 5 | 100,000 | 115.76 |
| 7 | 4 | 30,000 | 19.16 |
| 7 | 3 | 20,000 | 5.71 |
| 8 | 8 | 200,000,000 | 230,114.61 |
| 8 | 7 | 4,000,000 | 6,232.27 |
| 8 | 6 | 200,000 | 422.53 |
| 8 | 5 | 50,000 | 54.64 |
| 8 | 0 | 20,000 | 11.33 |
| 9 | 9 | 600,000,000 | 1,380,687.65 |
| 9 | 8 | 20,000,000 | 30,681.95 |
| 9 | 7 | 1,000,000 | 1,690.11 |
| 9 | 6 | 100,000 | 174.84 |
| 9 | 5 | 30,000 | 30.67 |
| 9 | 4 | 20,000 | 8.76 |
| 10 | 10 | 2,000,000,000 | 8,911,711.18 |
| 10 | 9 | 100,000,000 | 163,381.37 |
| 10 | 8 | 5,000,000 | 7,384.47 |
| 10 | 7 | 200,000 | 620.68 |
| 10 | 6 | 50,000 | 87.11 |
| 10 | 5 | 30,000 | 19.44 |
| 10 | 0 | 20,000 | 21.84 |

## Expected value per select (Co ban, 10,000 VND ticket)

| select | expected winnings (VND) | EV (VND) | house edge |
|-------:|------------------------:|---------:|-----------:|
| 1 | 5,000 | -5,000 | 50.0% |
| 2 | 5,411 | -4,589 | 45.9% |
| 3 | 5,273 | -4,727 | 47.3% |
| 4 | 6,343 | -3,657 | 36.6% |
| 5 | 5,726 | -4,274 | 42.7% |
| 6 | 5,929 | -4,071 | 40.7% |
| 7 | 7,808 | -2,192 | 21.9% |
| 8 | 4,665 | -5,335 | 53.4% |
| 9 | 5,510 | -4,490 | 44.9% |
| 10 | 4,868 | -5,132 | 51.3% |

**Key teaching points:**
- All selects have negative EV. The lowest house edge is select 7 (~22%).
- House edge is non-monotonic in select count — more numbers is not automatically better.
- "Match 0" pays for select 8/10 (a designed consolation), which slightly raises win frequency but not EV.

## The frequency risk: why per-draw edge misleads

Keno draws ~144 times/day. A 22% house edge (select 7) means ~2,192 VND expected loss per ticket. Playing just 10 draws/day = ~21,920 VND/day expected loss = ~657,600 VND/month = ~7.9M VND/year — far exceeding a once-daily Mega player's expected loss, despite Keno's "lower" per-draw edge.

**Teaching framing:**
```
Keno's per-draw edge is the lowest in Vietlott. That is NOT the same as
"cheapest to play." Keno's danger is the 10-minute draw cadence:
- Mega/Power: 1 draw/day  -> 1 EV event/day
- Keno: ~144 draws/day    -> 144 EV events/day

Always compare expected loss over the SAME time horizon, not per draw.
```

## Other Keno modes (structural note)

- **Trung lon (Big-Win):** select 10-12; only top tiers pay. Higher volatility, same negative EV; appeals to "big-win" psychology (linked to availability heuristic, see `cognitive-biases.md`).
- **Lon / Nho (Big/Small):** bet that >13 of the 20 drawn numbers are >40 (Lon) or <=40 (Nho). Near even-money minus house edge. Low volatility, still negative EV.

## Independence and the rapid-draw fallacy

Croson & Sundali (2005) document that rapid-draw games intensify gambler's-fallacy and hot-hand beliefs: players see "streaks" across rapid draws and infer patterns. Each Keno draw is statistically independent. A "hot" set of 20 numbers in one draw says nothing about the next draw 10 minutes later. See `cognitive-biases.md` §1-2.

## Calculation verification

Run `python scripts/keno_calculator.py` to reproduce every figure above and confirm distribution sums equal 1.0. `python scripts/seed_games.py` regenerates `config/games.json` from this calculator.

## Related Reference Files

- `combinatorics.md` — general Vietlott odds framework
- `expected-value.md` — EV methodology
- `cognitive-biases.md` — rapid-draw fallacies
- `max3d-math.md` — the other non-jackpot format
