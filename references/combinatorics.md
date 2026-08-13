# Combinatorics & Vietlott Odds Calculation

## Foundation

**Source:** Feller, W. (1968). *An Introduction to Probability Theory and Its Applications, Vol. 1* (3rd ed.). Wiley.
**Secondary:** Haigh, J. (1997). *Taking Chances: Winning with Probability*. Oxford University Press.
**Vietlott structure source:** Vietlott (Vietnam Lottery Company), published game rules for Mega 6/45, Power 6/55, Keno, and Max 3D.

This reference provides the combinatorial foundation for every Vietlott game format. All probabilities and odds below are **derived from first principles** by `scripts/combinatorics.py`, `scripts/keno_calculator.py`, and `scripts/max3d_calculator.py`; prize *amounts* are representative (verify current official figures at https://vietlott.vn).

## Core Concepts

### Binomial Coefficient (nCr)

Number of ways to choose r items from n distinct items, order irrelevant:

```
C(n,r) = n! / (r! * (n-r)!)
```

### Sample Space

For a jackpot draw of r numbers from a pool of n, sample-space size = `C(n,r)` and every combination is equally likely (assuming a fair machine).

### Match-k probability (single pool, no bonus)

```
P(match k) = C(r,k) * C(n-r, r-k) / C(n,r)
```

- `C(r,k)`: ways to pick k winning numbers from the r drawn
- `C(n-r, r-k)`: ways to pick the remaining (r-k) ticket numbers from the (n-r) non-winning numbers
- `C(n,r)`: total combinations

### Bonus-ball format (Power 6/55)

Power 6/55 draws 6 main numbers from 55, then 1 bonus ball from the remaining 49. Sample space of full draws = `C(55,6) * 49`.

- `P(match 6 main) = 1 / C(55,6)`
- `P(match 5 main + bonus) = [C(6,5)*C(49,1)/C(55,6)] * (1/49) = 6 / C(55,6)`
- `P(match 5 main, no bonus) = [C(6,5)*C(49,1)/C(55,6)] * (48/49) = 288 / C(55,6)`
- General pattern: main match count uses the single-pool formula; the bonus is a 1/(55-6)=1/49 Bernoulli applied to the ticket's non-matching slot(s).

## Per-Format Odds (Vietlott) — combinatorially derived

### Mega 6/45 (single pool, no bonus)

Pool n=45, draw r=6. `C(45,6) = 8,145,060`.

| Match | Favorable | Odds (1 in) | Typical prize (VND) |
|------:|----------:|------------:|----------------------|
| 6 | 1 | 8,145,060 | Jackpot (pari-mutuel, min ~12,000,000,000) |
| 5 | 234 | 34,808 | ~10,000,000 (pari-mutuel) |
| 4 | 11,115 | 733 | 300,000 (fixed) |
| 3 | 182,780 | 45 | 30,000 (fixed) |

P(any prize) = 0.02383 -> about 1 in 42.

Derivations:
- Match 6: `C(6,6)*C(39,0)/C(45,6) = 1/8,145,060`
- Match 5: `C(6,5)*C(39,1)/C(45,6) = 6*39/8,145,060 = 234/8,145,060 = 1/34,808`
- Match 4: `C(6,4)*C(39,2)/C(45,6) = 15*741/8,145,060 = 11,115/8,145,060 = 1/733`
- Match 3: `C(6,3)*C(39,3)/C(45,6) = 20*9,139/8,145,060 = 182,780/8,145,060 = 1/44.56 ~ 1/45`

### Power 6/55 (single pool + 1 bonus from remaining 49)

Pool n=55, draw r=6 main + 1 bonus from 49. `C(55,6) = 28,989,675`; full sample space = `28,989,675 * 49`.

| Match (main+bonus) | Favorable (of 1.42B draws) | Odds (1 in) | Typical prize (VND) |
|------:|------:|------:|----------------------|
| 6+0 (Jackpot) | 49 | 28,989,675 | ~30,000,000,000 (pari-mutuel) |
| 5+1 | 294 | 4,831,613 | ~40,000,000 (pari-mutuel) |
| 5+0 | 14,112 | 100,659 | ~1,000,000 (fixed) |
| 4+1 | 35,280 | 40,263 | ~100,000 (fixed) |
| 4+0 | 829,080 | 1,713 | ~100,000 (fixed) |
| 3+1 | 1,105,440 | 1,285 | ~30,000 (fixed) |
| 3+0 | 16,950,080 | 84 | ~30,000 (fixed) |
| 2+1 | 12,712,560 | 112 | ~20,000 (fixed) |

P(any prize) = 0.02228 -> about 1 in 45.

**Reconciliation note:** Vietlott's published marketing odds may round these values differently. The derived figures are mathematically exact given the draw mechanism (6 main + 1 bonus from the remaining 49). When teaching, show the derivation and cite the published figure side by side; small differences are rounding, **not** a predictive signal.

### Keno (rapid-draw hypergeometric, 20 of 80)

Player selects s (1-10) numbers; lottery draws 20 of 80. Probability of matching exactly m:

```
P(match m | select s) = C(s,m) * C(80-s, 20-m) / C(80,20)
```

Keno is **not** a single-combination jackpot; it is a hypergeometric match-count distribution with a payout per tier. See `references/keno-math.md` for the full per-select prize tables and EV (all tiers sum to probability 1.0; verified by `scripts/keno_calculator.py`).

### Max 3D (fixed-odds digit game)

Pool = 1,000 three-digit outcomes (000-999), equally likely. Single-number exact match = 1/1,000. Each chosen number is an independent Bernoulli(1/1000) against the single drawn number, so the match count across k chosen numbers is Binomial(k, 1/1000). See `references/max3d-math.md`.

## Step-by-Step Calculation Template

1. **Identify format & parameters:** Mega 6/45 / Power 6/55 / Keno / Max 3D; n, r, bonus rule, match requirement k.
2. **Sample space:** `C(n,r)` (single pool) or `C(n,r) * bonus_pool` (bonus format).
3. **Favorable outcomes:** single pool `C(r,k)*C(n-r,r-k)`; bonus format `main_favorable * bonus_factor`.
4. **Probability & odds:** `P = favorable/sample_space`; `odds = 1/P` ("1 in N").
5. **Cross-check:** verify against `config/games.json` and the corresponding script output; reconcile any rounding.

## Practical Interpretations (Vietnam context)

**Mega 6/45 jackpot (1 in 8,145,060):**
- Roughly flipping heads ~23 times in a row.
- Like picking one specific person from Hanoi + HCMC + Da Nang (~8 million) in a single try.
- A 10,000 VND ticket = ~0.0000123% jackpot chance.

**Power 6/55 jackpot (1 in 28,989,675):**
- Roughly flipping heads ~25 times in a row.
- About picking one specific second from ~336 days.
- Far less likely than being struck by lightning in Vietnam in a given year.

**Keno (select 10, match 10) top prize (1 in ~8,911,711):**
- Comparable per-draw magnitude to the Mega jackpot — but Keno draws every ~10 minutes, so the dominant risk is *frequency*, not per-draw difficulty.

**Max 3D single (1 in 1,000):**
- The "easiest" Vietlott prize per-ticket, but the prize is fully priced into the odds. The apparent "good odds" are not an advantage.

## Multiple Tickets

N distinct tickets improve odds by exactly factor N (assuming different combinations):

```
1 Mega ticket   : 1 in 8,145,060
100 tickets     : 1 in 81,451
1,000 tickets   : 1 in 8,146   (cost 10,000,000 VND, still ~1-in-8,146 jackpot, ~5,000,000 VND expected loss)
```

Buying more tickets does **not** change the negative expected value per VND spent.

## Common Misconceptions (preview; full treatment in `cognitive-biases.md`)

1. "Soi cau / du doan theo so lan xuat hien" — frequency-based prediction does not work; each draw is independent.
2. "Cap so dep / ngay sinh / ngay chung" — every specific combination has the same probability.
3. "Keno quay nhanh nen de trung hon" — per-draw Keno odds are comparable to jackpot games; the danger is frequency.

## Calculation Verification

1. Show intermediate factorial/binomial steps.
2. Verify probabilities are in [0,1] and odds > 1.
3. Cross-check with `config/games.json` (regenerated by `scripts/seed_games.py`).
4. Use exact fractions before converting to decimals.
5. For Keno/Max 3D aggregate tiers, run the corresponding calculator script for exact values.

## Teaching Tips

### For math-anxious users
- Start with a coin-flip analogy (Vietnamese: tung dong xuat).
- Use VND amounts and familiar prices (e.g., a banh mi ~30,000 VND).
- Emphasize order of magnitude (millions) over exact figures.

### For math-comfortable users
- Show the binomial-coefficient formula.
- Derive the bonus-ball factor explicitly for Power 6/55.
- Demonstrate Keno's hypergeometric distribution and Max 3D's binomial aggregation.

## Related Reference Files

- `cognitive-biases.md` — why users misread these probabilities
- `expected-value.md` — what these odds mean for spending
- `keno-math.md` — full Keno hypergeometric + EV
- `max3d-math.md` — Max 3D fixed-odds math
- `wheeling-systems.md` — covering systems on Mega/Power
