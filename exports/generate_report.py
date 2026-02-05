from pathlib import Path
import sys
# ensure project root is on sys.path so sibling package `core` can be imported when running
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.classifier import classify_contract
from core.summary import summarize_contract, explain_clause, suggest_alternative
from core.ner import extract_entities
from core.obligation_detector import summarize_obligations
from core.clause_extractor import split_into_clauses
from core.risk_engine import score_clause, contract_score

TEMPLATE = Path("templates") / "business_loan_sample.txt"
OUT = Path("exports") / "report.html"

text = TEMPLATE.read_text(encoding="utf-8")

ctype, ccounts = classify_contract(text)
summary = summarize_contract(text, max_sentences=6)
entities = extract_entities(text)
obligations = summarize_obligations(text)
clauses = split_into_clauses(text)
clauses_with_scores = []
clause_scores = {}
for i, cl in enumerate(clauses):
    score, _ = score_clause(cl)
    clause_scores[i] = score
    clauses_with_scores.append((cl, score))
comp = contract_score(clause_scores)

html = []
html.append(f"<html><head><meta charset='utf-8'><title>Contract Report</title></head><body style='font-family:Arial,sans-serif'>")
html.append(f"<h1>Contract Analysis — Demo: Business Loan Agreement</h1>")
html.append(f"<h2>Contract Type</h2><p>{ctype}</p>")
html.append("<h2>Simplified Summary</h2><ul>")
for s in summary:
    html.append(f"<li>{s}</li>")
html.append("</ul>")

html.append("<h2>Extracted Entities</h2>")
html.append("<ul>")
html.append(f"<li><b>PARTIES:</b> {', '.join(entities.get('PARTIES',[])) or '—'}</li>")
html.append(f"<li><b>DATES:</b> {', '.join(entities.get('DATES',[])) or '—'}</li>")
html.append(f"<li><b>AMOUNTS:</b> {', '.join(entities.get('AMOUNTS',[])) or '—'}</li>")
html.append(f"<li><b>JURISDICTION:</b> {', '.join(entities.get('JURISDICTION',[])) or '—'}</li>")
html.append("</ul>")

html.append("<h2>Obligations / Rights / Prohibitions</h2>")
for label, items in obligations.items():
    html.append(f"<h3>{label} ({len(items)})</h3><ul>")
    for it in items[:10]:
        html.append(f"<li>{it}</li>")
    html.append("</ul>")

html.append("<h2>Suggested Alternative Clauses (Top Matches)</h2>")
for i, (cl, score) in enumerate(clauses_with_scores[:20]):
    sug = suggest_alternative(cl)
    html.append(f"<p><b>Clause {i+1} suggestion:</b> {sug}</p>")

html.append("<h2>Clause-level Risk & Explanations</h2>")
for i, (cl, score) in enumerate(clauses_with_scores[:20]):
    html.append(f"<p><b>Clause {i+1} — {score}</b> — {explain_clause(cl)}</p>")

html.append(f"<h2>Contract Composite Risk Score</h2><p>{comp} / 100</p>")
html.append("</body></html>")

OUT.write_text('\n'.join(html), encoding='utf-8')
print(f"Report written to {OUT}")
