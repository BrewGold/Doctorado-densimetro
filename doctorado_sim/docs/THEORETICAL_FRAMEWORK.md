# Marco teórico

## 1. Introducción

El problema central de la investigación es la modelización y simulación de una cápsula desbalanceada instrumentada con IMU, cuyo comportamiento está influido por la interacción con un fluido. El sistema se comporta como un proceso dinámico acoplado en el que la orientación de la cápsula, la distribución de masas y las propiedades del fluido determinan la respuesta observada por los sensores inerciales.

La investigación parte del principio de que la cápsula puede actuar como un transductor físico de propiedades del medio, aprovechando la relación entre equilibrio hidrostático, orientación, densidad y amortiguamiento. El objetivo es no solo describir el fenómeno, sino también reproducirlo en simulación, estimar parámetros a partir de medidas del sistema y, en un nivel más avanzado, diseñar estrategias de control y validación experimental.

## 2. Fundamentos físicos

### 2.1 Equilibrio de fuerzas

El sistema está sometido a las fuerzas principales:

- peso: F_g = m g
- empuje hidrostático: F_b = rho_f V g
- fuerza de arrastre: F_d
- fuerza de tensión superficial: F_sigma (si el sistema opera en interfaz o bajo condiciones capilares relevantes)

En equilibrio, la orientación de la cápsula depende de la relación entre el momento gravitacional y el momento del empuje. El desbalance de masa genera un momento neto que introduce una inclinación relativa al eje de equilibrio.

### 2.2 Momento de fuerza

El comportamiento angular puede describirse con una ecuación del tipo:

- I theta_ddot + c(theta_dot, mu) + k(theta, rho, sigma) = tau_ext

Donde:

- I es la inercia efectiva
- c(theta_dot, mu) representa el amortiguamiento viscoso y no lineal
- k(theta, rho, sigma) representa la fuerza restauradora asociados a empuje y equilibrio hidrostático
- tau_ext es una perturbación externa o fuerza de excitación

### 2.3 Dependencia con la densidad

La densidad del fluido afecta directamente al empuje y, por tanto, a la posición y orientación de equilibrio. En una aproximación elemental, el empuje se modela como:

- F_b = rho_f V g

Lo que provoca un momento que modifica el ángulo de equilibrio de la cápsula. Dado que el ángulo observado es una función de la densidad, la relación experimental del TFM se puede entender como una asociación entre la orientación de equilibrio y la propiedad física del fluido.

## 3. Modelo dinámico base

### 3.1 Aproximación 1D

Para una primera etapa, se considera un movimiento predominantemente angular alrededor de un eje principal. La variable relevante es la orientación theta(t). Un modelo base es:

- I theta_ddot + c_mu theta_dot + k_theta (theta - theta_eq) = tau_noise

donde:

- c_mu representa el amortiguamiento dependiente de la viscosidad
- theta_eq es el ángulo de equilibrio
- tau_noise representa una perturbación externa o un término de ruido del proceso

### 3.2 Modelo de primer orden alrededor del equilibrio

En muchos ensayos experimentales el sistema responde con una evolución temporal que puede aproximarse por un modelo de primer orden:

- theta(t) = theta_eq (1 - exp(-t/tau))

donde tau es una constante temporal que caracteriza la velocidad de respuesta. Este modelo resulta útil para identificar la orientación de equilibrio y el tiempo de relajación del sistema a partir de señales observadas.

## 4. Interacción fluido-estructura

### 4.1 Viscosidad

La viscosidad mu modifica la disipación de energía del sistema. El término de amortiguamiento puede modelarse como:

- c_mu = c0 + k_mu mu

y en un modelo no lineal más general:

- F_d = -c1 theta_dot - c2 |theta_dot| theta_dot

Este tipo de estructura permite capturar tanto la disipación lineal como la no lineal generada por el fluido.

### 4.2 Arrastre

El arrastre depende de la velocidad relativa entre la cápsula y el fluido. En un sistema de rotación, un término usual es:

- tau_drag = -C_d |omega| omega

Este término es relevante cuando la orientación del cuerpo presenta oscilaciones o cambios rápidos.

### 4.3 Tensión superficial

Cuando la cápsula opera en una interfaz o cerca de una superficie de contacto, la tensión superficial puede introducir una fuerza adicional. En un modelo práctico, este efecto puede representarse como una contribución efectiva:

- tau_sigma = -k_sigma sin(theta - theta_iface)

o como un término empírico en el momento residual. En una formulación de investigación más avanzada, este término permite estudiar la sensibilidad del sistema a cambios en la superficie libre o en la geometría del cuerpo.

## 5. Modelo de la IMU

La IMU aporta mediciones de aceleración y velocidad angular. Un modelo realista incluye ruido y bias:

- omega_meas = omega_real + b_g + n_g
- a_meas = a_real + b_a + n_a

Siendo:

- b_g, b_a bias del sensor
- n_g, n_a ruido blanco gaussiano
- en una extensión más realista, pueden incluirse random walk, escala y desalineación

### 5.1 Bias y deriva

Para capturar mejor el comportamiento del sensor, puede añadirse:

- b_g_dot = w_g
- b_a_dot = w_a

donde w_g y w_a representan perturbaciones de deriva o variación lenta del bias.

### 5.2 Sensibilidad al ángulo

En un sistema de cápsula inclinada respecto a la vertical, la aceleración medida puede interpretarse, de forma aproximada, como un proxy del ángulo. Esto justifica la estrategia de fusión sensorial basada en filtro complementario o estimadores bayesianos.

## 6. Fusión sensorial y estimación de estado

### 6.1 Filtro complementario

El filtro complementario es una primera aproximación útil para la estimación del ángulo. La estructura general es:

- theta_gyro(k) = theta_prev + omega_meas dt
- theta_est(k) = alpha theta_gyro + (1-alpha) theta_acc

donde:

- theta_acc se obtiene a partir de la aceleración
- alpha regula la mezcla entre la estimación por giroscopio y la estimación por gravedad o inclinación

### 6.2 EKF/UKF

En un nivel más avanzado, el sistema puede formularse como sistema de estado no lineal y estimarse con EKF o UKF. La ecuación de estado toma la forma:

- x_dot = f(x, u, p) + w
- y = h(x, p) + v

Esto permite estimar simultáneamente:

- orientación
- velocidad angular
- parámetros físicos
- incertidumbres asociadas

## 7. Identificación de parámetros

La identificación consiste en estimar los parámetros del modelo a partir de datos experimentales o sintéticos. Los parámetros de interés incluyen:

- theta_eq
- tau
- rho
- mu
- sigma
- C_d
- I
- k_restoring
- c_viscous

### 7.1 Identificación no lineal

Se puede resolver mediante mínimos cuadrados no lineales o optimización directa:

- min_theta sum (y_model - y_medida)^2

### 7.2 Identificabilidad

No todos los parámetros pueden estimarse con igual robustez bajo la misma configuración experimental. La calidad de la identificación depende de:

- amplitud de la excitación
- variación de densidad
- duración del ensayo
- presencia de ruido
- observabilidad del sistema

Por ello, un componente central de la investigación es analizar la identificabilidad y diseñar experimentos que hagan detectable cada parámetro.

## 8. Control del proceso

La cápsula no debe verse solo como sensor sino también como proceso dinámico que puede ser controlado. El control puede enfocarse en varias tareas:

### 8.1 Control de orientación

Buscar que la cápsula alcance una configuración angular deseada y se estabilice en ella.

### 8.2 Control para identificación

Excitar el sistema con un perfil determinado para mejorar la estimación de parámetros. Esto es especialmente relevante para mu y sigma, que pueden quedar confundidos si el sistema no se excita suficientemente.

### 8.3 Control basado en modelo

Utilizar el modelo matemático para diseñar un controlador en espacio de estados o un controlador robusto basado en la dinámica del sistema.

## 9. Validación y criterio de éxito

La calidad del modelo se evalúa comparando señales simuladas y medidas experimentales. Las métricas principales son:

- RMSE de theta
- MAE de theta
- error del ángulo de equilibrio
- error de estimación de rho
- error de estimación de mu y sigma
- intervalos de confianza de los parámetros

La validación debe cubrir:

- varios fluidos con densidades conocidas
- distintas condiciones de viscosidad
- diferentes niveles de excitación
- presencia del ruido IMU
- comparación con datos reales del TFM

## 10. Relación con el TFM inicial

El trabajo del TFM puede entenderse como la primera capa experimental y empírica del proyecto doctorado. En esa etapa, la relación densidad–ángulo y los modelos de primer orden son la base de evidencia. El doctorado amplía este principio hacia un marco más amplio:

- modelado físico explícito,
- simulación realista,
- estimación robusta,
- control del proceso,
- extensión a más parámetros físicos.

## 11. Conclusión

El sistema de cápsula desbalanceada instrumentada con IMU puede tratarse como un proceso dinámico de interés científico en el campo del modelado, la simulación y el control de procesos. La base teórica del proyecto se apoya en la dinámica del cuerpo rígido, la interacción con un fluido, el modelo de medición inercial y la formulación de un problema de identificación y control.

Desde este marco, el repositorio adquiere un sentido claro: hacer evolucionar un conjunto de experimentos iniciales hacia un modelo formal, reproducible y extensible que pueda sostener una línea de investigación doctoral.
