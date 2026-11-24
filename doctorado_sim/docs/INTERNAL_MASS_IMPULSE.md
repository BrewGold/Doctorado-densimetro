# Impulso mediante masa movil interna

## Objetivo y alcance

Se comparan dos movimientos de una misma masa interna situada cerca de la punta lastrada: uno paralelo al eje longitudinal y otro vertical **en la posicion inicial de equilibrio**. Ambos usan el mismo recorrido y duracion; la direccion del movimiento permanece fija respecto a la capsula y gira con ella. Por tanto, el segundo recorrido no permanece exactamente vertical durante la oscilacion y tampoco es perpendicular al eje longitudinal inicialmente.

La inclinacion geometrica de **34,91 grados sobre la horizontal** es la estimacion hipotetica explicada en [ondas en paredes circulares](CIRCULAR_WALL_WAVES.md), no una medida directa del angulo del TFM. El modelo representa desplazamientos angulares respecto a ese equilibrio, no convierte los grados en `ang_deg` de la IMU. El punto de reposo de la masa movil se situa a 60 mm del centro de masa supuesto de la carcasa, hacia la punta. La carcasa agrega la masa fija, incluido el lastre: no se calcula su distribucion interna.

La simulacion **no identifica ni predice el actuador real**. La trayectoria de la masa se impone idealmente; no hay modelo de solenoide, fuerzas de motor, topes, consumo, campo magnetico ni control. La geometria dibujada es esquematica, no un plano ni una comprobacion de espacio.

## Hipotesis numericas

| Parametro | Valor | Estado |
|---|---:|---|
| Inclinacion de equilibrio | 34,91 grados | Inferida bajo hipotesis, no medida |
| Masa de carcasa y elementos fijos | 45 g | Ilustrativa |
| Masa movil | 5 g | Ilustrativa |
| Inercia de la carcasa respecto a su centro de masas | 1,2 × 10⁻⁴ kg m² | Ilustrativa |
| Posicion inicial de masa movil | −60 mm sobre eje de capsula | Ilustrativa |
| Recorrido de ida | 4 mm | Ilustrativo |
| Tiempo de ida y vuelta | 0,25 s | Ilustrativo |
| Frecuencia angular de referencia de la rigidez | 1,9 Hz | Inspirada por pico observado; no es una identificacion del modelo acoplado |
| Amortiguamiento angular | 0,15 s⁻¹ | Ilustrativo |
| Rigidez vertical efectiva | 8 N/m | Ilustrativa |
| Amortiguamiento traslacional | 0,08 N s/m por eje | Ilustrativo |

La frecuencia real del sistema con gravedad y traslacion acopladas no tiene por que ser 1,9 Hz. No se modelan el oleaje, el arrastre no lineal, la geometria sumergida, la inercia añadida ni el ruido de la IMU. Las fuerzas y rigideces efectivas se usan solo como aproximacion local alrededor del equilibrio; los resultados no sirven para dimensionar el actuador.

## Modelo

Se usa un sistema plano: posicion horizontal y vertical del centro de masas de la carcasa, y giro angular. La masa movil tiene posicion relativa `r = R(beta + theta)(r0 + q d)`, donde `d` es un vector fijo en la carcasa. La trayectoria prescrita `q = A(1 - cos(2 pi t/T))/2` para `0 <= t < T` vuelve al origen con velocidad nula; despues `q = 0`. La aceleracion presenta saltos en los extremos y el accionamiento real debe verificarse por separado.

Las ecuaciones usan el balance de fuerzas y momentos del sistema carcasa-masa, con la reaccion y los terminos cineticos debidos a la masa movil. Una fuerza vertical constante compensa el peso total en reposo; el momento hidrostatico constante compensa el torque gravitatorio de la masa movil en la postura inicial. Se añaden rigidez y amortiguamiento efectivos lineales. El torque gravitatorio adicional asociado al movimiento de la masa se calcula explicitamente, evitando atribuir todo el efecto a un impulso angular.

La masa que se desplaza cambia el centro de masas y la reaccion depende de la direccion, el brazo, la gravedad, el fluido y la trayectoria de ida y regreso. Por ello, un movimiento axial puede producir giro mediante el acoplamiento con gravedad y fluido, aunque no deba suponerse que una fuerza axial interna produce siempre un torque directo. Tampoco se supone que exista una fuerza externa aplicada por el actuador.

## Ejecucion y salida

En MATLAB u Octave, desde la raiz del repositorio:

```matlab
addpath('doctorado_sim/sim/scenarios');
run_internal_mass();
addpath('doctorado_sim/tests');
test_internal_mass();
```

Los resultados aparecen en `doctorado_sim/results/internal_mass/`: `internal_mass.csv`, `pulse_comparison.csv`, `internal_mass.png`, `internal_mass.pdf` y `geometry.png`. Los CSV se regeneran y no se versionan; las figuras son referencia. Se puede pasar otro directorio a `run_internal_mass`. La figura angular compara desviaciones respecto al equilibrio, mientras que los desplazamientos corresponden al centro de masas de la carcasa.

## Comparacion despues del impulso

Para aproximar la pregunta de sustituir la liberacion manual, se mide el maximo absoluto de la desviacion angular en los **dos segundos posteriores al retorno de la masa**. Con los parametros de la tabla anterior, salvo la duracion indicada:

| Duracion ida y vuelta | Longitudinal | Vertical en reposo |
|---|---:|---:|
| 0,10 s | 0,254° | 0,215° |
| 0,25 s | 0,558° | 0,477° |
| 0,50 s | 0,651° | 0,584° |

En esta seleccion de parametros el recorrido longitudinal excita algo mas el giro, pero **no se puede concluir que sea mejor para la capsula real**. La comparacion depende especialmente de la accion de la gravedad sobre la masa desplazada y del acoplamiento con la traslacion. Por ejemplo, con la misma configuracion de 0,25 s y sin gravedad, el modelo da aproximadamente 0,127° longitudinal frente a 0,476° vertical. Las fuerzas y rigideces no estan identificadas; el perfil impuesto de ida y vuelta no demuestra que un actuador electromagnetico pueda reproducirlo.

La liberacion manual del TFM a unos 30° es una desviacion inicial, no un impulso calibrado. En este ejemplo las oscilaciones son mucho menores; escalar linealmente estos resultados a 30° no estaria justificado con un modelo local. Una prueba practica requiere conocer masa, carrera, tiempo de ida y retorno, posicion y alimentacion del actuador, y comparar con registros reales en el mismo fluido. Puede ser suficiente una perturbacion menor si permite identificar el modo con buena relacion señal/ruido.

El ensayo conserva el momento lineal y angular en el caso aislado sin gravedad ni fuerzas externas; tambien verifica reposo, retorno de la masa y reaccion traslacional sin giro para una trayectoria que atraviesa el centro de masas.
