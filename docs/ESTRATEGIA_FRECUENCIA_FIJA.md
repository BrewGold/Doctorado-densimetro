# Estrategia de excitación a frecuencia fija

## Decisión de trabajo

Se continuará con **excitación sinusoidal a frecuencia fija** como estrategia
principal para estudiar la estimación conjunta de densidad y viscosidad. La
frecuencia inicial de referencia es **1,9 Hz**, porque está cerca de un modo
observado en los registros y se utilizó en la comparación sintética más
reciente. Es un punto de partida para ensayos, no una frecuencia óptima ni
una resonancia mecánica demostradas.

El pulso único y la frecuencia adaptativa se conservan como comparadores.
Esta decisión no implica que deban descartarse si nuevos ensayos muestran
ventajas, ni que la actuación continua sea siempre superior.

## Resultados que motivan la elección

En la [simulación con rebotes](../doctorado_sim/estudios/observabilidad_2026_11_25/ajuste_registros/rebotes_control_resultados.json)
se compararon un pulso, una sinusoidal fija y un seguidor de frecuencia:
40 pares sintéticos de densidad–viscosidad, tres realizaciones de ruido por
par, 15 s por ensayo y la misma amplitud máxima de mando.

| Perturbación hipotética | Frecuencia fija a 1,9 Hz | Error medio de densidad | Error medio relativo de viscosidad |
|---|---|---:|---:|
| Sin rebotes | Modelo coincidente | 0,017 kg/m³ | 3,04 % |
| Rebotes con pico del 10 % del mando | Modelo coincidente | 0,118 kg/m³ | 3,29 % |
| Rebotes con pico del 50 % del mando | Modelo coincidente | 0,590 kg/m³ | 7,89 % |

El error de densidad es el **MAE**, promedio de los valores absolutos en
kg/m³; el de viscosidad es el **MAPE**, promedio del error relativo absoluto
en porcentaje. Los intervalos bootstrap están en el JSON y describen la
variación del error medio entre los pares sintéticos; no son intervalos de
una medición individual ni incluyen incertidumbre del modelo.

Estos resultados son **alentadores como prueba de concepto**, pero no son
exactitudes experimentales. El generador y el estimador comparten la dinámica
principal y la relación hipotética entre frecuencia, densidad y viscosidad;
la sensibilidad real a la densidad todavía no está identificada. Los rebotes
son seis impulsos de perturbación supuestos, no ruido medido en el líquido.
El sensor usa un filtro hipotético de 20 Hz y omite aceleraciones
traslacionales y deriva temporal. No se conoce aún la respuesta real del
actuador bajo carga.

La frecuencia fija empezó directamente cerca del modo nominal; el método
adaptativo partió de 1,7 Hz. Aunque el pico de mando fue igual, la sinusoidal
actuó durante mucho más tiempo que el pulso: la integral del mando al cuadrado
fue aproximadamente **37,5 veces mayor**, un indicador de esfuerzo de mando,
no una medición de energía eléctrica. Por tanto, la comparación no iguala
energía ni demuestra una ventaja universal de la frecuencia fija.

## Cifras que no deben confundirse

- En un barrido **anterior**, con otro modelo sobreamortiguado, densidades de
  800–1400 kg/m³ y un estimador por características, la frecuencia fija de
  **1 Hz** dio MAE de densidad **89,62 kg/m³**. El **chirp lineal** dio
  **33,11 kg/m³**, no la frecuencia fija. Véase
  [`imu_resultados.json`](../doctorado_sim/estudios/observabilidad_2026_11_25/barrido_5000/imu_resultados.json).
- La comparación reciente usa otro modelo con modo próximo a 1,9 Hz,
  densidades de 997,3–1017,1 kg/m³, viscosidades de 0,005–0,05 Pa·s y
  ajuste de la señal completa con la orden conocida. No se pueden explicar
  las diferencias de error solo por cambiar el tipo de excitación.
- El **0,50 %** de viscosidad se obtuvo en otra simulación: un **pulso**
  con combinación de estimadores calibrados en datos sintéticos. No es el
  resultado de la sinusoidal fija, cuyo valor sin rebotes fue 3,04 %.
- El **31,62 %** de la tabla de rebotes es error de viscosidad del pulso,
  no densidad en kg/m³. Esos valores no son especificaciones del dispositivo.
- El valor 0,005–0,05 Pa·s equivale a 5–50 mPa·s; no incluye agua cercana
  a 20 °C, de alrededor de 1 mPa·s.

## Protocolo propuesto para validar

1. Registrar el montaje completo, propiedades de referencia de cada fluido,
   temperatura y su estabilidad; comprobar el tiempo de calentamiento del
   sensor. Mantener el montaje, recipiente y nivel reproducibles.
2. Verificar los ejes, rangos, frecuencia de muestreo efectiva y filtros
   configurados del LSM6DSOX; medir el sesgo del giroscopio en reposo y
   conservar las señales crudas con marcas de tiempo.
3. Ensayar inicialmente a 1,9 Hz, registrando la orden y, cuando sea posible,
   una medida independiente de la actuación real. Definir amplitud,
   duración, límites de movimiento, saturación y repetibilidad. No asumir
   que la orden eléctrica equivale a un par conocido.
4. Usar fluidos de referencia que permitan explorar por separado, en lo
   posible, cambios de densidad y viscosidad; incluir agua y ampliar el rango
   de viscosidades. Reservar fluidos y repeticiones independientes para
   validación y calcular MAE, sesgo, dispersión e incertidumbre.
5. Comparar métodos con límites de amplitud, tiempo y energía explícitos;
   analizar señales y residuos para detectar rebotes y sesgos sistemáticos.
   Registrar antes y después un tramo sin actuación para estudiar el
   equilibrio, que no debe confundirse con una respuesta forzada.

Una única sinusoide en régimen permanente no identifica por sí sola una
función de transferencia de segundo orden completa y desconocida. El arranque
transitorio puede aportar información adicional si se modela correctamente;
si la información no basta, habrá que incorporar ensayos independientes
adicionales sin confundirlos con el modo operativo de frecuencia fija.

## Trazabilidad

El [seguimiento completo](../doctorado_sim/estudios/observabilidad_2026_11_25/README.md)
conserva código, predicciones, figuras, configuraciones y límites de todos los
experimentos. Los CSV y JSON son resultados sintéticos, salvo el análisis
identificado explícitamente como procedente de los registros del TFM.
