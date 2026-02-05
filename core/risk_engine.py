from typing import Tuple, Dict
import re

# More comprehensive, weighted keyword lists. Each level has keywords with an associated weight.
RISK_PATTERNS = {
    "High": [
        (r"indemnif", 3), (r"liabilit", 3), (r"penalt", 3), (r"forfeit", 3), (r"breach", 3),
        (r"unilateral termination", 4), (r"irrevoc", 3), (r"assign", 2), (r"security", 2),
        (r"default", 3), (r"guarantee", 2), (r"personal guarant", 3)
    ],
    "Medium": [
        (r"auto-?renew", 2), (r"lock-?in", 2), (r"non-?compete", 2), (r"confidential", 2),
        (r"arbitration", 2), (r"jurisdiction", 2), (r"late fee", 2), (r"pre-?payment", 2)
    ],
    "Low": [
        (r"notice period", 1), (r"renewal", 1), (r"payment", 1), (r"deliverable", 1),
        (r"performance", 1), (r"interest", 1), (r"repay", 1)
    ]
}


def score_clause(clause: str) -> Tuple[str, Dict[str, int]]:
    """Score a clause using weighted regex matching.

    Returns a tuple of (label, reasons) where reasons contains counts per level and a numeric
    `severity` between 0.0 and 1.0.
    """
    text = clause.lower()
    reasons = {"High": 0, "Medium": 0, "Low": 0, "severity": 0.0}
    total_weight = 0.0
    for level, pats in RISK_PATTERNS.items():
        for pat, w in pats:
            if re.search(pat, text, flags=re.I):
                reasons[level] += 1
                total_weight += w

    # Normalize severity: map total_weight into [0,1]. Use a soft cap so larger weights saturate.
    # Heuristic: treat 6+ weight as high severity
    severity = min(1.0, total_weight / 6.0)
    reasons["severity"] = round(severity, 3)

    if severity >= 0.6:
        label = "High"
    elif severity >= 0.25:
        label = "Medium"
    else:
        label = "Low"

    return label, reasons


def contract_score(clause_scores: Dict[int, object]) -> float:
    """Compute a composite contract score between 0 and 100.

    Accepts clause_scores where values may be label strings, numeric severities, or reason dicts
    returned by score_clause.
    """
    if not clause_scores:
        return 0.0

    total = 0.0
    count = 0
    for v in clause_scores.values():
        if isinstance(v, str):
            # map labels to weights
            weights = {"High": 1.0, "Medium": 0.5, "Low": 0.1}
            total += weights.get(v, 0.1)
        elif isinstance(v, dict) and "severity" in v:
            total += float(v.get("severity", 0.0))
        else:
            try:
                total += float(v)
            except Exception:
                total += 0.0
        count += 1

    # average severity in [0,1], scale to 0-100
    avg = total / max(1, count)
    return round(avg * 100, 1)
