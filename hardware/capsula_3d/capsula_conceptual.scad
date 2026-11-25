// Maqueta geométrica, sin cierres, soportes ni estanqueidad.
// Eje X: tapa de carga (izquierda) hacia punta lastrada (derecha).
modo = "corte"; // [corte, conjunto, cuerpo, tapa, punta]
$fn = 128;

diametro_exterior = 48;
pared = 2;
largo_cuerpo = 184;
espesor_tapa = 3;
placa_largo = 164;
placa_ancho = 24;
placa_espesor = 1.6;
placa_x = 10;

radio = diametro_exterior / 2;
radio_interior = radio - pared;
assert(diametro_exterior > 2 * pared, "Pared incompatible con diámetro");
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
        translate([-0.1, 0, 0]) cilindro_x(radio_interior, largo_cuerpo + 0.2);
    }
}

module tapa() {
    translate([-espesor_tapa, 0, 0]) cilindro_x(radio, espesor_tapa);
}

module semiesfera(r) {
    intersection() {
        sphere(r = r);
        translate([0, -r, -r]) cube([r, 2 * r, 2 * r]);
    }
}

module punta() {
    translate([largo_cuerpo, 0, 0])
        difference() {
            semiesfera(radio);
            semiesfera(radio_interior);
        }
}

module carcasa_en_corte() {
    difference() {
        children();
        translate([-espesor_tapa - 1, -radio - 1, -radio - 1])
            cube([largo_cuerpo + radio + espesor_tapa + 2,
                  radio + 1, 2 * radio + 2]);
    }
}

module caja_modulo(x, longitud, ancho, alto) {
    translate([placa_x + x, -ancho / 2, placa_espesor / 2])
        cube([longitud, ancho, alto]);
}

module componentes() {
    color([0.03, 0.43, 0.27])
        translate([placa_x, -placa_ancho / 2, -placa_espesor / 2])
            cube([placa_largo, placa_ancho, placa_espesor]);

    // Alturas provisionales: no representan las envolventes medidas.
    color([0.13, 0.55, 0.38]) caja_modulo(3, 18, 15, 5);
    color([0.16, 0.32, 0.60]) caja_modulo(24, 36, 17, 8);
    color([0.25, 0.25, 0.28]) caja_modulo(63, 12, 12, 10);
    color([0.18, 0.20, 0.22]) caja_modulo(78, 25.4, 17.78, 5);
    color([0.12, 0.12, 0.16]) caja_modulo(106, 22.5, 17.8, 6);
    color([0.22, 0.25, 0.38]) caja_modulo(132, 25.4, 17.78, 6);

    // 14500 nominal: 50 x 14; sin portapilas ni terminales.
    color([0.12, 0.39, 0.75])
        translate([placa_x + 78, 0, -9.5]) cilindro_x(7, 50);

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
    componentes();
}
if (modo == "corte") {
    color([0.78, 0.83, 0.84]) carcasa_en_corte() cuerpo();
    color([0.83, 0.86, 0.88]) carcasa_en_corte() tapa();
    color([0.54, 0.58, 0.61]) carcasa_en_corte() punta();
    componentes();
}
