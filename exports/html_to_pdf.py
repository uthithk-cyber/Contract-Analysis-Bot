from pathlib import Path
import sys
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

HTML = Path("exports") / "report.html"
OUT = Path("exports") / "report.pdf"

if not HTML.exists():
    print(f"Input HTML not found: {HTML}")
    raise SystemExit(1)

raw = HTML.read_text(encoding="utf-8")
# simple convert: replace some tags with newlines/bullets
s = raw
s = s.replace("<li>", "\n- ")
s = s.replace("</li>", "")
s = re.sub(r"<h1.*?>", "\n\n", s)
s = re.sub(r"<h2.*?>", "\n\n", s)
s = re.sub(r"<h3.*?>", "\n\n", s)
s = s.replace("<p>", "\n\n")
s = s.replace("</p>", "\n\n")
# remove all remaining tags
s = re.sub(r"<[^>]+>", "", s)
# unescape simple HTML entities
s = s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
# normalize whitespace
s = re.sub(r"\r\n|\r", "\n", s)
lines = [ln.rstrip() for ln in s.split('\n') if ln.strip()]

c = canvas.Canvas(str(OUT), pagesize=A4)
width, height = A4
margin = 40
x = margin
y = height - margin
text_obj = c.beginText(x, y)
text_obj.setFont("Helvetica", 10)
max_width = width - 2*margin
# approx char width for Helvetica 10 is ~5.2 pts; estimate max chars
max_chars = int(max_width / 5.2)

for para in lines:
    # wrap paragraph
    while para:
        chunk = para[:max_chars]
        # try to break at last space
        if len(para) > max_chars:
            space = chunk.rfind(' ')
            if space != -1:
                chunk = para[:space]
                para = para[space+1:]
            else:
                para = para[max_chars:]
        else:
            para = ''
        text_obj.textLine(chunk)
        y -= 12
        if y < margin + 20:
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText(x, height - margin)
            text_obj.setFont("Helvetica", 10)
            y = height - margin
    # blank line
    text_obj.textLine("")
    y -= 12
    if y < margin + 20:
        c.drawText(text_obj)
        c.showPage()
        text_obj = c.beginText(x, height - margin)
        text_obj.setFont("Helvetica", 10)
        y = height - margin

c.drawText(text_obj)
c.save()
print(f"Wrote PDF: {OUT}")
