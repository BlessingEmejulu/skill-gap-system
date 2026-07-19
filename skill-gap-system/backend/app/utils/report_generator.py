"""
Generates PDF (ReportLab) and Excel (OpenPyXL) exports for employability /
skill-gap / analytics reports.
"""
import os
from datetime import datetime

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.config import settings


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def generate_pdf_report(title: str, rows: list[dict], out_dir: str = "./reports") -> str:
    _ensure_dir(out_dir)
    filename = f"{title.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.pdf"
    filepath = os.path.join(out_dir, filename)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = [Paragraph(title, styles["Title"]), Spacer(1, 16)]

    if rows:
        headers = list(rows[0].keys())
        table_data = [headers] + [[str(row.get(h, "")) for h in headers] for row in rows]
        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ]
            )
        )
        elements.append(table)
    else:
        elements.append(Paragraph("No data available for this report.", styles["Normal"]))

    doc.build(elements)
    return filepath


def generate_excel_report(title: str, rows: list[dict], out_dir: str = "./reports") -> str:
    _ensure_dir(out_dir)
    filename = f"{title.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.xlsx"
    filepath = os.path.join(out_dir, filename)

    wb = Workbook()
    ws = wb.active
    ws.title = title[:31] if title else "Report"

    if rows:
        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([row.get(h, "") for h in headers])
    else:
        ws.append(["No data available"])

    wb.save(filepath)
    return filepath
