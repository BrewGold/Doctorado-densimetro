#!/usr/bin/env python3
"""Generate the visual layout PDF from the KiCad mechanical rectangles."""

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
BOARD = HERE / "prototipo_mecanico.kicad_pcb"
PDF = HERE / "prototipo_mecanico.pdf"


def rectangles(text, layer):
    pattern = (
        r"\(gr_rect\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)"
        r"\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)"
        r"(?:(?!\(tstamp\b).)*?\(layer\s+\"" + re.escape(layer) + r"\"\)"
    )
    return [tuple(map(float, match)) for match in re.findall(pattern, text, re.S)]


text = BOARD.read_text(encoding="utf-8")
outline = rectangles(text, "Edge.Cuts")
front = rectangles(text, "F.Fab")
back = rectangles(text, "B.Fab")
clips = rectangles(text, "Dwgs.User")
if len(outline) != 1 or len(front) != 6 or len(back) != 1 or len(clips) != 2:
    raise ValueError("Unexpected mechanical rectangles; review the rendering script")

page_width, page_height = landscape(A4)
pdf = canvas.Canvas(str(PDF), pagesize=(page_width, page_height))
pdf.setTitle("Maqueta mecanica PCB portadora - no fabricar")
scale = 4.1
origin_x = 70


def draw_box(rect, origin_y, fill, stroke=colors.HexColor("#476474")):
    x1, y1, x2, y2 = rect
    pdf.setFillColor(fill)
    pdf.setStrokeColor(stroke)
    pdf.setLineWidth(1)
    pdf.rect(
        origin_x + x1 * scale,
        origin_y - y2 * scale,
        (x2 - x1) * scale,
        (y2 - y1) * scale,
        stroke=1,
        fill=1,
    )


def label(rect, origin_y, lines):
    x1, y1, x2, y2 = rect
    x = origin_x + (x1 + x2) * scale / 2
    y = origin_y - (y1 + y2) * scale / 2
    pdf.setFillColor(colors.HexColor("#172b35"))
    pdf.setFont("Helvetica-Bold", 9)
    for i, line in enumerate(lines):
        pdf.drawCentredString(x, y + (len(lines) - 1) * 6 - i * 12, line)


pdf.setFillColor(colors.HexColor("#172b35"))
pdf.setFont("Helvetica-Bold", 19)
pdf.drawString(55, page_height - 48, "Cápsula: primera distribución de la PCB")
pdf.setFont("Helvetica-Bold", 11)
pdf.setFillColor(colors.HexColor("#b63d2b"))
pdf.drawString(55, page_height - 70, "MAQUETA MECÁNICA · SIN CONEXIONES · NO FABRICAR")
pdf.setFillColor(colors.HexColor("#172b35"))
pdf.setFont("Helvetica", 11)
pdf.drawString(55, page_height - 94, "Cara superior: reservas aproximadas de los módulos")

top_y = page_height - 112
draw_box(outline[0], top_y, colors.HexColor("#eef4f1"))
labels = [
    ["ESP32-C3", "USB hacia tapa"],
    ["RECEPTOR", "18 x 15"],
    ["BOOST MT3608", "36 x 17"],
    ["C1", "reserva"],
    ["IMU", "25,4 x 17,78"],
    ["DRV8833", "25,4 x 17,78"],
]
for rect, lines in zip(front, labels):
    draw_box(rect, top_y, colors.HexColor("#c5dfe6"))
    label(rect, top_y, lines)
for rect in clips:
    draw_box(rect, top_y, colors.HexColor("#f8a737"), colors.HexColor("#a45605"))

pdf.setFont("Helvetica", 10)
pdf.setFillColor(colors.HexColor("#172b35"))
pdf.drawString(70, top_y - 24 * scale - 18, "TAPA / BOBINA")
pdf.drawRightString(70 + 164 * scale, top_y - 24 * scale - 18, "ACTUADOR / PUNTA")
pdf.setFont("Helvetica-Bold", 11)
pdf.drawString(55, top_y - 24 * scale - 49, "Batería situada bajo la PCB (proyección desde arriba)")

bottom_y = top_y - 24 * scale - 65
draw_box(outline[0], bottom_y, colors.HexColor("#eef4f1"))
draw_box(back[0], bottom_y, colors.HexColor("#f8d7a7"), colors.HexColor("#ae7130"))
label(back[0], bottom_y, ["14500 · 50 x 14 nominal", "bajo la PCB"])
for rect in clips:
    draw_box(rect, bottom_y, colors.HexColor("#f8a737"), colors.HexColor("#a45605"))

pdf.setFillColor(colors.HexColor("#172b35"))
pdf.setFont("Helvetica", 10)
notes_y = bottom_y - 24 * scale - 28
for note in [
    "Contorno provisional: 164 x 24 mm. C1: reserva arbitraria de 12 x 12 mm.",
    "Bobina y actuador fuera de la placa. Dimensiones en mm; dibujo no apto para fabricar.",
    "Faltan huellas, conectores, pines, pistas, corriente del actuador y protecciones.",
    "Naranja: reservas para clips, no ranuras finales. Verificar pines y cobre.",
]:
    pdf.drawString(55, notes_y, note)
    notes_y -= 15
pdf.save()
print(PDF)
