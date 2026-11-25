# Distribución preliminar de los componentes

## Alcance

Propuesta para diseñar la cápsula impresa en 3D **a partir de los componentes**: primero se determina la envolvente del conjunto y después se dimensiona la carcasa, no al revés. Los dibujos son **esquemas sin escala**, no un plano ni una comprobación de encaje. Se mantiene el orden acordado desde la tapa y se reserva la punta para el actuador de recorrido longitudinal y su etapa de accionamiento. Las medidas del TFM sirven únicamente como referencia y no fijan las dimensiones de esta cápsula.

## Vista longitudinal

```text
       TAPA / EXTREMO DE CARGA                         EXTREMO LASTRADO
    _________________________________________________________________
   /                                                                 \
  |  [bobina] [receptor] [boost] [IMU] [ESP32] [etapa] [actuador]    |
  |           ───────────── PCB / soporte ────────────    <───> x      |
  |                         [batería bajo la PCB]         [lastre]*  |
   \_________________________________________________________________/
                       x positivo hacia la punta

   * Posición, forma y masa del lastre por ajustar; no invadir la carrera.
```

- La bobina receptora va junto a la tapa, enfrentada al transmisor externo, con su orientación y separación a validar mediante una prueba de carga.
- Receptor/cargador, boost, IMU y ESP32 conservan ese orden físico. Se diseñará una PCB portadora para soldar los módulos; en los que no traigan pines se colocarán pines adecuados. El dibujo no presupone que los módulos estén conectados eléctricamente en serie.
- La batería se sitúa bajo la PCB y cerca del extremo lastrado, donde quepa sin invadir el actuador. La orientación «bajo» se refiere a la cara del soporte, no a una dirección vertical fija durante la flotación.
- El actuador se sitúa en la punta, sujeto por su parte fija. Su masa móvil se guía paralela al eje `x` de la cápsula, con espacio para el recorrido y sin tocar carcasa, cables o lastre. La etapa de accionamiento se propone cerca del actuador, pero su ubicación depende de sus dimensiones, temperatura e interferencias.
- El lastre debe ser fijable y, si es posible, ajustable; su posición final se determina con el conjunto real y no se supone que coincida con el espacio inmediatamente detrás del actuador.

Para el objetivo de generar ángulo también importa la **posición transversal de la guía respecto al centro de masas conjunto**: un recorrido longitudinal alineado con él no produce par instantáneo directo alrededor de ese centro en un modelo ideal. El centro de masas, el empuje y sus cambios durante el movimiento se deben medir o estimar con el montaje real; la disposición axial por sí sola no garantiza una excitación angular suficiente.

## Sección transversal orientativa

```text
             interior de la carcasa
                ___________
              /             \
             |    módulos    |
             | ─── PCB ───── |    PCB y soporte fijados a la carcasa
             |   batería     |
              \_____________/
```

La sección es esquemática: módulos, conectores, soportes y batería pueden sobresalir de la PCB. El espacio disponible se reduce hacia los extremos curvos y por el espesor de pared, las fijaciones y las tolerancias. La ubicación de la batería bajo la PCB no implica que ambas ocupen toda la longitud de la cápsula.

## Dimensiones conocidas y comprobaciones

| Elemento | Referencia disponible | Pendiente para comprobar el montaje |
|---|---|---|
| Cápsula del TFM | Aproximadamente 125 × 40 mm exteriores; referencia, no límite del nuevo diseño | Dimensionar longitud y diámetro a partir del conjunto, perfil de extremos, espesor, cierre y montaje |
| Bobina receptora | Diámetro 25 mm | Espesor, salida de cables, orientación y distancia efectiva al transmisor con la tapa y soportes |
| Placa del receptor | Aproximadamente 15 × 18 mm | Espesor, conectores, posición de cables y fijación |
| Actuador completo | Diámetro 20 mm, cuerpo de 13,5 mm de altura y masa total 25 g | Orientación real y envolvente completa, fijación, masa móvil y espacio de la guía |
| Parte móvil | Altura medida 12,2 mm; ficha de variante 20VC001: carrera de 3 mm | Carrera útil y posiciones extremas reales; no confundir altura con carrera |
| Batería | Recargable de litio 14500, 3,7 V nominales y 800 mAh indicados; aproximadamente 14 mm de diámetro y 50 mm de largo nominales | Medidas reales con terminales y protección, masa, referencia, límites de carga y descarga, protección y fijación |
| ESP32-C3 | Imagen identificada por el usuario: 17,8 × 22,5 mm y ocho contactos por fila; paso entre pines 2,54 mm. Separación entre filas igual a la placa de nueve según el usuario: estimación 15,24 mm si sus márgenes son simétricos | Medir separación entre filas y demás dimensiones en la unidad física; verificar modelo, pinout, altura, masa y zona de antena |
| IMU | Diseño Adafruit LSM6DSOX 4438 visualmente similar al TFM: PCB 25,40 × 17,78 mm, fila principal de nueve contactos a 2,54 mm | Confirmar modelo y revisión de la unidad, altura, masa, conectores y orientación; incluir pines y soldaduras |
| Boost | Sin dimensiones completas confirmadas | Modelo, largo × ancho × alto, masa, conectores y orientación |
| Etapa de accionamiento y lastre | Sin diseño o dimensiones definidos | Envolvente, masa, fijación, alimentación y margen térmico |

La batería 14500 se propone bajo la PCB, con su eje paralelo al de la cápsula; su portabatería o sujeción y conexiones aumentarán la envolvente. Las cotas nominales no sustituyen la medida de la unidad: algunas protecciones o terminales modifican su tamaño.

Todavía no se puede determinar la longitud ni el diámetro necesarios: faltan envolventes y orientaciones, así como la forma en que los componentes se solapan. El diámetro exterior de referencia del TFM no es un diámetro interior disponible ni una restricción de diseño.

## Dimensionado y preparación del montaje

1. Medir cada componente con conectores y cables, incluyendo la envolvente completa del actuador en sus posiciones extremas. Verificar mecánicamente su carrera antes de fijar topes o mandar desplazamientos.
2. Dibujar o modelar cada envolvente en el mismo sistema de referencia: `x` desde la tapa hacia la punta y dos ejes transversales fijos a la cápsula. Registrar posición, orientación y masa de cada pieza, soportes y cables incluidos.
3. Definir la longitud interior a partir de las posiciones y envolventes, permitiendo solapamientos donde sean posibles. Dimensionar cada sección transversal para la combinación de PCB, batería y componentes que coincidan en ella, así como para el actuador y su guía. Incluir la altura de pines, soldaduras y posibles conectores; añadir espacio para fijaciones, cables, tolerancias de impresión, cierre y montaje; comprobar también los extremos curvos.
4. Diseñar la carcasa, el soporte desmontable y el cierre alrededor de esa envolvente. Sumar espesor de pared y cierre para obtener las dimensiones exteriores; evitar interferencias, proteger la batería de contactos y rozamientos, y permitir montaje, mantenimiento y sellado. Fijar rígidamente la IMU y registrar sus ejes respecto a los de la cápsula.
5. Estimar la masa total y el volumen exterior para comprobar la flotación en los fluidos previstos. Revisar la distribución de masas y empuje y reservar lastre ajustable: que los componentes quepan no garantiza flotación ni el ángulo deseado. Iterar dimensiones y posiciones según sea necesario.
6. Comprobar experimentalmente carga inalámbrica, temperatura, interferencia del boost y del actuador con la IMU y funcionamiento de la antena del ESP32 en su ubicación real. No fijar separaciones definitivas sin las fichas y pruebas correspondientes.
7. Pesar el conjunto fabricado, comprobar flotación y ángulo de equilibrio, y ajustar el lastre. Añadir los 25 g del actuador completo cambia la masa y el centro de masas; no deben tratarse como masa móvil. Registrar la configuración antes de comparar ensayos.

La función y polaridad del receptor, la compatibilidad de carga con la celda concreta, la protección de batería y el puente H siguen pendientes de verificación. Los 3,7 V son nominales, no una tensión constante; la capacidad indicada no determina la corriente de carga o descarga admisible. La disposición mecánica no valida el circuito ni autoriza a conectar la bobina al GPIO; véase el [esquema funcional](ESQUEMA_INICIAL_CONEXIONES.md) y el [inventario](MATERIALES_Y_ENSAMBLAJES.md).
