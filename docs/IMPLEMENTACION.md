# Estado operativo — CSMP Assistant personal

Actualizado: 29 de septiembre de 2026. Versión **0.4.0.dev13**. Único producto: Asistente personal Windows, Python 3.12–3.14. La referencia actual es [REVISION_Y_PLAN_20260929.md](REVISION_Y_PLAN_20260929.md); los resultados de versiones anteriores que siguen son evidencia histórica.

## Código vigente

- Entrada: `Abrir_CSMP.bat` → `nurus.personal.app`. Los accesos anteriores solo redirigen aquí.
- `personal/app.py` define el flujo; `app_base.py` los controles compartidos, sin métodos operativos duplicados. La antigua clase `NuRusApp` y `product_ui.py` fueron retiradas.
- Lectores, exportación preservada, adaptadores Office y servicios compartidos se conservan. Las categorías de plantilla y preferencias adicionales son campos opcionales compatibles con configuraciones y sesiones anteriores.
- Una sola carga, cinco áreas, productos editables; sin aprobación individual ni envío automático. Trabajo y Resoluciones tienen búsqueda/filtros visuales; avisos y excepciones concentran el resaltado. Original intacto; nunca escribe RUS/SATURNO.
- Cumplimiento sin cruce advierte y omite C-10. No requiere excepción.
- Un Word agrupado por tribunal/RIT/tipo; `RES` categórico (`PC_IE`, `PC_INFO`, `NOMENCL`) es la fuente humana prioritaria; seis matrices Laja/Mulchén. No se inventan matrices Tomé.

La limpieza y las correcciones de uso están en `LIMPIEZA_ASISTENTE_20260921.md`. `VERIFICACION_PERSONAL.md` registra el SHA y resultado de CI, sin confundir ejecuciones anteriores con el código actual. `INDICE_DOCUMENTACION.md` separa instrucciones vigentes de informes históricos.

Verificación dev10 previa: commit `8546dab08ae9976c2e0f26810e2e49d5fee30ced`, run `35729404913`, Windows Python 3.12/3.13/3.14 **success**, 256 pruebas aprobadas y 1 omitida por versión. El cierre dev11 se registra en `VERIFICACION_PERSONAL.md`.

Pendientes externos: aceptación Office institucional, decisión DCE, matrices Tomé y medición real de ahorro de trabajo. No se añaden pasos de aprobación para resolverlos.
