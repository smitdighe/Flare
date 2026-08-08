"""
PDF report generator using reportlab.
"""
from io import BytesIO
from typing import List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER


def generate_pdf(
    alerts: List[dict],
    title: str = "Flare Security Alert Report",
    stats: Optional[dict] = None,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=20, alignment=TA_CENTER)
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.3 * inch))

    if stats:
        elements.append(Paragraph("Executive Summary", styles["Heading2"]))
        summary_data = [
            ["Total Alerts", str(stats.get("total", 0))],
            ["High Severity", str(stats.get("by_severity", {}).get("high", 0))],
            ["Medium Severity", str(stats.get("by_severity", {}).get("medium", 0))],
            ["Low Severity", str(stats.get("by_severity", {}).get("low", 0))],
            ["Unique Source IPs", str(stats.get("unique_src_ips", 0))],
            ["Pipeline Success Rate", f"{stats.get('pipeline_success_rate', 0)}%"],
        ]
        summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Alert Details", styles["Heading2"]))

    if alerts:
        table_data = [["ID", "Severity", "Type", "Source IP", "Signature"]]
        for alert in alerts[:50]:
            table_data.append([
                str(alert.get("id", ""))[:8],
                str(alert.get("severity", "")),
                str(alert.get("attack_type", "")),
                str(alert.get("src_ip", "")),
                str(alert.get("signature", ""))[:40],
            ])

        table = Table(table_data, colWidths=[0.8 * inch, 0.8 * inch, 0.8 * inch, 1.2 * inch, 2.9 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No alerts to display.", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()
