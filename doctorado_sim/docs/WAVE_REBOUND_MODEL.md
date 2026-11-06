# Balanceo amortiguado con un modo efectivo del agua

## Objetivo y alcance

Reproducir cualitativamente el decaimiento y las recuperaciones de amplitud
sin introducir energia artificial. Es una hipotesis exploratoria, no un
ajuste a los ensayos ni una demostracion del origen de sus modulaciones.
El baseline existente no se modifica.

## Ecuaciones

Con `x = theta - theta_eq` y una coordenada modal equivalente del agua `q`:

```text
I_c x'' + c_c x' + k_c x + k_r (x-q) = 0
I_w q'' + c_w q' + k_w q + k_r (q-x) = 0
```

`q` se expresa en radianes equivalentes por eleccion de normalizacion; no es
altura de ola ni un angulo observado. `I_w` es una inercia modal equivalente.
`k_r` acopla ambos movimientos y genera sobre la capsula el momento
`k_r*(q-x)`. Se modela un modo del conjunto agua-recipiente capaz de almacenar
y devolver energia, no una onda individual viajando hasta una pared.
El modelo completo tiene dos grados de libertad y cuatro estados mecanicos:
no es un unico sistema de segundo orden.

La energia mecanica total es:

```text
E = I_c*x'^2/2 + I_w*q'^2/2 + k_c*x^2/2 + k_w*q^2/2
    + k_r*(x-q)^2/2
dE/dt = -c_c*x'^2 - c_w*q'^2 <= 0
```

La capsula puede recuperar amplitud al recibir energia del agua, aunque la
energia total disminuya. No hay actuacion externa. Sin acoplamiento y con
el agua inicialmente en reposo se recupera el oscilador aislado; sin
amortiguamiento se conserva la energia.

## Parametros ilustrativos

`wave_rebound_config.m` fija 80 s a 100 Hz, desviacion inicial de 2 grados y
agua inicialmente en reposo. El equilibrio de 65 grados solo desplaza la
referencia angular. Ambos osciladores aislados tienen frecuencia natural de
1.9 Hz, elegida como referencia exploratoria del TFM, no como parametro
identificado. Las inercias equivalentes se fijan en 1.2e-4 kg m2, sin
considerarlas medidas fisicas del prototipo.

El acoplamiento es el 2.5 % de la rigidez de la capsula. Las tasas de
amortiguamiento aisladas `c/(2I)` son 0.035 y 0.020 s^-1. Esta seleccion
ilustrativa produce dos frecuencias naturales acopladas cercanas, 1.9000 y
aproximadamente 1.9469 Hz, con una escala de batido cercana a 21.3 s.
No se han extraido esas dos frecuencias de los datos. El amortiguamiento
modifica la respuesta y sus tiempos de maximos.

Para explorar, modificar la configuracion y llamar
`dynamics_wave_rebound(cfg)`. Reducir `k_coupling_nm_rad` debilita el intercambio;
ponerlo a cero elimina el modo del agua de la respuesta de la capsula.
Cambiar `k_wave_nm_rad/I_wave_kgm2` cambia la frecuencia del modo del agua.
La salida contiene energias separadas, energia disipada integrada y error
del balance energetico; no se estima una envolvente experimental.

## Lo que aun no representa

- No calcula propagacion, tiempo de ida y vuelta, reflexiones individuales
  ni modos a partir de anchura, profundidad y condiciones de borde.
- No atribuye el amortiguamiento exclusivamente a viscosidad ni lo calibra
  con densidad, viscosidad o temperatura.
- No incluye la ranura, capilaridad, entrada de agua, IMU ni ruido.
- No establece que una modulacion observada sea un batido.

Una ampliacion geometrica requeriria estimar los modos del recipiente y su
acoplamiento. Para estudiar una reflexion aislada haria falta un modelo de
propagacion o memoria causal con perdidas; agregar una senoide arbitraria
como fuerza externa no demostraria un retorno pasivo de energia.
La hipotesis se contrastara variando recipiente y absorcion, con liberaciones
reproducibles, antes de ajustar o interpretar parametros del fluido.

## Fundamento

- Fossen, *Marine Craft Model*: inercia, masa anadida, amortiguamiento y
  restauracion en dinamica de cuerpos en fluidos.
  https://www.fossen.biz/html/marineCraftModel.html
- ITTC (2024), *Estimation of Roll Damping*, 7.5-02-07-04.5, revision 02,
  secciones 2 y 3: ecuacion de balanceo y ensayos de decaimiento.
  https://ittc.info/media/11942/75-02-07-045.pdf

Estas fuentes sustentan la estructura hidrodinamica general; la reduccion
a dos osciladores y los valores usados aqui son una eleccion exploratoria.
