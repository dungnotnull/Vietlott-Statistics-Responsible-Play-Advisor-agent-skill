# Wheeling & Covering Systems (Mega 6/45 & Power 6/55)

## Foundation

- Combinatorial design / covering-system theory (Schuette, lotto covering designs).
- Haigh, J. (1997). *Taking Chances: Winning with Probability*. Oxford.
- Ziemba et al. (1986). *Dr. Z's 6/49 Lotto Guidebook*. (Popular systems book; critiqued for implying systems beat the odds when they cannot.)

This reference explains wheeling/covering systems applied to Vietlott's jackpot formats (Mega 6/45, Power 6/55) and what they can and cannot achieve. Math backend: `scripts/wheeling_analyzer.py` (if provided) or manual combinatorics from `combinatorics.md`.

## What is a wheeling system?

A structured way to play multiple combinations of a selected set of numbers. It *guarantees* a minimum win **if** your selected numbers include enough of the drawn winners. It does **not** select numbers for you and does **not** improve odds per VND spent.

### Simple example (Mega 6/45)

Choose 4 numbers (1,2,3,4) and want to guarantee a 3-number match if 3 of your 4 are drawn. Play all C(4,3)=4 triples: {1,2,3},{1,2,4},{1,3,4},{2,3,4}. If the draw includes 1-2-3 (anywhere among the 6), your {1,2,3} ticket wins the match-3 tier.

## What wheeling CAN do

1. **Guarantee coverage** — *conditional* on your chosen numbers containing enough winners.
2. **Structured play** — organize combinations systematically instead of randomly.
3. **Group/syndicate coverage** — ensure different combinations across members.

## What wheeling CANNOT do

1. **Improve EV per VND** — expected value per ticket is unchanged; total EV = (number of tickets) x EV-per-ticket, still negative.
2. **Beat the house edge** — the lottery's mathematical advantage persists.
3. **Predict numbers** — wheeling organizes play; it does not select which numbers to wheel.

## Mathematical analysis (Mega 6/45)

### Full wheel — choose 10 numbers, play all 6-number combinations

```
C(10,6) = 210 combinations
Cost: 210 x 10,000 VND = 2,100,000 VND per draw
```

- Guarantees the jackpot **if** all 6 winners are among your 10.
- P(your 10 contain all 6 winners) = C(10,6)/C(45,6) = 210/8,145,060 = 1 in 38,786.
- EV: still -EV per ticket; total expected loss = 210 x (negative EV-per-ticket).

**Key insight:** you spend 2.1M VND to guarantee a jackpot *only if* you beat 1-in-38,786 odds that your 10 numbers contain all 6 winners. Still strongly negative EV.

### Abbreviated wheel — 10 numbers, guarantee 4-match if 5 of your 10 hit

Reduced cost (e.g., ~50 tickets vs 210) at the price of a weaker guarantee. EV unchanged per VND.

### Cost-effectiveness proof

```
Wheeling EV = sum(EV of each ticket) = N x EV_per_ticket = N x (negative)
Regular EV  = N x (negative)
=> Wheeling EV = Regular EV  (per VND identical)
```

The math does not change: whether you wheel or pick randomly, you expect to lose the same amount per VND long-term.

## Power 6/55 wheeling note

Wheeling on Power 6/55 must also account for the bonus ball. A "guarantee 5+bonus" wheel is far more expensive than a "guarantee 5" wheel because the bonus condition multiplies the required coverage. The same negative-EV conclusion holds.

## Deceptive marketing claims

### "Dam bao trung 3 so!" (Guarantee a 3-number match!)

Reality: only **if** X of your chosen numbers are drawn. The guarantee is conditional. The condition is usually unlikely.

```
"Dam bao trung 4 neu 5/10 so cua ban trung" — "neu" la dieu kien lon.
P(5/10 cua ban trung trong Mega) = C(10,5)*C(35,1)/C(45,6) ... rat nho.
Phan lon cac ky, dieu kien khong dat va bao hanh khong ap dung.
```

### "Tang co hoi thang!" (Improve your odds!)

Reality: improves coverage of *your* chosen numbers, not overall odds per VND. Each ticket still has the same probability as any other.

### "Choi 100 so voi gia 10 ve!" (Play 100 numbers for the price of 10!)

Reality: abbreviated wheels reduce cost by reducing guarantee strength. You are trading guarantee for cost; EV is identical.

## When wheeling makes sense

- **Group play** — a syndicate wants non-duplicate coverage. (Alternative: random non-duplicate tickets; same EV, less complexity.)
- **Lucky-number attachment** — a player insists on birthdays; wheeling lets them play all combinations of those. (Reality: attachment doesn't improve odds; birthday numbers 1-31 increase pari-mutuel split risk.)
- **Psychological comfort** — structured play feels better. This is emotional benefit, not mathematical; the cost is complexity.

## Teaching framework

1. **Explain what wheeling is** — structured combination play; it organizes, doesn't predict.
2. **Show the math** — EV per 10,000 VND ticket is negative; N tickets = N x negative EV; wheeling EV = random EV.
3. **Address conditional guarantees** — read the "if" carefully; the condition is usually unlikely.
4. **Offer alternatives** — random selection is mathematically equivalent; focus on budgeting and entertainment framing.

## Wheeling evaluation checklist (before using any system)

- [ ] I understand this does not improve expected value per VND.
- [ ] I can afford the total cost of all tickets.
- [ ] I understand the guarantee is conditional (read the "if").
- [ ] I am doing this for entertainment, not profit.
- [ ] I know the house edge still applies.

## Common questions & responses

| Q | A (principle) |
|---|---------------|
| "Wheeling giup toi thang nhieu hon?" | No. Wheeling guarantees a minimum *if conditions met*; EV per VND is identical to random play. |
| "Co nen mua phan mem wheeling?" | It automates combination generation; it does not improve odds. You pay for convenience, not advantage. |
| "He thong wheeling tot nhat la gi?" | Mathematically all wheels have the same EV. There is no "best" wheel for beating the odds. |
| "Nghe nghiep lottery players dung wheeling?" | There are no professional Vietlott players in the poker-pro sense; no system beats the house edge long-term. |

## Related Reference Files

- `combinatorics.md` — math behind wheeling calculations
- `expected-value.md` — why wheeling cannot beat the house edge
- `cognitive-biases.md` — why users believe wheeling works
