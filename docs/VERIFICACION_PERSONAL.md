# Verificación CSMP personal

Versión documental: **0.4.0.dev4**.

## Evidencia automatizada

La línea base inmediatamente anterior a esta revisión documental fue el commit `093c74a4cf53e5bf92846139fc184884a18d8397`: GitHub Actions en Windows 3.12, 3.13 y 3.14 terminó en `success`. En Python 3.13 se registraron **191 pruebas aprobadas y 1 omitida**. Los tres entornos verificaron instalación, wheel, dependencias, compilación y los cinco parches de matrices; Python 3.12 además aprobó el smoke de GUI y construyó la distribución Windows.

La release 0.4.0.dev4 conserva los contratos de sincronía entre `MATRIZ_REGLAS_PERSONAL.json` y `textos_base.json`, coherencia de versión/documentación y exclusión de `.venv-csmp`/artefactos de build. Agrega regresiones para fechas judiciales íntegramente en palabras, preparación integral de correos por modo + acciones, persistencia de `NURUS_REGLAS` y recuperación desde trazabilidad de exportaciones anteriores. El run final debe consultarse sobre el HEAD de la rama.

## Matrices y recursos

El paquete instalado debe contener exactamente seis matrices base de Laja/Mulchén y cinco payloads de revisión. Cada payload se decodifica, descomprime y valida por SHA-256. La regresión cubre migración, respaldo, preservación de edición posterior y reposición de matriz eliminada.

## Límites de esta evidencia

GitHub Actions usa Windows Server, no el PC institucional. La verificación automática no acredita Excel 2010, Outlook clásico, cuenta/firma institucional, tiempos reales del ciclo mensual ni corrección jurídica de un proyecto concreto. No se usan causas reales en CI.

[COMPROBADO] No existe ninguna llamada de envío de correo en el código de la rama personal; Outlook se usa para guardar borradores y consultar Enviados.
