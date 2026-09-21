# Estado operativo — CSMP Assistant personal

Actualizado: 21 de septiembre de 2026. Versión **0.4.0.dev9**. Único producto: Asistente personal Windows, Python 3.12–3.14.

## Código vigente

- Entrada: `Abrir_CSMP.bat` → `nurus.personal.app`. Los accesos anteriores solo redirigen aquí.
- `personal/app.py` define el flujo; `app_base.py` los controles compartidos, sin métodos operativos duplicados. La antigua clase `NuRusApp` y `product_ui.py` fueron retiradas.
- Lectores, exportación preservada, adaptadores Office y servicios compartidos se conservan. No se cambia el formato de configuración, sesiones ni planillas existentes.
- Una sola carga, cinco áreas, productos editables; sin aprobación individual ni envío automático. Original intacto, excluidos coloreados; nunca escribe RUS/SATURNO.
- Cumplimiento sin cruce advierte y omite C-10. No requiere excepción.
- Un Word agrupado por tribunal/RIT/tipo; seis matrices Laja/Mulchén. No se inventan matrices Tomé.

La limpieza y las correcciones de uso están en `LIMPIEZA_ASISTENTE_20260921.md`. `VERIFICACION_PERSONAL.md` registra el SHA y resultado de CI, sin confundir ejecuciones anteriores con el código actual. `INDICE_DOCUMENTACION.md` separa instrucciones vigentes de informes históricos.

Verificación vigente: commit `c262321e227302cc9349061a941c06af29879219`, run `35646164874`, Windows Python 3.12/3.13/3.14 **success**, 254 pruebas aprobadas y 1 omitida por versión; smoke CustomTkinter y distribución dev9 correctos en 3.12.

Pendientes externos: aceptación Office institucional, decisión DCE, matrices Tomé y medición real de ahorro de trabajo. No se añaden pasos de aprobación para resolverlos.
