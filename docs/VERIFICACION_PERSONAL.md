> Actualización vigente: **0.4.0.dev7**, 21-09-2026. Consultar `REVISION_USABILIDAD_20260921.md` para cambios y comprobaciones posteriores. La evidencia fechada que sigue corresponde a dev6.

# Verificación CSMP personal

Versión documental: **0.4.0.dev6**.

## Evidencia automatizada

**Checkpoint comprobado:** `0523f3cb666a7e55b6a4fd64eb92949c89a58e26`, GitHub Actions run `35127052431` (16-09-2026): los jobs Windows Python 3.12, 3.13 y 3.14 concluyeron `success`. En Python 3.12 la suite registró **230 passed, 1 skipped**; también pasaron smoke GUI, construcción del wheel y distribución `CSMP-Windows-dev6`.

La revisión 0.4.0.dev6 se valida en GitHub Actions exclusivamente sobre Windows con Python 3.12, 3.13 y 3.14. Los tres entornos deben completar instalación, wheel, recursos instalados, dependencias, compilación y suite. Python 3.12 además ejecuta el smoke de la GUI y construye la distribución `CSMP-Windows-dev6`.

Los contratos automáticos verifican además:

- sincronía de versión entre paquete y documentos vigentes;
- cinco parches de matrices y seis matrices base Laja/Mulchén;
- ausencia de la antigua capa `runtime_fixes_20260916*`;
- ausencia de basura generada común (`__pycache__`, `.pyc`, `.pyo`, `.DS_Store`, `Thumbs.db`);
- captura/exportación de edición humana con estados `REVISADO` y `PENDIENTE`;
- preservación de campos de revisión originales no editados;
- neutralización de fórmulas en observaciones;
- identidad estable de borradores aunque el mismo adjunto se regenere bajo otra ruta temporal;
- precedencia del tipo de resolución y deduplicación por tribunal/RIT/tipo;
- modificación individual del tipo de resolución;
- correspondencia nombre/cédula para varios NNA y fechas judiciales íntegramente en palabras.

La fuente de cierre sigue siendo el run correspondiente al SHA que se pretende adoptar. El dato anterior documenta el último checkpoint de código previo a la consolidación documental del 20-09; una modificación funcional posterior exige nueva CI.

## Matrices y recursos

El paquete instalado debe contener exactamente seis matrices base de Laja/Mulchén y cinco payloads de revisión. Cada payload se decodifica, descomprime y valida por SHA-256. La regresión cubre migración, respaldo, preservación de edición posterior y reposición de matriz eliminada.

## Límites de esta evidencia

GitHub Actions usa Windows Server, no el PC institucional. La verificación automática no acredita Excel 2010, Outlook clásico, cuenta/firma institucional, tiempos reales del ciclo mensual ni corrección jurídica de un proyecto concreto. No se usan causas reales en CI.

[COMPROBADO POR DISEÑO] El adaptador Outlook del producto personal solo guarda borradores; no existe una ruta autorizada de envío automático desde CSMP Assistant.

## Cierre de verificación del 20 de septiembre de 2026

GitHub Actions run `35535124753`, commit `574955b5e63608ff7bcf16db29ee36d859a59385`: **success** en Windows con Python 3.12, 3.13 y 3.14. En Python 3.12: **230 passed, 1 skipped**; también aprobaron el smoke de la GUI, la construcción del wheel y la distribución `CSMP-Windows-dev6`. Este commit contiene el estado consolidado y el contrato que exige su presencia. Los commits posteriores de cierre documental usan `[skip ci]` y no modifican runtime ni pruebas.

## Estado al 20 de septiembre de 2026

La aceptación institucional sigue pendiente. El hecho de que CI esté verde no acredita Excel 2010, Outlook clásico, firma/cuenta institucional ni ahorro real de tiempo. Esos puntos deben cerrarse mediante `ACEPTACION_CSMP_PERSONAL.md`.
