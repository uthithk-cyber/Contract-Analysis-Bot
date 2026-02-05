import json
from core.classifier import classify_contract
from core.ner import extract_entities
from core.clause_extractor import split_into_clauses
from core.obligation_detector import detect_obligations
from core.risk_engine import score_clause, contract_score
from core.summary import summarize_contract

sample_text = (
    "This Agreement is made between Alpha Pvt Ltd and Beta LLP. "
    "The Supplier shall deliver goods within 30 days. The Buyer may cancel the order. "
    "The Contractor must not assign this Agreement. The Client is entitled to inspect the work. "
    "The agreement is governed by the laws of India. Salary and probation clauses for employees are included."
)

def run():
    ctype, counts = classify_contract(sample_text)
    ents = extract_entities(sample_text)
    clauses = split_into_clauses(sample_text)
    obligations = detect_obligations(sample_text)
    clause_scores = {}
    scored = []
    for i, cl in enumerate(clauses):
        s, reasons = score_clause(cl)
        clause_scores[i] = s
        scored.append({"clause": cl, "score": s})
    comp = contract_score(clause_scores)
    summary = summarize_contract(sample_text, max_sentences=3)

    out = {
        "contract_type": ctype,
        "type_counts": counts,
        "entities": ents,
        "num_clauses": len(clauses),
        "obligations_sample": obligations[:5],
        "clause_scores": scored,
        "composite_score": comp,
        "summary": summary,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
