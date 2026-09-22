# Verificación vigente — CSMP Assistant personal 0.4.0.dev10

Estado: **CI de dev10 en ejecución**. El cambio funcional es acotado a `RES` categórico, validación Excel y origen visible en Resoluciones.

Base previa acreditada: dev9, commit `c262321e227302cc9349061a941c06af29879219`, run `35646164874`: Windows Python 3.12/3.13/3.14 success, 254 passed y 1 skipped por versión, smoke CustomTkinter y distribución dev9 correctos.

Dev10 debe comprobar:
- desplegable `PC_IE / PC_INFO / NOMENCL` en la columna RES de las copias nuevas;
- lectura compatible de marcas antiguas como `1` o `X`;
- advertencia por valores RES desconocidos, sin corrección automática;
- etiqueta `Definido en RES` cuando el tipo es explícito;
- ajuste manual en Resoluciones preservado como corrección final;
- invariantes existentes de Excel, Outlook solo borradores, Word y configuración.

La aceptación con Excel 2010/Outlook institucional sigue definida en `ACEPTACION_CSMP_PERSONAL.md`.
