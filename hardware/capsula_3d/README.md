# Cápsula: maqueta 3D conceptual

Interpretación del croquis y de la aclaración del usuario: **cuerpo cilíndrico recto cerrado por el extremo de la ojiva**, tapa roscada con junta tórica en el extremo de carga y ojiva circular independiente que se atornillará al exterior del fondo cerrado y alojará el lastre. La ojiva podría ser de otro material, incluso metálica. La PCB va longitudinalmente con la batería debajo. Abrir `capsula_conceptual.scad` con OpenSCAD. El modo `corte` muestra el interior; `conjunto`, `cuerpo`, `tapa` y `punta` permiten examinar el conjunto y sus piezas.

La [vista en corte](capsula_corte.png) muestra la bandeja extraíble en amarillo, la bobina de carga naranja junto a la tapa, la batería azul bajo la PCB y el actuador **dentro del cilindro**, antes de la ojiva. En OpenSCAD, `modo="bandeja"` permite aislar la bandeja.

## Modelo para SolidWorks

El [conjunto STEP](capsula_conceptual.step) se puede importar desde SolidWorks con **Archivo → Abrir**, seleccionando el formato STEP. Es un intercambio de geometría, **no un archivo nativo `.SLDASM` ni conserva un árbol de operaciones paramétricas de SolidWorks**. La importación y la apariencia pueden depender de la versión y sus opciones. También están disponibles las piezas [bandeja](bandeja_conceptual.step), [cuerpo](cuerpo_conceptual.step), [tapa](tapa_conceptual.step) y [ojiva](ojiva_conceptual.step). Para ver el interior, ocultar `Cuerpo_PETG` o activar una vista de sección longitudinal.

El conjunto contiene piezas y bloques simplificados en milímetros: cuerpo, bandeja, tapa, ojiva, PCB de **1,6 mm**, batería, actuador, bobina de carga y envolventes de módulos. La junta tórica, los clips y sus aberturas en la PCB son ilustrativos; no incluye contactos ni cableado. El perfil de la ojiva se aproxima mediante segmentos, con una pequeña diferencia en el extremo interior respecto a OpenSCAD. El STEP es una representación de estudio, no un plano ni una comprobación de montaje.

La tapa **deberá ser roscada con junta tórica**, pero los STEP conservan el encaje liso y la ranura ilustrativa del modelo anterior: ni la rosca ni la compresión de la junta están diseñadas. Una opción a desarrollar es una junta facial comprimida entre superficies de la tapa y el cuerpo, con la rosca proporcionando el apriete y un tope controlando la compresión; exige definir la sección y el alojamiento de la junta, el tipo de rosca, las tolerancias, la accesibilidad de la bobina y los ensayos de estanqueidad. No se debe fabricar o sumergir como cierre terminado.

El ESP32 se ha trasladado al extremo de la tapa para orientar su USB-C hacia ella; el bloque no modela el conector. La bobina puede bloquear el acceso: falta comprobar el espacio del cable y definir si se aparta la bobina o se extrae el conjunto. La batería se dibuja bajo la PCB, con su extremo nominal alineado con el extremo de la placa hacia la ojiva. Dos abrazaderas naranjas con pestañas y aberturas simbólicas representan la idea del croquis. Sus pestañas se sitúan entre IMU y DRV8833 y después del DRV8833, sin solapar los bloques representados. La segunda queda muy cerca del borde y puede requerir redistribuir los módulos o alargar la placa. No hay un mecanismo de clic validado ni garantía de elasticidad, retención axial o aislamiento; faltan contactos, dimensionado de ranuras y comprobación de pines y cobre.

**No es una cápsula terminada ni estanca.** El fondo del cuerpo es cerrado en la geometría, pero el PETG impreso y sus capas pueden presentar fugas: falta validar la fabricación y la estanqueidad del cuerpo. El cuello exterior y el alojamiento de la ojiva son lisos y simbólicos: **todavía no hay roscas helicoidales**. La tapa tiene una junta tórica con ranura ilustrativa; su sección se superpone intencionadamente a la superficie del cuerpo y no es una simulación validada de compresión. El diámetro, sección, alojamiento, compresión y material de la junta, el tipo de rosca, sentido, paso y holguras deben diseñarse para las piezas y el proceso de impresión. La ojiva y su unión quedan fuera de la barrera estanca: puede entrar líquido en su alojamiento, por lo que habrá que evaluar material, lastre, corrosión y drenaje o sellado según el diseño final.

La ojiva hueca reserva espacio para el **lastre**, pero no modela su forma, masa ni fijación. El cilindro gris es una envolvente ilustrativa del actuador, situado fuera de la ojiva y dentro del cuerpo principal; no representa su parte móvil. Su ubicación exacta respecto al lastre y al centro de masas sigue pendiente; los bloques de componentes no son modelos reales.

## Propuesta de bandeja extraíble en PETG translúcido

El material previsto es **PETG translúcido**. Las holguras son valores de partida, no tolerancias verificadas; dependen de la impresora, orientación, material y piezas reales.

- **Bandeja y PCB:** dos largueros de la bandeja deslizan en guías internas del cuerpo; la PCB nominal de 1,6 mm descansa sobre apoyos simbólicos en la bandeja. La abertura está en el extremo de la tapa. La unión de la PCB a sus apoyos, la retención axial de la bandeja, tolerancias y compatibilidad con pines, soldaduras, cables y clips aún no están resueltas.
- **Bobina de carga:** corona de centrado en el extremo de la bandeja, diámetro interior nominal 25,8 mm para la bobina anunciada de 25 mm. Viaja con la PCB y no gira al roscar la tapa. No tiene retención, alojamiento del ferrito, salida de cables ni solución para el USB-C; puede obstruir el conector. No forzar ni dañar los hilos finos de la bobina.
- **Actuador:** aro de posición unido al extremo opuesto de la bandeja, diámetro interior nominal 20,8 mm; se introduce con la PCB y sus cables ya conectados. No forma parte de la ojiva. Según ha aclarado el usuario, **se sujeta la bobina** y se deja libre la parte móvil. Se reserva espacio para **3 mm de desplazamiento longitudinal**. La ficha de la variante seleccionada 20VC001 aportada por el usuario muestra Ø20 mm, longitud de cuerpo aproximada 13 mm y una parte móvil de 12,2 mm; el usuario midió 13,5 mm de cuerpo. La imagen indica agujeros roscados en las caras, pero no define con suficiente claridad sus superficies de fijación. El aro es solo una envolvente de estudio: verificar cómo sujetar la bobina **sin apretar ni pegar la parte móvil**, dañar sus hilos ni obstaculizar la carrera. La trayectoria de 3 mm indicada por la ficha y las posiciones inicial y extremas deben verificarse; el aro no es una guía de la parte móvil, no aporta topes ni detecta posición.

Montaje propuesto: ensamblar y conectar los componentes fuera del tubo; introducir primero el extremo del actuador, encauzando los largueros en las guías; fijar axialmente la bandeja mediante un mecanismo aún por diseñar y cerrar la tapa sin hacer girar la bandeja. Las guías comienzan tras la zona de encaje de la tapa; faltan una entrada que facilite su alineación y una forma segura de extraer la bandeja. No se han representado cables ni conectores, de modo que no se ha demostrado el montaje completo.

Como comprobación geométrica preliminar se han ensayado siete posiciones axiales discretas del modelo simplificado, sin intersecciones entre el cuerpo y las envolventes de bandeja, PCB, batería, actuador y bobina. No es una simulación continua ni incluye clips, módulos reales, conexiones, tolerancias de impresión o flexión. Los largueros son deliberadamente esquemáticos: su rigidez y la escasa zona de contacto con las guías no están dimensionadas para uso real.

Los cupones siguientes corresponden a la **versión anterior**, con PCB deslizante directamente en el cuerpo; no validan la bandeja ni las guías nuevas. Solo sirven para estudiar ajustes aproximados **en seco y sin electrónica ni batería**:

| Pieza | Comprobación | Archivo |
|---|---|---|
| Anillo anterior de 20 mm de cuerpo | Antigua guía directa de PCB, ya no aplicable a la bandeja | [prueba_pcb.stl](prueba_pcb.stl) |
| Aro de bobina | Centrado a Ø25,8 mm | [prueba_bobina.stl](prueba_bobina.stl) |
| Aro de actuador | Centrado a Ø20,8 mm | [prueba_actuador.stl](prueba_actuador.stl) |

Estos STL son **cupones de ajuste**, no componentes funcionales ni un cierre. No fuerzan ni fijan la batería o el actuador. La sujeción definitiva de la bobina, la parte fija del actuador, la guía y parada de su parte móvil y el lastre requieren diseño posterior. La dirección del movimiento es longitudinal; compruébese también la posición de su línea de acción respecto al centro de masas para obtener excitación angular.

## Dimensiones de partida, en mm

| Elemento | Valor | Alcance |
|---|---:|---|
| Cuerpo tubular | 214 largo, 48 diámetro exterior, pared principal 2, fondo cerrado de 3 | Hipótesis inicial; diámetro interior 44 en el tramo central, 42 en los 8 mm de cada extremo; sin validación de estanqueidad |
| Cuello exterior | 8 de largo, Ø40,4 | Parte del fondo cerrado; liso, reserva para rosca |
| Ojiva | 40 de largo desde el extremo del cuerpo: casquillo 8 + arco 32; diámetro de base 48 | Pieza independiente exterior, encaje liso ilustrativo; lastre y rosca sin diseñar |
| Tapa | Disco de espesor 3 | Encaje liso ilustrativo y ranura para junta, sin rosca |
| Junta tórica | Diámetro medio 44, sección 2 | Modelo y ranura ilustrativos, compresión y estanqueidad no verificadas |
| Longitud total exterior | 257 | 3 de tapa + 214 de cuerpo + 8 de casquillo + 32 de ojiva |
| PCB | 164 × 24 × 1,6 | Maqueta mecánica provisional, no PCB terminada |
| Batería | Cilindro 50 × Ø14 | Dimensiones nominales, sin terminales ni soporte |
| Bobina | Ø25 × 1 | Espesor ilustrativo, no medido |
| Actuador | Ø20 × 13,5 | Solo envolvente aproximada del cuerpo; no incluye fijación ni carrera |

Tomando `x = 0` en el inicio del cuerpo, la PCB ocupa `x = 10–174 mm`; la batería nominal ocupa `x = 124–174 mm` bajo ella, con su eje 9,5 mm por debajo de su plano medio. Las guías de la bandeja ocupan `x = 8–200 mm`; la bandeja dibujada ocupa `x = 4–189 mm`. La envolvente indicativa del actuador ocupa `x = 181–194,5 mm` y el aro de centrado `x = 185–189 mm`. Solo quedan 7 mm entre el extremo nominal de la batería y el comienzo de la envolvente del actuador; no incluye contactos, protección, cables ni tolerancias y no garantiza que quepan. El fondo cerrado ocupa `x = 211–214 mm`; el cuello exterior ocupa `x = 214–222 mm` y no comunica con el interior. El casquillo de la ojiva independiente rodea ese cuello. La reserva axial no está validada para la parte móvil, montaje, cables ni recorrido. Las alturas de los bloques electrónicos son **suposiciones**; la holgura, el aislamiento de la batería, los conectores, los radios de cable, la antena y el acceso al USB no están verificados. El condensador está representado por un bloque de 12 mm reservado, no por una medida confirmada.

Como comprobación inicial de espacio, al añadir 3 mm hacia el fondo a la envolvente ilustrativa se llega a `x = 197,5 mm`, a 13,5 mm del fondo. **No se ha identificado la geometría ni el sentido real de la pieza móvil**: esta suma no constituye una comprobación de colisiones ni permite asegurar que el recinto tenga una carrera útil de 3 mm. El soporte de la bobina, la guía, el espacio para cables, los topes y la parada segura se dimensionarán al conocer esa geometría; no usar la estructura actual como tope.

La longitud de 164 mm procede de la primera maqueta de la portadora: puede cambiar al diseñar huellas, conectores, PCB y antena. El diámetro exterior de 48 mm y el resto de las dimensiones de carcasa son propuestas, no resultados optimizados. El aro actual es coaxial con la cápsula, solo para estudiar el alojamiento; esa posición no establece la línea de acción respecto al centro de masas ni garantiza que produzca el ángulo deseado. La orientación y sentido de la parte móvil, sus superficies de fijación, cables, guía y posiciones extremas deberán verificarse con el actuador real antes de definir la sujeción.

La geometría no demuestra flotación, estabilidad ni resistencia. Es necesario medir masas y envolventes completas, definir cierres y estanqueidad, comprobar la flotación en los fluidos de ensayo y reajustar el lastre. Antes de fabricar o sumergir componentes deben revisarse también la batería, la carga inalámbrica, el calentamiento y la etapa de accionamiento.

## Exportación

Para actualizar el STEP se necesita Python con CadQuery instalado. El generador toma del archivo OpenSCAD las dimensiones escalares principales; las geometrías y bloques simplificados restantes están definidos en el propio generador y deben revisarse al cambiar el modelo:

```bash
python3 hardware/capsula_3d/exportar_step.py
```

```bash
openscad -D 'modo="corte"' -o vista.csg hardware/capsula_3d/capsula_conceptual.scad
```

Los STL históricos no se regeneran automáticamente: el modo `prueba_pcb` ahora recorta las nuevas guías de bandeja y no reproduce el cupón anterior.

La exportación de las piezas completas no implica que sean aptas para cerrar la cápsula o para uso en líquido. La [PCB de referencia](../pcb_portadora/README.md) continúa sin conexiones ni huellas terminadas.
