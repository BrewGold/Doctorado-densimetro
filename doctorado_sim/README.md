# Doctorado SIM (paralelo al TFM)

Este módulo extiende el TFM sin alterar su estructura original.
Objetivo: simular cápsula desbalanceada + IMU + ruido + efectos de viscosidad/tensión superficial.

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
