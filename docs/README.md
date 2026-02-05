# Contract Analysis & Risk Assessment Bot — Prototype

This repository contains a lightweight prototype for contract analysis focused on Indian SME needs. It provides local, rule-based parsing, entity extraction, clause splitting, risk scoring, simple summaries, PDF export, and audit logs.

Run locally with Streamlit.

Setup (recommended virtualenv):

1. Install dependencies (see `setup/requirements.txt`):

```bash
python -m pip install -r setup/requirements.txt
python -m spacy download en_core_web_sm
```

2. Run the app:

```bash
streamlit run app.py
```

Notes:
- This is a prototype with rule-based NLP and does not call external LLMs. You can integrate `GPT-4` or `Claude` later for richer legal reasoning.
- The project writes audit entries to `audit_logs/sample_log.json`.
