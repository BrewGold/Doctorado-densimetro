# Arquitectura de investigación doctoral

## 1. Línea de investigación

Modelado, simulación y control de procesos

## 2. Título orientativo

Modelado físico-estocástico, simulación y control de una cápsula desbalanceada instrumentada con IMU para estimación de propiedades de fluidos.

## 3. Objetivo general

Desarrollar un modelo híbrido físico-estocástico para describir la dinámica de una cápsula desbalanceada en contacto con un fluido, integrando sensores inerciales, efectos de densidad, viscosidad, tensión superficial y ruido de medida; y utilizar este modelo para estimar propiedades del medio y diseñar estrategias de control y validación experimental.

## 4. Hipótesis central

Un modelo que combine dinámica de cuerpo rígido, interacción fluido-estructura y un modelo estocástico de la IMU permite reproducir con precisión la evolución de la cápsula, estimar parámetros relevantes del medio y ofrecer una base robusta para control y validación experimental.

## 5. Problema científico

El sistema de medida basado en cápsula flotante desbalanceada no es solo una curva de calibración densidad-ángulo. Es un sistema dinámico acoplado, con:

- comportamiento rotacional y traslacional,
- amortiguamiento hidrodinámico,
- empuje y peso,
- posible efecto de tensión superficial,
- ruido, sesgo y deriva del IMU,
- dependencia con la geometría y distribución de masas,
- incertidumbre en los parámetros del fluido.

El reto es modelarlo sin perder la relación con el experimento físico y manteniendo una base reproducible para simulación, estimación y control.

## 6. Estructura del sistema

El sistema puede representarse en forma general como:

- Estado: x(t)
- Entrada: u(t)
- Parámetros: p
- Salida: y(t)
- Ruido de proceso: w(t)
- Ruido de medida: v(t)

Con ecuaciones:

- x_dot = f(x, u, p) + w
- y = h(x, p) + v

### 6.1 Variables de estado

- theta: orientación angular
- omega: velocidad angular
- v: velocidad lineal
- z: posición o desplazamiento
- parámetros de estado extendidos si se requieren

### 6.2 Parámetros físicos

- rho: densidad del fluido
- mu: viscosidad
- sigma: tensión superficial
- C_d: coeficiente de arrastre
- I: inercia
- geometría y desbalance
- offset de masa y centro de gravedad

### 6.3 Variables de salida

- aceleraciones medidas: ax, ay, az
- velocidades angulares: gx, gy, gz
- ángulo estimado de equilibrio
- señales derivadas para filtrado y fusión

## 7. Modelado físico

### 7.1 Dinámica rotacional

La cápsula se modela como un cuerpo rígido con equilibrio hidrostático y fuerzas restitutivas. Una estructura de referencia es:

- I * theta_ddot + damping(theta_dot, mu) + restoring(theta, rho, sigma) + coupling = tau_ext

Donde:

- I: inercia efectiva
- damping: amortiguamiento viscoso y no lineal
- restoring: fuerza de equilibrio debida a empuje y desbalance
- coupling: acoplamientos geométricos y de fluido
- tau_ext: perturbaciones externas o excitaciones de control

### 7.2 Fuerzas de interacción fluido-estructura

- peso
- empuje hidrostático
- arrastre viscoso
- arrastre cuadrático
- fuerza superficial asociada a tension superficial
- posibles términos no lineales por interacción de interfaz

### 7.3 Modelo de sensor IMU

- omega_meas = omega_real + b_g + n_g
- a_meas = a_real + b_a + n_a

Donde:

- b_g, b_a: bias
- n_g, n_a: ruido blanco y componentes de deriva
- puede añadirse random walk y desalineación si se requiere mayor realismo

## 8. Simulación

La simulación debe separar claramente:

1. verdad física del sistema
2. medición sensorial realista
3. estimación del estado
4. identificación de parámetros

### 8.1 Objetivos de simulación

- reproducir la evolución dinámica de la cápsula
- estudiar el efecto de rho, mu y sigma
- comparar verdad vs medición
- evaluar robustez frente a ruido e incertidumbre
- generar datos sintéticos para validación y pruebas de algoritmo

### 8.2 Herramientas de análisis

- integración numérica temporal
- Monte Carlo
- sensibilidad local/global
- análisis de observabilidad e identificabilidad
- comparación de modelos frente a datos reales del TFM

## 9. Estimación

La estimación debe contemplar dos niveles:

### 9.1 Estimación de estado

- filtro complementario
- EKF
- UKF
- observador de orientación

Se busca estimar:

- theta(t)
- omega(t)
- estado del sistema a partir de IMU

### 9.2 Estimación de parámetros

- theta_eq
- tau
- rho
- mu
- sigma
- coeficientes de amortiguamiento y arrastre

Se pueden emplear:

- mínimos cuadrados no lineales
- ajuste por optimización
- identificación basada en ecuaciones de estado
- enfoque bayesiano incremental

## 10. Control de procesos

La segunda dimensión del doctorado es asumir el sistema como proceso dinámico controlable.

### 10.1 Objetivos de control

- estabilizar la cápsula en una orientación deseada
- excitar el sistema para mejorar la identificación de parámetros
- compensar perturbaciones externas
- mejorar la observabilidad del sistema
- mantener condiciones operativas repetibles en experimentos

### 10.2 Estrategias potenciales

- control de orientación
- control basado en modelo
- control robusto
- control adaptativo
- MPC o control óptimo
- estrategias híbridas con observador de estado

## 11. Validación experimental

La validación se realiza comparando:

- resultados simulados
- datos reales del flujo del TFM
- curvas de densidad, orientación y equilibrio
- métricas de error y robustez

### 11.1 Métricas recomendadas

- MAE y RMSE de theta
- error de theta_eq
- error de rho estimada
- sensibilidad del modelo a mu y sigma
- intervalo de confianza de parámetros
- robustez ante ruido y bias

## 12. Roadmap doctoral

### Fase 1: modelo base 1DoF

Objetivo: reproducir la dinámica principal de la cápsula con una sola variable angular.

- ecuación de movimiento angular
- viscosidad efectiva
- IMU sintética con ruido y bias
- comparación con TFM
- ajuste de theta_eq y tau

### Fase 2: modelado extendido del fluido

Objetivo: introducir rho, mu y sigma como parámetros relevantes.

- fuerza de empuje
- arrastre viscoso y cuadrático
- efecto superficial
- análisis de sensibilidad

### Fase 3: estimación de estado y parámetros

Objetivo: extraer información útil de la IMU y reconstruir el sistema real.

- filtro complementario y EKF
- observabilidad
- identifiabilidad
- validación por simulación y experimentos

### Fase 4: control del proceso

Objetivo: convertir el sistema en un proceso controlado y reproducible.

- control de orientación
- excitación bajo control
- diseño de experimentos para identificación
- control robusto o basado en modelo

### Fase 5: validación y publicación

Objetivo: consolidar resultados experimentales y teóricos.

- métricas finales
- comparación con trabajos previos
- generación de resultados, figuras y artículos

## 13. Entregables esperados

- modelo matemático documentado
- simulador ejecutable
- dataset sintético reproducible
- algoritmo de estimación
- algoritmo de control base
- validación experimental contra TFM
- resultados para artículos y tesis

## 14. Conclusión

La investigación doctoral no debe quedarse en un problema de calibración de densidad, sino en el modelado y control de un proceso dinámico acoplado. La cápsula desbalanceada, la IMU y el fluido forman un sistema de interés científico que combina:

- modelado físico,
- simulación estocástica,
- estimación y observación,
- identificación paramétrica,
- control de procesos.

Ese es el eje coherente para convertir el repositorio inicial en una línea de investigación de doctorado y, a la vez, mantener la conexión precisa con el TFM original.
