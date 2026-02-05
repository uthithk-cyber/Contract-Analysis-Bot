from typing import List, Tuple
import re

KEYWORDS = [
    "termination",
    "indemnity",
    "penalty",
    "arbitration",
    "jurisdiction",
    "confidential",
    "renewal",
    "non-compete",
    "ip",
    "ownership",
]


def _sentences_from_text(text: str) -> List[str]:
    try:
        import nltk
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)
    except LookupError:
        # punkt_tab not found; download it
        try:
            import nltk
            nltk.download("punkt_tab", quiet=True)
            from nltk.tokenize import sent_tokenize
            return sent_tokenize(text)
        except Exception:
            # fallback to regex-based splitting
            return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    except Exception:
        # any other error; use fallback
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def summarize_contract(text: str, max_sentences: int = 5) -> List[str]:
    """Return a short extractive summary: top sentences ranked by keyword hits and sentence length.

    This is a lightweight heuristic summarizer suitable for quick overviews.
    """
    sents = _sentences_from_text(text)
    scored: List[Tuple[int, str]] = []
    for s in sents:
        score = sum(1 for kw in KEYWORDS if kw in s.lower())
        # small boost for longer sentences that often carry more detail
        score += min(2, max(0, len(s.split()) // 30))
        scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s for _, s in scored[:max_sentences]]
    return top


def explain_clause(clause: str) -> str:
    """Produce a plain-language explanation and short mitigation advice for a clause."""
    c = clause.strip()
    low = c.lower()
    if "indemn" in low:
        return (
            "Explainer: This clause requires one party to compensate the other for specified losses. "
            "Mitigation: Limit the scope, carve out indirect losses, and add a monetary cap and notice/defence rights."
        )
    if "non-compete" in low or "non compete" in low:
        return (
            "Explainer: Restricts commercial activity after termination. "
            "Mitigation: Narrow duration, geographic scope and activities; prefer non-solicit over broad non-compete."
        )
    if "auto" in low and "renew" in low:
        return (
            "Explainer: Contract auto-renews unless notice is given. "
            "Mitigation: Add a clear notice window and maximum auto-renew terms."
        )
    if "termination" in low:
        return (
            "Explainer: Defines how parties may end the agreement. "
            "Mitigation: Check notice periods, cure rights for breaches, and whether termination causes penalties."
        )
    if "confidential" in low or "nda" in low:
        return (
            "Explainer: Protects confidential information. "
            "Mitigation: Ensure duration is reasonable and carve out prior and independently-developed information."
        )
    if "arbitrat" in low or "jurisdiction" in low:
        return (
            "Explainer: Sets dispute resolution forum and law. "
            "Mitigation: Check if forum is neutral and whether arbitration is mandatory; consider injunctive relief carveouts."
        )
    return (
        "Explainer: This clause sets obligations or rights. "
        "Mitigation: Clarify ambiguous terms, add limits and timelines, and consider caps for liabilities."
    )


def suggest_alternative(clause: str) -> str:
    """Return a short suggested alternative clause (template-style) for common risky clauses."""
    low = clause.lower()
    if "indemn" in low:
        return (
            "Suggested alternative: The indemnifying party's liability shall be limited to direct damages and capped at the total fees paid under this Agreement in the preceding 12 months. Indirect or consequential losses are excluded."
        )
    if "non-compete" in low or "non compete" in low:
        return (
            "Suggested alternative: The restricted period shall not exceed 6 months and be limited to the State of Maharashtra; restrictions limited to direct competition only."
        )
    if "auto" in low and "renew" in low:
        return (
            "Suggested alternative: The Agreement shall automatically renew for successive 1-year terms unless either party provides 60 days' prior written notice of non-renewal."
        )
    if "termination" in low:
        return (
            "Suggested alternative: Either party may terminate for material breach if the breaching party fails to remedy such breach within 30 days of written notice; termination shall not relieve accrued payment obligations."
        )
    if "confidential" in low or "nda" in low:
        return (
            "Suggested alternative: Confidential information shall be protected for a period of 3 years post-termination; obligations shall not apply to information independently developed or publicly available."
        )
    return "No template suggestion available; consider clarifying obligations and adding limits or timelines."
