# Estado operativo de NuRus

Actualizado: 12 de septiembre de 2026. Rama: `implementacion-plan-2026-09-08`. Aplicación: `0.3.0.dev4`; motor: `0.2.1`; esquema SQLite: 8. Evidencia y cambios: [revisión automatizada](REVISION_AUTOMATIZADA_20260912.md). Los informes anteriores describen sus versiones y no sustituyen este estado.

## Objetivo e invariantes vigentes

NuRus produce propuestas para revisar cada registro en RUS. La observación oficial queda en RUS; Excel conserva la constancia humana y alimenta correos, estadísticas y proyectos. NuRus no registra información en RUS/SATURNO ni envía correos: Outlook solo guarda borradores. Cada correo incluye CC a `ucc_concepcion@pjud.cl`.

Los originales se conservan y archivan por hash. Las exportaciones se realizan sobre copias, incluyen las filas excluidas marcadas con color y mantienen las hojas OB y Medidas vencidas como parte del original, sin analizarlas como productos. La fidelidad completa de Office debe comprobarse en el equipo institucional; la ruta portable solo se ofrece con aceptación explícita de sus límites.

Cumplimiento sin hoja de cruce permite excepción documentada con responsable y motivo. Una ambigüedad entre hojas exige selección explícita; no se convierte en ausencia de cruce. Las plantillas y valores institucionales no se reinterpretan por decisión técnica.

## Implementado

- Motor común de Espera, Cumplimiento e Informes, lector de `.xls/.xlsx/.xlsm`, búsqueda de encabezados y selección explícita de hojas desde la interfaz.
- Archivo, hash, hoja y fila física en cada registro; hash del catálogo evaluado y conservación de la entrada original.
- Exportación de propuestas antes de la revisión humana; nueva salida final desde la constancia congelada, con OBSERVACION, FECHA_OBS, TT, CC y RES.
- Importación de revisiones parciales, verificación de ID e identidad, procedencia por devolución y cierre solo cuando las filas revisables tienen constancia. La edición/restauración invalida la confirmación anterior de la fila.
- Ruta de revisión recordada por lote; **Usar revisión guardada** evita elegir el archivo para cada producto; **Retomar lote…** recupera el mismo trabajo tras reiniciar.
- Correos agrupados, comunicaciones particulares, nóminas limitadas al grupo, contactos con vista previa, plantillas versionadas y proyectos Word desde matrices identificadas.
- Borradores Outlook con aprobación, cuenta/carpeta, adjuntos verificados sobre copias estables y tratamiento de guardado incierto. Contador de Enviados de solo lectura.
- Estadísticas por fecha con valores administrativos originales; separación entre exclusión, falta de confirmación, fecha inválida y fuera de período.
- Productos nuevos protegidos contra sobrescritura y limpieza de archivos parciales ante errores capturados. Texto externo protegido contra fórmulas en las salidas nuevas.
- Instalación aislada no editable, detección de Python 3.12 y CI Windows/Linux con paquete instalado, recursos, construcción de wheel, compilación y pruebas.

## Límites y pendientes materiales

1. Ejecutar [aceptación institucional](ACEPTACION_INSTITUCIONAL_20260910.md) en Windows 10, Excel 2010 y Outlook clásico. CI y simulaciones COM no equivalen a esa aceptación.
2. Ratificar matrices funcionales/jurídicas, destinatarios y adjuntos con los documentos institucionales vigentes. TT/CC/RES se cuentan tal como fueron consignados; falta un diccionario institucional aprobado para reinterpretarlos.
3. Obtener el `.xls` exacto de Espera que produjo el error de las capturas si persiste tras actualizar. El archivo entregado y comprobado anteriormente es de Cumplimiento; no demuestra por sí mismo el caso de Espera.
4. Mantener revisión humana por registro y documentar cualquier excepción de cruce. NuRus no puede acreditar por su cuenta que una observación fue ingresada en RUS.

## Continuidad

[G-ESTADO] Se implementaron las correcciones técnicas identificadas en esta revisión; el estado de publicación y CI se acredita con el commit y su ejecución en GitHub Actions. No se declara aptitud productiva hasta completar los pendientes institucionales.

[L-SIGUIENTE] Tras la verificación remota, ejecutar A01 y A05–A07/A14 en el PC institucional con una copia autorizada, registrando versión y resultado de Excel.
