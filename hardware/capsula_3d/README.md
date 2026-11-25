# Cápsula: maqueta 3D conceptual

Interpretación del croquis y de la aclaración del usuario: **cuerpo cilíndrico recto**, tapa roscada con junta tórica en el extremo de carga y ojiva circular roscada para alojar el lastre en el otro extremo. La PCB va longitudinalmente con la batería debajo. Abrir `capsula_conceptual.scad` con OpenSCAD. El modo `corte` muestra el interior; `conjunto`, `cuerpo`, `tapa` y `punta` permiten examinar el conjunto y sus piezas.

La [vista en corte](capsula_corte.png) muestra la geometría y los bloques de referencia; la bobina naranja se representa junto a la tapa, la batería azul bajo la PCB y el actuador **dentro del cilindro**, antes de la ojiva.

El ESP32 se ha trasladado al extremo de la tapa para orientar su USB-C hacia ella; el bloque no modela el conector. La bobina puede bloquear el acceso: falta comprobar el espacio del cable y definir si se aparta la bobina o se extrae el conjunto. Dos abrazaderas naranjas con pestañas y aberturas simbólicas representan la idea del croquis para sujetar la batería bajo la PCB. Sus pestañas están en los espacios entre boost y condensador y entre IMU y DRV8833, no bajo las envolventes mostradas. No hay un mecanismo de clic validado ni garantía de elasticidad, retención axial o aislamiento; faltan contactos, dimensionado de ranuras y comprobación de pines y cobre.

**No es una cápsula terminada ni estanca.** Se representan encajes lisos simbólicos en ambas uniones y una junta tórica con ranura ilustrativa en la tapa: **todavía no hay roscas helicoidales** ni dimensiones de sellado verificadas. La sección transversal de la junta se superpone intencionadamente a la superficie del cuerpo en la vista ensamblada: no es una simulación validada de compresión. El diámetro, sección, alojamiento, compresión y material de la junta, el tipo de rosca, sentido, paso, holguras y sellado deben diseñarse para las piezas y el proceso de impresión. La unión de la ojiva también requiere una solución de estanqueidad.

La ojiva hueca reserva espacio para el **lastre**, pero no modela su forma, masa ni fijación. El cilindro gris es una envolvente ilustrativa del actuador, situado fuera de la ojiva y dentro del cuerpo principal; no representa su parte móvil. Su ubicación exacta respecto al lastre y al centro de masas sigue pendiente; los bloques de componentes no son modelos reales.

## Primer prototipo de guías en PETG translúcido

El material previsto es **PETG translúcido**. Las holguras son valores de partida, no tolerancias verificadas; dependen de la impresora, orientación, material y piezas reales.

- **PCB:** dos rieles longitudinales integrados en el cuerpo, con ranuras de 2,0 mm de alto para una placa nominal de 1,6 mm. La profundidad de cada ranura debe revisarse con el contorno final y las tolerancias. La retención axial, la entrada del montaje y la compatibilidad con pines, soldaduras, cables y clips aún no están resueltas.
- **Bobina:** corona de centrado junto a la tapa, diámetro interior nominal 25,8 mm para la bobina anunciada de 25 mm. No tiene retención, alojamiento del ferrito, salida de cables ni solución para el USB-C; puede obstruir el conector. No forzar ni dañar los hilos finos de la bobina.
- **Actuador:** aro de centrado en el interior del cilindro, diámetro interior nominal 20,8 mm, con nervios a la pared del cuerpo; no forma parte de la ojiva. Solo representa una posible sujeción de la **parte fija**: no se conocen todavía sus superficies de montaje, cables ni holguras reales. No es una guía de la parte móvil, no aporta topes ni detecta posición, y no garantiza que la carrera permanezca libre.

El usuario puede imprimir en seco las piezas de prueba independientes para comprobar dimensiones **sin electrónica ni batería**:

| Pieza | Comprobación | Archivo |
|---|---|---|
| Anillo de 20 mm de cuerpo | Deslizamiento de una muestra inerte de PCB de 24 × 1,6 mm | [prueba_pcb.stl](prueba_pcb.stl) |
| Aro de bobina | Centrado a Ø25,8 mm | [prueba_bobina.stl](prueba_bobina.stl) |
| Aro de actuador | Centrado a Ø20,8 mm | [prueba_actuador.stl](prueba_actuador.stl) |

Estos STL son **cupones de ajuste**, no componentes funcionales ni un cierre. No fuerzan ni fijan la batería o el actuador. La sujeción definitiva de la bobina, la parte fija del actuador, la guía y parada de su parte móvil y el lastre requieren diseño posterior. La dirección del movimiento es longitudinal; compruébese también la posición de su línea de acción respecto al centro de masas para obtener excitación angular.

## Dimensiones de partida, en mm

| Elemento | Valor | Alcance |
|---|---:|---|
| Cuerpo tubular | 214 largo, 48 diámetro exterior, pared principal 2 | Hipótesis inicial; diámetro interior 44 en el tramo central, 42 en los 8 mm de cada extremo |
| Ojiva | 32 de largo exterior, diámetro de base 48 | Arco circular tangente al cilindro; espesor radial nominal 2; encaje liso ilustrativo, sin rosca |
| Tapa | Disco de espesor 3 | Encaje liso ilustrativo y ranura para junta, sin rosca |
| Junta tórica | Diámetro medio 44, sección 2 | Modelo y ranura ilustrativos, compresión y estanqueidad no verificadas |
| Longitud total exterior | 249 | 3 de tapa + 214 de cuerpo + 32 de ojiva |
| PCB | 164 × 24 × 1,6 | Maqueta mecánica provisional, no PCB terminada |
| Batería | Cilindro 50 × Ø14 | Dimensiones nominales, sin terminales ni soporte |
| Bobina | Ø25 × 1 | Espesor ilustrativo, no medido |
| Actuador | Ø20 × 13,5 | Solo envolvente aproximada del cuerpo; no incluye fijación ni carrera |

Tomando `x = 0` en el inicio del cuerpo, la PCB ocupa `x = 10–174 mm`; las guías terminan en `x = 179 mm`. La envolvente indicativa del actuador ocupa `x = 181–194,5 mm` y el aro de centrado `x = 185–189 mm`. La unión de la ojiva empieza en `x = 206 mm`, antes del fin del cuerpo en `x = 214 mm`. Estos 30 mm adicionales respecto al diseño anterior son una **reserva provisional**, no el espacio validado para montaje, cableado ni recorrido. La batería se dibuja bajo la PCB, con su eje 9,5 mm por debajo de su plano medio. Las alturas de los bloques electrónicos son **suposiciones**; la holgura, el aislamiento de la batería, los conectores, los radios de cable, la antena y el acceso al USB no están verificados. El condensador está representado por un bloque de 12 mm reservado, no por una medida confirmada.

La longitud de 164 mm procede de la primera maqueta de la portadora: puede cambiar al diseñar huellas, conectores, PCB y antena. El diámetro exterior de 48 mm y el resto de las dimensiones de carcasa son propuestas, no resultados optimizados. El aro actual es coaxial con la cápsula, solo para estudiar el alojamiento; esa posición no establece la línea de acción respecto al centro de masas ni garantiza que produzca el ángulo deseado. La orientación y sentido de la parte móvil, sus superficies de fijación, cables, guía y posiciones extremas deberán verificarse con el actuador real antes de definir la sujeción.

La geometría no demuestra flotación, estabilidad ni resistencia. Es necesario medir masas y envolventes completas, definir cierres y estanqueidad, comprobar la flotación en los fluidos de ensayo y reajustar el lastre. Antes de fabricar o sumergir componentes deben revisarse también la batería, la carga inalámbrica, el calentamiento y la etapa de accionamiento.

## Exportación

```bash
openscad -D 'modo="corte"' -o vista.csg hardware/capsula_3d/capsula_conceptual.scad
```

Para regenerar los cupones:

```bash
for parte in prueba_pcb prueba_bobina prueba_actuador; do
  openscad -D "modo=\"$parte\"" -o "hardware/capsula_3d/$parte.stl" hardware/capsula_3d/capsula_conceptual.scad
done
```

La exportación de las piezas completas no implica que sean aptas para cerrar la cápsula o para uso en líquido. La [PCB de referencia](../pcb_portadora/README.md) continúa sin conexiones ni huellas terminadas.
