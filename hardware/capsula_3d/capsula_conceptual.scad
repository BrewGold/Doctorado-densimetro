// Maqueta geométrica: encajes lisos simbólicos, sin roscas funcionales.
// Eje X: tapa de carga (izquierda) hacia punta lastrada (derecha).
modo = "corte"; // [corte, conjunto, cuerpo, tapa, punta]
$fn = 128;

diametro_exterior = 48;
pared = 2;
largo_cuerpo = 184;
espesor_tapa = 3;
largo_ojiva = 32;
largo_encaje = 8;
radio_encaje = 20.6;
radio_paso_extremos = 21;
radio_junta = 22;
seccion_junta = 2;
placa_largo = 164;
placa_ancho = 24;
placa_espesor = 1.6;
placa_x = 10;
pos_clips = [86.15, 130.3];
ancho_clip = 2.7;

radio = diametro_exterior / 2;
radio_interior = radio - pared;
assert(diametro_exterior > 2 * pared, "Pared incompatible con diámetro");
assert(largo_ojiva >= radio, "La ojiva tangente requiere longitud >= radio");
assert(radio_encaje < radio_paso_extremos &&
       radio_paso_extremos < radio_interior, "Encajes incompatibles");
assert(largo_encaje < placa_x && placa_x + placa_largo < largo_cuerpo - largo_encaje,
       "La PCB interfiere con las zonas de encaje");
assert(largo_cuerpo >= placa_x + placa_largo, "La PCB excede el cuerpo");
assert(placa_ancho < 2 * radio_interior, "La PCB excede el diámetro interior");
assert(modo == "corte" || modo == "conjunto" || modo == "cuerpo" ||
       modo == "tapa" || modo == "punta", "Modo desconocido");

module cilindro_x(r, h) {
    rotate([0, 90, 0]) cylinder(r = r, h = h);
}

module cuerpo() {
    difference() {
        cilindro_x(radio, largo_cuerpo);
        translate([-0.1, 0, 0]) cilindro_x(radio_paso_extremos, largo_cuerpo + 0.2);
        translate([largo_encaje, 0, 0])
            cilindro_x(radio_interior, largo_cuerpo - 2 * largo_encaje);
    }
}

module tapa() {
    difference() {
        union() {
            translate([-espesor_tapa, 0, 0]) cilindro_x(radio, espesor_tapa + 0.05);
            difference() {
                cilindro_x(radio_encaje, largo_encaje);
                translate([-0.1, 0, 0])
                    cilindro_x(radio_encaje - 1.8, largo_encaje + 0.2);
            }
        }
        // Ranura orientativa; no está dimensionada para estanqueidad.
        translate([-1.2, 0, 0])
            difference() {
                cilindro_x(radio_junta + 1.2, 1.3);
                translate([-0.1, 0, 0]) cilindro_x(radio_junta - 1.2, 1.5);
            }
    }
}

module junta() {
    translate([-0.5, 0, 0]) rotate([0, 90, 0])
        rotate_extrude() translate([radio_junta, 0, 0]) circle(d = seccion_junta);
}

// Arco circular tangente al cilindro; espesor radial ilustrativo.
radio_arco = (largo_ojiva * largo_ojiva + radio * radio) / (2 * radio);
function radio_ojiva(x) = sqrt(max(0, radio_arco * radio_arco - x * x))
                          + radio - radio_arco;
module volumen_ojiva(reduccion = 0) {
    rotate([0, 90, 0]) rotate_extrude()
        polygon(concat([[0, 0]],
                       [for (i = [0:128])
                            [max(0, radio_ojiva(largo_ojiva * i / 128) - reduccion),
                             largo_ojiva * i / 128]],
                       [[0, largo_ojiva]]));
}

module punta() {
    translate([largo_cuerpo, 0, 0]) {
        union() {
            difference() {
                volumen_ojiva();
                volumen_ojiva(pared);
            }
            difference() {
                translate([-largo_encaje, 0, 0])
                    cilindro_x(radio_encaje, largo_encaje + 0.5);
                translate([-largo_encaje - 0.1, 0, 0])
                    cilindro_x(radio_encaje - 1.8, largo_encaje + 0.7);
            }
            difference() {
                cilindro_x(radio_interior + 0.1, 1);
                translate([-0.1, 0, 0])
                    cilindro_x(radio_encaje - 1.8, 1.2);
            }
        }
    }
}

module carcasa_en_corte() {
    difference() {
        children();
        translate([-espesor_tapa - 1, -radio - 1, -radio - 1])
            cube([largo_cuerpo + largo_ojiva + espesor_tapa + 2,
                  radio + 1, 2 * radio + 2]);
    }
}

module caja_modulo(x, longitud, ancho, alto) {
    translate([placa_x + x, -ancho / 2, placa_espesor / 2])
        cube([longitud, ancho, alto]);
}

module clip_bateria(x) {
    translate([placa_x + x, 0, -9.5]) {
        difference() {
            cilindro_x(8.3, ancho_clip);
            translate([-0.1, 0, 0]) cilindro_x(7.3, ancho_clip + 0.2);
            translate([-0.1, -3.5, -10]) cube([ancho_clip + 0.2, 7, 5]);
        }
        translate([0, -2, 7]) cube([ancho_clip, 4, 4]);
    }
}

module componentes() {
    color([0.03, 0.43, 0.27])
        difference() {
            translate([placa_x, -placa_ancho / 2, -placa_espesor / 2])
                cube([placa_largo, placa_ancho, placa_espesor]);
            for (x = pos_clips)
                translate([placa_x + x, -2, -placa_espesor])
                    cube([ancho_clip, 4, 2 * placa_espesor]);
        }

    // Alturas provisionales: no representan las envolventes medidas.
    color([0.12, 0.12, 0.16]) caja_modulo(3, 22.5, 17.8, 6);
    color([0.13, 0.55, 0.38]) caja_modulo(29, 18, 15, 5);
    color([0.16, 0.32, 0.60]) caja_modulo(50, 36, 17, 8);
    color([0.25, 0.25, 0.28]) caja_modulo(89, 12, 12, 10);
    color([0.18, 0.20, 0.22]) caja_modulo(104, 25.4, 17.78, 5);
    color([0.22, 0.25, 0.38]) caja_modulo(135, 25.4, 17.78, 6);

    // 14500 nominal: 50 x 14; sin portapilas ni terminales.
    color([0.12, 0.39, 0.75])
        translate([placa_x + 84, 0, -9.5]) cilindro_x(7, 50);

    // Abrazaderas y ranuras simbólicas, no dimensiones de fabricación.
    color([0.9, 0.55, 0.16]) {
        for (x = pos_clips) clip_bateria(x);
    }

    // Bobina de carga de 25 mm: plano transversal, espesor ilustrativo.
    color([0.79, 0.45, 0.18])
        translate([1, 0, 0]) cilindro_x(12.5, 1);

    // Envolvente indicativa del cuerpo del actuador; no es la guía ni la carrera.
    color([0.65, 0.68, 0.70])
        translate([largo_cuerpo + 1, 0, 0]) cilindro_x(10, 13.5);
}

if (modo == "cuerpo") cuerpo();
if (modo == "tapa") tapa();
if (modo == "punta") punta();
if (modo == "conjunto") {
    color([0.78, 0.83, 0.84, 0.35]) cuerpo();
    color([0.83, 0.86, 0.88, 0.5]) tapa();
    color([0.54, 0.58, 0.61, 0.5]) punta();
    color([0.1, 0.1, 0.1]) junta();
    componentes();
}
if (modo == "corte") {
    color([0.78, 0.83, 0.84]) carcasa_en_corte() cuerpo();
    color([0.83, 0.86, 0.88]) carcasa_en_corte() tapa();
    color([0.54, 0.58, 0.61]) carcasa_en_corte() punta();
    color([0.1, 0.1, 0.1]) carcasa_en_corte() junta();
    componentes();
}
