import io
import re
from typing import Tuple

def detect_hindi(text: str) -> bool:
    return bool(re.search(r"[\u0900-\u097F]", text))

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        import pdfplumber
    except Exception:
        raise ImportError("pdfplumber is required to parse PDFs. Install from requirements.txt")
    text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        import docx
    except Exception:
        raise ImportError("python-docx is required to parse DOCX. Install from requirements.txt")
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)

def extract_text_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except Exception:
        return file_bytes.decode("latin-1", errors="ignore")

def load_uploaded_file(file_bytes: bytes, filename: str) -> Tuple[str, bool]:
    name = filename.lower()
    if name.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx") or name.endswith(".doc"):
        text = extract_text_from_docx(file_bytes)
    else:
        text = extract_text_from_txt(file_bytes)
    is_hindi = detect_hindi(text)
    return text, is_hindi
