# Responsible Gambling & Problem-Gambling Risk (Vietnam context)

## Foundation

- National Council on Problem Gambling (NCPG). (2021). *Problem Gambling Screening and Brief Intervention Toolkit*. (reference framework for screening)
- Ferris & Wynne (2001). *Problem Gambling Severity Index (PGSI)*. (reference framework)
- Shaffer, H.J., Hall, M.N., & Vander Bilt, J. (1999). *Estimating the Prevalence of Disordered Gambling Behavior in the United States and Canada*. American Journal of Public Health.
- Ladouceur, R., & Walker, C. (1996). *A Cognitive Perspective on Gambling*. (CBT framework for gambling distorted beliefs)
- Wood, R.T., & Griffiths, M.D. (2002). *Adolescent Perceptions of the National Lottery and Scratchcards*. Journal of Adolescence.
- Ministry of Finance of Vietnam. Decree No. 30/2007/ND-CP (and amendments) on Lottery Business. (regulatory context)
- WHO ICD-11: Gambling disorder is classified as a mental-health condition. (clinical framing)

This reference provides frameworks for recognizing problem-gambling risk indicators and providing **Vietnam-appropriate** support resources. Vietnam does not yet have a dedicated problem-gambling hotline; mental-health, medical, and social services are the appropriate entry points. Screening backend: `scripts/risk_screener.py`.

## Core Principles

### 1. Lottery as entertainment
- **Healthy frame:** Vietlott is entertainment with a cost.
- **Unhealthy frame:** Vietlott as investment, income source, or problem-solving strategy.
- Teaching: "Nghi ve chi tieu Vietlott nhu di xem phim: ban tra tien de giai tri, ban ky vong di ra voi it tien hon. Gia tri nam o trai nghiem, khong phai loi nhuan."

### 2. Budget limits
- **Healthy:** set and keep a predetermined entertainment budget from disposable income only.
- **Warning:** exceeding budget, borrowing, using essential funds.
- Guideline: only disposable income (after essentials + savings); set a weekly/monthly cap; never exceed; track spending. Example: 200,000 VND/week cap.

### 3. No chasing losses (không gỡ lại)
- **Healthy:** accept losses as entertainment cost.
- **Warning:** increasing bets to recover losses ("gỡ lại").
- Teaching: "Gỡ lại thuong dan den mat them. Moi cuoc doc lap va cung gia tri ky vong am. Neu ban muon 'lay lai', do la dau hieu canh bao."

## Risk screening frameworks (reference instruments)

### NCPG Brief Screen (7 yes/no items) — Vietnamese items in `scripts/risk_screener.py`
- 0-1 yes: Low risk (monitor)
- 2-3 yes: Moderate risk (consider professional consultation)
- 4+ yes: High risk (seek professional help)

### PGSI (9 items, 0-3 scale)
- 0: Non-problem; 1-2: Low-risk; 3-7: Moderate-risk; 8+: Problem gambler

### Indicator-based screening (behavioral / financial / psychological)
Lists in `scripts/risk_screener.py`; threshold-based risk level.

> All three are **educational screening only**, not diagnosis. Always recommend professional consultation above the skill's scope.

## Risk indicator checklist

### Behavioral
- [ ] Gambling more frequently / longer than intended
- [ ] Repeatedly unable to control or stop
- [ ] Restless/irritable when cutting down
- [ ] Gambling to escape problems or relieve negative feelings
- [ ] Chasing losses / gambling to recover money
- [ ] Lying to family/others about gambling
- [ ] Illegal acts to finance gambling
- [ ] Jeopardizing relationships, job, or career
- [ ] Relying on others for money to cover losses

### Financial
- [ ] Exceeding predetermined budget
- [ ] Borrowing to gamble
- [ ] Using savings/emergency funds
- [ ] Selling possessions to finance gambling
- [ ] Difficulty paying bills due to losses
- [ ] Accumulating debt from gambling

### Psychological
- [ ] Preoccupation with gambling
- [ ] Needing increasing amounts
- [ ] Withdrawal symptoms when stopping
- [ ] Denying problem despite consequences
- [ ] Guilt/shame about gambling
- [ ] Using gambling to cope with negative emotions

## Vietnam-context support resources

Vietnam does not yet have a dedicated problem-gambling hotline. Appropriate entry points (verify current details independently; full data in `config/resources.json`):

- **Duong day nong 111** (national hotline, 24/7) — crisis & referral; can redirect to relevant support.
- **Vien Tam than / Benh vien Tam than** (HCMC, Hanoi) — psychiatric assessment & treatment; gambling disorder is WHO-classified as a mental-health condition; specialist consultation is the standard pathway.
- **So Lao dong - Thuong binh va Xa hoi** (provincial) — social support for financial hardship.
- **Trung tam Tro giup phap ly Nha nuoc** (provincial) — free legal aid for those in hardship (e.g., debt from gambling).
- **International/online:** Gamblers Anonymous International (https://www.gamblersanonymous.org), Gambling Therapy (multilingual, https://www.gamblingtherapy.org).

**Crisis:** if a user expresses suicidal intent or self-harm related to gambling, direct immediately to 115 (emergency), 111 (national hotline), or the nearest medical facility. Crisis response strings in `config/resources.json` (`crisis.response_vi` / `crisis.response_en`).

## Intervention framework

### Step 1 — Recognition (when to flag)
- User mentions 2+ risk indicators
- User describes chasing losses
- User mentions borrowing for gambling
- User describes negative life consequences
- User expresses inability to control gambling
- Keyword heuristic (`scripts/risk_screener.py detect_risk_in_text`, diacritic-insensitive VI+EN) flags risk language

### Step 2 — Non-judgmental inquiry
```
"Toi thay ban nhac den vai dieu co the la dau hieu kho khan voi tro choi.
Nhiu nguoi gap tinh trang nay, khong co gi xau ho, va co ho tro hieu qua.
Ban co muon toi chia se mot so tai nguyen ho tro khong?"
```
Avoid judgment, minimizing, or offering gambling advice instead of professional resources.

### Step 3 — Resource provision (Vietnam)
```
# Tai nguyen ho tro

## Kham y te / tam than
- Vien Tam than / Benh vien Tam than (HCMC, Hanoi) — kham va dieu tri
- Gay rung (gambling disorder) la benh tam than duoc WHO cong nhan

## Ho tro khan cap
- Duong day nong 111 (24/7)
- Cap cuu 115 neu nguy khan

## Ho tro xa hoi / phap ly
- So Lao dong - Thuong binh va Xa hoi (tinh/TP)
- Trung tam Tro giup phap ly Nha nuoc (tinh/TP)

## Ho truc tuyen (da ngu)
- Gambling Therapy: https://www.gamblingtherapy.org
- Gamblers Anonymous: https://www.gamblersanonymous.org

## Buoc tiep theo
1. Goi 111 hoac hen kham chuyen khoa tam than
2. Hoan thanh screening chuyen mon neu duoc de xuat
3. Lien he nguoi ho tro

Co nguoi san sang nghe ban.
```

### Step 4 — Boundary setting
For Vietlott math questions vs gambling-behavior concerns:
```
"Toi co the giup ban hieu toan hoc Vietlott va xac suat. Voi cau hoi ve hanh vi
choi, ngan sach, hoac kha nang kiem soat, toi khuyen ban tham kham chuyen gia
hoac goi 111. Toan hoc cho thay Vietlott co gia tri ky vong am — no duoc thiet
ke de giai tri, khong phai de sinh loi. Neu ban dang dua vao Vietlott de
kiem tien, do la van de ma chuyen gia co the giup."
```

## Budgeting & entertainment framing (VND)

### Healthy guidelines
1. **Budget:** monthly disposable income = income - essentials - savings; gambling <= 10% of disposable (max). Example: 2,000,000 VND disposable -> <= 200,000 VND/month.
2. **Time limits:** cap weekly hours on lottery activities.
3. **Win/loss limits:** pre-set stop loss; accept limits as final.
4. **Never chase:** golden rule — never increase bets to recover losses. If the urge arises: stop, accept loss as entertainment cost, wait 24h, seek professional help if it persists.

### Entertainment-value calculation (VND)
```
200,000 VND/thang chi Vietlott:
- Ky vong mat ~100,000 VND/thang (house edge ~50%)
- Gia tri giai tri: choi, cho doi, mo uoc
So sanh: caphe ~60,000 VND/lan, phim ~100,000 VND/ve, gym ~400,000 VND/thang.
Cau hoi: su giai tri co dang ky vong mat khong? Co -> duoc; Khong -> xet thay the.
```

## When to recommend professional help

### Clear indicators (immediate recommendation)
- Inability to stop despite desire
- Life problems (financial, relationships, work) from gambling
- Borrowing / using essential funds for gambling
- Lying about gambling
- Distress about gambling behaviour

**Framing (VI):**
```
"Dieu ban mo ta la pho bien va co ho tro hieu qua. Nhieu nguoi duoc loi khi
ho tro chuyen mon. Toi nhieu khuyen lien he:
- Duong day nong 111 (24/7)
- Vien/Benh vien Tam than (kham chuyen khoa)
- Gambling Therapy (truc tuyen, da ngu)
Cac dich vu nay bao mat va duoc thiet ke dung cho tinh huong nay."
```

### Borderline indicators
```
"Toi khong du tu van de chuan doan, nhung mot so dieu ban nhac co the lien
quan den kho khan voi tro choi. Nhieu nguoi duoc loi khi noi chuyen voi chuyen
gia. Ban co muon toi chia se tai nguyen de tim hieu them hoac noi chuyen voi
nguoi co nang luc khong?"
```

## Age-considerate messaging

### Young adults (18-25)
Prefrontal cortex still developing; higher impulsivity; vulnerable to "big-win" fantasies. Note: Vietlott legal age is 18+. Messaging: brain develops until ~25 -> higher vulnerability to impulsive gambling decisions; set strict limits; if you can't stick to them, that's not failure — seek help.

### Older adults (50+)
May be on fixed income; losses matter more; gambling may be social. Messaging: on fixed income, treat as entertainment cost strictly; if spending savings or essential money, or if it feels necessary rather than optional, seek help.

## Regulatory context (Vietnam)
- **Decree 30/2007/ND-CP** (and amendments) governs Vietlott/lottery business.
- **Legal age:** 18+ to purchase Vietlott tickets.
- **Operator:** Vietlott (Vietnam Lottery Company) — state-owned enterprise operating under license.

## Disclaimer

This skill provides general educational information about responsible gambling. It is **not** a diagnosis, treatment, or professional advice regarding gambling disorders. Always consult qualified professionals for personalized guidance. Vietnam does not yet have a dedicated problem-gambling hotline; the mental-health, medical, and social services listed are the appropriate entry points.

## Related Reference Files

- `expected-value.md` — mathematical framing of gambling as entertainment
- `cognitive-biases.md` — psychological mechanisms maintaining gambling problems
- `combinatorics.md`, `keno-math.md`, `max3d-math.md` — real odds that counter gambling fantasies
- `config/resources.json` — machine-readable Vietnam resources (consumed by `scripts/risk_screener.py`)
