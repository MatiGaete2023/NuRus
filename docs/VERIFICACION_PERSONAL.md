# Verificación CSMP personal

Versión documental: **0.4.0.dev6**.

## Evidencia automatizada

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

La fuente de cierre es siempre el run correspondiente al SHA actual de la rama; números de ejecuciones anteriores se consideran evidencia histórica, no garantía de una versión posterior.

## Matrices y recursos

El paquete instalado debe contener exactamente seis matrices base de Laja/Mulchén y cinco payloads de revisión. Cada payload se decodifica, descomprime y valida por SHA-256. La regresión cubre migración, respaldo, preservación de edición posterior y reposición de matriz eliminada.

## Límites de esta evidencia

GitHub Actions usa Windows Server, no el PC institucional. La verificación automática no acredita Excel 2010, Outlook clásico, cuenta/firma institucional, tiempos reales del ciclo mensual ni corrección jurídica de un proyecto concreto. No se usan causas reales en CI.

[COMPROBADO POR DISEÑO] El adaptador Outlook del producto personal solo guarda borradores; no existe una ruta autorizada de envío automático desde CSMP Assistant.
