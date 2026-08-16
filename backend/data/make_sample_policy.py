"""
Generates a sample payer-policy PDF to exercise the ingestion pipeline.
Realistic in structure, entirely fabricated content. Run:
    python -m data.make_sample_policy
"""
from pypdf import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

POLICY_TEXT = """MERIDIAN HEALTH PLAN
Medical Policy: Advanced Imaging - MRI Brain without Contrast

Policy Number: POL-MRI-70551
Procedure: MRI brain without contrast (CPT 70551)

PRIOR AUTHORIZATION REQUIRED: Yes

Coverage Criteria. Prior authorization for MRI of the brain without contrast
(CPT 70551) will be approved when ALL of the following criteria are met:

1. Documented new or progressive neurological symptoms persisting for at
   least 4 weeks (for example, persistent headache with red-flag features,
   focal weakness, or new-onset seizure).

2. Completion of an appropriate initial clinical evaluation, including a
   documented neurological examination.

3. Absence of a recent equivalent brain MRI within the prior 6 months, unless
   there is a documented clinical change warranting repeat imaging.

Requests that do not meet these criteria will be routed for manual clinical
review.
"""

def build():
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    text = c.beginText(60, 740)
    text.setFont("Helvetica", 11)
    for line in POLICY_TEXT.strip().split("\n"):
        text.textLine(line)
    c.drawText(text)
    c.save()
    buf.seek(0)

    writer = PdfWriter()
    writer.append(buf)
    with open("data/sample_policy_mri_brain.pdf", "wb") as f:
        writer.write(f)
    print("wrote data/sample_policy_mri_brain.pdf")

if __name__ == "__main__":
    build()