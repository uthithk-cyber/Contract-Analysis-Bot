import re
from typing import Dict, List

def extract_entities(text: str) -> Dict[str, List[str]]:
    ents = {"PARTIES": [], "DATES": [], "AMOUNTS": [], "JURISDICTION": []}
    # Simple regex-based entity extraction as fallback
    # Amounts
    for m in re.findall(r"\bRs\.?\s?[0-9,]+(?:\.[0-9]{1,2})?\b|\bINR\s?[0-9,.,]+\b|\b[0-9,]+\s?(?:INR|Rs)\b", text, flags=re.I):
        ents["AMOUNTS"].append(m)
    # Dates (simple)
    for m in re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b", text, flags=re.I):
        ents["DATES"].append(m)
    # Parties: look for 'between X and Y' patterns
    for m in re.findall(r"between\s+([^,\n]+?)\s+and\s+([^,\n]+?)(?:[.,\n]|$)", text, flags=re.I):
        ents["PARTIES"].extend([m[0].strip(), m[1].strip()])
    # Jurisdiction keywords
    for m in re.findall(r"\b(governed by|jurisdiction of|subject to the laws of)\s+([^\n,.]+)", text, flags=re.I):
        ents["JURISDICTION"].append(m[1].strip())
    # deduplicate
    for k in ents:
        ents[k] = list(dict.fromkeys(ents[k]))
    return ents
