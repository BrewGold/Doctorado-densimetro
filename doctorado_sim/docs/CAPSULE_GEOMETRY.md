# Geometría paramétrica de la cápsula

## 1. Objetivo

Definir una parametrización geométrica de una cápsula formada por un cilindro central con dos semiesferas en los extremos, que sirva tanto para simulación como para diseño experimental del prototipo físico.

La geometría se toma como referencia para el análisis del empuje, el centro de empuje, el centro de gravedad, el momento de inercia, el diámetro de la línea de flotación y la sensibilidad del sistema ante cambios en densidad y viscosidad.

## 2. Suposiciones geométricas

Se considera una cápsula con simetría axial alrededor del eje z, formada por:

- un cilindro de longitud L_c y diámetro D
- dos semiesferas de radio R = D/2 en los extremos

La cápsula se puede representar como un cuerpo de revolución con eje longitudinal z.

## 3. Parámetros geométricos principales

- D: diámetro externo de la cápsula
- L_c: longitud del cilindro central
- R = D/2: radio de la cápsula
- L_total = L_c + 2R: longitud total del cuerpo
- V_c: volumen del cilindro
- V_s: volumen de una semiesfera
- V_total: volumen total de la cápsula

## 4. Volúmenes

### 4.1 Volumen del cilindro

- V_c = pi * R^2 * L_c

### 4.2 Volumen de una semiesfera

- V_s = (2/3) * pi * R^3

### 4.3 Volumen total

- V_total = V_c + 2 * V_s

Es decir:

- V_total = pi * R^2 * L_c + (4/3) * pi * R^3

## 5. Centro de volumen

La cápsula es simétrica respecto al eje z, por lo que el centro de volumen está sobre el eje longitudinal. Si se toma el origen en el centro del cilindro, la posición del centro de volumen en z se obtiene de la contribución de cada sección.

### 5.1 Centro del cilindro

- z_c = 0

### 5.2 Centro de cada semiesfera

Si el centro de cada semiesfera está desplazado a distancia R/2 desde el extremo del cilindro, el centro del hemisferio superior está en:

- z_s = L_c/2 + 3R/8

y el inferior en:

- z_s_inf = -(L_c/2 + 3R/8)

El centro total del volumen se obtiene por suma ponderada:

- z_V = (V_c * z_c + V_s * z_s + V_s * z_s_inf) / V_total

Como el sistema es simétrico, el centro total del volumen queda en el eje z, con una ligera variación respecto al centro geométrico si la geometría no es perfectamente simétrica respecto a la distribución de material. En una primera aproximación, se toma:

- z_V = 0

si se considera uniforme el material y una distribución simétrica.

## 6. Centro de masa

En un modelo con lastre excéntrico, la masa total no está distribuida uniformemente. El centro de masa se define como:

- z_G = (m_c z_c + m_l z_l + m_estructura z_estructura) / m_total

Donde:

- m_c: masa del cuerpo principal
- m_l: masa del lastre
- z_l: posición del lastre respecto al eje de referencia
- m_total = m_c + m_l + m_estructura

En el caso de una efectiva cápsula desbalanceada, el lastre debe estar desplazado respecto al eje longitudinal para crear un momento de restauración o de equilibrio.

## 7. Empuje hidrostático

El empuje vertical es:

- F_b = rho_f * g * V_desplazado

Mientras que el centro geométrico de volumen desplazado define el centro de empuje, que es una variable clave para la estabilidad.

## 8. Momento de restauración

La orientación del cuerpo en el fluido depende de la diferencia entre el centro de gravedad y el centro de empuje. Si la cápsula tiene un último desplazamiento del centro de masa respecto al eje, el momento restaurador puede aproximarse por:

- M_rest = (rho_f * V_desplazado) * g * d_GB * sin(theta)

donde:

- d_GB es la distancia horizontal entre centro de gravedad y centro de empuje
- theta es el ángulo de inclinación respecto a la vertical

Con una primera aproximación lineal, el término restaurador puede escribirse como:

- M_rest ≈ -k_theta * theta

## 9. Momento de inercia

Para una sección de revolución, la inercia alrededor del eje longitudinal z se puede aproximar por:

- I_z ≈ (1/2) m R^2

Si se desea una aproximación más detallada para la cápsula completa, se utiliza la suma de cilindro más semiesferas:

- I_total = I_cil + I_hemisferios + contribuciones del lastre

## 10. Área mojada y arrastre

La parte exterior de la cápsula que queda sumergida en contacto con el fluido tiene un área de superficie mojada A_wet. Para la aproximación de un cilindro con semiesferas, se puede estimar:

- A_wet ≈ 2 pi R L_sub + 2 * (2 pi R^2 / 2)

siendo L_sub la parte sumergida del cilindro. La geometría de la superficie mojada influye directamente en el coeficiente de arrastre y, por tanto, en la respuesta dinámica del sistema.

## 11. Sección de flotación

La línea de flotación se define como la intersección entre el cuerpo y la superficie libre del fluido. Si se quiere modelar la estabilidad y la orientación en función del nivel de inmersión, se debe calcular la fracción de volumen sumergido:

- V_sub = rho_cuerpo / rho_fluido * V_total

En el caso de que la densidad del cuerpo sea menor que la del fluido, la cápsula flotará con una parte inmersa que depende de la relación de densidades.

## 12. Parámetros físicos relevantes para el modelo

La geometría define directamente varias magnitudes del modelo:

- volumen desplazado
- centro de empuje
- centro de masa
- momento de inercia
- superficie mojada
- longitud efectiva de palanca
- sensibilidad del equilibrio a cambios de densidad

Estos parámetros permiten definir una versión del simulador donde se cambien los parámetros geométricos y puedan compararse diferentes prototipos.

## 13. Diseño práctico recomendado

Para el primer prototipo real, la recomendación es:

- D: diámetro moderado, que permita alojar IMU y lastre interno
- L_c: longitud suficiente para crear un momento de equilibrio claro
- lastre excéntrico desplazable para ajustar la sensibilidad del sistema
- paredes con espesor suficiente para robustez estructural
- semiesferas fáciles de imprimir o de fabricar en dos piezas

## 14. Conclusión

La geometría de la cápsula debe elegirse en función de tres propiedades clave:

1. capacidad de flotar de forma estable,
2. sensibilidad del ángulo de equilibrio a la densidad,
3. facilidad de modelado y fabricación.

La opción cilíndrica con dos semiesferas es la más apropiada para una primera implementación realista y reproducible. Su parametricidad permite reproducción en simulación y comparación con prototipos experimentales, manteniendo una complejidad razonable y un camino claro hacia validación y doctorado.
