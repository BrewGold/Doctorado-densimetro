# Doctorado SIM (paralelo al TFM)

Este módulo extiende el TFM sin alterar su estructura original.
Objetivo: simular cápsula desbalanceada + IMU + ruido + efectos de viscosidad/tensión superficial.

## Base de investigación

Las [conclusiones de trabajo y preliminares](../docs/PRELIMINARES_INVESTIGACION.md) recogen las decisiones metodológicas, sus supuestos y las hipótesis pendientes para continuar la identificación experimental.

## Ejecución rápida
1. Abrir MATLAB en la raíz del repo.
2. Ejecutar:
   run('doctorado_sim/sim/scenarios/run_baseline.m')

## Salidas
- CSV sintético en `doctorado_sim/data/synthetic/`
- Figuras en `doctorado_sim/results/figures/`
- Tabla resumen en `doctorado_sim/results/tables/`

## Convenciones
- theta_rad, omega_rads, rho_gcm3, mu_pas, sigma_npm

## Balanceo amortiguado y modo del agua

Simulacion exploratoria independiente del baseline, compatible con MATLAB y
GNU Octave. Desde la raiz:

```matlab
addpath('doctorado_sim/sim/scenarios');
run_wave_rebound();
addpath('doctorado_sim/tests');
test_wave_rebound();
```

Genera `results/wave_rebound/wave_rebound.csv`, un grafico PNG y un PDF:
balanceo aislado con envolvente exponencial, balanceo acoplado, coordenada del
agua y balance de energia. Los archivos tienen nombres fijos y se sobrescriben
al repetir la ejecucion; puede pasarse otro directorio a `run_wave_rebound`.
El CSV se regenera y se excluye de Git; se incluyen las figuras de referencia.
En Octave sin interfaz grafica se necesita un backend como gnuplot, fuentes
y Ghostscript para exportar las figuras.

El [modelo y sus limites](docs/WAVE_REBOUND_MODEL.md) explican por que puede
recuperarse la amplitud de la capsula mientras disminuye la energia total.
Los parametros son ilustrativos: no se ha ajustado el modelo a los registros
ni demostrado que sus modulaciones procedan de ondas reflejadas.
