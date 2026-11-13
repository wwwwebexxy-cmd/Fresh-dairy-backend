"""Code 128 barcode rendering for admin product labels."""

import base64
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.graphics import renderSVG
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.barcode.code128 import Code128
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


BARCODE_MAX_LENGTH = 36
BARCODE_BAR_WIDTH = 0.30 * mm
BARCODE_HEIGHT = 18 * mm


def is_valid_barcode_value(value):
    return bool(
        isinstance(value, str)
        and value
        and len(value) <= BARCODE_MAX_LENGTH
        and value.isascii()
        and all(character.isprintable() for character in value)
    )


def barcode_svg_data_uri(value):
    if not is_valid_barcode_value(value):
        return None

    drawing = createBarcodeDrawing(
        "Code128",
        value=value,
        barHeight=BARCODE_HEIGHT,
        barWidth=BARCODE_BAR_WIDTH,
        humanReadable=False,
    )
    svg = renderSVG.drawToString(drawing).encode("utf-8")
    encoded = base64.b64encode(svg).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def render_product_barcode_pdf(product_name, entries):
    """Return a printable PDF with one product label for every sellable SKU."""
    buffer = BytesIO()
    page_width, _ = A4
    margin = 12 * mm
    label_width = page_width - 2 * margin
    styles = getSampleStyleSheet()
    product_style = ParagraphStyle(
        "BarcodeProductName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#173B53"),
    )
    variant_style = ParagraphStyle(
        "BarcodeVariantName",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#536875"),
    )
    code_style = ParagraphStyle(
        "BarcodeValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=1,
        textColor=colors.HexColor("#173B53"),
    )
    story = []

    for entry in entries:
        value = entry["barcode"]
        barcode = Code128(
            value,
            barHeight=BARCODE_HEIGHT,
            barWidth=BARCODE_BAR_WIDTH,
            humanReadable=False,
        )
        if barcode.width > label_width - 16 * mm:
            raise ValueError("A barcode is too wide to fit on a printable product label.")

        label = Table(
            [
                [Paragraph(escape(product_name), product_style)],
                [Paragraph(escape(entry["variant_label"]), variant_style)],
                [barcode],
                [Paragraph(escape(value), code_style)],
            ],
            colWidths=[label_width],
        )
        label.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#C8D8E2")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("ALIGN", (0, 2), (0, 2), "CENTER"),
            ("ALIGN", (0, 3), (0, 3), "CENTER"),
        ]))
        story.append(KeepTogether([label, Spacer(1, 4 * mm)]))

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=f"{product_name} Barcodes",
        author="The Fresh Dairy Delight FZE",
    )
    document.build(story)
    return buffer.getvalue()
