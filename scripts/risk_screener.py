#!/usr/bin/env python3
"""
Problem-gambling risk screening for the Vietlott skill.

Implements three complementary screening instruments and a Vietnamese-context
resource referral layer:
  - NCPG Brief Screen (7 yes/no items)  [reference framework]
  - PGSI (9 items, 0-3 scale)           [reference framework]
  - Indicator-based screening (behavioral/financial/psychological)

This module is the backend for the `screen_risk` tool schema in SKILL.md. It is
strictly educational screening, NOT diagnosis. Results always recommend
professional consultation above the skill's scope.
"""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def _load_resources() -> Dict:
    return json.loads((CONFIG_DIR / "resources.json").read_text(encoding="utf-8"))


@dataclass
class ScreeningResult:
    framework: str
    risk_level: str
    recommendation: str
    indicators_present: List[str] = field(default_factory=list)
    score: Optional[int] = None
    max_score: Optional[int] = None
    support_resources: Dict = field(default_factory=dict)
    extra: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "framework": self.framework,
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
            "indicators_present": self.indicators_present,
            "score": self.score,
            "max_score": self.max_score,
            "support_resources": self.support_resources,
            "extra": self.extra,
        }



def _strip_diacritics(text: str) -> str:
    """Lowercase Vietnamese text with diacritics removed (NFD + strip combining marks)."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


class RiskScreener:
    """Vietlott-context problem-gambling risk screener (educational only)."""

    NCPG_QUESTIONS = [
        "Have you ever tried to cut down or stop gambling but couldn't?",
        "Have you ever lied to family or others about how much you gamble?",
        "Have you ever felt restless, irritable, or anxious when trying to stop gambling?",
        "Have you ever gambled to escape problems or relieve negative feelings?",
        "Have you ever chased losses (gambled more to win back money)?",
        "Have you ever borrowed money or sold things to gamble?",
        "Has gambling caused significant problems in your relationships, work, or finances?",
    ]

    NCPG_QUESTIONS_VI = [
        "Ban tung co gang giam hoac dung choi ma khong duoc?",
        "Ban tung noi doi gia dinh hoac nguoi khac ve so tien ban choi?",
        "Ban tung thay bat an, kho chiu khi co gang dung choi?",
        "Ban tung choi de tranh kho hoac giam cam xuc tieu cuc?",
        "Ban tung gỡ lai (choi them de lay lai tien da thua)?",
        "Ban tung vay tien hoac ban do de lay tien choi?",
        "Choi co bac da gay kho khan lon cho moi quan he, cong viec hoac tai chinh cua ban?",
    ]

    PGSI_ITEMS = [
        "In the last 12 months, have you bet more than you could afford to lose?",
        "Have you needed to gamble with larger amounts to get the same feeling?",
        "Have you gone back another day to win back money you lost?",
        "Have you borrowed money or sold anything to get money to gamble?",
        "Have you felt that you might have a problem with gambling?",
        "Have people criticized your betting or told you that you had a gambling problem?",
        "Have you felt guilty about the way you gamble or what happens when you gamble?",
        "Has gambling caused you any health problems, including stress or anxiety?",
        "Have people in your life been negatively affected by your gambling?",
    ]

    BEHAVIORAL_INDICATORS = [
        "Gambling more frequently or for longer periods than intended",
        "Trying repeatedly but unsuccessfully to control or stop gambling",
        "Feeling restless or irritable when attempting to cut down",
        "Gambling to escape problems or relieve negative feelings",
        "Chasing losses or gambling to recover money",
        "Lying to family or others about gambling involvement",
        "Committing illegal acts to finance gambling",
        "Jeopardizing or losing relationships, job, or career due to gambling",
        "Relying on others for money to cover gambling losses",
    ]
    FINANCIAL_INDICATORS = [
        "Exceeding predetermined gambling budget",
        "Borrowing money to gamble",
        "Using savings or emergency funds for gambling",
        "Selling possessions to finance gambling",
        "Difficulty paying bills due to gambling losses",
        "Accumulating debt from gambling",
    ]
    PSYCHOLOGICAL_INDICATORS = [
        "Preoccupation with gambling (thinking about past/future betting)",
        "Needing to gamble with increasing amounts of money",
        "Experiencing withdrawal symptoms when stopping",
        "Denying problem despite negative consequences",
        "Feeling guilt or shame about gambling",
        "Using gambling to cope with negative emotions",
    ]

    def screen_ncpg(self, responses: List[bool]) -> ScreeningResult:
        if len(responses) != len(self.NCPG_QUESTIONS):
            raise ValueError(f"Expected {len(self.NCPG_QUESTIONS)} responses, got {len(responses)}")
        yes = sum(1 for r in responses if r)
        if yes <= 1:
            level, rec = "Low risk", "Monitor your gambling behaviour and keep a fixed entertainment budget."
        elif yes <= 3:
            level, rec = "Moderate risk", "Consider speaking with a qualified mental-health professional."
        else:
            level, rec = "High risk", "Seek professional help from a mental-health/medical service. See resources below."
        indicators = [self.NCPG_QUESTIONS_VI[i] for i, r in enumerate(responses) if r]
        return ScreeningResult(
            framework="NCPG Brief Screen",
            risk_level=level,
            recommendation=rec,
            indicators_present=indicators,
            score=yes,
            max_score=len(self.NCPG_QUESTIONS),
            support_resources=self.vietnam_resources(),
        )

    def screen_pgsi(self, responses: List[int]) -> ScreeningResult:
        if len(responses) != len(self.PGSI_ITEMS):
            raise ValueError(f"Expected {len(self.PGSI_ITEMS)} responses, got {len(responses)}")
        if any(r < 0 or r > 3 for r in responses):
            raise ValueError("Each PGSI response must be 0-3")
        total = sum(responses)
        if total == 0:
            level, rec = "Non-problem gambler", "Continue healthy practices; treat lottery as entertainment only."
        elif total <= 2:
            level, rec = "Low-risk gambler", "Monitor your gambling behaviour and keep a fixed entertainment budget."
        elif total <= 7:
            level, rec = "Moderate-risk gambler", "Consider speaking with a qualified mental-health professional."
        else:
            level, rec = "Problem gambler", "Seek professional help from a mental-health/medical service. See resources below."
        return ScreeningResult(
            framework="Problem Gambling Severity Index (PGSI)",
            risk_level=level,
            recommendation=rec,
            score=total,
            max_score=len(self.PGSI_ITEMS) * 3,
            support_resources=self.vietnam_resources(),
        )

    def screen_indicators(self, present: List[str]) -> ScreeningResult:
        present_set = set(present)
        all_ind = self.BEHAVIORAL_INDICATORS + self.FINANCIAL_INDICATORS + self.PSYCHOLOGICAL_INDICATORS
        unknown = present_set - {i for i in all_ind}
        if unknown:
            raise ValueError(f"Unknown indicators: {sorted(unknown)}")
        b = sum(1 for i in self.BEHAVIORAL_INDICATORS if i in present_set)
        f = sum(1 for i in self.FINANCIAL_INDICATORS if i in present_set)
        p = sum(1 for i in self.PSYCHOLOGICAL_INDICATORS if i in present_set)
        total = len(present_set)
        if total == 0:
            level, rec = "No indicators present", "Continue monitoring; keep a fixed entertainment budget."
        elif total <= 2:
            level, rec = "Low risk", "Be mindful of your gambling behaviour and budget."
        elif total <= 5:
            level, rec = "Moderate risk", "Consider professional consultation."
        else:
            level, rec = "High risk", "Seek professional help from a mental-health/medical service. See resources below."
        return ScreeningResult(
            framework="Indicator-based Screening",
            risk_level=level,
            recommendation=rec,
            indicators_present=sorted(present_set),
            score=total,
            max_score=len(all_ind),
            support_resources=self.vietnam_resources(),
            extra={"behavioral": b, "financial": f, "psychological": p},
        )

    def detect_risk_in_text(self, text: str, threshold: int = 2) -> ScreeningResult:
        """Heuristic, diacritic-insensitive keyword scan for problem-gambling risk language (VI + EN).

        Vietnamese keywords are matched after stripping diacritics so that both
        "gỡ lại" (with diacritics) and "go lai"/"gỡ lai" (mixed/ASCII) are caught.
        """
        settings = json.loads((CONFIG_DIR / "skill-settings.json").read_text(encoding="utf-8-sig"))
        keywords = (
            settings["skill_settings"]["risk_detection"]["keywords_en"]
            + settings["skill_settings"]["risk_detection"]["keywords_vi"]
        )
        norm_text = _strip_diacritics(text)
        hits = [kw for kw in keywords if _strip_diacritics(kw) in norm_text]
        level = "High risk" if len(hits) >= threshold else ("Moderate risk" if hits else "No indicators present")
        rec = (
            "Seek professional help from a mental-health/medical service. See resources below."
            if len(hits) >= threshold
            else ("Consider professional consultation." if hits else "Continue monitoring.")
        )
        return ScreeningResult(
            framework="Keyword heuristic scan",
            risk_level=level,
            recommendation=rec,
            indicators_present=hits,
            score=len(hits),
            max_score=len(keywords),
            support_resources=self.vietnam_resources(),
        )

    @staticmethod
    def vietnam_resources() -> Dict:
        res = _load_resources()["support_resources"]
        return {
            "vietnam": res["vietnam"],
            "international_and_online": res["international_and_online"],
            "crisis": res["crisis"],
            "disclaimer": "Educational screening only, not a diagnosis. Vietnam does not yet have a dedicated problem-gambling hotline; mental-health, medical, and social services above are the appropriate entry points.",
        }


def format_result(r: ScreeningResult) -> str:
    lines = [
        f"Risk Screening Results ({r.framework})",
        "=" * 60,
        f"Risk level     : {r.risk_level}",
        f"Recommendation : {r.recommendation}",
    ]
    if r.score is not None:
        lines.append(f"Score          : {r.score}/{r.max_score}")
    if r.indicators_present:
        lines.append("Indicators present:")
        for ind in r.indicators_present:
            lines.append(f"  - {ind}")
    res = r.support_resources.get("vietnam", {})
    if res:
        lines.append("Vietnam-context resources:")
        for key, val in res.items():
            if isinstance(val, dict):
                name = val.get("name", key)
                phone = val.get("phone", "")
                lines.append(f"  - {name}" + (f" | {phone}" if phone else ""))
    lines.append("Disclaimer: Educational screening only, not a diagnosis. Consult a qualified professional.")
    return "\n".join(lines)


def main() -> None:
    s = RiskScreener()
    print(format_result(s.screen_ncpg([False, False, True, False, True, False, False])))
    print()
    print(format_result(s.screen_pgsi([0, 0, 1, 0, 1, 0, 0, 0, 0])))
    print()
    print(format_result(s.detect_risk_in_text("Toi muon gỡ lai so tien da thua, co can vay tien de choi them khong?")))


if __name__ == "__main__":
    main()
