# PROJECT-detail.md — Vietlott Statistics & Responsible-Play Advisor

## 1. Problem Statement

An educational skill focused specifically on Vietlott's game formats (Mega 6/45, Power 6/55, Keno, Max 3D), teaching the actual combinatorial mathematics behind each game's odds and expected value using established probability theory, and explaining clearly why no statistical method can predict individual future draws. It does not generate 'winning number predictions' and instead promotes statistical literacy and responsible-play awareness appropriate to the Vietnamese context.

## 2. Target Users

Describe the primary user personas for this skill (fill in based on real usage once built): e.g., students, professionals, hobbyists, or practitioners in the relevant domain.

## 3. Functional Specification

### 3.1 Core Capabilities

- Explain the specific combinatorial structure and odds for each Vietlott game format (Mega 6/45, Power 6/55, Keno, Max 3D)
- Calculate expected value and house edge for each game format given published prize structures
- Debunk common 'phương pháp dự đoán' (prediction method) myths using probability and behavioral-economics research
- Explain why historical draw-frequency analysis does not improve future-draw prediction for a fair lottery
- Explain budgeting and entertainment-spending framing consistent with responsible-gambling research
- Recognize and flag problem-gambling risk indicators, with culturally appropriate Vietnamese-context resource guidance
- Explicitly refuse to generate or endorse 'predicted winning numbers' framed as having real predictive power

### 3.2 Key Methodologies & Frameworks Applied

- **Combinatorial probability theory applied to specific multi-format lottery structures**
- **Independence of random events / law of large numbers**
- **Expected value and house-edge calculation in games of chance**
- **Behavioral economics of gambling (gambler's fallacy, availability heuristic, near-miss effect)**
- **Responsible Gambling guidelines adapted to a Vietnamese regulatory and cultural context**

Each framework above should be operationalized as a concrete step, checklist, or template inside the skill's SKILL.md and reference files once this scaffold is turned into a runnable skill (see `DEVELOPMENT-TASK-BY-PHASES.md`).

### 3.3 Expected Input

Typical user requests this skill should handle (fill in with real example prompts during development and testing).

### 3.4 Expected Output Format

Define the structured output format(s) this skill should produce (e.g., structured report, checklist, scored recommendation, memo). Align with the methodologies above so outputs are consistent and auditable.

## 4. Out of Scope / Guardrails

- Always include the standing disclaimer for this domain (see CLAUDE.md).
- Never present output as a certified/professional determination (e.g., not a diagnosis, not a legal opinion, not a guaranteed forecast).
- Where the skill involves a named third party (e.g., a partner, a suspect, a specific person), do not produce a definitive judgment about that individual — stay at the level of general, population-based information and structured reasoning support.
- Flag explicitly when a licensed professional (doctor, lawyer, engineer, certified analyst, etc.) should be consulted.

## 5. Knowledge Base Dependency

This skill's reasoning quality depends on the research foundations catalogued in `SECOND-BRAIN-KNOWLEDGE-PAPER.md`. When building the actual skill (SKILL.md + references/), extract the operational principles from each paper into concrete reference files rather than leaving them as a flat reading list.

## 6. Success Criteria

- Output correctly applies the named methodologies rather than generic reasoning.
- Output is well-structured and consistent across repeated runs on similar inputs.
- Domain-appropriate guardrails/disclaimers are respected in every response.
- Test prompts (see `DEVELOPMENT-TASK-BY-PHASES.md`, Phase 5) produce outputs a subject-matter-competent reviewer would rate as sound.
