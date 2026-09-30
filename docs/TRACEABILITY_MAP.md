# Mapa de trazabilidad — TFM → Doctorado

Este documento conecta explícitamente los elementos del TFM con su evolución en el trabajo doctoral.

## 1. Objetivo

Asegurar continuidad metodológica, evitar ambigüedades y justificar técnicamente qué se reutiliza, qué se modifica y qué se reemplaza.

## 2. Regla general

- El TFM en `references/tfm/` es **material de referencia**.
- El desarrollo activo vive en `doctorado_sim/`.
- Toda reutilización debe registrarse en este mapa.

## 3. Referencia base

- **TFM:** *Estimación de densidad de fluidos mediante orientación angular*
- **Archivo:** `references/tfm/Densidad_orientacion_angular-F_Gold_Rev04.pdf`
- **Autor:** Fernando Gold Araoz
- **Tutor:** José Manuel Díaz
- **Centro:** Universidad Complutense de Madrid - UNED
- **Curso:** 2025-2026
- **Fecha:** 2026-09-15

## 4. Tabla de trazabilidad

| Elemento del TFM | Ubicación en TFM | Estado en doctorado | Ubicación nueva | Acción |
|---|---|---|---|---|
| Planteamiento de estimación por orientación angular | Documento principal, secciones conceptuales | Reutilizado parcial | `docs/` | Mantener el enfoque base y actualizar el alcance doctoral |
| Formulación hidrostática inicial | Documento principal, modelo | Replanteado | `doctorado_sim/docs/` | Adaptar al cuerpo cilíndrico con dos semiesferas y lastre excéntrico |
| Geometría del sensor/prototipo | Documento principal, diseño | Replanteado | `doctorado_sim/docs/` | Parametrizar dimensiones, centros y volumen desplazado |
| Procedimiento experimental preliminar | Documento principal o anexos | Reutilizado parcial | `docs/` | Convertirlo en protocolo reproducible con control de incertidumbre |
| Scripts y utilidades del TFM | `references/tfm/` si hay snapshots | Referencia histórica | `references/tfm/snapshots/` | No ejecutar como pipeline activo sin validación |
| Resultados del TFM | Documento principal o anexos | Comparativo | `docs/` | Usarlos como línea base para contrastar mejoras doctorales |

## 5. Estados permitidos

- **Reutilizado:** se incorpora casi igual, con revisión menor.
- **Reutilizado parcial:** se aprovecha la estructura o la idea, pero se modifica.
- **Replanteado:** se rehace el enfoque o las ecuaciones.
- **Descartado:** no se incorpora en la fase doctoral.

## 6. Criterios de aceptación de reutilización

Un elemento del TFM solo pasa a estar activo en el doctorado si cumple:

1. hipótesis explícitas y vigentes;
2. unidades y parámetros documentados;
3. reproducibilidad mínima garantizada;
4. compatibilidad con la geometría objetivo: cilindro con dos semiesferas;
5. validación básica contra simulación o datos.

## 7. Checklist de migración

- [ ] Confirmar la ruta real del PDF y de los anexos.
- [ ] Identificar scripts, datos y resultados reutilizables.
- [ ] Definir los parámetros geométricos nominales del prototipo.
- [ ] Documentar por separado la contribución estática de equilibrio.
- [ ] Documentar la contribución dinámica de amortiguamiento y arrastre.
- [ ] Comparar los resultados nuevos con la línea base del TFM.
- [ ] Registrar cada decisión en este mapa y en `references/notes/`.
