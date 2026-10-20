# Biobibliografía y estado del arte del densímetro tipo cápsula

## 1. Objetivo y alcance

Consolidar las referencias discutidas y facilitar la continuación de la investigación de una cápsula flotante que estima densidad mediante su orientación. Es una **matriz de trabajo, no una revisión sistemática exhaustiva**. Se distingue entre el principio de medición, la dinámica del sensor y la disponibilidad temporal de sus lecturas.

En la etapa estática planteada por el usuario se busca identificar la densidad a partir del ángulo medido, la masa, la geometría y los centros de gravedad y empuje. No se necesita suponer una densidad inicial: se imponen simultáneamente los balances de fuerzas y momentos. El volumen sumergido y su primer momento deben considerar el cilindro y las dos semiesferas, no solo el cilindro. Esto no equivale a usar el volumen total de la cápsula cuando está parcialmente sumergida.

La extensión dinámica estudiaría el movimiento angular, la inercia, el amortiguamiento y la respuesta transitoria. Para el contexto del repositorio, véanse la [geometría de la cápsula](../doctorado_sim/docs/CAPSULE_GEOMETRY.md), el [marco teórico](../doctorado_sim/docs/THEORETICAL_FRAMEWORK.md) y el [mapa de trazabilidad del TFM](TRACEABILITY_MAP.md). Esta revisión no modifica ni valida sus modelos.

## 2. Problema de búsqueda y nota metodológica

Según la exploración reportada por el usuario, buscar «tilt densimeter» produce pocos resultados directos y bastante ruido en IEEE. No debe tratarse como un término académico estandarizado ni como la única denominación del dispositivo. *Hydrometer*, *densitometer*, *density sensor* y *specific gravity sensor* abarcan tecnologías distintas: compartir la magnitud medida no implica compartir el mecanismo. La referencia [R7] se incorpora con los datos aportados por el usuario, pero no pudo verificarse en una fuente primaria accesible durante esta revisión.

**Es necesario buscar por principio físico**, combinando flotación, equilibrio hidrostático, inclinación y orientación. La ausencia de coincidencias con una expresión exacta no demuestra ausencia de antecedentes ni novedad científica. Conviene ampliar IEEE Xplore con otras fuentes, como Crossref, Google Scholar, Web of Science, Scopus y repositorios institucionales; registrar fecha, consulta, filtros y motivo de inclusión o exclusión.

La evidencia externa utilizada aquí procede de fichas y resúmenes indexados localizados en la búsqueda, no de una lectura íntegra de los artículos. Los enlaces permiten continuar la comprobación; su presencia no significa que se haya verificado toda la ficha editorial. Se conservan los años proporcionados por el usuario cuando no fue posible corroborarlos. Los campos pendientes no deben copiarse a la bibliografía definitiva de la tesis como si estuvieran confirmados.

## 3. Criterios de clasificación

### Enfoque: equilibrio frente a dinámica

- **Equilibrio:** la densidad se obtiene de una relación estática de fuerzas, momentos, empuje o presión hidrostática. Una lectura continua o electrónica no cambia esta clasificación.
- **Dinámico:** la medición utiliza oscilaciones, propagación acústica, desplazamientos temporales o una respuesta transitoria. Se especifica si es dinámica resonante, acústica, de flujo o de cuerpo flotante: no son intercambiables.
- **Mixto:** el trabajo utiliza efectivamente tanto un balance estático como información dinámica. No basta con medir dos magnitudes o incorporar un circuito oscilador auxiliar.
- **No aplica:** el observable de densidad es óptico o dieléctrico sin utilizar equilibrio ni dinámica mecánica. **No determinado** indica que la fuente o la evidencia accesible no permite clasificar el principio.

«Real time», «monitorización» o «medición en flujo» no prueban por sí solos que se modele la dinámica del sensor. Tampoco una vibración MEMS demuestra un estudio del movimiento angular de una cápsula.

### Relación con «tilt densimeter»

En este documento, la expresión designa funcionalmente un **cuerpo flotante cuya inclinación permite inferir densidad o gravedad específica**, no cualquier inclinómetro ni exclusivamente un producto comercial.

- **Sí:** hay evidencia explícita de densidad estimada mediante la orientación de un cuerpo flotante.
- **Parcial:** comparte un fundamento físico relevante, como hidrostática o empuje, pero no demuestra medición por inclinación. Las afinidades meramente temáticas se indican expresamente.
- **No:** mide densidad mediante otro principio y no se encontró evidencia de relación con inclinación de flotación.
- **No determinado:** no hay evidencia suficiente para evaluar la relación.

Estas etiquetas valoran pertinencia respecto de la cápsula, no calidad científica. Las clasificaciones provisionales requieren revisión del texto completo; no deben interpretarse como exclusiones definitivas.

## 4. Tabla bibliográfica de trabajo

Los identificadores [R1]–[R7] remiten a los títulos y enlaces de la sección siguiente.

| Referencia (autor, año, título abreviado) | Fuente y enlace | Principio de medida; clasificación | ¿Relación con tilt densimeter? | Evidencia consultada | Pertinencia |
|---|---|---|---|---|---|
| [R1] Autoría pendiente; 1987, *Optical-Type Hydrometer for Lead-Acid Batteries…* | IEEE Xplore; ficha adicional TIB | Refractometría; no aplica | No | Resumen indexado: índice de refracción del electrolito y gravedad específica. Ficha completa por corroborar. | «Hydrometer» no implica aquí un flotador; no aporta evidencia de equilibrio angular ni dinámica de cápsula. |
| [R2] Autoría pendiente; 2007, *Plastic Optical Fiber Sensor for Real Time Density Measurements in a Liquid Medium* | Por confirmar; candidato de título parecido en IEEE | No determinado¹ | No determinado¹ | La coincidencia exacta no quedó confirmada; no se consultó el texto del artículo candidato. | «Real time» no permite decidir entre equilibrio y dinámica ni atribuirle empuje. No usar como antecedente físico demostrado. |
| [R3] Autoría pendiente; 2015, *High accuracy pressure type liquid level measurement system…* | IEEE Xplore | Presión hidrostática; equilibrio provisional | Parcial, provisional | El resumen describe sensores de presión absoluta y estimación de nivel/densidad; configuración y modelo pendientes. | Comparación hidrostática; no hay evidencia de inclinación de un flotador. Año por corroborar. |
| [R4] T. Manzaneque et al.; 2014, *Density-viscosity sensor based on piezoelectric MEMS resonator…* | IEEE SENSORS 2014 | Resonancia MEMS; dinámico | No | Ficha/resumen: resonador piezoeléctrico y circuito oscilador para densidad/viscosidad. | Alternativa de transducción, no modelo de orientación hidrostática ni del transitorio de un flotador. Lista de autores por verificar. |
| [R5] X. Fu, L. Lou y H. Ren; 2026, *A Liquid Density Sensor Based on AlN…* | Preprint arXiv; publicación editorial posterior no verificada | Acústica ultrasónica; dinámico | No | Resumen de arXiv: transmisión/recepción ultrasónica y amplitud recibida a frecuencia fija. | No confundir con desplazamiento de frecuencia resonante ni inclinación. La insensibilidad a viscosidad se limita al rango ensayado. |
| [R6] G. Holler, D. Hrach, A. Fuchs y G. Brasseur; 2009, *Application of a combined capacitive flow velocity and density sensor…* | IEEE I2MTC; registro institucional TU Graz | Densidad capacitiva; no aplica. Seguimiento de burbujas para velocidad/caudal; dinámico | No | Registro institucional: combinación de sensor capacitivo de densidad y seguimiento del paso de burbujas. | No se identificó equilibrio mecánico; «combinado» no justifica clasificarlo como mixto equilibrio–dinámico. |
| [L1] F. Gold Araoz; 2026, *Estimación de densidad de fluidos mediante orientación angular* | TFM conservado en el repositorio | Orientación de equilibrio; equilibrio | Sí | Metadatos locales: relación densidad–orientación de equilibrio. | Antecedente local directo; no clasifica todo el PDF ni presupone lectura íntegra. La extensión doctoral separa contribuciones estáticas y dinámicas. |
| [R7] Autores y afiliación aportados por el usuario; año pendiente, *Development of a PLC/IoT Control System with Real-Time Concentration Monitoring for the Osmotic Dehydration of Fruits* | Registro y fuente primaria no identificados; [búsqueda bibliográfica por título](https://search.crossref.org/?q=Development%20of%20a%20PLC%2FIoT%20Control%20System%20with%20Real-Time%20Concentration%20Monitoring%20for%20the%20Osmotic%20Dehydration%20of%20Fruits) | Principio no determinado; clasificación no determinada | No determinada | Solo se dispone del título, autoría y afiliación aportados por el usuario; no se verificaron resumen, texto completo, sección/página ni instrumento. No se puede determinar si usa un hidrómetro inclinado, otro sensor o una técnica distinta, ni identificar marca/modelo. | El título sugiere una aplicación alimentaria con monitoreo de concentración e integración PLC/IoT; esos detalles y su pertinencia física para la cápsula quedan pendientes de verificación. |

**¹ Referencia no identificada:** «No determinado» refleja la falta de evidencia para clasificar el principio o la relación con inclinación. No equivale a confirmar ni descartar flotación, empuje o inclinación. Debe reclasificarse al identificar la publicación y consultar evidencia pertinente.

### Lectura para el estado del arte

Entre los artículos externos identificados no se ha confirmado un antecedente directo del mecanismo de inclinación de equilibrio. Esto describe el alcance de esta búsqueda, no prueba que tal antecedente no exista. [R3] es una comparación hidrostática provisional; [R4] y [R5] son ejemplos de dinámica de otro tipo. [R6] permite distinguir dinámica de flujo de dinámica del sensor. [R2] y [R7] siguen pendientes de verificación.

[R7] podría aportar contexto de aplicación alimentaria y control temporal de concentración mediante PLC/IoT, pero solo se dispone del título y los datos bibliográficos proporcionados por el usuario. No es posible afirmar qué sensor emplea, ni equiparar el monitoreo «real-time» del proceso con una dinámica mecánica del instrumento; tampoco se puede asignar pertinencia respecto de un *tilt densimeter* hasta consultar una fuente primaria.

El siguiente paso prioritario es buscar trabajos que relacionen explícitamente **densidad–ángulo de equilibrio–geometría sumergida–centro de empuje**, antes de pasar a comparaciones sobre amortiguamiento o identificación dinámica.

## 5. Referencias y trazabilidad

- **[R1]** *Optical-Type Hydrometer for Lead-Acid Batteries and its Applications* (1987, año aportado en la consulta). [IEEE Xplore, registro 4794631](https://ieeexplore.ieee.org/document/4794631); [registro TIB](https://www.tib.eu/de/suchen/id/tema:TEMAE88030357048/Optical-type-hydrometer-for-lead-acid-batteries). Autoría, año editorial, publicación y DOI pendientes de comprobación directa.
- **[R2]** *Plastic Optical Fiber Sensor for Real Time Density Measurements in a Liquid Medium* (2007, título/año aportados en la consulta). No se confirmó un registro exacto. Como **pista, no sustituto**, se localizó [IEEE Xplore 4258431](https://ieeexplore.ieee.org/document/4258431), cuyo título indexado comienza *Plastic Optical Fiber Sensor for Real Time Density Measurements in Wine…*. Verificar identidad, autoría y año antes de fusionar ambas referencias. No trasladar a esta entrada resultados del artículo distinto de 2009 *A novel approach to the sensing of liquid density using a plastic…*, [DOI 10.1088/0031-9120/44/1/009](https://doi.org/10.1088/0031-9120/44/1/009).
- **[R3]** *High accuracy pressure type liquid level measurement system capable of measuring density* (2015, año aportado en la consulta). [IEEE Xplore, registro 7372925](https://ieeexplore.ieee.org/document/7372925). Autoría, año editorial, publicación y DOI pendientes. La interpretación hidrostática de la tabla es provisional, no una ecuación verificada del artículo.
- **[R4]** Manzaneque, T., et al. (2014). *Density-viscosity sensor based on piezoelectric MEMS resonator and oscillator circuit*. IEEE SENSORS 2014. [IEEE Xplore, registro 6984978](https://ieeexplore.ieee.org/document/6984978). Lista completa de autores y DOI pendientes. No confundir con el artículo distinto *Piezoelectric MEMS resonator-based oscillator for density and viscosity sensing*, cuyo DOI es [10.1016/j.sna.2014.10.002](https://doi.org/10.1016/j.sna.2014.10.002); ese DOI no se atribuye aquí al trabajo de congreso.
- **[R5]** Fu, X., Lou, L., y Ren, H. (2026). El registro localizado presenta *A Liquid Density Sensor Based on AlN Piezoelectric Micromachined Ultrasonic Transmitter Insensitive to Liquid Viscosity*, mientras que la consulta usa **Transducer**. [arXiv:2601.01173](https://arxiv.org/abs/2601.01173), [DOI del preprint 10.48550/arXiv.2601.01173](https://doi.org/10.48550/arXiv.2601.01173). Comprobar título y versión al citar; no se ha verificado una publicación IEEE ni revisión por pares.
- **[R6]** Holler, G., Hrach, D., Fuchs, A., y Brasseur, G. (2009). *Application of a combined capacitive flow velocity and density sensor for the measurement of liquid hydrogen mass flow*. I2MTC — IEEE International Instrumentation and Measurement Technology Conference. [Registro institucional TU Graz](https://tugraz.elsevierpure.com/en/publications/application-of-a-combined-capacitive-flow-velocity-and-density-se/). DOI y páginas pendientes de verificar.
- **[L1]** Gold Araoz, F. (2026). *Estimación de densidad de fluidos mediante orientación angular*. TFM, versión `Rev04`. [Metadatos y alcance heredado](../references/tfm/METADATA.md); [documento conservado](../references/tfm/Densidad_orientacion_angular-F_Gold_Rev04.pdf). Se cita como antecedente local, no como publicación externa revisada por pares.
- **[R7]** Sanchez-Chero, M.; Miranda-Zamora, W. R.; Flores-Mendoza, L. C.; Sanchez-Chero, J. *Development of a PLC/IoT Control System with Real-Time Concentration Monitoring for the Osmotic Dehydration of Fruits*. Autores y afiliación aportados por el usuario: Grupo de Investigación, Desarrollo e Innovación en Industrias Alimentarias-GIDIIA, Universidad Nacional de Frontera, Sullana 20103, Peru. Referencia pendiente de verificación: no se confirmaron año, revista, DOI, registro editorial ni texto completo. La [búsqueda bibliográfica por título](https://search.crossref.org/?q=Development%20of%20a%20PLC%2FIoT%20Control%20System%20with%20Real-Time%20Concentration%20Monitoring%20for%20the%20Osmotic%20Dehydration%20of%20Fruits) es una consulta para localizar el artículo, no una fuente primaria ni evidencia de su contenido.

## 6. Términos y consultas para siguientes iteraciones

### Familias de términos

- **Dispositivo:** `tilt hydrometer`, `tilt densimeter`, `floating hydrometer`, `floating density sensor`, `inclination-based density sensor`, `capsule density sensor`.
- **Magnitud:** `liquid density`, `densitometer`, `density measurement`, `specific gravity sensor`, `specific gravity measurement`.
- **Principio estático:** `buoyancy-based sensor`, `buoyancy`, `hydrostatic equilibrium`, `equilibrium angle`, `center of buoyancy`, `metacentric stability`, `eccentric ballast`.
- **Lectura angular:** `tilt angle`, `inclination`, `orientation`, `accelerometer`, `IMU`.
- **Extensión dinámica:** `floating body dynamics`, `angular response`, `free decay`, `damping`, `added inertia`, `fluid-structure interaction`, `viscosity estimation`.
- **En español:** `densímetro de inclinación`, `densímetro flotante`, `densímetro tipo cápsula`, `sensor de densidad por empuje`, `equilibrio hidrostático`, `orientación angular`.

### Combinaciones iniciales

Adaptar campos, comillas y operadores a cada buscador:

```text
("tilt hydrometer" OR "tilt densimeter")
("hydrometer" OR "specific gravity sensor") AND (tilt OR inclination)
("density sensor" OR densitometer) AND (buoyancy OR "hydrostatic equilibrium")
("floating sensor" OR capsule) AND density AND ("equilibrium angle" OR orientation)
("floating body" AND "center of buoyancy") AND (inclination OR stability)
("floating hydrometer" OR "buoyancy-based sensor") AND (damping OR "free decay")
```

Empezar por títulos y resúmenes, ampliar después a palabras clave y texto completo. Buscar también referencias citadas y trabajos citantes de los candidatos pertinentes. No excluir automáticamente «optical» o «capacitive»: pueden ser métodos de lectura de un mecanismo de empuje, aunque en otros trabajos correspondan a principios distintos.

Para cada nueva entrada, guardar la ficha bibliográfica exportada, DOI/URL, versión y tipo de publicación; anotar el observable de densidad y la sección o ecuación que justifica la clasificación. Priorizar la resolución de [R2] y la consulta de textos completos antes de formular afirmaciones de novedad en la tesis.
