# Verificación vigente — CSMP Assistant personal 0.4.0.dev9

Estado: **candidato dev9 validado por CI Windows**. Panel CustomTkinter, alcance de destinatarios y limpieza previa integrados. La aceptación institucional con Office real continúa separada.

## Evidencia vigente

Commit de runtime y pruebas: `c262321e227302cc9349061a941c06af29879219`. GitHub Actions run `35646164874`: **success** en Windows con Python 3.12, 3.13 y 3.14.

En cada versión se ejecutaron **254 passed, 1 skipped**. Python 3.12 ejecutó además el smoke de la ventana real CustomTkinter, que comprobó las cinco áreas, tarjetas seleccionables, conservación de ediciones al cambiar alcance, eliminación individual de adjuntos, editor de correo utilizable a 1024×650, configuración navegable y barra de progreso que vuelve a reposo.

Artefactos del mismo run:
- `CSMP-Windows-dev9`, distribución fuente Windows;
- `CSMP-Windows-interface`, capturas `correos-1024x650.png` y `configuracion-1024x650.png`;
- wheel para Python 3.12, 3.13 y 3.14.

La suite cubre además que **Solo programas** no incorpore el correo general al tribunal ni reutilice como correo de programa la plantilla de medidas; **Solo tribunales** conserva el informativo y medidas cuando corresponden; **Ambos** combina los grupos. La plantilla `programa_por_vencer` usa el texto del manual aportado para Informes por vencer y la migración conserva cuerpos personalizados.

## Base de limpieza

La limpieza dev8 quedó validada previamente en `bab202e9533e88b5130a277f01b90b816e98940e`, run `35620647820`. Dev9 conserva esa base: una sola interfaz operativa, sin `product_ui.py`, sin generador Word unitario obsoleto y con carga diferida del backend histórico que aún mantiene contratos compartidos.

## Límites

CI usa Windows Server y datos sintéticos. No acredita Excel 2010 ni Outlook clásico con cuenta/firma institucional, corrección jurídica de cada proyecto ni ahorro real de tiempo. Esos puntos siguen en `ACEPTACION_CSMP_PERSONAL.md`. El producto no envía correos y no escribe en RUS/SATURNO.
