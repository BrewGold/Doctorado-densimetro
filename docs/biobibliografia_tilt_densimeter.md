# Biobibliografía y estado del arte del densímetro tipo cápsula

## 1. Objetivo y alcance

Consolidar las referencias discutidas y facilitar la continuación de la investigación de una cápsula flotante que estima densidad mediante su orientación. Es una **matriz de trabajo, no una revisión sistemática exhaustiva**. Se distingue entre el principio de medición, la dinámica del sensor y la disponibilidad temporal de sus lecturas.

En la etapa estática planteada por el usuario se busca identificar la densidad a partir del ángulo medido, la masa, la geometría y los centros de gravedad y empuje. No se necesita suponer una densidad inicial: se imponen simultáneamente los balances de fuerzas y momentos. El volumen sumergido y su primer momento deben considerar el cilindro y las dos semiesferas, no solo el cilindro. Esto no equivale a usar el volumen total de la cápsula cuando está parcialmente sumergida.

La extensión dinámica estudiaría el movimiento angular, la inercia, el amortiguamiento y la respuesta transitoria. Para el contexto del repositorio, véanse la [geometría de la cápsula](../doctorado_sim/docs/CAPSULE_GEOMETRY.md), el [marco teórico](../doctorado_sim/docs/THEORETICAL_FRAMEWORK.md) y el [mapa de trazabilidad del TFM](TRACEABILITY_MAP.md). Esta revisión no modifica ni valida sus modelos.

## 2. Problema de búsqueda y nota metodológica

Según la exploración reportada por el usuario, buscar «tilt densimeter» produce pocos resultados directos y bastante ruido en IEEE. No debe tratarse como un término académico estandarizado ni como la única denominación del dispositivo. *Hydrometer*, *densitometer*, *density sensor* y *specific gravity sensor* abarcan tecnologías distintas: compartir la magnitud medida no implica compartir el mecanismo.

**Es necesario buscar por principio físico**, combinando flotación, equilibrio hidrostático, inclinación y orientación. La ausencia de coincidencias con una expresión exacta no demuestra ausencia de antecedentes ni novedad científica. Conviene ampliar IEEE Xplore con otras fuentes, como Crossref, Google Scholar, Web of Science, Scopus y repositorios institucionales; registrar fecha, consulta, filtros y motivo de inclusión o exclusión.

La evidencia de cada entrada se indica por separado. Se leyó íntegramente la disertación de PUC-Rio conservada en `docs/` y se cotejó su portada, ficha catalográfica, modelo y bibliografía. Para Baron y Bryant se consultaron los registros primarios de solicitud y concesión enlazados, incluidos sus datos bibliográficos, resumen y descripción. La disertación cita ambos documentos patentarios (p. 128). Las otras referencias externas previamente propuestas se apoyan en fichas o resúmenes indexados, no en una lectura íntegra; por ello, los campos pendientes y los candidatos no identificados no se presentan como referencias confirmadas.

## 3. Criterios de clasificación

### Enfoque: equilibrio frente a dinámica

- **Equilibrio:** la densidad se obtiene de una relación estática de fuerzas, momentos, empuje o presión hidrostática. Una lectura continua o electrónica no cambia esta clasificación.
- **Dinámico:** la medición utiliza oscilaciones, propagación acústica, desplazamientos temporales o una respuesta transitoria. Se especifica si es dinámica resonante, acústica, de flujo o de cuerpo flotante: no son intercambiables.
- **Mixto:** el trabajo utiliza efectivamente tanto un balance estático como información dinámica. No basta con medir dos magnitudes o incorporar un circuito oscilador auxiliar.
- **No determinado:** la evidencia disponible no permite decidir entre equilibrio y dinámica; no se infiere a partir del título, de la lectura continua ni de la validación experimental.
- **No aplica:** el observable de densidad es óptico o dieléctrico y no utiliza equilibrio ni dinámica mecánica.

«Real time», «monitorización» o «medición en flujo» no prueban por sí solos que se modele la dinámica del sensor. Tampoco una vibración MEMS demuestra un estudio del movimiento angular de una cápsula.

### Relación con «tilt densimeter»

En este documento, la expresión designa funcionalmente un **cuerpo flotante cuya inclinación permite inferir densidad o gravedad específica**, no cualquier inclinómetro ni exclusivamente un producto comercial.

- **Directa:** hay evidencia explícita de densidad estimada mediante la orientación de un cuerpo flotante.
- **Parcial:** comparte un fundamento físico relevante, como hidrostática o empuje, pero no demuestra medición por inclinación. Las afinidades meramente temáticas se indican expresamente.
- **No:** mide densidad mediante otro principio y no se encontró evidencia de relación con inclinación de flotación.

Estas etiquetas valoran pertinencia respecto de la cápsula, no calidad científica. Las clasificaciones provisionales requieren revisión del texto completo; no deben interpretarse como exclusiones definitivas.

## 4. Tabla bibliográfica de trabajo

Los identificadores [R1], [R4]–[R6], [H1] y [H2] remiten a referencias del corpus de trabajo descritas abajo. [C1] y [C2] se mantienen aparte porque no se pudo confirmar la identidad bibliográfica exacta.

| Referencia y enlace (estado de verificación indicado) | Principio de medición | Equilibrio / dinámica | Relación con tilt densimeter | Evidencia y pertinencia para una cápsula flotante inclinada |
|---|---|---|---|---|
| [H1] Noah Ananda Baron y Tyler Michelson Bryant, *Free Floating Tilt Hydrometer*. Solicitud de patente [US20140260607A1](https://patents.google.com/patent/US20140260607A1/en), concedida como [US9234828B2](https://patents.google.com/patent/US9234828B2/en). | Flotador libre cuya inclinación, medida con un acelerómetro, permite inferir gravedad específica. | Equilibrio: la descripción utiliza la orientación estable del flotador; no presenta un modelo dinámico del movimiento transitorio. | Directa | El título, inventores y mecanismo se verifican en el registro primario, resumen y descripción. La solicitud se presentó en 2013 y se publicó en 2014; la concesión es de 2016. La disertación [H2] cita ambos documentos en p. 128. Antecedente directo para comparar geometría, calibración y lectura angular, sin presumir equivalencia geométrica con la cápsula del proyecto. |
| [H2] R. A. da Paixão (2022), *Modelagem, validação experimental de protótipo e caracterização metrológica de densímetros que utilizam o princípio do deslocamento do centro de carena*. Disertación de maestría, PUC-Rio. [PDF del repositorio Maxwell](https://www.maxwell.vrac.puc-rio.br/59871/59871.PDF) y [copia del repositorio](Modelagem,%20valida%C3%A7%C3%A3o%20experimental%20de%20prot%C3%B3tipo.pdf). | Equilibrio hidrostático: volumen desplazado, centro de carena y orientación de un densímetro flotante. Modela una semiesfera y un tronco de cilindro; calcula sus volúmenes y centroides, y combina estos para hallar el centro de carena. | Equilibrio | Directa | Portada y ficha catalográfica (preliminares, pp. 1–3) confirman título, autor, 2022 y PUC-Rio. Las pp. 41–47 desarrollan geometría, centro de gravedad/carena y equilibrio de fuerzas y momentos; pp. 60–68 aplican el modelo. En p. 44, la integración del tronco de cilindro corrige el término del centroide a \(C_z=h/2+R^2\tan^2\theta/(8h)\), no \(2h\). La tesis valida experimentalmente un prototipo, pero las oscilaciones iniciales y lecturas temporales no constituyen por sí solas un modelo dinámico del sensor. Es especialmente pertinente para integrar geometría sumergida, empuje y ángulo en la cápsula. |
| [R1] *Optical-Type Hydrometer for Lead-Acid Batteries…* (1987; metadatos completos por verificar). [IEEE Xplore](https://ieeexplore.ieee.org/document/4794631) | Refractometría: índice de refracción del electrolito y gravedad específica. | No aplica | No | El resumen indexado no describe un flotador. No aporta evidencia de equilibrio angular ni dinámica de cápsula. |
| [R4] T. Manzaneque et al. (2014), *Density-viscosity sensor based on piezoelectric MEMS resonator…*. [IEEE Xplore](https://ieeexplore.ieee.org/document/6984978) | Resonador MEMS piezoeléctrico y circuito oscilador. | Dinámico: resonante | No | Alternativa de transducción; no es un modelo de orientación hidrostática ni del transitorio de un flotador. Lista completa de autores por verificar. |
| [R5] X. Fu, L. Lou y H. Ren (2026), *A Liquid Density Sensor Based on AlN…*. [arXiv:2601.01173](https://arxiv.org/abs/2601.01173) | Transmisión/recepción ultrasónica y amplitud recibida. | Dinámico: acústico | No | El registro preprint presenta una variante de título y no confirma publicación editorial posterior. No confundir con inclinación ni con desplazamiento de frecuencia resonante. |
| [R6] G. Holler, D. Hrach, A. Fuchs y G. Brasseur (2009), *Application of a combined capacitive flow velocity and density sensor…*. [Registro institucional TU Graz](https://tugraz.elsevierpure.com/en/publications/application-of-a-combined-capacitive-flow-velocity-and-density-se/) | Densidad capacitiva y seguimiento de burbujas para velocidad/caudal másico de hidrógeno líquido. | Dinámico para velocidad/caudal; no aplica para densidad capacitiva | No | «Combinado» no justifica clasificarlo como mixto equilibrio–dinámico. No se identificó equilibrio mecánico. |
| [L1] F. Gold Araoz (2026), *Estimación de densidad de fluidos mediante orientación angular*. TFM, versión Rev04. [Metadatos](../references/tfm/METADATA.md) y [documento](../references/tfm/Densidad_orientacion_angular-F_Gold_Rev04.pdf). | Densidad inferida desde orientación de equilibrio, según metadatos heredados. | Equilibrio (alcance heredado) | Directa | Antecedente local pertinente; esta clasificación no presupone una lectura íntegra del PDF ni clasifica su contenido dinámico. |

### Lectura para el estado del arte

La patente [H1] y la disertación [H2] son antecedentes directos que deben formar parte del estado del arte. La tesis de PUC-Rio cita ambas publicaciones patentarias de Baron y Bryant en su bibliografía (p. 128) y, en pp. 41–47, desarrolla un modelo hidrostático del densímetro flotante. Esto descarta cualquier formulación previa que sugiera que no se encontraron antecedentes directos; tampoco permite concluir novedad o inexistencia de otros trabajos. La validación experimental de [H2] no cambia el modelo de equilibrio a uno dinámico. [R4] y [R5] son ejemplos de mecanismos dinámicos diferentes; [R6] permite distinguir dinámica de flujo de dinámica del sensor. [C1] y [C2] siguen sin confirmar.

El siguiente paso prioritario es buscar trabajos que relacionen explícitamente **densidad–ángulo de equilibrio–geometría sumergida–centro de empuje**, antes de pasar a comparaciones sobre amortiguamiento o identificación dinámica.

## 5. Referencias y trazabilidad

- **[H1]** Baron, Noah Ananda, y Bryant, Tyler Michelson. (2014). *Free Floating Tilt Hydrometer*. Solicitud estadounidense publicada **US20140260607A1** (presentada el 15 de marzo de 2013 y publicada el 18 de septiembre de 2014), concedida como patente **US9234828B2** el 12 de enero de 2016. Los registros primarios confirman título e inventores y describen un flotador cuya inclinación medida se usa para estimar gravedad específica; el modelo de medición es de equilibrio y no se encontró un modelo transitorio. La bibliografía de [H2], p. 128, también consigna ambas publicaciones. [Solicitud publicada: resumen y descripción](https://patents.google.com/patent/US20140260607A1/en); [patente concedida](https://patents.google.com/patent/US9234828B2/en). Se trata de documentos patentarios, no de artículos académicos.
- **[H2]** Paixão, R. A. da (2022). *Modelagem, validação experimental de protótipo e caracterização metrológica de densímetros que utilizam o princípio do deslocamento do centro de carena*. Disertación de maestría, Programa de Pós-Graduação em Metrologia, Pontifícia Universidade Católica do Rio de Janeiro (PUC-Rio). [Repositorio institucional Maxwell](https://www.maxwell.vrac.puc-rio.br/59871/59871.PDF); [copia local](Modelagem,%20valida%C3%A7%C3%A3o%20experimental%20de%20prot%C3%B3tipo.pdf). Autoría, título, año e institución verificados en portada/ficha catalográfica (pp. 1–3); modelo geométrico/hidrostático en pp. 41–47 y 60–68; referencias a Baron y Bryant en p. 128.
- **[R4]** Manzaneque, T., et al. (2014). *Density-viscosity sensor based on piezoelectric MEMS resonator and oscillator circuit*. IEEE SENSORS 2014. [IEEE Xplore, registro 6984978](https://ieeexplore.ieee.org/document/6984978). Lista completa de autores y DOI pendientes. No confundir con el artículo distinto *Piezoelectric MEMS resonator-based oscillator for density and viscosity sensing*, cuyo DOI es [10.1016/j.sna.2014.10.002](https://doi.org/10.1016/j.sna.2014.10.002); ese DOI no se atribuye aquí al trabajo de congreso.
- **[R5]** Fu, X., Lou, L., y Ren, H. (2026). El registro localizado presenta *A Liquid Density Sensor Based on AlN Piezoelectric Micromachined Ultrasonic Transmitter Insensitive to Liquid Viscosity*, mientras que la consulta usa **Transducer**. [arXiv:2601.01173](https://arxiv.org/abs/2601.01173), [DOI del preprint 10.48550/arXiv.2601.01173](https://doi.org/10.48550/arXiv.2601.01173). Comprobar título y versión al citar; no se ha verificado una publicación IEEE ni revisión por pares.
- **[R6]** Holler, G., Hrach, D., Fuchs, A., y Brasseur, G. (2009). *Application of a combined capacitive flow velocity and density sensor for the measurement of liquid hydrogen mass flow*. I2MTC — IEEE International Instrumentation and Measurement Technology Conference. [Registro institucional TU Graz](https://tugraz.elsevierpure.com/en/publications/application-of-a-combined-capacitive-flow-velocity-and-density-se/). DOI y páginas pendientes de verificar.
- **[L1]** Gold Araoz, F. (2026). *Estimación de densidad de fluidos mediante orientación angular*. TFM, versión `Rev04`. [Metadatos y alcance heredado](../references/tfm/METADATA.md); [documento conservado](../references/tfm/Densidad_orientacion_angular-F_Gold_Rev04.pdf). Se cita como antecedente local, no como publicación externa revisada por pares.

### Candidatos bibliográficos pendientes (no confirmados)

- **[C1]** *Plastic Optical Fiber Sensor for Real Time Density Measurements in a Liquid Medium* (2007, datos previamente sugeridos). No se confirmó un registro exacto. [IEEE Xplore 4258431](https://ieeexplore.ieee.org/document/4258431) es solo una pista: su título indexado comienza *Plastic Optical Fiber Sensor for Real Time Density Measurements in Wine…* y no se presume que sea la misma obra. Autoría, año, publicación, principio y clasificación quedan pendientes. No trasladar a este candidato datos del artículo distinto de 2009 *A novel approach to the sensing of liquid density using a plastic…*, [DOI 10.1088/0031-9120/44/1/009](https://doi.org/10.1088/0031-9120/44/1/009).
- **[C2]** *High accuracy pressure type liquid level measurement system capable of measuring density* (2015, título/año previamente sugeridos). [IEEE Xplore 7372925](https://ieeexplore.ieee.org/document/7372925) se conserva como pista, no como referencia confirmada. Autoría, fecha editorial, tipo de publicación, principio efectivo y clasificación están pendientes de cotejo en la fuente primaria; no inferir equilibrio hidrostático solo a partir del título.

## 6. Términos y consultas para siguientes iteraciones

### Familias de términos

- **Dispositivo:** `free floating tilt hydrometer`, `tilt hydrometer`, `tilt densimeter`, `floating hydrometer`, `floating density sensor`, `inclination-based density sensor`, `capsule density sensor`, `Baron Bryant`.
- **Magnitud:** `liquid density`, `densitometer`, `density measurement`, `specific gravity sensor`, `specific gravity measurement`.
- **Principio estático:** `buoyancy-based sensor`, `buoyancy`, `hydrostatic equilibrium`, `equilibrium angle`, `center of buoyancy`, `metacentric stability`, `eccentric ballast`.
- **Lectura angular:** `tilt angle`, `inclination`, `orientation`, `accelerometer`, `IMU`.
- **Extensión dinámica:** `floating body dynamics`, `angular response`, `free decay`, `damping`, `added inertia`, `fluid-structure interaction`, `viscosity estimation`.
- **En español/portugués:** `densímetro de inclinação`, `densímetro de inclinación`, `densímetro flutuante`, `densímetro flotante`, `densímetro tipo cápsula`, `sensor de densidad por empuje`, `equilibrio hidrostático`, `orientación angular`, `PUC-Rio`, `Modelagem, validação experimental de protótipo e caracterização metrológica de densímetros que utilizam o princípio do deslocamento do centro de carena`.

### Combinaciones iniciales

Adaptar campos, comillas y operadores a cada buscador:

```text
("tilt hydrometer" OR "tilt densimeter")
("free floating tilt hydrometer" OR ("Baron" AND "Bryant"))
("hydrometer" OR "specific gravity sensor") AND (tilt OR inclination)
("density sensor" OR densitometer) AND (buoyancy OR "hydrostatic equilibrium")
("floating sensor" OR capsule) AND density AND ("equilibrium angle" OR orientation)
("floating body" AND "center of buoyancy") AND (inclination OR stability)
("floating hydrometer" OR "buoyancy-based sensor") AND (damping OR "free decay")
("densímetro de inclinação" OR "densímetro flutuante")
("PUC-Rio" AND "Modelagem, validação experimental de protótipo")
```

Empezar por títulos y resúmenes, ampliar después a palabras clave y texto completo. Buscar también referencias citadas y trabajos citantes de los candidatos pertinentes. No excluir automáticamente «optical» o «capacitive»: pueden ser métodos de lectura de un mecanismo de empuje, aunque en otros trabajos correspondan a principios distintos.

Para cada nueva entrada, guardar la ficha bibliográfica exportada, DOI/URL, versión y tipo de publicación; anotar el observable de densidad y la sección o ecuación que justifica la clasificación. Priorizar la resolución de [C1] y [C2] y la consulta de textos completos antes de formular afirmaciones de novedad en la tesis.
