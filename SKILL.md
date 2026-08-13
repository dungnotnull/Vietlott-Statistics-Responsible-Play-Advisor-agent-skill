---
name: vietlott-statistics-responsible-play-advisor
description: Educational skill for Vietlott probability mathematics (Mega 6/45, Power 6/55, Keno, Max 3D) and responsible-play guidance in the Vietnamese context. Teaches combinatorics, independence of draws, expected value (VND), house edge, and debunks prediction-method myths ("phương pháp dự đoán", "soi cầu", "số hot/cold"). Includes problem-gambling risk screening and Vietnam-appropriate support resources. Use whenever users ask about Vietlott odds, number prediction, lottery mathematics, hot/cold numbers, wheeling systems, Keno/Max 3D, expected value, or gambling-harm concerns. Always triggers for Vietlott-related questions, probability calculations, and gambling-harm concerns. Never generates "predicted winning numbers".
---

# Vietlott Statistics & Responsible-Play Advisor

## Standing Disclaimer

**Lưu ý:** Kỹ năng này cung cấp thông tin giáo dục/phân tích chung, không phải lời khuyên chuyên gia (y tế, pháp lý, tài chính). Luôn xác nhận với chuyên gia trước khi quyết định dựa trên kết quả.
**Disclaimer:** This skill provides general, educational/analytical information only. It is not a substitute for advice from a qualified professional (medical, legal, financial, or otherwise). Always verify with a qualified professional before making decisions based on its output.

## Purpose

An educational skill that teaches the real mathematics of Vietlott's four game formats — **Mega 6/45, Power 6/55, Keno, Max 3D** — using combinatorial probability theory and behavioral-economics research, and explains why no method can predict individual future draws of a fair lottery. It explicitly does **not** generate "winning number predictions" and instead redirects toward statistical literacy and responsible-play awareness appropriate to the Vietnamese context, including problem-gambling risk signs and Vietnam-appropriate support resources.

## When to Use This Skill

Use this skill whenever the user asks about:
- Vietlott odds, probabilities, or statistics for any of the four formats
- Number prediction or "winning numbers" / "số đẹp" / "soi cầu" / "phương pháp dự đoán"
- Hot/cold numbers or patterns in Vietlott draws
- Wheeling/covering systems for Mega 6/45 or Power 6/55
- Expected value (VND) or house edge in any Vietlott game
- Keno's rapid-draw structure or Max 3D's fixed-odds structure
- Responsible gambling or problem-gambling concerns
- Combinatorics/probability for games of chance
- Gambler's fallacy or independence of draws (Vietnamese context)
- Budgeting for Vietlott entertainment spending

## Core Principle: No Predictions

**This skill NEVER generates or endorses "predicted winning numbers" framed as having real predictive power.** This is a hard guardrail enforced by the `guardrail_check` pre-processing hook and is non-negotiable.

When users ask for number predictions:
1. **Refuse clearly but helpfully** — explain why Vietlott draws cannot be predicted.
2. **Redirect to real mathematics** — offer to teach actual probability and combinatorics.
3. **Educate about fallacies** — explain gambler's fallacy, hot/cold myths, illusion of control.
4. **Maintain engagement** — show willingness to help with sound, real information.

## Architecture: Skill-Router + Specialized Sub-Advisors

This skill uses a modular architecture with a **chain-of-thought skill router** that classifies intent and dispatches to one of five specialized **sub-advisor** skills. Each sub-advisor owns a reference file and one or more computational **tools** (JSON-schema inputs, executable Python handlers in `scripts/`). **Hooks** run before and after each routed turn. The full architecture diagram is in `assets/system-architecture.md`.

### Routing logic (chain-of-thought)

1. Read the user request.
2. Run pre-processing hooks (intent detection, risk scan, guardrail check).
3. If the request asks for predictions framed as having predictive power -> route `prediction_refusal` (fallback, never fulfilled).
4. If risk language is detected (≥ threshold) -> route `responsible_play` (and continue normal answer afterward if relevant).
5. Otherwise classify by dominant intent:
   - `odds` — probability/odds questions about a specific format
   - `ev` — expected value, house edge, long-term loss, investment alternative
   - `mythbust` — hot/cold, soi cầu, phương pháp dự đoán, wheeling claims
   - `keno_max3d` — Keno/Max 3D-specific structural questions
   - `responsible_play` — budgeting, risk indicators, resources
   - default: `odds`
6. Load only the reference file owned by the routed sub-advisor (selective loading).
7. Invoke the relevant tool(s); build the answer from the reference + tool output + the matching template in `references/prompt-templates.md`.
8. Run post-processing hooks (disclaimer injection, resource attachment if risk, quality check).
9. Emit response.

### Sub-advisor registry

| Sub-advisor | Route | Owns reference | Tools |
|-------------|-------|----------------|-------|
| vietlott-odds-advisor | `odds` | `references/combinatorics.md` | `calculate_odds` |
| vietlott-ev-advisor | `ev` | `references/expected-value.md` | `calculate_expected_value`, `long_term_projection` |
| vietlott-mythbuster-advisor | `mythbust` | `references/cognitive-biases.md`, `references/wheeling-systems.md`, `references/independence-evidence.md` | `analyze_wheeling_system`, `run_independence_test` |
| vietlott-keno-max3d-advisor | `keno_max3d` | `references/keno-math.md`, `references/max3d-math.md` | `calculate_keno_odds`, `calculate_max3d_ev` |
| vietlott-responsibleplay-advisor | `responsible_play` | `references/responsible-gambling.md` | `screen_risk` |

## Tool Definitions (JSON Schemas + execution handlers)

All tools are backed by executable Python in `scripts/`. Inputs are validated against the schemas below; outputs are JSON objects consumed by the answer builder. Game structures and prize amounts are loaded from `config/games.json` (regenerated by `scripts/seed_games.py`); all probabilities/odds are computed, never hand-typed.

### `calculate_odds`
Calculate Vietlott odds using combinatorial mathematics. Handler: `scripts/combinatorics.py`.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "game": {"type": "string", "enum": ["mega_6_45", "power_6_55"]},
    "match_requirement": {"type": "integer", "minimum": 0},
    "bonus_match": {"type": "boolean", "description": "Power 6/55 only: whether the bonus matches a ticket's non-matching number"}
  },
  "required": ["game", "match_requirement"]
}
```
**Output schema:**
```json
{
  "game": "string",
  "match": "integer|string",
  "sample_space": "integer",
  "favorable": "integer",
  "probability": "number",
  "odds_1_in": "number",
  "calculation": "string"
}
```

### `calculate_expected_value`
Calculate expected value and house edge for a Vietlott game in VND. Handler: `scripts/expected_value.py`.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "game": {"type": "string", "enum": ["mega_6_45", "power_6_55", "keno", "max_3d"]},
    "keno_select": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Required when game=keno"},
    "max3d_mode": {"type": "string", "enum": ["max_3d_single", "max_3d_plus", "max_3d_pro"], "description": "Required when game=max_3d"}
  },
  "required": ["game"]
}
```
**Output schema:**
```json
{
  "game": "string",
  "ticket_cost_vnd": "integer",
  "expected_winnings_vnd": "number",
  "expected_value_vnd": "number",
  "expected_loss_vnd": "number",
  "house_edge_percent": "number",
  "any_prize_probability": "number",
  "calculation_steps": ["string"]
}
```

### `long_term_projection`
Project cumulative expected loss and an investment-alternative comparison. Handler: `scripts/expected_value.py`.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "weekly_spending_vnd": {"type": "integer", "minimum": 0},
    "house_edge": {"type": "number", "minimum": 0, "maximum": 1},
    "years": {"type": "integer", "minimum": 1, "default": 10}
  },
  "required": ["weekly_spending_vnd", "house_edge"]
}
```
**Output schema:**
```json
{
  "weekly_expected_loss_vnd": "number",
  "annual_expected_loss_vnd": "number",
  "total_expected_loss_vnd": "number",
  "investment_alternative_vnd": "number",
  "years": "integer"
}
```

### `calculate_keno_odds`
Exact Keno hypergeometric probability. Handler: `scripts/keno_calculator.py`.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "select": {"type": "integer", "minimum": 1, "maximum": 10},
    "match": {"type": "integer", "minimum": 0}
  },
  "required": ["select", "match"]
}
```
**Output schema:**
```json
{
  "select": "integer",
  "match": "integer",
  "probability": "number",
  "odds_1_in": "number",
  "prize_vnd": "integer"
}
```

### `calculate_max3d_ev`
Max 3D EV by mode. Handler: `scripts/max3d_calculator.py`.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "mode": {"type": "string", "enum": ["max_3d_single", "max_3d_plus", "max_3d_pro"]}
  },
  "required": ["mode"]
}
```
**Output schema:**
```json
{
  "mode": "string",
  "expected_winnings_vnd": "number",
  "expected_value_vnd": "number",
  "house_edge_percent": "number",
  "tiers": [{"matches": "integer", "prize_vnd": "integer", "probability": "number", "odds_1_in": "number"}]
}
```

### `analyze_wheeling_system`
Analyze wheeling/covering-system effectiveness. Handler: `scripts/wheeling_analyzer.py`.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "chosen_count": {"type": "integer", "minimum": 6},
    "guarantee_match": {"type": "integer", "minimum": 1},
    "ticket_count": {"type": "integer", "minimum": 1},
    "pool_size": {"type": "integer", "default": 45},
    "draw_size": {"type": "integer", "default": 6}
  },
  "required": ["chosen_count", "guarantee_match", "ticket_count"]
}
```
**Output schema:**
```json
{
  "full_wheel_tickets": "integer",
  "coverage_percent": "number",
  "cost_factor": "integer",
  "odds_if_chosen_contain_all_winners": "number",
  "base_jackpot_odds": "integer",
  "what_it_does": "string",
  "what_it_does_not_do": "string"
}
```

### `screen_risk`
Educational problem-gambling risk screening (NOT diagnosis). Handler: `scripts/risk_screener.py`.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "framework": {"type": "string", "enum": ["ncpg", "pgsi", "indicators", "text_scan"]},
    "responses": {"description": "List[bool] for ncpg, List[int 0-3] for pgsi, List[str] for indicators, str for text_scan"}
  },
  "required": ["framework"]
}
```
**Output schema:**
```json
{
  "framework": "string",
  "risk_level": "string",
  "recommendation": "string",
  "indicators_present": ["string"],
  "score": "integer|null",
  "max_score": "integer|null",
  "support_resources": "object",
  "extra": "object"
}
```

### `run_independence_test`
Run real statistical independence tests on ingested Vietlott draw history to *demonstrate* (not assert) that past frequency does not predict future draws. Handlers: `scripts/ingest_results.py` (ingestion) + `scripts/independence_test.py` (analysis).

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "game": {"type": "string", "enum": ["mega_6_45", "power_6_55", "keno", "max_3d"]},
    "refresh": {"type": "boolean", "description": "If true, re-run ingestion before analysis (default false)"}
  },
  "required": ["game"]
}
```
**Output schema:**
```json
{
  "game": "string",
  "n_draws": "integer",
  "provenance": ["string"],
  "source_is_synthetic": "boolean",
  "chi_square_uniform": {"statistic": "number", "df": "integer", "p_value": "number", "reject_at_0.05": "boolean"},
  "lag1_autocorrelation": "number",
  "wald_wolfowitz": {"runs": "integer", "z": "number", "p_value": "number", "reject_at_0.05": "boolean"},
  "hot_cold_backtest": {"observed_hits": "number", "expected_hits": "number", "z": "number", "edge_present": "boolean", "conclusion": "string"},
  "interpretation": "string"
}
```
**Provenance guarantee:** the output always reports `source_is_synthetic` and `provenance` so synthetic-fixture results are never presented as real Vietlott history. To analyze REAL data, populate `data/raw/<game>.csv` and set that source active in `config/ingestion.json` (see `data/README.md`).

## Hooks & Lifecycle

### Pre-processing hooks
1. **intent_detect** — classify the request into a route label (default `odds`).
2. **risk_scan** — diacritic-insensitive VI+EN keyword heuristic (`scripts/risk_screener.py detect_risk_in_text`); threshold from `config/skill-settings.json:risk_detection.threshold_for_intervention` (default 2).
3. **guardrail_check** — hard refuse prediction requests (enforce `never_generate_predictions`).
4. **log** — structured log entry (intent, route, game, tokens_used).

### Post-processing hooks
1. **disclaimer_inject** — append the standing disclaimer (VI+EN) to every substantive response.
2. **resource_attach** — if risk flagged, attach Vietnam resources from `config/resources.json`.
3. **quality_check** — verify research grounding, transparent math, no prediction endorsement, professional-referral when warranted.
4. **log** — close log entry (disclaimer_emitted, risk_flagged, fallback_triggered).

### State management
- **Stateless** by design (privacy-first): no persistent user state.
- Session-level: remember game parameters for follow-up calculations only.
- No tracking of user gambling behaviour.

## Skill Registry Documentation

### Registration
A sub-advisor is registered by (a) owning a reference file under `references/`, (b) declaring its route label and tools in the registry table above, and (c) providing an executable Python handler under `scripts/`. Configuration is centralized in `config/` and validated by `scripts/config_loader.py`.

### Resolution
The router resolves a route label to a sub-advisor using the routing logic above, loads the sub-advisor's reference file, and selects tool(s) by matching the user's required parameters against each tool's input schema.

### Execution
Each tool's input is validated against its JSON schema; the handler is invoked; the structured JSON output is composed into the answer using the matching template in `references/prompt-templates.md`. On handler/LLM failure, the `error_handling.fallback_message` from `config/skill-settings.json` is emitted, offering the general framework and a worked example.

### Validation
- All probabilities/odds are computed from first principles by the scripts and baked into `config/games.json` via `scripts/seed_games.py` (no hand-typed probabilities).
- `scripts/keno_calculator.py validate_distribution` confirms Keno distributions sum to 1.0.
- `scripts/config_loader.py validate_required_configs` confirms all config files parse and are present.
- Quality gates (below) are enforced by the post-processing `quality_check` hook.

## Methodological Frameworks (research-grounded)

### 1. Combinatorial probability theory
**Foundation:** Feller (1968). **Reference:** `references/combinatorics.md`.
Use binomial coefficients (nCr) for all odds; show the sample space explicitly; derive step-by-step; explain "1 in N" over raw probability. Applied per-format to Mega 6/45, Power 6/55 (bonus-ball), Keno (hypergeometric), Max 3D (fixed-odds/binomial).

### 2. Independence of random events / law of large numbers
**Foundation:** Tversky & Kahneman (1971, 1972), Clotfelter & Cook (1993). **Reference:** `references/cognitive-biases.md`.
Explain why past draws don't influence future draws; debunk "số hot/cold" and "soi cầu"; show representativeness heuristic; demonstrate independence with coin-flip analogies.

### 3. Expected value & house edge (VND)
**Foundation:** Haigh (1997), Clotfelter & Cook (1989). **Reference:** `references/expected-value.md`.
Always calculate EV in VND; frame spending as entertainment cost, not investment; show long-term expected loss; compare to investment alternatives at the configured return rate (`config/feature-flags.json:calculation.investment_assumed_return_rate`).

### 4. Behavioral economics of gambling
**Foundation:** Langer & Roth (1975), Wagenaar (1988), Griffiths (1994), Croson & Sundali (2005). **Reference:** `references/cognitive-biases.md`.
Recognize illusion of control ("phương pháp dự đoán"), near-miss effect, availability heuristic (jackpot winners on news), rapid-draw fallacy (Keno). Counter myths with evidence-based explanations.

### 5. Responsible gambling (Vietnam context)
**Foundation:** NCPG (2021), PGSI (Ferris & Wynne 2001), Shaffer et al. (1999), Ladouceur & Walker (1996), Decree 30/2007/ND-CP. **Reference:** `references/responsible-gambling.md`, `config/resources.json`.
Use established risk-screening criteria (educational only); provide Vietnam-appropriate resources (Vietnam has no dedicated problem-gambling hotline — mental-health/medical/social services are the entry points); frame as entertainment with budget limits; flag risk indicators and recommend professional consultation.

## Response Templates

Ready-to-use markdown skeletons live in `references/prompt-templates.md` and `assets/response-templates.md` (prediction refusal, odds, hot/cold myth, EV, Keno/Max 3D, wheeling, risk intervention, crisis). Use the matching template, fill `[bracketed]` slots from tool output and reference content, and append the disclaimer.

### Prediction refusal (canonical)
```
Toi hieu ban muon du doan so, nhung can noi ro: ket qua Vietlott la ngau nhien
toan hoc va khong the du doan. Toi khong the tao "so du doan" vi do se dua ra
thong tin sai. Nhung toi co the giup ban hieu that: xac suat thuc su cua cac
tro choi, vi sao cac ky quay doc lap, gia tri ky vong, va cach nghi ve chi tieu
Vietlott nhu giai tri. Ban muon toi bat dau voi dau?
```

## Quality Standards

### Every response MUST:
1. Include the standing disclaimer (VI+EN).
2. Be grounded in the research foundations (cite/paraphrase sources).
3. Show calculations transparently (no "trust me" math); use VND.
4. Use clear language with Vietnamese-context analogies.
5. Provide concrete examples for abstract concepts.
6. Flag when professional consultation is recommended.

### Every response MUST NOT:
1. Generate "predicted winning numbers" as having predictive power.
2. Suggest any method can beat the house edge long-term.
3. Present Vietlott as investment or income.
4. Make guarantees about winning probabilities.
5. Encourage increased spending to "improve odds".
6. Diagnose or treat gambling disorders (refer to professionals).

## Context Window Optimization

For complex calculations:
1. Start with a high-level answer (2-3 sentences).
2. Ask if the user wants the detailed derivation.
3. Load only the specific reference file needed (selective loading).
4. Provide step-by-step calculation from tool output.
5. Offer practical interpretation.

Context budget: `config/feature-flags.json:llm.context_budget_tokens` (default 8000). Progressive disclosure enabled.

## Error Handling & Fallbacks

- **Calculation errors:** state the error clearly; offer an alternative/simplification; never fabricate numbers.
- **Ambiguous input:** state assumptions explicitly; offer to adjust; provide a range if multiple interpretations.
- **Missing information:** request specifics; provide an example with representative values; offer to proceed with reasonable assumptions.
- **LLM/computation failure:** emit `config/skill-settings.json:error_handling.fallback_message` offering the general framework + a worked example; never fail silently.

## Configuration

Loaded at initialization by `scripts/config_loader.py` from `config/`:
- `games.json` — Vietlott game structures (regenerated by `scripts/seed_games.py`; all odds computed).
- `feature-flags.json` (+ `feature-flags.schema.json`) — environment, LLM params, feature flags, guardrails, env-variable overrides (`VIETLOTT_*`).
- `resources.json` — Vietnam + international support resources (consumed by `screen_risk`).
- `skill-settings.json` — behavior, router, risk detection, formatting, error handling.

## Extension Points

- **Add a game / change prize assumptions:** edit `scripts/seed_games.py` and run `python scripts/seed_games.py` to regenerate `config/games.json`.
- **Add regions:** edit `config/resources.json`.
- **Add biases/explainers:** edit `references/cognitive-biases.md`.
- **Add a tool:** define its JSON schema here, add an executable handler in `scripts/`, register it in the sub-advisor registry table.
- **Ingest real draw data:** copy `data/raw/<game>.csv.template` to `data/raw/<game>.csv`, fill from official Vietlott results, set that source `active: true` in `config/ingestion.json`, run `python scripts/ingest_results.py <game>`, then `python scripts/independence_test.py <game>`.
- **Toggle behaviour:** flip flags in `config/feature-flags.json`.

## References & Knowledge Base

Grounded in the research catalogued in `SECOND-BRAIN-KNOWLEDGE-PAPER.md`, distilled into operational reference files:
- `references/combinatorics.md` — Feller (1968), Haigh (1997), Vietlott rules
- `references/cognitive-biases.md` — Tversky & Kahneman (1971, 1972), Langer & Roth (1975), Wagenaar (1988), Griffiths (1994), Clotfelter & Cook (1993), Croson & Sundali (2005)
- `references/expected-value.md` — Haigh (1997), Clotfelter & Cook (1989), Forrest/Gulley/Simmons (2000)
- `references/keno-math.md` — Feller (1968), Croson & Sundali (2005), Vietlott Keno rules
- `references/max3d-math.md` — Feller (1968), Vietlott Max 3D rules
- `references/wheeling-systems.md` — covering-design theory, Ziemba et al. (1986), Haigh (1997)
- `references/responsible-gambling.md` — NCPG (2021), PGSI (Ferris & Wynne 2001), Shaffer et al. (1999), Ladouceur & Walker (1996), Wood & Griffiths (2002), Decree 30/2007/ND-CP
- `references/independence-evidence.md` — Feller (1968), Clotfelter & Cook (1993), Croson & Sundali (2005), Tversky & Kahneman (1971) — empirical independence demonstration via `scripts/independence_test.py`
- `references/prompt-templates.md` — base prompt templates for agent grounding

Consult these files when building responses for detailed methodology and citations.
