# Problema de investigación, objetivos e hipótesis

## 1. Motivación

Los sistemas de medida basados en cápsulas desbalanceadas y sensores inerciales presentan un gran potencial para la estimación de propiedades físicas del entorno, en particular la densidad de fluidos. Sin embargo, su comportamiento dinámico depende de una combinación compleja de factores: geometría, distribución de masas, empuje, amortiguamiento viscoso, arrastre hidrodinámico, posible efecto de tensión superficial, ruido y bias del sensor. Esta complejidad convierte el problema en un caso de interés para el modelado, la simulación, la identificación y el control de procesos.

El trabajo inicial desarrollado en el TFM aporta la evidencia experimental y la demostración del principio de funcionamiento. No obstante, para avanzar hacia una línea de investigación doctoral es necesario ir más allá de la calibración empírica y construir un marco teórico y computacional que permita reproducir el sistema de manera general y extrapolarlo a nuevos escenarios.

## 2. Definición del problema

El problema de investigación consiste en modelar, simular y controlar una cápsula desbalanceada instrumentada con IMU para estimar propiedades del medio en el que se encuentra, con especial atención a la densidad, la viscosidad y, en su caso, la tensión superficial. La cápsula presenta un comportamiento dinámico que puede describirse como un sistema acoplado entre un cuerpo rígido, un medio fluido y un conjunto de sensores inerciales.

La dificultad central se debe a que:

- el movimiento no es puramente estático sino dinámico;
- la respuesta depende de múltiples parámetros físicos no directamente observables;
- la IMU introduce ruido, bias y errores de medida;
- la identificación de parámetros puede ser no trivial debido a la confusión entre efectos físicos;
- el sistema puede requerir estrategia de excitación y control para mejorar observabilidad e identificabilidad.

## 3. Pregunta de investigación

¿Es posible desarrollar un modelo físico-estocástico de una cápsula desbalanceada con IMU que reproduzca con precisión el comportamiento dinámico del sistema, permita estimar propiedades del fluido y sirva como base para estrategias de control y validación experimental?

## 4. Hipótesis general

Un modelo híbrido que combine dinámica de cuerpo rígido, interacción fluido-estructura y un modelo estocástico del sensor inercial permite representar adecuadamente la evolución del sistema, estimar propiedades relevantes del fluido y constituir una base útil para la identificación paramétrica y el control del proceso.

## 5. Objetivo general

Desarrollar un marco de modelado, simulación y control para una cápsula desbalanceada instrumentada con IMU, orientado a la estimación de propiedades del medio fluido y a la validación experimental del sistema a partir del trabajo previo del TFM.

## 6. Objetivos específicos

### 6.1 Modelado físico

- Formular un modelo dinámico de la cápsula desbalanceada considerando equilibrio hidrostático, empuje, peso, arrastre y amortiguamiento.
- Incorporar efectos de densidad, viscosidad y tensión superficial en la formulación del sistema.
- Definir una representación matemática del comportamiento rotacional y, en una extensión posterior, traslacional.

### 6.2 Simulación

- Implementar un entorno de simulación que capte la verdad física del sistema.
- Incorporar un modelo realista de la IMU con ruido, bias y deriva.
- Generar escenarios de prueba sintéticos con distintos parámetros del fluido y condiciones operativas.
- Evaluar la respuesta del sistema frente a perturbaciones y variabilidad paramétrica.

### 6.3 Estimación e identificación

- Estimar el estado del sistema a partir de señales de IMU.
- Identificar parámetros relevantes del proceso, como ángulo de equilibrio, constante temporal, viscosidad efectiva y coeficientes de arrastre.
- Analizar observabilidad e identificabilidad del sistema.
- Evaluar la incertidumbre y la robustez de la estimación.

### 6.4 Control de procesos

- Definir un problema de control basado en la orientación de la cápsula o en la excitación del sistema.
- Explorar estrategias de control para mejorar la observabilidad y la identificación experimental.
- Proponer una estructura que permita manipular el sistema en condiciones controladas.

### 6.5 Validación experimental

- Relacionar los resultados simulados con datos experimentales del TFM.
- Definir métricas de comparación entre dinámica real y modelada.
- Evaluar la capacidad del modelo para reproducir propiedades físicas del medio.

## 7. Metodología

La metodología de la investigación se organiza en varias fases:

1. Revisión de la base experimental del TFM.
2. Formulación del modelo físico de la cápsula en fluido.
3. Desarrollo del simulador con trazado de la verdad física y de la medición inercial.
4. Implementación de estimadores de estado y métodos de identificación.
5. Diseño de estrategias de control y experimentos de excitación.
6. Validación con datos experimentales y análisis de sensibilidad.

## 8. Contribuciones esperadas

La investigación pretende aportar una serie de contribuciones relevantes:

- un modelo dinámico para una cápsula desbalanceada en fluido con base física y matemáticamente formalizada;
- un simulador realista con ruido de IMU y parámetros físicos variables;
- un marco de identificación de parámetros para estimar propiedades del medio;
- un enfoque útil para la estimación del estado del sistema y para la observabilidad del problema;
- un punto de partida para estrategias de control y automatización del proceso experimental;
- una base sólida para publicaciones y desarrollo futuro de una línea de investigación doctoral.

## 9. Alcance y limitaciones

El alcance inicial de la investigación se centra en una formulación basada en la cápsula desbalanceada instrumentada con IMU, con especial atención a la dinámica angular y a una interpretación física del problema. Se asume una primera aproximación de bajo orden, con el objetivo de mantener un equilibrio entre rigor físico y viabilidad computacional e experimental.

Las limitaciones más relevantes son:

- complejidad del flujo real y posible no linealidad de la interacción fluido-estructura;
- necesidad de calibración sensorial y validación experimental;
- posible confusión entre efectos de viscosidad, tensión superficial y distribución de masas;
- dependencia de la geometría del sistema y del tipo de fluido.

## 10. Conclusión

El problema de investigación se sitúa en la intersección entre modelado físico, simulación, sensado inercial e identificación paramétrica. La línea doctoral propuesta permite transformar el trabajo experimental inicial en una investigación con base teórica formal, metodológica rigurosa y potencial de contribución científica más allá del TFM. Este enfoque no solo busca estimar densidad, sino comprender, reproducir y controlar un sistema dinámico cuyas propiedades físicas son directamente accesibles desde la observación de una cápsula desbalanceada.
