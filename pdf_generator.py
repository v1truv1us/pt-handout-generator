import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image as PILImage
from config import SELECTED_FILE, OUTPUT_PDF, EXERCISES


def get_image_size(path, max_width=1.2 * inch, max_height=1.2 * inch):
    try:
        with PILImage.open(path) as img:
            width, height = img.size
            ratio = min(max_width / width, max_height / height)
            if ratio < 1:
                return width * ratio, height * ratio
            return min(width, max_width), min(height, max_height)
    except:
        return max_width, max_height


def generate_pdf():
    if not os.path.exists(SELECTED_FILE):
        print(f"Error: {SELECTED_FILE} not found. Run 'select' first.")
        return False

    with open(SELECTED_FILE, "r") as f:
        selected_data = json.load(f)

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#2c3e50"),
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor("#7f8c8d"),
    )
    exercise_style = ParagraphStyle(
        "Exercise",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#34495e"),
        spaceBefore=0,
        spaceAfter=2,
    )
    reps_style = ParagraphStyle(
        "Reps",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#7f8c8d"),
    )

    story = []

    story.append(Paragraph("Hip Labral Tear & EDS PT Routine", title_style))
    story.append(Paragraph("Beginner Physical Therapy Handout", subtitle_style))
    story.append(Spacer(1, 0.2 * inch))

    table_data = []
    header = ["", "Exercise", "Reps/Sets"]
    table_data.append(header)

    for exercise in EXERCISES:
        exercise_id = exercise["id"]
        data = selected_data.get(exercise_id, {})

        local_path = data.get("local_path")
        img = None

        if local_path and os.path.exists(local_path):
            try:
                img_width, img_height = get_image_size(local_path)
                img = Image(local_path, width=img_width, height=img_height)
            except Exception as e:
                print(f"Error loading image for {exercise['name']}: {e}")
                img = Paragraph("No image", reps_style)
        else:
            img = Paragraph("No image", reps_style)

        exercise_para = Paragraph(
            f"<b>{data.get('name', exercise['name'])}</b>", exercise_style
        )
        reps_para = Paragraph(data.get("reps", exercise["reps"]), reps_style)

        table_data.append([img, exercise_para, reps_para])

    col_widths = [1.4 * inch, 3.5 * inch, 2 * inch]
    table = Table(
        table_data, colWidths=col_widths, rowHeights=[1.3 * inch] * len(table_data)
    )

    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (1, 1), (1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#7f8c8d")),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ecf0f1")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 0.3 * inch))

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#95a5a6"),
    )
    story.append(
        Paragraph(
            "Consult your physical therapist before starting any new exercise routine.",
            footer_style,
        )
    )

    doc.build(story)
    print(f"\nPDF generated: {OUTPUT_PDF}")
    return True
