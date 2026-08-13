# Response Templates (Vietlott)

Standardized response scaffolds for common Vietlott query types. These mirror
the prompt templates in `references/prompt-templates.md` but are kept here as
ready-to-use markdown skeletons (with English fallback notes) for quick lookup
and for reviewers/evaluators.

## Prediction refusal

```
Toi hieu ban muon du doan so, nhung can noi ro: ket qua Vietlott la ngau nhien
toan hoc va khong the du doan. Toi khong the tao "so du doan" vi do se dua ra
thong tin sai.

Toi co the giup ban hieu that:
- Xac suat thuc su cua Mega 6/45, Power 6/55, Keno, Max 3D
- Vi sao cac ky quay doc lap (khong the du doan)
- Gia tri ky vong (EV) va house edge
- Cach nghi ve chi tieu Vietlott nhu giai tri

Ban muon toi bat dau voi dau?
```

## Odds calculation

```
# Tinh xac suat — [GAME]

## Toan hoc
[step-by-step binomial-coefficient derivation]

## Ket qua
- [tier]: 1 trong [odds] ([prize VND])
- P(trung bat ky): [p]

## Y nghia
[practical interpretation, VND, Vietnamese analogies]
```

## Hot/cold myth

```
# So hot/cold/soi cau: huyen thoai

## Tra loi ngan gon
Phan tich hot/cold khong co tac dung vi moi ky quay Vietlott la doc lap thong ke.

## Vi sao
[independence + clustering analogy + research citations]

## Thu te
[birthday-number 1-31 pari-mutuel split point]
```

## Expected value

```
# EV — [GAME]

## Tinh toan
[tier-by-tier contributions]

## Ket qua
- Ky vong mat/ve: [VND]
- House edge: [%]
- P(trung bat ky): [p]

## Dai han
[annual + 10-year + investment-alternative VND]

## Khung giai tri
[VND entertainment comparison]
```

## Keno / Max 3D specific

```
# [Keno / Max 3D] — cau truc khac jackpot

## Dac diem
[Keno: hypergeometric + 10-min cadence | Max 3D: fixed-odds 1/1000]

## Toan hoc + EV
[formula + per-select/per-mode EV]

## Rui ro chinh
[Keno: tan suat 144 ky/ngay | Max 3D: "de trung" duoc tinh day vao odds]
```

## Wheeling analysis

```
# Phan tich wheeling

## Lam gi / KHONG lam gi
[conditional guarantee | no EV gain, no house-edge beat, no prediction]

## Toan hoc
[full-wheel cost; EV = N x EV_per_ticket = random]

## Ket luan
[redistributes risk only]
```

## Risk intervention

```
# Ho tro va tai nguyen

## Nhung gi ban mo ta
[acknowledgment]

## Pho bien & co ho tro
[normalization; WHO-classified condition]

## Tai nguyen Viet Nam
[111 / Vien Tam than / So Lao dong / Gambling Therapy]

## Buoc tiep theo
[1-2-3]

Khong co gi xau ho khi xin ho tro.
```

## Crisis (override)

```
# Ho tro khan cap
Neu ban co y dinh tu hai, goi ngay 115, hoac 111 (24/7), hoac den y te gan nhat.
Ban khong phai mot minh.
```

## Disclaimer block (appended to every substantive response)

VI:
```
**Luu y:** Ky nang nay cung cap thong tin giao duc/phan tich chung, khong phai
loi khuyen chuyen gia (y te, phap ly, tai chinh). Luu xac nhan voi chuyen gia
truoc khi quyet dinh dua tren ket qua.
```

EN:
```
**Disclaimer:** This skill provides general, educational/analytical information
only. It is not a substitute for advice from a qualified professional (medical,
legal, financial, or otherwise). Always verify with a qualified professional
before making decisions based on its output.
```
