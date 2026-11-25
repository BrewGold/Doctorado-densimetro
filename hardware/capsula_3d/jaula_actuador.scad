// Prototipo de ajuste en seco; no energizar ni utilizar como tope de impacto.
modo = "conjunto"; // [conjunto, base, cierre, impresion]
$fn = 96;

radio_exterior = 17.5;
espesor_base = 3;
espesor_cierre = 3;
largo_actuador = 13.5;
carrera = 3;
margen_axial = 0.5;
separacion_m25 = 9;
paso_m25 = 2.9;
paso_m3 = 3.4;
entrada_tornillo = 3;
cierre_x = espesor_base + largo_actuador + carrera + margen_axial;

assert(modo == "conjunto" || modo == "base" ||
       modo == "cierre" || modo == "impresion", "Modo desconocido");
echo("M2.5: longitud bajo cabeza sin arandela (provisional)",
     espesor_base + entrada_tornillo);

module cilindro_x(r, h) {
    rotate([0, 90, 0]) cylinder(r = r, h = h);
}

module pasos_m3(largo) {
    for (y = [-13, 13])
        translate([-0.1, y, 0]) cilindro_x(paso_m3 / 2, largo + 0.2);
}

module base() {
    difference() {
        union() {
            cilindro_x(radio_exterior, espesor_base);
            for (y = [-15.5, 10.5])
                translate([espesor_base - 0.1, y, -3.5])
                    cube([cierre_x - espesor_base + 0.1, 5, 7]);
        }
        pasos_m3(cierre_x);
        for (y = [-separacion_m25 / 2, separacion_m25 / 2])
            translate([-0.1, y, 0])
                cilindro_x(paso_m25 / 2, espesor_base + 0.2);
        // Alivio central y salida de cables provisionales, pendientes de medir.
        translate([-0.1, 0, 0]) cilindro_x(2, espesor_base + 0.2);
        translate([-0.1, -3, 10.8]) cube([espesor_base + 0.2, 6, 8]);
    }
}

module cierre() {
    difference() {
        cilindro_x(radio_exterior, espesor_cierre);
        pasos_m3(espesor_cierre);
        translate([-0.1, 0, 0]) cilindro_x(4, espesor_cierre + 0.2);
    }
}

if (modo == "base") base();
if (modo == "cierre") cierre();
if (modo == "conjunto") {
    color([0.85, 0.65, 0.12]) base();
    color([0.95, 0.75, 0.25]) translate([cierre_x, 0, 0]) cierre();
}
if (modo == "impresion") {
    rotate([0, -90, 0]) base();
    translate([40, 0, 0]) rotate([0, -90, 0]) cierre();
}
