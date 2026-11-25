#!/usr/bin/env python3
"""Export an analytic, simplified representation for SolidWorks."""

import math
import re
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
source = (HERE / "capsula_conceptual.scad").read_text(encoding="utf-8")


def parameter(name, text=source):
    match = re.search(rf"^{re.escape(name)}\s*=\s*(-?[0-9.]+)\s*;", text, re.M)
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
for side in (-1, 1):
    y = 15 if side > 0 else -22
    slot_y = 14.9 if side > 0 else -15.7
    guide = box(engagement, y, -12, guide_length, 7, 5)
    guide = guide.cut(box(engagement - 0.1, slot_y, -10.7,
                          guide_length + 0.2, 0.8, 2.4))
    guide = guide.intersect(cylinder(engagement - 0.1, radius, guide_length + 0.2))
    body = body.union(guide)

support_x = parameter("soporte_actuador_x")
support_length = parameter("soporte_actuador_largo")
tray = annulus(4, 14.8, (25 + parameter("holgura_bobina_diametral")) / 2, 3)
for side in (-1, 1):
    tray = tray.union(box(4, 14.2 if side > 0 else -15.3, -10.4, 185, 1.1, 1.8))
    web_y = parameter("alma_bandeja_y")
    web_width = parameter("alma_bandeja_ancho")
    tray = tray.union(box(parameter("alma_bandeja_x"),
                          web_y if side > 0 else -web_y - web_width,
                          parameter("alma_bandeja_z"), parameter("alma_bandeja_largo"),
                          web_width, parameter("alma_bandeja_alto")))
    for x in (20, 72, 112, 166):
        tray = tray.union(box(x, 11.5 if side > 0 else -14.4, -9, 3, 2.9, 8.2))
    tray = tray.union(box(4, 10.5 if side > 0 else -14.4, -10, 3, 3.9, 1.2))
    tray = tray.union(box(support_x, 6.5 if side > 0 else -14.4, -10, 3, 7.9, 1.2))
tray = tray.union(annulus(support_x, 12.5,
                          (20 + parameter("holgura_actuador_diametral")) / 2,
                          support_length))

cap_thickness = parameter("espesor_tapa")
cap = cylinder(-cap_thickness, radius, cap_thickness + 0.05)
cap = cap.union(annulus(0, parameter("radio_encaje"), parameter("radio_encaje") - 1.8,
                        engagement))
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
assembly.add(tray, name="Bandeja_extraible", color=cq.Color(0.85, 0.65, 0.12))
assembly.add(board, name="PCB_1_6mm_referencia", color=cq.Color(0.03, 0.43, 0.27))
assembly.add(cylinder(board_x + 114, 7, 50).translate((0, 0, -9.5)),
             name="Bateria_14500_nominal", color=cq.Color(0.12, 0.39, 0.75))
assembly.add(cylinder(parameter("actuador_x"), 10, parameter("actuador_largo_referencia")),
             name="Actuador_envolvente", color=cq.Color(0.65, 0.68, 0.70))
assembly.add(cylinder(5, 12.5, 1), name="Bobina_carga_referencia",
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

for name, part in (("cuerpo", body), ("tapa", cap), ("ojiva", nose), ("bandeja", tray)):
    if not part.val().isValid():
        raise ValueError(f"Invalid CAD geometry: {name}")
    cq.exporters.export(part, str(HERE / f"{name}_conceptual.step"))

assembly.save(str(HERE / "capsula_conceptual.step"), exportType="STEP")

cage_source = (HERE / "jaula_actuador.scad").read_text(encoding="utf-8")


def cage_parameter(name):
    return parameter(name, cage_source)


cage_radius = cage_parameter("radio_exterior")
base_thickness = cage_parameter("espesor_base")
cover_thickness = cage_parameter("espesor_cierre")
cover_x = (base_thickness + cage_parameter("largo_actuador")
           + cage_parameter("carrera") + cage_parameter("margen_axial"))
cage_base = cylinder(0, cage_radius, base_thickness)
for y in (-15.5, 10.5):
    cage_base = cage_base.union(box(base_thickness - 0.1, y, -3.5,
                                    cover_x - base_thickness + 0.1, 5, 7))
cage_cover = cylinder(0, cage_radius, cover_thickness)
for y in (-13, 13):
    cage_base = cage_base.cut(cylinder(-0.1, cage_parameter("paso_m3") / 2,
                                       cover_x + 0.2).translate((0, y, 0)))
    cage_cover = cage_cover.cut(cylinder(-0.1, cage_parameter("paso_m3") / 2,
                                         cover_thickness + 0.2).translate((0, y, 0)))
for y in (-cage_parameter("separacion_m25") / 2, cage_parameter("separacion_m25") / 2):
    cage_base = cage_base.cut(cylinder(-0.1, cage_parameter("paso_m25") / 2,
                                       base_thickness + 0.2).translate((0, y, 0)))
cage_base = cage_base.cut(cylinder(-0.1, 2, base_thickness + 0.2))
cage_base = cage_base.cut(box(-0.1, -3, 10.8, base_thickness + 0.2, 6, 8))
cage_cover = cage_cover.cut(cylinder(-0.1, 4, cover_thickness + 0.2))
cage_assembly = cq.Assembly(name="Jaula_ajuste_en_seco")
for name, part, x in (("jaula_base", cage_base, 0), ("jaula_cierre", cage_cover, cover_x)):
    if not part.val().isValid() or len(part.val().Solids()) != 1:
        raise ValueError(f"Invalid cage geometry: {name}")
    cq.exporters.export(part, str(HERE / f"{name}.step"))
    cage_assembly.add(part.translate((x, 0, 0)), name=name)
cage_assembly.save(str(HERE / "jaula_actuador.step"), exportType="STEP")
