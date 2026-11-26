# Seguimiento: observabilidad, pulsos y control

Registro de trabajo del 25 de noviembre de 2026. Se conservan código, datos
generados, figuras y resultados numéricos para dar continuidad al modelo de la
cápsula. **Las precisiones indicadas son simuladas y no están validadas como
prestaciones de un densímetro ni de un viscosímetro.**

La [decisión de continuar con frecuencia fija](../../../docs/ESTRATEGIA_FRECUENCIA_FIJA.md)
resume el punto de partida a 1,9 Hz y los límites de las comparaciones.

## Evidencia y límites comunes

- Los primeros barridos usan \(I=8·10^{-5}+5·10^{-8}\rho\),
  \(k=5·10^{-7}\rho\), \(c=0,005\sqrt{\mu/0,02}\) y una ganancia de
  actuador hipotética de 0,02. En el rango simulado este modelo está
  sobreamortiguado y no reproduce el modo observado de 1,9 Hz.
- Los ensayos posteriores de pulsos usan otro modelo subamortiguado, con
  \(f_d=1,89991\) Hz y decaimiento \(0,06447\ \mathrm{s}^{-1}\) en el
  punto de referencia. Se suponen dependencias de inercia, rigidez y
  amortiguamiento con \(\rho\) y \(\mu\) que **no se han calibrado**.
- La relación sintética de equilibrio–densidad se ancló localmente a datos del
  TFM en torno a 997,3–1017,1 kg/m³. Su extrapolación a 800–1400 kg/m³ es
  una hipótesis, no una calibración válida para ese rango.
- Los modelos de IMU son aproximaciones; el filtro unipolar de 20 Hz es
  supuesto, no una configuración comprobada del LSM6DSOX. Se simulan sesgos
  constantes, no deriva temporal o térmica. El acelerómetro en movimiento
  también puede medir aceleraciones no gravitatorias que no se incluyen.
- En varios ensayos el generador y el estimador comparten ecuaciones y
  parámetros: esto reduce artificialmente el error (*inverse crime*).
  Los intervalos bootstrap son del error medio dentro de cada simulación,
  agrupados por par de parámetros; no incluyen incertidumbre estructural ni
  equivalen a incertidumbre de una medición individual.
- Los rebotes simulados son impulsos de perturbación inventados, no un modelo
  del líquido identificado con registros. No se ha demostrado que los rebotes
  reales procedan de ondas del recipiente.

## Experimentos conservados

1. **Barrido inicial y excitaciones**: el modelo original de nueve columnas se
   reprodujo en `simulacion_observabilidad.py`, con sus CSV y figuras. En
   `barrido_5000/` se amplió el barrido y compararon frecuencia fija, chirps y
   multiseno. La fórmula de chirp original produce una frecuencia instantánea
   de 0,1 a 3,9 Hz; el chirp corregido integra la fase para barrer 0,1–2 Hz.
   `Td` con excitación activa no representa una relajación libre, y el
   máximo de aceleración angular puede ser sensible a la integración numérica.
2. **IMU y dos etapas**: en el modelo inicial, 1000 pares de prueba con cinco
   realizaciones por par dieron errores medios absolutos de densidad de
   89,62 kg/m³ a frecuencia fija de 1 Hz y 33,11 kg/m³ con chirp lineal;
   se estimaron mediante características y un interpolador entrenado con datos
   sintéticos. Ver `barrido_5000/imu_resultados.json`. En el protocolo
   chirp–pulso–reposo, la primera inversión de viscosidad omitió filtro y
   muestreo y arrojó un MAPE de 53,28 %; al modelar una cadena de sensor
   coincidente, el MAPE bajó a 0,01785 %. Con una ganancia real de actuador
   un 5 % mayor que la asumida, subió a 9,29 %. El filtro de 20 Hz y la
   calibración de equilibrio siguen siendo hipotéticos.
3. **Registros reales**: `ajuste_registros/ajustar_registros.py` procesa los
   25 CSV de `references/tfm/datos_udp.zip`: aceptó 19, excluyó seis por
   huecos mayores de 100 ms y separó 12 para ajustar y 7 para validar.
   Tras filtrar `ang_deg` del acelerómetro entre 1 y 3 Hz, la mediana de la
   frecuencia amortiguada fue 1,89991 Hz; la mediana del decaimiento,
   0,06447 s⁻¹. La mediana de la puntuación de validación fue 0,702 y 6 de
   7 ensayos superaron la predicción nula. Es un análisis exploratorio de
   una señal filtrada, no una identificación de \(G(s)\) ni una prueba de
   que el pico sea una resonancia mecánica.
4. **Frecuencia y filtro**: `barrido_frecuencia_filtro.*` compara
   frecuencias de excitación de 0,05–3 Hz y cortes hipotéticos de 0,5–40 Hz
   con densidad verdadera y filtro conocido en el estimador. No se probó
   excitación de 5 Hz. Las pequeñas diferencias de error no establecen una
   frecuencia óptima del dispositivo real.
5. **Uno o cinco pulsos**: `cinco_pulsos.*` compara el primer pulso con un
   ajuste compartido de cinco pulsos separados 20 s; el sistema no ha vuelto
   completamente al equilibrio entre pulsos. `densidad_un_pulso.*` compara
   equilibrio de primer y segundo orden, respuesta completa y combinación;
   `viscosidad_un_pulso.*` compara envolvente, segundo orden, transición y
   combinación. Los tres métodos comparten la señal y no son independientes.
   Con modelo coincidente, la combinación dio MAPE de viscosidad de 0,50 %;
   con una discrepancia del 5 % en la relación de amortiguamiento, 10,26 %.
   El ajuste de transición dio MAE de densidad de 0,015 kg/m³, pero con una
   rigidez real 0,5 % mayor que la supuesta subió a 8,23 kg/m³.
6. **Rebotes y retroalimentación**: `rebotes_control.*` compara un pulso,
   sinusoidal fija a 1,9 Hz y frecuencia adaptativa desde 1,7 Hz durante
   15 s, con idéntica amplitud máxima y el mismo ruido por caso. Se inyectan
   seis rebotes sintéticos de 0,12 s y el ajuste no los conoce. Con pico
   de rebote del 10 % del actuador, los errores medios absolutos de densidad
   fueron 2,95, 0,12 y 0,40 kg/m³ respectivamente; el MAPE de viscosidad
   fue 31,62 %, 3,29 % y 6,43 %. La señal retroalimentada procede del
   giroscopio; la estimación usa ángulo del acelerómetro simulado y la
   orden de actuación registrada. La frecuencia fija parte con conocimiento
   favorable del modo nominal y la actuación continua acumula más energía
   de mando; la comparación no iguala energía. Con rebotes al 50 %, 45 de
   120 ajustes de pulso llegaron a un límite del optimizador.
7. **Uno y dos modos en espacio de estados**: una simulación sin
   realimentación compara modelos de dos y cuatro estados con una entrada
   fija de 1,9 Hz y señales de acelerómetro y giroscopio simuladas. El
   [detalle del modelo y sus resultados](ajuste_registros/ESPACIO_ESTADOS_UNO_DOS.md)
   distingue el error de predicción de señal de la identificación de
   densidad o viscosidad; no demuestra que existan dos modos reales.

### Por qué no se comparan directamente los errores de densidad

Los 33,11 kg/m³ corresponden al **chirp lineal** del primer modelo; en esa
misma simulación la frecuencia fija de 1 Hz dio 89,62 kg/m³. En cambio, los
0,02 kg/m³ de frecuencia fija sin rebotes corresponden al modelo posterior
subamortiguado a 1,9 Hz, con 40 pares en un rango estrecho
(997,3–1017,1 kg/m³), actuador y ecuaciones conocidos, y ajuste de la señal
completa. El barrido anterior cubría 800–1400 kg/m³ y usaba características
e interpolación. Cambian el modelo, la frecuencia, el rango, la duración y el
estimador: no se puede atribuir la diferencia solo al tipo de excitación ni
considerar que la precisión nueva esté validada.

En la tabla de rebotes, el 31,62 % es el error de **viscosidad** del pulso
con rebotes del 10 %, no un error de densidad en kg/m³.

## Archivos y reproducción

Los archivos CSV, JSON y PNG son instantáneas de las ejecuciones, no datos
experimentales nuevos. El CSV por predicción permite volver a calcular los
errores; los JSON incluyen hipótesis, tamaños y, cuando se calcularon, IC.
Las ejecuciones usan nombres fijos y **sobrescriben** estos archivos: para
conservar los resultados publicados, ejecutar sobre una copia de trabajo.
Las bibliotecas compartidas y binarios se compilan localmente y no se guardan.

Se usaron Python 3.12, NumPy 2.5.5, SciPy 1.18.1, Matplotlib 3.11.2 y
g++ 13.3.0. Desde esta carpeta, en Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
g++ -O3 -std=c++17 -fPIC -shared barrido_5000/ajuste_sensor.cpp -o barrido_5000/ajuste_sensor.so
g++ -O3 -std=c++17 -fPIC -shared ajuste_registros/retroalimentacion.cpp -o ajuste_registros/retroalimentacion.so

OPENBLAS_NUM_THREADS=1 .venv/bin/python ajuste_registros/ajustar_registros.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python ajuste_registros/cinco_pulsos.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python ajuste_registros/densidad_un_pulso.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python ajuste_registros/viscosidad_un_pulso.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python ajuste_registros/rebotes_control.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python ajuste_registros/espacio_estados_uno_dos.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python barrido_5000/barrido_frecuencia_filtro.py
```

El análisis de registros requiere `references/tfm/datos_udp.zip` en la raíz
del repositorio. Para regenerar los ensayos del barrido original:

```bash
g++ -O3 -std=c++17 barrido_5000/comparar_excitaciones.cpp -o barrido_5000/comparar_excitaciones
g++ -O3 -std=c++17 barrido_5000/imu_sim.cpp -o barrido_5000/imu_sim
g++ -O3 -std=c++17 barrido_5000/dos_etapas.cpp -o barrido_5000/dos_etapas
barrido_5000/comparar_excitaciones barrido_5000
.venv/bin/python barrido_5000/analizar_comparacion.py
.venv/bin/python barrido_5000/preparar_imu.py
barrido_5000/imu_sim barrido_5000
.venv/bin/python barrido_5000/analizar_imu.py
barrido_5000/dos_etapas barrido_5000
.venv/bin/python barrido_5000/analizar_dos_etapas.py
.venv/bin/python barrido_5000/ajustar_sensor.py
```

`ajustar_sensor.py` también acepta `--pairs`, `--cutoff`,
`--actuator-factor` y `--tag` para las sensibilidades guardadas. Los datos
de `dataset_observabilidad.csv` en la carpeta principal corresponden al
barrido inicial de 2000 casos; los de `barrido_5000/` son un ensayo distinto.

## Próximo contraste experimental

Registrar entrada y señales crudas con marcas de tiempo, verificar ejes y
filtros reales, medir el sesgo en reposo y controlar la temperatura. Comparar
pulso y excitación continua en los mismos fluidos de referencia, con
restricciones explícitas de amplitud, energía, duración y repetibilidad.
Variar densidad y viscosidad lo más independientemente posible, reservar
fluidos y ensayos para validación, e investigar los rebotes reales antes de
decidir si deben filtrarse, modelarse o usarse en control.
