# Verificación vigente — CSMP Assistant personal 0.4.0.dev8

Estado: cambios implementados; validación Windows pendiente de resultado. No atribuir el resultado dev7 a esta revisión. La auditoría y el alcance están en `LIMPIEZA_ASISTENTE_20260921.md`.

## Verificación prevista

Windows con Python 3.12, 3.13 y 3.14: instalación, wheel y recursos instalados, dependencias, compilación y suite. Python 3.12 añade ventana real de cinco áreas, geometría 1024×650 y distribución Windows. Las regresiones incluyen acceso único, hoja al cambiar de modo, conservación de resoluciones, cambio de copia, editores y reglas desactivadas.

## Evidencia anterior (dev7)

Commit `86e8ba8e095db5aa97e9d1a0fae8a51937633c2d`, run [35551027804](https://github.com/MatiGaete2023/NuRus/actions/runs/35551027804): éxito Windows 3.12/3.13/3.14; 239 aprobadas y 1 omitida por versión. Ventana real y distribución aprobadas. `REVISION_USABILIDAD_20260921.md` conserva detalles y límites. Dev8 retira seis pruebas de la interfaz antigua y añade diez regresiones del Asistente; no son suites idénticas.

## Límites

CI utiliza Windows Server y archivos sintéticos. No acredita Excel 2010, Outlook clásico con cuenta/firma institucional ni ahorro de tiempo real. Sigue pendiente `ACEPTACION_CSMP_PERSONAL.md`. El adaptador conserva exclusivamente la operación de guardar borradores; no hay envío automático ni escritura en RUS/SATURNO.
