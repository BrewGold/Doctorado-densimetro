# Materiales y ensamblajes

## Propósito y alcance

Este documento organiza el inventario del prototipo y el procedimiento para montar y repetir ensayos. Por ahora es una plantilla de trabajo: recoge los componentes mencionados en la investigación, pero no presupone que sus modelos, materiales, dimensiones o disponibilidad estén confirmados.

La prioridad es que la cápsula pueda ensayarse en una configuración documentada y reproducible. Cualquier cambio de masa, posición del lastre, cableado o montaje del sensor puede alterar el centro de masas y la respuesta dinámica.

## Inventario preliminar

| Conjunto | Componente | Función | Estado actual | Datos por registrar |
|---|---|---|---|---|
| Cápsula | Cuerpo/carcasa | Flotabilidad y soporte de componentes | Geometría conceptual; fabricación y material por confirmar | Material, dimensiones, masa, espesor, uniones y estanqueidad |
| Balanceo | Lastre | Crear o ajustar el desbalance | Mencionado; pieza y ubicación exactas por documentar | Material, masa, forma, posición respecto a ejes y método de fijación |
| Medida | IMU | Registrar movimiento y estimar orientación | Sensor disponible según el planteamiento experimental | Modelo, rango, frecuencia de muestreo, orientación de ejes, configuración y calibración |
| Alimentación | Batería 14500 | Alimentar la instrumentación | Recargable de litio, 3,7 V nominales y 800 mAh indicados | Medidas reales, masa, referencia, límites de carga y descarga, protección, posición y sujeción |
| Alimentación | Receptor/cargador inalámbrico con bobina circular | Carga de la batería dentro de la cápsula | Pedido; sustituye al cargador anterior | Bobina de 25 mm, placa aprox. 15 × 18 mm; confirmar polaridad, corriente, protección, temperatura y compatibilidad |
| Alimentación | MT3608 | Elevador de tensión para la electrónica | Usado en el TFM; candidato sujeto a validación | Verificar tensión y corriente de `BOUT`, salida necesaria y compatibilidad con el ESP32 |
| Eléctrico | Cableado y conectores | Alimentación y adquisición | Mencionados; recorrido por documentar | Masa, longitud, conectores, sujeción y efecto sobre sellado o movimiento |
| Ensayo | Recipiente | Contener el fluido y permitir el movimiento | Existe contexto de ensayos y simulaciones; dimensiones físicas por verificar | Forma, dimensiones interiores, nivel de llenado y material |
| Ensayo | Fluidos | Medio de prueba | Agua de referencia; se proponen agua-sal y agua-glicerina | Composición, densidad, viscosidad, temperatura y método/procedencia de medida |
| Excitación | Actuador de bobina de voz (futuro) | Aplicar una perturbación controlada | Recibido; la ficha mostrada identifica la variante como 20VC001; confirmar en la unidad | Diámetro 20 mm; cuerpo medido 13,5 mm; parte móvil 12,2 mm de altura; masa total 25 g; ficha: 3,7 V, 0,41 A, 9 Ω ±10 %, 1,8 mH ±10 % y carrera 3 mm |
| Excitación | Amplificador/etapa de accionamiento (futura) | Accionar el actuador | Pendiente de selección según el actuador | Dimensiones, alimentación, señales de control, potencia, temperatura y compatibilidad |

Las dimensiones usadas en un escenario de simulación no se consideran medidas del prototipo físico hasta verificarlas. Completar el inventario con fabricante/modelo cuando exista, identificador de pieza, cantidad, masa medida, estado y enlace a ficha técnica o plano.

## Subconjuntos y montaje

### A. Cápsula y lastre

1. Registrar las dimensiones exteriores de la cápsula real y su masa sin componentes, si se dispone de esa configuración.
2. Instalar el lastre en una posición definida y medir la masa total.
3. Registrar la posición del lastre respecto a un sistema de ejes y fijarlo para que no se desplace durante el ensayo.
4. Anotar cualquier adhesivo, soporte, tornillo o pieza añadido, ya que también contribuye a la masa y a la inercia.

### B. IMU, alimentación y cableado

1. Definir los ejes de referencia de la cápsula y documentar la orientación física de los ejes del IMU.
2. Fijar rígidamente el IMU a la cápsula; evitar holguras y flexión relativa.
3. Sujetar batería y cableado, registrar sus posiciones y comprobar que no puedan moverse ni interferir con el balanceo.
4. Registrar la configuración de adquisición: frecuencia, rangos, filtros y formato de datos.
5. Si los componentes quedan dentro de la carcasa, verificar la protección frente al fluido antes de sumergirlos. El tipo de sellado se debe documentar y validar para el montaje real; no se presupone aquí un grado de estanqueidad.

La propuesta sitúa la batería cerca del extremo lastrado, bajo la PCB, y la bobina receptora junto a la tapa opuesta. En sentido longitudinal, desde la tapa hacia el extremo lastrado, se prevé el siguiente orden físico:

```text
Tapa / bobina → módulo receptor-cargador → elevador (boost) → IMU → ESP32 → punta lastrada
```

Se prevé una PCB portadora para soldar los módulos, incorporando pines donde falten. Sus huellas, fijaciones y la altura del conjunto se determinarán al medir las placas y sus conexiones; véase el [esquema funcional](ESQUEMA_INICIAL_CONEXIONES.md).

La posición de la batería bajo la PCB y la distribución de los módulos deben ajustarse a las dimensiones reales. El orden describe su ubicación física, no conexiones eléctricas en serie. Deben verificarse espacio y sujeción, estanqueidad, temperatura, separación del convertidor respecto a la IMU y condiciones de antena del ESP32 antes de fijar la disposición definitiva. Se prevé una interfaz de cuatro pines entre la PCB principal y el receptor/cargador, con pinout pendiente; `BOUT` se considera una posible entrada al elevador, no una conexión validada.

Para una vista esquemática del conjunto y las dimensiones pendientes, consultar la [distribución interior preliminar](DISTRIBUCION_INTERIOR_CAPSULA.md).

Para una ampliación futura se propone reservar espacio en la punta lastrada para el **actuador y su amplificador o etapa de accionamiento**. La ficha de la variante seleccionada 20VC001 lo describe como bobina de voz: la fuerza puede cambiar de sentido al invertir la corriente, por lo que un puente H con control de corriente es una opción a estudiar. La parte móvil se desplaza libremente sin alimentación y no se aprecia un muelle a primera vista; por tanto, el retorno sin corriente no está garantizado. El resumen automático del anuncio menciona un muelle, pero no se toma como prueba de que esté presente.

Para continuar el experimento se selecciona como configuración de trabajo un **recorrido guiado de la masa móvil paralelo al eje longitudinal de la cápsula**, con el actuador en la punta lastrada. La selección se apoyó en una simulación exploratoria y no demuestra que esa orientación sea óptima para todos los fluidos. Registrar la posición del actuador y el sentido de movimiento respecto a los ejes de la cápsula.

La ficha 20VC001 indica **3 mm de carrera**, mientras otra imagen del anuncio indica 4 mm sin identificar con claridad la variante. Se descarta la hipótesis previa de 5 mm como carrera de diseño hasta confirmar mecánicamente el límite útil de la unidad y las condiciones especificadas. La ficha indica **1,8 mH ±10 %**, frente al dato preliminar de 4,8 mH: no se consideran equivalentes y hay que verificar modelo y medición. La masa móvil no se conoce por separado; los 25 g son del conjunto y la altura de 12,2 mm no es su carrera.

La etapa de accionamiento, sus límites térmicos y la alimentación siguen por definir; no conectar la bobina directamente a un GPIO del ESP32. Se comprobará la compatibilidad con el espacio de la batería y el lastre, la antena del ESP32, la disipación y posibles interferencias con el IMU. Al añadirlo habrá que volver a medir masa y equilibrio y reajustar el lastre si fuera necesario.

### C. Preparación del ensayo

1. Identificar el recipiente y medir sus dimensiones interiores y el nivel de llenado.
2. Identificar cada muestra de fluido; registrar composición, temperatura y propiedades medidas o estimadas.
3. Colocar la cápsula con el mismo montaje y condición inicial definidos para esa serie.
4. Comprobar la adquisición del IMU y realizar un registro de reposo antes de perturbar.
5. Aplicar el procedimiento de perturbación y liberación previsto, anotando cualquier desviación.
6. Al terminar, revisar el registro, la cápsula y el estado de cualquier sello o unión.

## Registro de configuración y ensamblaje

Cada configuración física debe tener un identificador (por ejemplo, `CAP-01`, `IMU-01`, `FLUIDO-AGUA-01`) y conservar un registro con:

- fecha, responsable e identificadores de piezas;
- masa total y masas añadidas o retiradas;
- dimensiones relevantes y posición del lastre, IMU, batería y actuador;
- fotografías o esquema con escala, ejes y orientación del IMU;
- uniones, fijaciones, materiales de sellado y cambios desde el montaje anterior;
- recipiente, muestra, temperatura y nivel de llenado;
- frecuencia y parámetros de adquisición;
- observaciones, incidencias y archivos de datos asociados.

Antes de comparar dos ensayos, verificar que la cápsula, el lastre, la posición del sensor, el cableado, el recipiente y el procedimiento sean equivalentes. Si cambia un componente o su posición, registrar la configuración como una variante nueva.

## Decisiones pendientes

- material y método de fabricación de la carcasa;
- geometría y dimensiones verificadas del prototipo físico;
- diseño, masa y posición ajustable del lastre;
- modelo y montaje del IMU, batería y cableado;
- método de cierre y validación de estanqueidad;
- recipiente y dimensiones físicas del montaje de ensayo;
- identificar y caracterizar el actuador recibido, seleccionar su etapa de accionamiento y validar el espacio en la punta;
- formato de hoja de ensamblaje y responsables de su mantenimiento.

Hasta cerrar estas decisiones, el documento sirve como inventario y protocolo inicial, no como una lista de compra ni como instrucciones de fabricación definitivas.
