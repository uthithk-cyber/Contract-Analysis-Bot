from typing import Dict, Tuple
import re

CONTRACT_KEYWORDS = {
	"Employment Agreement": ["employee", "employer", "salary", "probation", "notice period", "termination", "joining"],
	"Vendor/Procurement Contract": ["delivery", "supplier", "vendor", "purchase order", "invoice", "goods", "services provided"],
	"Lease Agreement": ["lease", "rent", "tenant", "landlord", "premises", "renewal", "security deposit"],
	"Partnership Deed": ["partners", "partnership", "profit share", "capital contribution", "partner"],
	"Service Agreement": ["service", "statement of work", "sow", "service level", "sla", "performance"],
}

def classify_contract(text: str) -> Tuple[str, Dict[str, int]]:
	"""Return the best-matching contract type and raw keyword hit counts.

	This is a lightweight rule-based classifier suitable for prototyping.
	"""
	counts: Dict[str, int] = {}
	norm = text.lower()
	for label, kws in CONTRACT_KEYWORDS.items():
		c = 0
		for kw in kws:
			# simple substring match; kw may contain spaces
			if kw in norm:
				c += norm.count(kw)
			else:
				# also try word-boundary match for single words
				if re.search(r"\b" + re.escape(kw) + r"\b", norm):
					c += 1
		counts[label] = c

	# choose highest count; if all zero, return 'Unknown'
	best = max(counts.items(), key=lambda x: x[1])
	if best[1] == 0:
		return "Unknown", counts
	return best[0], counts

if __name__ == "__main__":
	sample = """
	This agreement is made between the Employer and the Employee. The employee shall receive salary, be subject to a probation period and will have a notice period of 1 month for termination.
	"""
	print(classify_contract(sample))

