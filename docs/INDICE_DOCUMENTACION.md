# Índice y vigencia de documentación

Actualizado: 20 de septiembre de 2026. Versión vigente: **0.4.0.dev6**.

## Documentos vigentes para CSMP Assistant personal

- `ESTADO_CONSOLIDADO_20260920.md`: **referencia canónica de estado**; reúne evolución, observaciones del usuario, soluciones, decisiones, conflictos y próximos pasos.
- `../README.md`: instalación, uso y alcance actual.
- `IMPLEMENTACION.md`: portada del estado operativo del repositorio.
- `IMPLEMENTACION_PERSONAL.md`: estado funcional/técnico de 0.4.0.dev6.
- `AUDITORIA_REPOSITORIO_20260916.md`: auditoría integral y limpieza de código del 16-09-2026; evidencia fechada que complementa el estado consolidado.
- `CAMBIOS_USO_20260916.md`: cambios funcionales y técnicos vigentes incorporados el 16-09-2026.
- `VERIFICACION_PERSONAL.md`: evidencia automática y límites.
- `ACEPTACION_CSMP_PERSONAL.md`: protocolo de prueba institucional.
- `MATRIZ_REGLAS_PERSONAL.json`: índice documental de reglas, sincronizado con `textos_base.json`.
- `REFERENCIA_CATALOGO_ASISTENTE.md`: referencia congelada de reglas de dominio; una modificación de regla exige actualizar código y pruebas.

## Documentos históricos

- `CAMBIOS_USO_20260914.md`: estado consolidado de la versión 0.4.0.dev5 al 14-09-2026. Se conserva como trazabilidad y no describe la release vigente.
- Los documentos fechados entre el 8 y el 13 de septiembre (`AUDITORIA_*`, `CHECKPOINT_*`, `REVISION_*`, `EJECUCION_*`, `RENDIMIENTO_*`, `README_NURUS_DEV7.md`, `INSTALACION_Y_EXCEPCION_*` y equivalentes) describen estados anteriores. Se conservan para trazabilidad y **no sustituyen** los documentos vigentes anteriores.

Referencias históricas a CI Linux, versiones dev1/dev2/dev6/dev7 anteriores, excepción obligatoria de cruce o arquitecturas previas deben interpretarse dentro de su fecha. La coincidencia del identificador “dev6” con documentación histórica no convierte aquella documentación en vigente: la release actual se identifica además por la rama y el SHA del 16-09-2026.

La rama `revision-producto-csmp-2026-09-13` conserva una auditoría documental independiente del 13-09; sus conclusiones relevantes están incorporadas en `ESTADO_CONSOLIDADO_20260920.md` y no requieren fusionar su runtime.

El núcleo general de NuRus y sus documentos propios no se clasifican como basura: mantienen componentes, entradas o pruebas distintas del producto personal. La auditoría actual elimina código transitorio ejecutable cuando existe reemplazo definitivo comprobable, pero conserva evidencia histórica.
