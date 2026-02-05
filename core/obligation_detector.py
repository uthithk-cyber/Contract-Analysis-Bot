import re
from typing import List, Dict

OBLIGATION_PATTERNS = [
	r"\bshall\b",
	r"\bmust\b",
	r"\bwill\b",
	r"\bis required to\b",
	r"\bagrees to\b",
	r"\bundertakes to\b",
	r"\bis obliged to\b",
]

PROHIBITION_PATTERNS = [
	r"\bshall not\b",
	r"\bmust not\b",
	r"\bprohibit(?:ed|s)?\b",
	r"\bforbidden\b",
	r"\bmay not\b",
]

RIGHT_PATTERNS = [
	r"\bis entitled to\b",
	r"\bhas the right to\b",
	r"\bmay exercise\b",
]

def _matches_any(text: str, patterns: List[str]) -> List[str]:
	hits = []
	for p in patterns:
		if re.search(p, text, flags=re.I):
			hits.append(p)
	return hits

def detect_obligations(text: str) -> List[Dict[str, str]]:
	"""Split text into candidate clauses and label each as Obligation/Right/Prohibition/Neutral.

	Returns a list of dicts: {"clause": str, "label": str, "matches": List[str]}
	"""
	# naive splitting: by line breaks or sentence endings
	parts = [p.strip() for p in re.split(r"(?<=[\n\.\;\:])\s+", text) if p.strip()]
	results: List[Dict[str, str]] = []
	for p in parts:
		prov = _matches_any(p, PROHIBITION_PATTERNS)
		if prov:
			results.append({"clause": p, "label": "Prohibition", "matches": prov})
			continue
		oblig = _matches_any(p, OBLIGATION_PATTERNS)
		if oblig:
			results.append({"clause": p, "label": "Obligation", "matches": oblig})
			continue
		right = _matches_any(p, RIGHT_PATTERNS)
		if right:
			results.append({"clause": p, "label": "Right", "matches": right})
			continue
		results.append({"clause": p, "label": "Neutral", "matches": []})
	return results

def summarize_obligations(text: str) -> Dict[str, List[str]]:
	data = {"Obligation": [], "Prohibition": [], "Right": [], "Neutral": []}
	for item in detect_obligations(text):
		data[item["label"]].append(item["clause"])
	return data

if __name__ == "__main__":
	sample = (
		"The Supplier shall deliver goods within 30 days. The Buyer may cancel the order. "
		"The Contractor must not assign this Agreement. The Client is entitled to inspect the work."
	)
	from pprint import pprint

	pprint(detect_obligations(sample))

