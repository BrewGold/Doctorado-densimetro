# Cápsula: maqueta 3D conceptual

Primera interpretación del croquis facilitado: cuerpo tubular, tapa en el extremo de la bobina de carga, PCB longitudinal con batería debajo y punta separada para el actuador y el lastre. Abrir `capsula_conceptual.scad` con OpenSCAD. El modo `corte` muestra el interior; `conjunto`, `cuerpo`, `tapa` y `punta` permiten examinar el conjunto y sus piezas.

La [vista en corte](capsula_corte.png) muestra la geometría y los bloques de referencia; la bobina naranja se representa junto a la tapa, la batería azul bajo la PCB y el actuador en la punta.

**No es un diseño imprimible ni estanco.** Las piezas son envolventes sin roscas, encajes, juntas, fijaciones, guías, soporte de PCB ni solución para cables. El croquis indica roscas en los extremos; se deben diseñar y validar después, con tolerancias del proceso de impresión y un cierre estanco apropiado. Los componentes internos son bloques o cilindros de referencia, no sus modelos reales; la punta no incluye todavía el lastre ni el mecanismo de guiado del actuador.

## Dimensiones de partida, en mm

| Elemento | Valor | Alcance |
|---|---:|---|
| Cuerpo tubular | 184 largo, 48 diámetro exterior, 2 pared | Hipótesis inicial; diámetro interior 44 |
| Punta | Semiesfera exterior de radio 24, pared 2 | Envolvente ilustrativa, sin unión |
| Tapa | Disco de espesor 3 | Sin unión, junta ni alojamiento de la bobina |
| Longitud total exterior | 211 | 3 de tapa + 184 de cuerpo + 24 de punta |
| PCB | 164 × 24 × 1,6 | Maqueta mecánica provisional, no PCB terminada |
| Batería | Cilindro 50 × Ø14 | Dimensiones nominales, sin terminales ni soporte |
| Bobina | Ø25 × 1 | Espesor ilustrativo, no medido |
| Actuador | Ø20 × 13,5 | Solo envolvente aproximada del cuerpo; no incluye fijación ni carrera |

El PCB empieza 10 mm después del inicio del tubo y acaba 10 mm antes de su extremo. La batería se dibuja bajo la PCB, con su eje 9,5 mm por debajo de su plano medio. Las alturas de los bloques electrónicos son **suposiciones**; la holgura, el aislamiento de la batería, los conectores, los radios de cable, la antena y el acceso al USB no están verificados. El condensador está representado por un bloque de 12 mm reservado, no por una medida confirmada.

La longitud de 164 mm procede de la primera maqueta de la portadora: puede cambiar al diseñar huellas, conectores, PCB y antena. El diámetro exterior de 48 mm y el resto de las dimensiones de carcasa son propuestas, no resultados optimizados. El posicionamiento en la punta no establece la línea de acción del actuador con respecto al centro de masas ni garantiza que produzca el ángulo deseado. La dimensión y orientación exactas del actuador, sus cables, guía y posiciones extremas deberán verificarse.

La geometría no demuestra flotación, estabilidad ni resistencia. Es necesario medir masas y envolventes completas, definir cierres y estanqueidad, comprobar la flotación en los fluidos de ensayo y reajustar el lastre. Antes de fabricar o sumergir componentes deben revisarse también la batería, la carga inalámbrica, el calentamiento y la etapa de accionamiento.

## Exportación

```bash
openscad -D 'modo="corte"' -o vista.csg hardware/capsula_3d/capsula_conceptual.scad
```

La exportación de piezas geométricas puede servir para estudiar el modelo, pero **no implica que sean aptas para impresión o para uso en líquido**. La [PCB de referencia](../pcb_portadora/README.md) continúa sin conexiones ni huellas terminadas.
