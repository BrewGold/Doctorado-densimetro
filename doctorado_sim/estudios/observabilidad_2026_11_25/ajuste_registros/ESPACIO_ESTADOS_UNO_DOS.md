# Simulación de uno y dos modos a frecuencia fija

Este ensayo compara la predicción de un modelo de un modo con otro de dos
modos usando una entrada sinusoidal fija de **1,9 Hz**. Es una simulación:
las señales de la IMU y la actuación son sintéticas. No estima densidad ni
viscosidad y no demuestra que la cápsula tenga dos modos físicos.

## Qué significa «dos modos»

Se representan dos osciladores amortiguados independientes, ambos excitados
por la misma orden del actuador. La salida angular es la suma de sus respuestas.
No hay realimentación: la señal de la IMU **no cambia** la entrada del
actuador. Después se comparan las salidas predichas con las simuladas para
evaluar el modelo.

Para cada modo $i$, el estado es $x_i=[q_i,\dot q_i]^T$ y:

$$
\dot{x}_i =
\begin{bmatrix}
0 & 1\\
-(\omega_{d,i}^2+\gamma_i^2) & -2\gamma_i
\end{bmatrix} x_i +
\begin{bmatrix}0\\b_i\end{bmatrix}u(t),
\qquad
u(t)=0{,}001\sin(2\pi\,1{,}9\,t).
$$

Aquí $\omega_{d,i}=2\pi f_{d,i}$ es la frecuencia angular amortiguada,
$\gamma_i$ es el decaimiento y $b_i$ representa una ganancia hipotética.
El modelo de un modo tiene dos estados; el de dos modos tiene cuatro. El
ángulo simulado es $\theta=\sum_i q_i$ y la velocidad angular es su derivada.
La amplitud de la entrada se expresa en unidades arbitrarias, no como una
fuerza o par medidos.

La señal sintética del acelerómetro incluye $g\sin(\theta)$; la del
giroscopio incluye $\dot\theta$. Se añaden sesgos constantes, ruido,
cuantización y un filtro idealizado de 20 Hz. El sensor genera datos a 104 Hz
y el receptor lee a 100 Hz mediante retención de la última muestra. El
ajuste utiliza conjuntamente ambas señales, con aproximación lineal
$g\theta$ para el acelerómetro, y estima los sesgos, parámetros modales,
ganancias y condiciones iniciales. **El filtro es supuesto, no una
configuración verificada de la IMU.**

## Diseño y resultados

Cada ensayo dura 30 s: se ajustan los primeros 15 s y se predicen los últimos
15 s, manteniendo la entrada conocida. Hay 12 realizaciones por escenario,
con parámetros modales, ruido y sesgos generados de forma aleatoria. En el
escenario de dos modos la frecuencia amortiguada del segundo se supone entre
1,81 y 1,85 Hz y su ganancia de entrada es el 35 % de la del primero.

El error indicado es la **mediana del RMSE de la predicción de señal**, en la
ventana de 15–30 s, dividido por el RMS de la señal verdadera centrada en
esa ventana. La señal verdadera sin ruido solo se conoce en simulación;
se incluye el error al estimar el sesgo. No es un error de densidad ni de
viscosidad.

| Planta simulada | Modelo ajustado | Acelerómetro | Giroscopio |
|---|---|---:|---:|
| Un modo | Un modo | 0,073 % | 0,019 % |
| Un modo | Dos modos | 0,078 % | 0,023 % |
| Dos modos | Un modo | 12,575 % | 12,664 % |
| Dos modos | Dos modos | 0,114 % | 0,101 % |

Si la planta simulada tiene solo un modo, añadir otro no mejora la mediana;
en cuatro de las 12 realizaciones algún parámetro modal del ajuste llegó a
un límite permitido. Si la planta tiene dos modos, el modelo de dos reproduce
mejor los datos en esta prueba, pero **usa la misma estructura que el
generador**, por lo que su precisión es optimista.

Se probó además una aceleración tangencial hipotética correspondiente a un
brazo de 3 cm, incluida en el acelerómetro simulado pero omitida en el
estimador. En ese escenario de dos modos, el error mediano del acelerómetro
fue 66,1 % con un modo y 76,8 % con dos; para el giroscopio fue 9,52 % y
0,30 %. El brazo y la geometría son supuestos: las cifras muestran
**sensibilidad al error de modelo**, no una medición de ese efecto en la
cápsula. Los escenarios se generan por separado y sus realizaciones no son
comparaciones emparejadas.

## Archivos y ejecución

- [`espacio_estados_uno_dos.py`](espacio_estados_uno_dos.py): simulación,
  ajuste y gráfico.
- [`espacio_estados_uno_dos_resultados.json`](espacio_estados_uno_dos_resultados.json):
  parámetros, restricciones, resumen y resultados por realización.
- [`espacio_estados_uno_dos_resultados.csv`](espacio_estados_uno_dos_resultados.csv):
  resultados por escenario y ajuste.
- [`espacio_estados_uno_dos.png`](espacio_estados_uno_dos.png): ejemplo de
  señales y predicciones; la línea vertical separa ajuste y predicción.

Con el entorno preparado según el [README del estudio](../README.md), desde
la carpeta `observabilidad_2026_11_25`:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python ajuste_registros/espacio_estados_uno_dos.py
```

La ejecución sobrescribe el CSV, el JSON y la figura; usar una copia si se
desea conservar la instantánea publicada. La semilla es 20261125.

## Qué falta comprobar

El segundo modo, sus ganancias, la entrada real del actuador y la posición
efectiva del sensor no están identificados. Es necesario contrastar las
predicciones con señales crudas y actuación registrada, validar en ensayos
independientes y examinar sensibilidad a excitación, filtro, aceleraciones
traslacionales y acoplamientos. Un buen ajuste de estados o de señales no
demuestra por sí mismo que densidad y viscosidad sean identificables.
