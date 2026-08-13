# Expected Value & House Edge (Vietlott, VND)

## Foundation

**Primary sources:**
- Haigh, J. (1997). *Taking Chances: Winning with Probability*. Oxford University Press.
- Clotfelter, C., & Cook, P. (1989). *Selling Hope: State Lotteries in America*. Harvard University Press.
- Vietlott published prize structures for Mega 6/45, Power 6/55, Keno, Max 3D.

This reference explains expected-value (EV) and house-edge calculations in VND and frames lottery spending as entertainment cost, not investment. All numeric examples are reproducible via `scripts/expected_value.py` reading `config/games.json`.

## Core Concepts

### Expected Value (EV)

Average outcome per trial if repeated many times:

```
EV = sum( P(outcome_i) * Value(outcome_i) ) - Ticket_Cost
```

For a Vietlott ticket:

```
EV(ticket) = sum( Prize_VND_i / Odds_i ) - Ticket_Cost_VND
```

### House Edge

```
House_Edge_% = (Ticket_Cost - Expected_Winnings) / Ticket_Cost * 100%
```

Vietlott house edges span a wide range by format (representative values, verify current prizes):
- Mega 6/45: ~50-72% depending on accumulated jackpot size (pari-mutuel)
- Power 6/55: ~50-83% (pari-mutuel jackpot; bonus tiers add small-win frequency but not positive EV)
- Keno Co ban: ~22-54% by select count (select 7 lowest, select 8 highest)
- Max 3D single: very high (~95% at a representative 500,000 VND prize) — verify current official prize

## Calculation Framework

### Worked example: Mega 6/45 (representative jackpot 12,000,000,000 VND)

Ticket cost: 10,000 VND.

| Tier | Prize (VND) | Odds (1 in) | Contribution (VND) |
|------|------------:|------------:|--------------------:|
| Jackpot | 12,000,000,000 | 8,145,060 | 1,473.29 |
| Giai Nhi | 10,000,000 | 34,808 | 287.29 |
| Giai Ba | 300,000 | 733 | 409.39 |
| Giai Tu | 30,000 | 45 | 673.22 |

Expected winnings = 2,843.18 VND. EV = 2,843.18 - 10,000 = **-7,156.82 VND**. House edge = 71.6%.

> Note: this EV is sensitive to the assumed jackpot. At a smaller (typical, non-accumulated) jackpot the house edge is higher; at a very large accumulated jackpot it is lower but still negative because the jackpot is shared (pari-mutuel) and ticket sales rise with jackpot size.

### Worked example: Keno select 7 (lowest house edge)

| Tier | Prize (VND) | Odds (1 in) | Contribution (VND) |
|------|------------:|------------:|--------------------:|
| match 7 | 47,000,000 | 40,979 | 1,146.92 |
| match 6 | 1,000,000 | 1,366 | 732.08 |
| match 5 | 100,000 | 116 | 863.85 |
| match 4 | 30,000 | 19.16 | 1,565.73 |
| match 3 | 20,000 | 5.71 | 3,499.87 |

Expected winnings = 7,808.45 VND. EV = -2,191.55 VND. House edge = 21.9% — the lowest of any Vietlott Co ban select. **But** Keno draws every ~10 minutes (~144 draws/day), so even a 22% edge compounds rapidly with frequency.

### Worked example: Max 3D single

Single exact match: 500,000 VND at 1 in 1,000 -> expected winnings = 500 VND. EV = 500 - 10,000 = **-9,500 VND**. House edge = 95.0% (at the representative prize; verify current official prize). Fixed-odds means this payout is constant regardless of how many players win.

## Long-Term Perspective (VND)

For a player spending 200,000 VND/week on Vietlott at a 50% house edge:

- Weekly expected loss: 100,000 VND
- Annual expected loss: 5,200,000 VND
- 10-year expected loss: 52,000,000 VND
- If the same 200,000 VND/week were invested at 7%/yr instead: ~143,700,000 VND after 10 years

Use `scripts/expected_value.py long_term_projection()` for arbitrary inputs.

## Entertainment Value Framing (Vietnamese context)

Compare weekly lottery spend to other VND entertainment costs (illustrative):

| Activity | Cost (VND) | Hours | VND/hour |
|----------|-----------:|------:|---------:|
| Lottery (200k/week, ~3 days anticipation) | 200,000 | 72 | 2,778 |
| Cinema ticket | 100,000 | 2 | 50,000 |
| Coffee outing | 60,000 | 1.5 | 40,000 |
| Gym (1 month) | 400,000 | 30 | 13,333 |
| A novel | 120,000 | 8 | 15,000 |

On a per-hour basis lottery looks cheap, but only because "anticipation" is counted generously. The honest frame: you are paying for the experience of hoping, and you should expect to lose most of what you spend.

## Common Misconceptions

### "Jackpot cao len thi co khang co duong (EV duong)"

Reality: Even at very large accumulated jackpots, EV stays negative because (1) the jackpot is pari-mutuel and split among winners, (2) ticket sales spike as jackpots rise (raising split probability), and (3) taxes/annuity discounting apply. If a lottery ever offered positive EV, institutional buyers would purchase every combination — that does not happen because the math does not allow it.

### "Keno de trung nen an (Keno is easier to win)"

Reality: Keno's *per-draw* house edge is the lowest in the Vietlott lineup, but the ~10-minute draw cadence is the dominant risk. 144 draws/day means 144 independent chances to lose EV per day. Frequency, not per-draw odds, is the harm amplifier.

### "Trung nho chung minh dang len (small wins prove I'm ahead)"

Reality: Small wins are baked into the EV calculation and the house edge. The house edge of ~50% means: for every 100,000 VND spent, players get back ~50,000 VND across all prize sizes; the operator keeps ~50,000 VND. Small wins are designed in, not a sign of beating the game.

## Teaching Strategies

1. **Transparency:** always show the full step-by-step calculation (the skill's `calculate_expected_value` tool does this).
2. **Contextualize:** use VND and familiar Vietnamese prices (banh mi, cinema, coffee).
3. **Frame as entertainment:** "I spend 200,000 VND/week for the excitement; I expect to lose most of it; that is my entertainment budget."
4. **Show opportunity cost:** the investment-alternative comparison above.

## EV Calculator Template (Vietlott)

```
# Expected Value Analysis for [Game]

## Game parameters
- Ticket cost: [X] VND
- Prize structure: [tiers with VND and odds]

## Calculation
[step-by-step contributions per tier]

## Results
- Expected winnings/ticket: [Y] VND
- Expected loss/ticket: [X - Y] VND
- House edge: [Z]%
- P(any prize): [p]

## What this means
- For every 100,000 VND spent, expect to lose [100,000 * house edge] VND.
- Weekly spend of [W] VND -> annual expected loss [W * 52 * house edge] VND.

## Entertainment framing
[compare to VND entertainment costs]

## Recommendation
Treat Vietlott as entertainment, not investment. Only spend what you can afford to lose for the enjoyment of playing.
```

## Special Cases

### Progressive/accumulated jackpots (Mega/Power)
EV rises with jackpot size but stays negative due to pari-mutuel splitting, sales spikes, and (where applicable) tax/annuity effects. Teaching point: "even a 100-billion-VND jackpot does not make a 10,000-VND ticket a positive-EV investment."

### Syndicates (choi nhom)
Pooling buys more tickets and raises win probability proportionally, but expected loss per VND spent is unchanged and winnings are split. Syndicates redistribute risk; they do not beat the house edge.

## Research-Backed Insights

- **Clotfelter & Cook (1989):** lottery players underestimate the house edge and overestimate win chances -> explicitly show house edge and expected loss.
- **Haigh (1997):** transparent math + relatable analogies build accurate intuition.
- **Forrest, Gulley & Simmons (2000):** number-selection patterns reflect biased beliefs, not rational EV-maximizing behavior.

## Related Reference Files

- `combinatorics.md` — odds that feed into EV
- `cognitive-biases.md` — why users misunderstand EV
- `responsible-gambling.md` — when EV-chasing indicates problem gambling
- `keno-math.md`, `max3d-math.md` — format-specific EV
