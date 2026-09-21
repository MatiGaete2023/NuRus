# Verificación vigente — CSMP Assistant personal 0.4.0.dev9

Estado: implementación de panel y correos terminada; CI Windows pendiente de cierre. Ver `PANEL_CORREOS_20260921.md`.

Base dev8: commit `bab202e9533e88b5130a277f01b90b816e98940e`, [run 35620647820](https://github.com/MatiGaete2023/NuRus/actions/runs/35620647820) exitoso. La prueba inicial incorrecta fue corregida en esa base; no se atribuye su resultado a los cambios dev9.

Verificación: Windows Python 3.12, 3.13 y 3.14; instalación, wheel, recursos, dependencias y suite. La prueba de interfaz usa CustomTkinter real en Windows, revisa cinco áreas, tarjetas, adjuntos, campos, conservación de ediciones y tamaño 1024×650; genera capturas con datos sintéticos.

Límites: Windows Server en CI no equivale a Excel 2010/Outlook institucional. Aceptación Office, DCE, Tomé y medición del ciclo real permanecen pendientes. No se envían correos ni se usan causas reales en las pruebas.
