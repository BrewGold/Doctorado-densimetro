#!/usr/bin/env python3
"""Export an analytic, simplified representation for SolidWorks."""

import math
import re
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
source = (HERE / "capsula_conceptual.scad").read_text(encoding="utf-8")


def parameter(name):
    match = re.search(rf"^{re.escape(name)}\s*=\s*([0-9.]+)\s*;", source, re.M)
    if not match:
        raise ValueError(f"Missing scalar OpenSCAD parameter: {name}")
    return float(match.group(1))


def cylinder(x, radius, length):
    return cq.Workplane("YZ").workplane(offset=x).circle(radius).extrude(length)


def box(x, y, z, length, width, height):
    return cq.Workplane("XY").box(length, width, height, centered=False).translate((x, y, z))


def annulus(x, outer, inner, length):
    return cylinder(x, outer, length).cut(cylinder(x - 0.1, inner, length + 0.2))


radius = parameter("diametro_exterior") / 2
wall = parameter("pared")
length = parameter("largo_cuerpo")
engagement = parameter("largo_encaje")
end_radius = parameter("radio_paso_extremos")
board_x = parameter("placa_x")
board_length = parameter("placa_largo")
board_width = parameter("placa_ancho")
board_thickness = parameter("placa_espesor")

body = cylinder(0, radius, length)
body = body.cut(cylinder(-0.1, end_radius, length + 0.2))
body = body.cut(cylinder(engagement, radius - wall, length - 2 * engagement))
bottom = parameter("espesor_fondo")
body = body.union(cylinder(length - bottom, end_radius + 0.1, bottom + 0.1))
body = body.union(cylinder(length - 0.1, parameter("radio_cuello_exterior"), engagement + 0.1))

guide_end = parameter("fin_guias_pcb")
guide_length = guide_end - engagement
clearance = parameter("holgura_guia_pcb")
for side in (-1, 1):
    y = 11.6 if side > 0 else -22.1
    slot_y = 11.6 if side > 0 else -14
    guide = box(engagement, y, -3, guide_length, 10.5, 6)
    guide = guide.cut(box(engagement - 0.1, slot_y, -(board_thickness + clearance) / 2,
                          guide_length + 0.2, 2.4, board_thickness + clearance))
    guide = guide.intersect(cylinder(engagement - 0.1, radius, guide_length + 0.2))
    body = body.union(guide)

support_x = parameter("soporte_actuador_x")
support_length = parameter("soporte_actuador_largo")
support = cylinder(support_x, 12.5, support_length)
support = support.union(box(support_x, -22.1, -2, support_length, 44.2, 4))
support = support.union(box(support_x, -2, -22.1, support_length, 4, 44.2))
support = support.cut(cylinder(support_x - 0.1,
                               (20 + parameter("holgura_actuador_diametral")) / 2,
                               support_length + 0.2))
body = body.union(support)

cap_thickness = parameter("espesor_tapa")
cap = cylinder(-cap_thickness, radius, cap_thickness + 0.05)
cap = cap.union(annulus(0, parameter("radio_encaje"), parameter("radio_encaje") - 1.8,
                        engagement))
cap = cap.union(annulus(-0.1, 14.8, (25 + parameter("holgura_bobina_diametral")) / 2, 2.6))
cap = cap.cut(annulus(-1.2, parameter("radio_junta") + 1.2,
                      parameter("radio_junta") - 1.2, 1.3))

nose_length = parameter("largo_ojiva")
arc_radius = (nose_length**2 + radius**2) / (2 * radius)


def ogive_radius(x, reduction=0):
    return math.sqrt(max(0, arc_radius**2 - x**2)) + radius - arc_radius - reduction


def ogive_solid(reduction):
    points = [(0, 0)]
    for i in range(129):
        x = nose_length * i / 128
        r = max(0, ogive_radius(x, reduction))
        if r <= 1e-8:
            break
        points.append((x, r))
    if reduction:
        x = math.sqrt(arc_radius**2 - (arc_radius - radius + reduction)**2)
    points.append((x, 0))
    return cq.Workplane("XZ").polyline(points).close().revolve(360, (0, 0), (1, 0))


nose_shell = ogive_solid(0).cut(ogive_solid(wall)).translate((length + engagement, 0, 0))
nose = annulus(length, radius, parameter("radio_alojamiento_ojiva"), engagement + 0.5)
nose = nose.union(nose_shell)

board = box(board_x, -board_width / 2, -board_thickness / 2,
            board_length, board_width, board_thickness)
for x in (130.3, 160.8):
    board = board.cut(box(board_x + x, -2, -board_thickness, 2.7, 4, 2 * board_thickness))

assembly = cq.Assembly(name="Capsula_conceptual")
assembly.add(body, name="Cuerpo_PETG", color=cq.Color(0.75, 0.82, 0.84, 0.45))
assembly.add(cap, name="Tapa_encaje_liso", color=cq.Color(0.83, 0.86, 0.88, 0.6))
assembly.add(nose, name="Ojiva_encaje_liso", color=cq.Color(0.55, 0.58, 0.61, 0.7))
assembly.add(board, name="PCB_1_6mm_referencia", color=cq.Color(0.03, 0.43, 0.27))
assembly.add(cylinder(board_x + 114, 7, 50).translate((0, 0, -9.5)),
             name="Bateria_14500_nominal", color=cq.Color(0.12, 0.39, 0.75))
assembly.add(cylinder(parameter("actuador_x"), 10, parameter("actuador_largo_referencia")),
             name="Actuador_envolvente", color=cq.Color(0.65, 0.68, 0.70))
assembly.add(cylinder(1, 12.5, 1), name="Bobina_carga_referencia",
             color=cq.Color(0.79, 0.45, 0.18))
seal = (cq.Workplane("XZ").moveTo(-0.5, parameter("radio_junta"))
        .circle(parameter("seccion_junta") / 2).revolve(360, (0, 0), (1, 0)))
assembly.add(seal, name="Junta_ilustrativa", color=cq.Color(0.1, 0.1, 0.1))

for i, x in enumerate((130.3, 160.8), 1):
    clip_x = board_x + x
    clip = annulus(clip_x, 8.3, 7.3, 2.7).translate((0, 0, -9.5))
    clip = clip.cut(box(clip_x - 0.1, -3.5, -19.5, 2.9, 7, 5))
    clip = clip.union(box(clip_x, -2, -2.5, 2.7, 4, 4))
    assembly.add(clip, name=f"Clip_{i}_ilustrativo", color=cq.Color(0.9, 0.55, 0.16))

for name, x, size, color in (
    ("ESP32", 3, (22.5, 17.8, 6), (0.12, 0.12, 0.16)),
    ("Receptor", 29, (18, 15, 5), (0.13, 0.55, 0.38)),
    ("Boost", 50, (36, 17, 8), (0.16, 0.32, 0.60)),
    ("Condensador_reserva", 89, (12, 12, 10), (0.25, 0.25, 0.28)),
    ("IMU", 104, (25.4, 17.78, 5), (0.18, 0.20, 0.22)),
    ("DRV8833", 135, (25.4, 17.78, 6), (0.22, 0.25, 0.38)),
):
    lx, width, height = size
    assembly.add(box(board_x + x, -width / 2, board_thickness / 2, lx, width, height),
                 name=name, color=cq.Color(*color))

for name, part in (("cuerpo", body), ("tapa", cap), ("ojiva", nose)):
    if not part.val().isValid():
        raise ValueError(f"Invalid CAD geometry: {name}")
    cq.exporters.export(part, str(HERE / f"{name}_conceptual.step"))

assembly.save(str(HERE / "capsula_conceptual.step"), exportType="STEP")
