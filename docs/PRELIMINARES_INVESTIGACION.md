# Preliminares de la investigación

## Propósito y alcance

Este documento recoge observaciones exploratorias derivadas del TFM y una propuesta inicial para el siguiente grupo de pruebas. Son preliminares: describen lo observado hasta ahora y las preguntas que se investigarán, sin presentar como demostrados mecanismos que todavía requieren validación.

## Observación inicial en los datos del TFM

Se realizó una inspección exploratoria de los 25 archivos CSV disponibles en [`references/tfm/datos_udp.zip`](../references/tfm/datos_udp.zip). Los registros incluyen la señal angular `ang_deg` y marcas de tiempo `t_ms`, con muestreo nominal de aproximadamente 100 Hz.

En la mayoría de los registros, el ángulo presenta oscilaciones rápidas con un pico espectral dominante cercano a 1,9 Hz. La amplitud global suele disminuir con el tiempo, pero algunos ensayos muestran rebotes o modulaciones más lentas durante el transitorio. Estos rasgos se aprecian, entre otros, en los archivos `imu_20260628_130351.csv`, `imu_20260628_132705.csv` e `imu_20260628_132857.csv`.

La respuesta oscilatoria es compatible con un comportamiento subamortiguado y no con una relajación monótona de primer orden durante esos transitorios. Los rebotes de amplitud motivan investigar un posible batido o acoplamiento de modos, pero la inspección actual no demuestra que exista una envolvente lenta periódica y estable ni identifica su causa. En consecuencia:

- el modelo de segundo orden es una hipótesis de trabajo físicamente razonable por la inercia de la cápsula;
- un modelo 1DoF de segundo orden con un único modo no debe darse por suficiente para explicar los rebotes;
- la atribución a dos modos, al batido u otro mecanismo permanece abierta;
- el ajuste de primer orden puede servir como aproximación en tramos adecuados, pero no caracteriza por sí solo toda la respuesta observada.

## Segundo grupo de pruebas propuesto

Se plantea realizar un nuevo grupo de ensayos con soluciones de agua con sal y agua con glicerina. La finalidad es observar cómo cambia la respuesta dinámica de la cápsula al variar las propiedades del fluido y comprobar si los rebotes de amplitud se reproducen bajo condiciones controladas.

Estas mezclas no aíslan automáticamente una sola propiedad: agregar sal o glicerina puede modificar tanto la densidad como la viscosidad. Por ello, no se atribuirán los cambios observados a una propiedad concreta sin medir o estimar las propiedades de cada muestra y considerar sus efectos combinados. Si se busca separar específicamente los efectos de densidad y viscosidad, se procurará incluir condiciones comparables en densidad con viscosidades diferentes, o viceversa, según sea viable experimentalmente.

## Variables y criterios de comparación

Para cada ensayo se propone registrar:

- composición de la muestra y temperatura;
- densidad y, cuando sea posible, viscosidad medidas o estimadas;
- señal angular, aceleraciones y velocidades angulares de la IMU;
- condiciones iniciales y forma de perturbación/liberación de la cápsula;
- frecuencia dominante del balanceo;
- ángulo de equilibrio;
- evolución temporal de la amplitud, incluyendo su decaimiento y posibles rebotes.

Se intentarán mantener constantes la cápsula, la orientación inicial, la perturbación, la adquisición y las condiciones de contorno. Cada condición debería repetirse para evaluar la variabilidad experimental. Las comparaciones buscarán determinar si la modulación lenta es reproducible, si presenta una escala temporal definida y cómo se relaciona con las propiedades medidas del fluido.

## Análisis pendiente

Con los nuevos datos, y cuando corresponda reanalizando los datos originales, se propone:

1. verificar y corregir discontinuidades o reinicios de las marcas de tiempo;
2. analizar las frecuencias dominantes y la envolvente de la oscilación en cada repetición;
3. comparar ajustes de primer orden, segundo orden subamortiguado y modelos de dos componentes o modos;
4. evaluar los residuos y la repetibilidad entre ensayos, no solo el ajuste visual;
5. relacionar las diferencias entre condiciones con densidad, viscosidad y temperatura, atendiendo a posibles factores confundentes.

Hasta completar estos análisis, las oscilaciones y rebotes descritos aquí se consideran observaciones preliminares; el batido y el acoplamiento modal son hipótesis por contrastar.
