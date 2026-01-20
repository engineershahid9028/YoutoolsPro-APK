from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_pdf(user_id, tool, content):
    filename = f"/tmp/report_{user_id}_{tool}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "YouToolsPro AI Report")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"User ID: {user_id}")
    c.drawString(50, height - 100, f"Tool: {tool}")
    c.drawString(50, height - 120, f"Date: {datetime.utcnow()}")

    text = c.beginText(50, height - 160)
    text.setFont("Helvetica", 11)

    for line in content.split("\n"):
        text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()

    return filename