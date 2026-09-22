# Verificación vigente — CSMP Assistant personal 0.4.0.dev10

Estado: **candidato dev10 validado por CI Windows**. El cambio final incorpora `RES` categórico, validación Excel y origen visible en Resoluciones.

## Evidencia vigente

Commit funcional y contrato: `8546dab08ae9976c2e0f26810e2e49d5fee30ced`. GitHub Actions run `35729404913`: **success** en Windows con Python 3.12, 3.13 y 3.14.

Resultados:
- Python 3.12: **256 passed, 1 skipped**; smoke CustomTkinter correcto; construcción de distribución Windows correcta.
- Python 3.13: **256 passed, 1 skipped**.
- Python 3.14: **256 passed, 1 skipped**.

Dev10 comprueba:
- desplegable `PC_IE / PC_INFO / NOMENCL` en la columna RES de las copias nuevas;
- `RES` vacío como decisión autoritativa de no generar proyecto al reimportar una copia revisada;
- lectura compatible de marcas antiguas como `1` o `X`;
- advertencia por valores RES desconocidos, sin corrección automática;
- etiqueta `Definido en RES` cuando el tipo es explícito;
- ajuste manual en Resoluciones preservado como corrección final;
- invariantes existentes de Excel, Outlook solo borradores, Word y configuración.

Python 3.12 también produjo las capturas de interfaz `CSMP-Windows-interface`. El job construyó la distribución `CSMP-Windows-dev10` y los tres wheels del paquete.

## Límites

CI usa Windows Server y datos sintéticos. No acredita todavía Excel 2010 ni Outlook clásico con cuenta/firma institucional, corrección jurídica de cada proyecto ni ahorro real de tiempo. Esos puntos siguen en `ACEPTACION_CSMP_PERSONAL.md`. El producto no envía correos y no escribe en RUS/SATURNO.
