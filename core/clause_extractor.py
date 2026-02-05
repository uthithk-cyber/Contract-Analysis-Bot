import re
from typing import List

def split_into_clauses(text: str) -> List[str]:
    # Split on common clause numbering and headings
    parts = re.split(r"\n\s*(?=(?:\d+\.|\d+\)|Section\s+\d+|Clause\s+\d+))", text)
    clauses = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # further split long paragraphs by double newlines
        sub = [s.strip() for s in re.split(r"\n\n+", p) if s.strip()]
        clauses.extend(sub)
    # fallback: if no clauses found, split by sentences
    if not clauses:
        clauses = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    return clauses
