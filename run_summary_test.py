from core.summary import summarize_contract, explain_clause, suggest_alternative

sample_text = (
    "The Supplier shall indemnify the Purchaser against any and all losses arising from breach. "
    "This Agreement will automatically renew unless either party gives 30 days' prior written notice. "
    "The Employee shall serve a probation of 6 months and is subject to a notice period of 1 month for termination. "
    "The Contractor must not assign this Agreement without prior written consent. "
    "All disputes shall be finally settled by arbitration in Mumbai under Indian law."
)

def run():
    print("=== Summary ===")
    for s in summarize_contract(sample_text, max_sentences=4):
        print("-", s)

    print("\n=== Clause Explanations & Suggestions ===")
    # pick a few clauses from the text by splitting simply
    clauses = [c.strip() for c in sample_text.split(".") if c.strip()]
    for cl in clauses:
        print("\nClause:", cl)
        print("Explanation:", explain_clause(cl))
        print("Suggestion:", suggest_alternative(cl))

if __name__ == "__main__":
    run()
