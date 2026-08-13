# Prompt Templates (base templates for agent grounding / RAG)

These base templates are loaded by the skill-router and sub-advisors in SKILL.md.
They are *structures*, not canned answers: each `[bracketed]` slot is filled from
the corresponding reference file or tool output at runtime. Keeping templates
here (rather than inlining into SKILL.md) keeps SKILL.md within context budget
and lets templates evolve independently.

## 1. Prediction-refusal template (route: prediction_refusal)

```
Toi hieu ban muon [du doan cap so dep / soi cau / phuong pháp du doan], nhung
can noi ro: ket qua Vietlott la ngau nhien toan hoc va khong the du doan.
Khong co phuong phap nao — soi cau, so hot/cold, phan mem, cong thuc — co the
du bao mot ky quay cu the.

Toi khong the tao "so du doan" vi dieu do se dua ra thong tin sai. Nhung toi co
the giup ban hieu that:
- Xac suat thuc su cua [Mega 6/45 / Power 6/55 / Keno / Max 3D]
- Vi sao cac ky quay doc lap (khong the du doan)
- Gia tri ky vong (EV) va house edge cua moi tro choi
- Cach nghi ve chi tieu Vietlott nhu giai tri, dau tu lai

Ban muon toi bat dau voi dau?
```

## 2. Odds-calculation template (route: odds)

```
# Tinh xac suat Vietlott — [GAME]

## Yeu cau
- Chon [r] so tu [n]; [khong co / co 1] so bo sung.

## Toan hoc (combinatorics)
Su dung he so nhi thuc C(n,r) = n! / (r! * (n-r)!):
1. Khong gian mau: C([n],[r]) = [sample_space]
2. Ket qua co loi: C([r],[k]) * C([n-r],[r-k]) = [favorable]
3. Xac suat: [favorable] / [sample_space] = [probability]
4. Ti le: 1 trong [odds]

## Ket qua cua ban
- [Tier name]: 1 trong [odds] (giai [prize VND])
- P(trung bat ky): [any_prize]

## Y nghia
[practical interpretation with VND and Vietnamese-context analogies]

**Luu y:** [disclaimer]
```

## 3. Hot/cold myth template (route: mythbust)

```
# So hot / so lanh / soi cau: huyen thoai

## Tra loi ngan gon
Phan tich so hot/cold khong co tac dung vi moi ky quay Vietlott la doc lap
thong ke. May quay khong co bo nho.

## Vi sao khong tac duoc
- Tung dong xuat [example sequence] cho thay "cum" ngau nhien khong phai du bao.
- Nghien cuu (Tversky & Kahneman 1971; Clotfelter & Cook 1993) da test hot/cold
  voi chon ngau nhien qua hang ngan ky: khong co loi the.

## Thu te
Nhiu nguoi choi [so sinh nhat 1-31] -> neu trung, jackpot pari-mutuel chia
nhieu nguoi hon -> EV giam them.

**Luu y:** [disclaimer]
```

## 4. Expected-value template (route: ev)

```
# Phan tich gia tri ky vong (EV) — [GAME]

## Tham so
- Gia ve: [cost] VND
- Cau truc giai: [tiers table]

## Tinh toan
[tier-by-tier contribution lines]

## Ket qua
- Ky vong thang/ve: [ew] VND
- Ky vong mat/ve: [loss] VND
- House edge: [he]%
- P(trung bat ky): [p]

## Y nghia dai va ngan han
- Tren 100,000 VND: mat ky vong [amount] VND.
- [W] VND/tuan -> mat nam [amount] VND.
- 10 nam -> [amount] VND; dau tu lai @7% -> [fv] VND.

## Khung giai tri
[entertainment comparison in VND]

**Luu y:** [disclaimer]
```

## 5. Keno / Max 3D specific template (route: keno_max3d)

```
# [Keno / Max 3D] — cau truc khac jackpot

## Dieu khac biet
[Keno: hypergeometric, quay ~10 phut/ky | Max 3D: fixed-odds 1/1000]

## Toan hoc
[Keno: P(match m|select s) = C(s,m)C(80-s,20-m)/C(80,20) | Max 3D: Binomial(k,1/1000)]

## EV
[per-select / per-mode EV table]

## Rui ro chinh
[Keno: tan suat 144 ky/ngay | Max 3D: "de trung" nhung gia duoc tinh day vao odds]

**Luu y:** [disclaimer]
```

## 6. Wheeling-system template (route: mythbust, wheeling sub-topic)

```
# Phan tich he thong wheeling

## No lam gi
- Bao hanh trung toi thieu [k] so [NEU] X/[n] so cua ban trung.

## No KHONG lam gi
- Khong tang EV moi VND.
- Khong danh bai house edge.
- Khong du doan so.

## Toan hoc
[full wheel cost C(n,6) x ticket; EV = N x EV_per_ticket = same as random]

## Ket luan
Wheeling = tai phan phoi rui ro, khong phai loi the. Chi dung neu ban hieu no
khong tang EV va chi tieu trong ngan sach.

**Luu y:** [disclaimer]
```

## 7. Responsible-gambling / risk template (route: responsible_play)

```
# Ho tro va tai nguyen

## Nhung gi ban mo ta
[non-judgmental acknowledgment]

## Dieu nay pho bien
[normalization; gambling disorder is WHO-classified, not a moral failing]

## Ho tro co san (Viet Nam)
- Duong day nong 111 (24/7)
- Vien/Benh vien Tam than (HCMC, Hanoi) — kham chuyen khoa
- So Lao dong - Thuong binh va Xa hoi (tinh/TP)
- Gambling Therapy (truc tuyen da ngu): https://www.gamblingtherapy.org

## Buoc tiep theo
1. Goi 111 hoac hen kham tam than
2. Hoan thanh screening chuyen mon neu de xuat
3. Lien he tai nguyen khu vuc

Khong co gi xau ho khi xin ho tro. Co nguoi san sang nghe ban.

**Luu y:** [disclaimer] Day la screening giao duc, khong phai chuan doan.
```

## 8. Crisis template (route: responsible_play, crisis sub-route)

```
# Ho tro khan cap

Neu ban dang co y dinh lam thu hai than hoac tu hai, vui long:
- Goi ngay 115 (cap cuu) HOAC
- Duong day nong 111 (24/7) HOAC
- Den co so y te gan nhat

Co nguoi san sang nghe ban ngay bay gio. Ban khong phai mot minh.
```
(Crisis template overrides normal flow; emit immediately, then offer continuing support.)
