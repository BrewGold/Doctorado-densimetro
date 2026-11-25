# Prototipo de PCB portadora

## Maqueta 0: distribución mecánica

Abrir `prototipo_mecanico.kicad_pcb` con el editor de PCB de KiCad 7 o posterior. Es una **maqueta, no una PCB eléctrica ni fabricable**: no contiene huellas, pads, taladros, redes, pistas, plano de masa ni conexiones. No generar archivos de fabricación a partir de ella. Los rectángulos en `F.Fab` representan las envolventes aproximadas de los módulos, no sus huellas; habilitar esa capa en el editor. La batería está representada bajo la placa en `B.Fab`; habilitarla para ver su reserva.

Para visualizarla sin KiCad, abrir [prototipo_mecanico.pdf](prototipo_mecanico.pdf). La imagen se regenera desde los rectángulos del archivo KiCad con `python3 hardware/pcb_portadora/generar_vista.py` y la biblioteca Python `reportlab`; el PDF separa las vistas superior y de batería para evitar solapamientos.

El contorno rectangular de **164 × 24 mm** es una primera hipótesis de empaquetado, no una medida de cápsula ni un contorno validado. Está organizado desde la tapa hacia la punta: receptor, boost, reserva para condensador, IMU, ESP32 y DRV8833. La bobina receptora y el actuador quedan fuera de la placa, cerca de la tapa y la punta respectivamente. Los espacios no incluyen necesariamente conectores, cables, tornillos, pines, antena, carrera, altura o accesibilidad.

| Reserva en la maqueta | Dimensiones de referencia (mm) | Estado |
|---|---:|---|
| Receptor | 18 × 15 | Dimensiones de la imagen; contactos sin verificar |
| MT3608 | 36 × 17 | Dimensiones comunicadas; posición de contactos estimada de imagen |
| Condensador C1 | 12 × 12 | **Espacio arbitrario**, no medida del componente 470 µF / 16 V |
| IMU | 25,40 × 17,78 | Referencia Adafruit 4438, identidad física pendiente |
| ESP32-C3 | 22,5 × 17,8 | Imagen seleccionada; separación de filas por confirmar |
| DRV8833 | 25,40 × 17,78 | Contorno Adafruit 3297; conectores y altura excluidos |
| Batería bajo la placa | 50 × 14 | Celda 14500 nominal; soporte, terminales y protección excluidos |

Las separaciones entre contornos son solo una primera propuesta, **no distancias eléctricas, térmicas o de antena validadas**. La ubicación de la batería es una hipótesis; deberá revisarse con el centro de masas, el soporte y la sección de la cápsula. El diseño no garantiza flotación, estanqueidad ni accesibilidad. La ubicación y orientación del ESP32 y el metal y cobre alrededor de la antena requieren revisión específica.

## Prototipo funcional: conexiones previstas

```text
Bobina de carga -- receptor/cargador -- batería 14500
                        |
                        +-- salida de carga por verificar -- MT3608
                                                             |
                                            C1 470 µF / 16 V en paralelo
                                                             |
                                             alimentación ESP32 por verificar
                                                             |
                           GPIO5 (SDA) / GPIO6 (SCL) -- IMU LSM6DSOX

Alimentación y protección por definir -- DRV8833 -- bobina del actuador
                                     ESP32 -- señales de control por definir
```

Es un esquema de intención, no una conexión para energizar. `BAT` y la posible salida de carga, sus polaridades y relación de masas siguen sin confirmar; no unir retornos ni conectar el boost sin comprobarlos. La alimentación del DRV8833, el comportamiento durante la carga, los GPIO, el control de corriente y la protección de batería y actuador están pendientes. El límite de 1 A del breakout no protege por sí solo el actuador de 0,41 A. Antes de accionar, validar guiado, posición inicial, finales de carrera y parada segura. La salida del MT3608 se ajusta y mide con las cargas desconectadas, y no se conecta 5 V al pin 3V3 del ESP32.

## Siguiente revisión antes del esquema eléctrico y la PCB

1. Identificar referencia y pinout del receptor, salida de carga, polaridades, protección y compatibilidad con la batería; confirmar corriente de carga y descarga.
2. Confirmar huellas y orientación con las unidades reales, paso de filas ESP32, contactos del boost, tipo y tamaño del condensador y envolvente completa del DRV8833.
3. Decidir la alimentación del puente y la limitación o medida de corriente, la detección de posición y la parada segura. Verificar límites térmicos y corriente admisible.
4. Crear el esquema KiCad con símbolos, conexiones y protecciones verificadas; completar huellas y actualizar el PCB desde el esquema. Comprobar distancias y efectuar ERC, DRC y revisión eléctrica y mecánica antes de fabricar.

Referencias y supuestos adicionales: [esquema funcional](../../docs/ESQUEMA_INICIAL_CONEXIONES.md) y [distribución interior](../../docs/DISTRIBUCION_INTERIOR_CAPSULA.md).
