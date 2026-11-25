// Primer prototipo de guías: encajes lisos, sin roscas funcionales.
// Eje X: tapa de carga (izquierda) hacia punta lastrada (derecha).
modo = "corte"; // [corte, conjunto, bandeja, cuerpo, tapa, punta, prueba_pcb, prueba_bobina, prueba_actuador]
$fn = 128;

diametro_exterior = 48;
pared = 2;
largo_cuerpo = 214;
espesor_tapa = 3;
largo_ojiva = 32;
largo_encaje = 8;
radio_encaje = 20.6;
radio_paso_extremos = 21;
espesor_fondo = 3;
radio_cuello_exterior = 20.2;
radio_alojamiento_ojiva = 20.6;
radio_junta = 22;
seccion_junta = 2;
placa_largo = 164;
placa_ancho = 24;
placa_espesor = 1.6;
placa_x = 10;
pos_clips = [130.3, 160.8];
ancho_clip = 2.7;
holgura_guia_pcb = 0.4;
holgura_bobina_diametral = 0.8;
holgura_actuador_diametral = 0.8;
actuador_x = 181;
actuador_largo_referencia = 13.5;
carrera_referencia = 3;
soporte_actuador_x = 185;
soporte_actuador_largo = 4;
fin_guias_pcb = 200;

radio = diametro_exterior / 2;
radio_interior = radio - pared;
assert(diametro_exterior > 2 * pared, "Pared incompatible con diámetro");
assert(largo_ojiva >= radio, "La ojiva tangente requiere longitud >= radio");
assert(radio_encaje < radio_paso_extremos &&
       radio_paso_extremos < radio_interior, "Encajes incompatibles");
assert(radio_cuello_exterior < radio_alojamiento_ojiva &&
       radio_alojamiento_ojiva < radio, "Alojamiento incompatible");
assert(largo_encaje < placa_x && placa_x + placa_largo < largo_cuerpo - largo_encaje,
       "La PCB interfiere con las zonas de encaje");
assert(largo_cuerpo >= placa_x + placa_largo, "La PCB excede el cuerpo");
assert(placa_ancho < 2 * radio_interior, "La PCB excede el diámetro interior");
assert(fin_guias_pcb > soporte_actuador_x + soporte_actuador_largo &&
       fin_guias_pcb < largo_cuerpo - espesor_fondo, "Longitud de guías incompatible");
assert(actuador_x > placa_x + placa_largo &&
       soporte_actuador_x >= actuador_x &&
       soporte_actuador_x + soporte_actuador_largo <= actuador_x + actuador_largo_referencia &&
       actuador_x + actuador_largo_referencia + carrera_referencia < largo_cuerpo - espesor_fondo &&
       espesor_fondo > 0 && espesor_fondo < largo_encaje,
       "Envolvente del actuador fuera de su reserva");
assert(modo == "corte" || modo == "conjunto" || modo == "bandeja" || modo == "cuerpo" ||
       modo == "tapa" || modo == "punta" || modo == "prueba_pcb" ||
       modo == "prueba_bobina" || modo == "prueba_actuador", "Modo desconocido");

module cilindro_x(r, h) {
    rotate([0, 90, 0]) cylinder(r = r, h = h);
}

module cuerpo() {
    union() {
        difference() {
            cilindro_x(radio, largo_cuerpo);
            translate([-0.1, 0, 0]) cilindro_x(radio_paso_extremos, largo_cuerpo + 0.2);
            translate([largo_encaje, 0, 0])
                cilindro_x(radio_interior, largo_cuerpo - 2 * largo_encaje);
        }
        // Fondo cerrado y cuello exterior liso, reserva para rosca.
        translate([largo_cuerpo - espesor_fondo, 0, 0])
            cilindro_x(radio_paso_extremos + 0.1, espesor_fondo + 0.1);
        translate([largo_cuerpo - 0.1, 0, 0])
            cilindro_x(radio_cuello_exterior, largo_encaje + 0.1);
        guias_pcb();
    }
}

module guias_pcb() {
    // Las ranuras reciben los largueros de la bandeja, no los bordes de la PCB.
    for (lado = [-1, 1])
        difference() {
            translate([largo_encaje, lado > 0 ? 15 : -22, -12])
                cube([fin_guias_pcb - largo_encaje, 7, 5]);
            translate([largo_encaje - 0.1, lado > 0 ? 14.9 : -15.7, -10.7])
                cube([fin_guias_pcb - largo_encaje + 0.2, 0.8, 2.4]);
            difference() {
                translate([largo_encaje - 0.1, -25, -13])
                    cube([fin_guias_pcb - largo_encaje + 0.2, 50, 7]);
                translate([largo_encaje - 0.2, 0, 0])
                    cilindro_x(radio, fin_guias_pcb - largo_encaje + 0.4);
            }
        }
}

module tapa() {
    union() {
      difference() {
        union() {
            translate([-espesor_tapa, 0, 0]) cilindro_x(radio, espesor_tapa + 0.05);
            difference() {
                cilindro_x(radio_encaje, largo_encaje);
                translate([-0.1, 0, 0])
                    cilindro_x(radio_encaje - 1.8, largo_encaje + 0.2);
              }
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
            // Casquillo externo separado: el hueco no comunica con el cilindro cerrado.
            difference() {
                cilindro_x(radio, largo_encaje + 0.5);
                translate([-0.1, 0, 0])
                    cilindro_x(radio_alojamiento_ojiva, largo_encaje + 0.7);
            }
            translate([largo_encaje, 0, 0])
            difference() {
                volumen_ojiva();
                volumen_ojiva(pared);
            }
        }
    }
}

module soporte_actuador() {
    // Aro de posición, no sujeción validada de la bobina fija.
    translate([soporte_actuador_x, 0, 0])
    difference() {
        cilindro_x(12.5, soporte_actuador_largo);
        translate([-0.1, 0, 0])
            cilindro_x((20 + holgura_actuador_diametral) / 2,
                       soporte_actuador_largo + 0.2);
    }
}

module bandeja() {
    union() {
        for (lado = [-1, 1]) {
            translate([4, lado > 0 ? 14.2 : -15.3, -10.4])
                cube([185, 1.1, 1.8]);
            for (x = [20, 72, 112, 166])
                translate([x, lado > 0 ? 11.5 : -14.4, -9])
                    cube([3, 2.9, 8.2]);
            translate([4, lado > 0 ? 10.5 : -14.4, -10])
                cube([3, 3.9, 1.2]);
            translate([soporte_actuador_x, lado > 0 ? 6.5 : -14.4, -10])
                cube([3, 7.9, 1.2]);
        }
        translate([4, 0, 0])
            difference() {
                cilindro_x(14.8, 3);
                translate([-0.1, 0, 0])
                    cilindro_x((25 + holgura_bobina_diametral) / 2, 3.2);
            }
        soporte_actuador();
    }
}

module carcasa_en_corte() {
    difference() {
        children();
        translate([-espesor_tapa - 1, -radio - 1, -radio - 1])
            cube([largo_cuerpo + largo_encaje + largo_ojiva + espesor_tapa + 2,
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
        translate([placa_x + 114, 0, -9.5]) cilindro_x(7, 50);

    // Abrazaderas y ranuras simbólicas, no dimensiones de fabricación.
    color([0.9, 0.55, 0.16]) {
        for (x = pos_clips) clip_bateria(x);
    }

    // Bobina de carga de 25 mm: plano transversal, espesor ilustrativo.
    color([0.79, 0.45, 0.18])
        translate([5, 0, 0]) cilindro_x(12.5, 1);

    // Envolvente indicativa del cuerpo del actuador; no es la guía ni la carrera.
    color([0.65, 0.68, 0.70])
        translate([actuador_x, 0, 0]) cilindro_x(10, actuador_largo_referencia);
}

if (modo == "cuerpo") cuerpo();
if (modo == "tapa") tapa();
if (modo == "punta") punta();
if (modo == "bandeja") bandeja();
if (modo == "prueba_pcb")
    intersection() {
        cuerpo();
        translate([40, -radio, -radio]) cube([20, 2 * radio, 2 * radio]);
    }
if (modo == "prueba_bobina")
    difference() {
        cilindro_x(14.8, 2.5);
        translate([-0.1, 0, 0])
            cilindro_x((25 + holgura_bobina_diametral) / 2, 2.7);
    }
if (modo == "prueba_actuador")
    difference() {
        cilindro_x(12.5, 4);
        translate([-0.1, 0, 0])
            cilindro_x((20 + holgura_actuador_diametral) / 2, 4.2);
    }
if (modo == "conjunto") {
    color([0.78, 0.83, 0.84, 0.35]) cuerpo();
    color([0.83, 0.86, 0.88, 0.5]) tapa();
    color([0.54, 0.58, 0.61, 0.5]) punta();
    color([0.1, 0.1, 0.1]) junta();
    color([0.85, 0.65, 0.12]) bandeja();
    componentes();
}
if (modo == "corte") {
    color([0.78, 0.83, 0.84]) carcasa_en_corte() cuerpo();
    color([0.83, 0.86, 0.88]) carcasa_en_corte() tapa();
    color([0.54, 0.58, 0.61]) carcasa_en_corte() punta();
    color([0.1, 0.1, 0.1]) carcasa_en_corte() junta();
    color([0.85, 0.65, 0.12]) bandeja();
    componentes();
}
