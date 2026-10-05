# Índice y vigencia de documentación

**Prototipo 0.4.0.dev16 · 5 de octubre de 2026.** Conserva la base corregida dev14, el flujo conjunto y las alertas. Añade diario recuperable y conciliación de fechas con Excel. El adaptador real de bitácoras y registro sigue pendiente; la interfaz todavía no escribe observaciones en RUS. Véanse REGISTRO_RECUPERABLE_20261005.md y ESTADO_PLAN_INTEGRAL_20261005.md. Las secciones anteriores a este avance se conservan como antecedentes, no como aceptación de las funciones nuevas.


Actualizado: 30 de septiembre de 2026. Versión de trabajo: **0.4.0.dev14** en `codex/auditoria-ux-20260925-final`. `main` conserva la candidata anterior hasta su integración.

## Documentos vigentes para CSMP Assistant personal

- `REVISION_Y_PLAN_20260929.md`: referencia actual de revisión, pasos de implementación y evidencia por cada mejora.
- `CORRECCION_ADJUNTOS_20260930.md`: parche dev14 de bordes y campos operativos de nóminas.
- `../README.md`: instalación, actualización y uso de dev14.
- `VERIFICACION_PERSONAL.md`: resultados registrados y límites de validación.
- `ACEPTACION_CSMP_PERSONAL.md`: protocolo de Office y aceptación real fechada, sin trasladar resultados antiguos a dev14.
- `IMPLEMENTACION.md`: portada operativa actual.
- `IMPLEMENTACION_AUDITORIA_20260928.md`: cambios heredados en integridad, recuperación y edición.
- `correccion_mulchen_20260928.md` y `correccion_residencial_20260929.md`: antecedentes del arreglo de Mulchén y RTA/RTT/RVA.

## Referencias funcionales y checkpoints anteriores

- `UX_OBSERVACIONES_DEV12_20260922.md`: checkpoint de la evolución dev12, redacciones aprobadas, UX acotada, límites y validación pendiente.

- `CONGELAMIENTO_CANDIDATA_20260922.md`: checkpoint funcional congelado, política de cambios y criterio para avanzar hacia 1.0.
- `UX_FINAL_20260922.md`: pulido final de búsqueda, filtros, contexto, atajos y visualización por excepción.
- `RES_CATEGORICO_20260922.md`: cierre funcional de `RES` como tipo explícito, validación, compatibilidad y UX de Resoluciones.
- `PANEL_CORREOS_20260921.md`: panel oscuro dev9, alcance de destinatarios, plantilla del manual y verificación.
- `LIMPIEZA_ASISTENTE_20260921.md`: auditoría dev8, código retirado, errores corregidos y verificación.
- `REVISION_USABILIDAD_20260921.md`: evidencia fechada de dev7; mejoras previas que se conservan.

- `ESTADO_CONSOLIDADO_20260920.md`: checkpoint histórico; reúne evolución, observaciones del usuario, soluciones y decisiones anteriores.
- `../README.md`: instalación, uso y alcance actual.
- `IMPLEMENTACION.md`: portada del estado operativo del repositorio.
- `IMPLEMENTACION_PERSONAL.md`: comportamiento funcional vigente, incluido el alcance de correos y cierre dev9.
- `AUDITORIA_REPOSITORIO_20260916.md`: auditoría integral y limpieza de código del 16-09-2026; evidencia fechada que complementa el estado consolidado.
- `CAMBIOS_USO_20260916.md`: cambios funcionales y técnicos vigentes incorporados el 16-09-2026.
- `VERIFICACION_PERSONAL.md`: evidencia automática y límites.
- `ACEPTACION_CSMP_PERSONAL.md`: protocolo de prueba institucional.
- `MATRIZ_REGLAS_PERSONAL.json`: índice documental de reglas, sincronizado con `textos_base.json`.
- `REFERENCIA_CATALOGO_ASISTENTE.md`: referencia congelada de reglas de dominio; una modificación de regla exige actualizar código y pruebas.

## Documentos históricos

- `CAMBIOS_USO_20260914.md`: estado consolidado de la versión 0.4.0.dev5 al 14-09-2026. Se conserva como trazabilidad y no describe la release vigente.
- Los documentos fechados entre el 8 y el 13 de septiembre (`AUDITORIA_*`, `CHECKPOINT_*`, `REVISION_*`, `EJECUCION_*`, `RENDIMIENTO_*`, `README_NURUS_DEV7.md`, `INSTALACION_Y_EXCEPCION_*` y equivalentes) describen estados anteriores. Se conservan para trazabilidad y **no sustituyen** los documentos vigentes anteriores.

Referencias históricas a CI Linux, versiones anteriores, excepción obligatoria de cruce o arquitecturas previas deben interpretarse dentro de su fecha. La versión de trabajo actual es 0.4.0.dev13. La evidencia nueva se registra en `REVISION_Y_PLAN_20260929.md`; `VERIFICACION_PERSONAL.md` conserva también los resultados fechados anteriores.

La rama `revision-producto-csmp-2026-09-13` conserva una auditoría documental independiente del 13-09; sus conclusiones relevantes están incorporadas en `ESTADO_CONSOLIDADO_20260920.md` y no requieren fusionar su runtime.

La interfaz NuRus, `product_ui.py`, el benchmark histórico y las versiones duplicadas de métodos del Asistente se retiraron en dev8. El historial Git conserva sus fuentes. Se mantienen los servicios compartidos y sus regresiones; el nombre técnico `nurus` no designa un segundo producto activo.
