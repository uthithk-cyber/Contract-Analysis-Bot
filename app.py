import json
import time
import io
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from core.loader import load_uploaded_file
from core.clause_extractor import split_into_clauses
from core.ner import extract_entities
from core.risk_engine import score_clause, contract_score
from core.summary import summarize_contract, explain_clause, suggest_alternative
from core.classifier import classify_contract
from core.obligation_detector import summarize_obligations

from reportlab.pdfgen import canvas

AUDIT_PATH = Path("audit_logs") / "sample_log.json"
AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)


def append_audit(entry: dict):
    data = []
    if AUDIT_PATH.exists():
        try:
            data = json.loads(AUDIT_PATH.read_text())
        except Exception:
            data = []
    data.append(entry)
    AUDIT_PATH.write_text(json.dumps(data, indent=2))


def main():
    st.title("Contract Analysis & Risk Assessment Bot — SME Prototype")
    st.sidebar.title("Controls")
    if st.sidebar.button("Load demo sample (Business Loan)"):
        demo_path = Path("templates") / "business_loan_sample.txt"
        if demo_path.exists():
            text = demo_path.read_text(encoding="utf-8")
            is_hindi = False
            uploaded = None
        else:
            st.sidebar.error("Demo sample not found in templates/")
            uploaded = None
            text = None
            is_hindi = False
    else:
        uploaded = st.file_uploader(
            "Upload contract (PDF / DOCX / TXT)",
            type=["pdf", "docx", "doc", "txt"]
        )

        if uploaded is None:
            st.info("Upload a contract to begin analysis or use 'Load demo sample'.")
            return

        raw = uploaded.read()
        text, is_hindi = load_uploaded_file(raw, uploaded.name)
    # source name for audit logs: uploaded file name or demo sample
    if uploaded is not None:
        source_name = getattr(uploaded, "name", "uploaded_contract")
    else:
        source_name = demo_path.name if 'demo_path' in locals() and demo_path.exists() else "demo_sample"
    st.write("**Hindi detected:**", is_hindi)

    # ---------------- Contract Classification ----------------
    ctype, ccounts = classify_contract(text)
    col1, col2, col3 = st.columns([2, 1, 1])
    col1.subheader("Contract Type")
    col1.write(ctype)

    # ---------------- Summary ----------------
    with st.expander("Simplified Summary", expanded=True):
        summary = summarize_contract(text, max_sentences=6)
        for s in summary:
            st.write("•", s)

    # ---------------- Clause Analysis ----------------
    clauses = split_into_clauses(text)
    clauses_with_scores = []
    clause_scores = {}

    for i, cl in enumerate(clauses[:200]):
        score, _ = score_clause(cl)
        clause_scores[i] = score
        clauses_with_scores.append((cl, score))

    # ---------------- GRAPH 1: Clause Risk Distribution ----------------
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    for _, score in clauses_with_scores:
        risk_counts[score] += 1

    df_risk = pd.DataFrame.from_dict(
        risk_counts, orient="index", columns=["Count"]
    )

    st.subheader("Clause Risk Distribution")

    fig1, ax1 = plt.subplots()
    df_risk.plot(kind="bar", ax=ax1)
    ax1.set_xlabel("Risk Level")
    ax1.set_ylabel("Number of Clauses")
    st.pyplot(fig1)

    # ---------------- Entities ----------------
    entities = extract_entities(text)
    with st.container():
        st.subheader("Extracted Entities")
        ent_cols = st.columns(2)
        left = ent_cols[0]
        right = ent_cols[1]
        left.write("**PARTIES:**")
        left.write(', '.join(entities.get('PARTIES', [])) or '—')
        left.write("**DATES:**")
        left.write(', '.join(entities.get('DATES', [])) or '—')
        right.write("**AMOUNTS:**")
        right.write(', '.join(entities.get('AMOUNTS', [])) or '—')
        right.write("**JURISDICTION:**")
        right.write(', '.join(entities.get('JURISDICTION', [])) or '—')

    # ---------------- Obligations ----------------
    obligations_summary = summarize_obligations(text)

    st.subheader("Obligations / Rights / Prohibitions")
    ob_cols = st.columns(3)
    for (label, items), c in zip(obligations_summary.items(), ob_cols):
        c.write(f"**{label} ({len(items)})**")
        for it in items[:8]:
            c.write(f"- {it}")

    # ---------------- GRAPH 2: Obligations Distribution ----------------
    ob_counts = {k: len(v) for k, v in obligations_summary.items()}
    df_ob = pd.DataFrame.from_dict(
        ob_counts, orient="index", columns=["Count"]
    )

    st.subheader("Obligations Distribution")

    fig2, ax2 = plt.subplots()
    df_ob.plot(kind="bar", ax=ax2)
    ax2.set_xlabel("Obligation Type")
    ax2.set_ylabel("Count")
    st.pyplot(fig2)

    # ---------------- Clause Explanations ----------------
    st.subheader("Clause Risk & Explanation")
    for i, (cl, score) in enumerate(clauses_with_scores[:20]):
        color = '#e9f7ef' if score == 'Low' else ('#fff6d1' if score == 'Medium' else '#ffd6d6')
        st.markdown(
            f"<div style='background:{color};padding:8px;margin-bottom:6px'>"
            f"<b>Clause {i+1} – {score}</b><br>{explain_clause(cl)}</div>",
            unsafe_allow_html=True
        )

    # ---------------- Composite Risk Score ----------------
    comp = contract_score(clause_scores)

    st.subheader("Overall Contract Risk Score")
    score_col1, score_col2 = st.columns([3, 1])
    score_col1.progress(comp / 100)
    score_col2.metric("Score", f"{comp} / 100")

    # ---------------- Audit Log ----------------
    append_audit({
        "timestamp": int(time.time()),
        "filename": source_name,
        "composite_score": comp,
        "num_clauses": len(clauses)
    })


if __name__ == "__main__":
    main()
