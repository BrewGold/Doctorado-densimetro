# Capsula y ondas en paredes circulares

## Datos y referencias angulares

El usuario aporta diametro interior a nivel del agua de 22 cm, profundidad
aproximada de 8 cm, longitud aproximada de capsula de 15 cm y elevacion del
extremo opuesto al lastre de unos 5 cm. Aclara que **30 grados es la desviacion
inicial respecto al equilibrio**, no el angulo de equilibrio. Se impone esa
desviacion como condicion inicial; no se interpreta 5 cm como altura de ola.

El TFM Rev04, apendice B, script de calibracion, da para 0.9973 g/cm3 una
referencia angular de -0.959728 rad (aproximadamente -55 grados). Se usa solo
como origen de coordenadas: `theta_model = referencia_TFM + x`. El signo
positivo de `x` define el levantamiento en esta simulacion, no una calibracion
del signo de la IMU. El reanalisis del Modulo III obtiene 64.13963 grados
para ese grupo en la variable `ang_deg`, calculada con otra formula.
**No se equiparan estos dos observables ni se toma ninguno directamente
como inclinacion geometrica del eje de la capsula.**

Fuentes internas:
- `references/tfm/Densidad_orientacion_angular-F_Gold_Rev04.pdf`, apendices A/B:
  formulas distintas para `ang_deg` y `theta_acc`; referencia por densidad.
- [Resumen del Modulo III](https://github.com/BrewGold/Doctorado-cursos_transversales/blob/HEAD/tareas/modulo_III/resultados/resumen_grupos.csv).

Solo para estimar la proyeccion horizontal de la fuente y dibujar un esquema,
se supone que durante el levantamiento el extremo lastrado mantiene su
altura. Con longitud L, elevacion H y desviacion delta:

```text
H = L [sin(beta + delta) - sin(beta)]
beta = acos(H / (2 L sin(delta/2))) - delta/2
```

Con los valores aproximados aportados resulta beta = 34.91 grados y una
postura elevada de 64.91 grados. Son valores **inferidos bajo esa hipotesis**,
no una nueva medida de reposo ni una reinterpretacion del TFM. Si se desplaza
el extremo lastrado, esa inferencia deja de ser valida. La simulacion no
mantiene despues un pivote material en ese extremo.

## Ondas con geometria y dispersion

Se idealiza el cuenco como cilindro de radio R y fondo plano a profundidad h.
Se retienen N=8 modos dipolares (numero azimutal m=1), apropiados para una
excitacion angular centrada:

```text
eta(r,phi,t) = sum q_n(t) psi_n(r,phi)
psi_n = J1(k_n r) cos(phi) / J1(alpha_n)
J1'(alpha_n) = 0,   k_n = alpha_n/R
omega_n^2 = (g k_n + sigma k_n^3/rho) tanh(k_n h)
```

La derivada radial nula en la pared satisface la condicion impermeable del
flujo potencial. Los modos incorporan las reflexiones en la solucion espacial;
no se suma una senoide externa ni un eco arbitrario. Cada modo tiene integral
de superficie nula, por lo que conserva el volumen de agua.
La dispersion incluye profundidad finita y capilaridad: no se usa la
aproximacion de aguas someras, inadecuada aqui para todos los modos.

Con normalizacion A_n = integral(psi_n^2 dA):

```text
A_n = pi R^2/2 (1 - 1/alpha_n^2)
M_n = rho A_n / [k_n tanh(k_n h)]
K_n = (rho g + sigma k_n^2) A_n
C_n = 2 M_n [alpha_extra + 2 (mu/rho) k_n^2]
```

El ultimo termino es una aproximacion de perdidas viscosas debiles de ondas
limpias. `alpha_extra` representa perdidas efectivas no resueltas; no se ha
calculado el rozamiento en pared/fondo ni la disipacion del menisco.
La densidad de 997.3 kg/m3 procede del TFM; mu=1.002 mPa s y sigma=0.0728 N/m
son referencias orientativas de agua cerca de 20 C, no propiedades medidas
ni una reconstruccion termodinamica de aquella disolucion.

## Acoplamiento pasivo y restauracion angular

Como el desplazamiento inicial es grande, se usa una restauracion pendular
`k_c sin(x)` en vez de extender una rigidez lineal a 30 grados. Es una
hipotesis fenomenologica: no sustituye al calculo de la geometria sumergida.
Se define una energia potencial positiva:

```text
U = k_c (1-cos(x)) + 1/2 sum K_n [q_n - a_n sin(x)]^2
I x'' + c_c x' + k_c sin(x)
    - cos(x) sum K_n a_n [q_n - a_n sin(x)] = 0
M_n q_n'' + C_n q_n' + K_n [q_n - a_n sin(x)] = 0
dE/dt = -c_c x'^2 - sum C_n q_n'^2 <= 0
```

La forma espacial de la fuente es un dipolo gaussiano suavizado:
`s_n = k_n exp[-(k_n w)^2/2] / [2 J1(alpha_n)]`, con
`w = L cos(beta)/4`. Se elige `a_n = gamma s_n/K_n` y se normaliza gamma
para que `sum K_n a_n^2 = coupling_fraction*k_c`.
Esta ley reciprocamente acoplada conserva energia sin perdidas, pero su
intensidad y forma **no proceden de una solucion hidrodinamica de la capsula**.
El valor ilustrativo de `coupling_fraction` es 0.01.

Se conserva I=1.2e-4 kg m2 y frecuencia natural local aislada de 1.9 Hz del
ejercicio exploratorio; no son parametros identificados del prototipo.
El decaimiento angular aislado c_c/(2I)=0.035 s^-1 y las perdidas adicionales
del agua de 0.04 s^-1 tampoco estan medidos. Se inicializa el agua en equilibrio
estatico con la capsula sostenida: q_n=a_n sin(x0), velocidades cero. Si la
liberacion real fue rapida o habia ondas previas, sus condiciones son distintas.

El CSV separa energia de capsula, energia libre del agua e interaccion.
La interaccion puede ser negativa: la energia total positiva es la suma de
energia cinetica, potencial de capsula y potencial en los desajustes q-a sin(x).
Se integra tambien la energia disipada para verificar el balance.

## Resultados que dependen de la geometria

Para el recipiente ideal **sin la capsula**, el primer modo dipolar es
aproximadamente 1.9058 Hz. Esa cercania al pico exploratorio de 1.9 Hz merece
contraste experimental, pero no prueba que el pico medido sea del recipiente:
la capsula ocupa una fraccion importante de la superficie y modifica el fluido.
Los modos del conjunto acoplado tampoco coinciden exactamente con los del
agua sola.

Con c_g=domega/dk, a 1.9 Hz resulta c_g aproximadamente 0.493 m/s. La escala
de ida-vuelta centro-pared-centro es unos 0.446 s; desde el borde de la
proyeccion estimada de la capsula es unos 0.197 s. No son un retardo puro
impuesto al modelo ni el periodo de los batidos o de una envolvente lenta.
La superposicion dispersiva, el campo cercano y la condicion inicial global
impiden identificar un primer eco solo con estas escalas.

Se comparan capsula sin acoplamiento, agua con paredes y perdidas bajas, y
el mismo recipiente con perdidas modales altas. **Aumentar esas perdidas no
equivale a instalar una pared absorbente ni a simular un medio infinito.**
Se exporta el campo eta sobre un diametro y una sensibilidad de frecuencias
a profundidades de 3, 5, 8 y 12 cm. No se pretende ajustar rebotes de los CSV.

## Limites y comprobaciones

El modelo incorpora ondas lineales dispersivas con condicion de pared y
balance energetico, no CFD de superficie libre. No reproduce la curvatura
real del cuenco, la obstruccion por la capsula, heave, migracion del centro,
linea de flotacion variable, ranura, mojado/desmojado, entrada de aire/agua
ni errores IMU. La perturbacion de 30 grados puede activar esos mecanismos.
El acoplamiento centrado y la postura inferida son aproximaciones relevantes,
especialmente con una capsula de 15 cm en un recipiente de 22 cm.

Se informa de maximo |eta|/h y pendiente superficial reconstruida. Si alguno
supera 0.1 se emite advertencia orientativa sobre la aproximacion lineal;
no es una certificacion de validez por debajo de ese umbral.
La resolucion espectral depende del numero de modos. Las pruebas comparan
8 y 12 modos, verifican J1'=0, normalizacion, dispersion, velocidad de grupo,
conservacion sin perdidas, disipacion, desacoplamiento y desplazamiento del
origen angular. La energia mecanica total debe decaer aunque la amplitud
angular pueda recuperarse.

## Fuentes

- Abramson, H. N. (ed.), 1966, *The Dynamic Behavior of Liquids in Moving
  Containers*, NASA SP-106, capitulo sobre sloshing lateral: fundamento de
  modos de recipientes cilindricos en teoria lineal.
  https://ntrs.nasa.gov/citations/19670006555
- Bush, J. W. M., MIT, *HQA Lecture 8: Water waves*: relacion de dispersion
  gravitocapilar y profundidad finita.
  https://thales.mit.edu/bush/wp-content/uploads/2024/03/Lec-8-Waves.pdf
- ITTC (2024), *Estimation of Roll Damping*, revision 02: balanceo y
  caracterizacion del amortiguamiento.
  https://ittc.info/media/11942/75-02-07-045.pdf

Las fuentes sustentan las ondas y la estructura dinamica general, no los
parametros de acoplamiento elegidos ni su validez para este recipiente real.
