> Actualización vigente: **0.4.0.dev7**, 21-09-2026. Consultar `REVISION_USABILIDAD_20260921.md` para cambios y comprobaciones posteriores. La evidencia fechada que sigue corresponde a dev6.

# Estado operativo del repositorio NuRus

Actualizado: 20 de septiembre de 2026. Rama auditada: `csmp-personal-2026-09-13`. Versión del paquete: **0.4.0.dev6**.

## Alcance actual

El estado transversal y la historia de decisiones se consolidan en `ESTADO_CONSOLIDADO_20260920.md`; este archivo queda como portada técnica breve.

El repositorio contiene el núcleo general/histórico de NuRus y la aplicación personal `CSMP Assistant`. El núcleo general no se elimina: mantiene scripts de entrada y cobertura de pruebas propios. Para esta rama, el estado operativo vigente del producto personal se documenta en `IMPLEMENTACION_PERSONAL.md`. Los informes fechados anteriores se conservan como evidencia histórica y no describen automáticamente el comportamiento vigente.

Invariantes: solo Windows para CSMP Assistant; no escribir en RUS/SATURNO; no enviar correos; Outlook solo guarda borradores; el Excel original se conserva; los productos son insumos para revisión humana.

## Estado técnico

- Python soportado: 3.12, 3.13 y 3.14.
- CI: Windows con Python 3.12, 3.13 y 3.14; cierre `574955b5…`, run `35535124753`, verde en los tres jobs. Python 3.12: **230 passed, 1 skipped**.
- Exportación: copia preservada; captura las ediciones humanas visibles antes de exportar, distingue `REVISADO`/`PENDIENTE` y conserva neutralización de fórmulas.
- Cumplimiento sin cruce utilizable: C-10 no se evalúa y se deja advertencia; el flujo personal continúa sin exigir excepción.
- Resoluciones: seis matrices base Laja/Mulchén; Tomé sigue sin matriz fuente. Una fila visible por tribunal/RIT/tipo; precedencia tipo explícito en `RES` > observación revisada > regla del motor.
- Correos: borradores en lote, sin envío automático, con identidad estable por contenido; las rutas temporales de adjuntos no generan falsos borradores nuevos.
- Arquitectura personal: eliminados los módulos transitorios `runtime_fixes_20260916*`; las correcciones están en los módulos definitivos.

## Documentación

`INDICE_DOCUMENTACION.md` identifica documentos vigentes e históricos. `ESTADO_CONSOLIDADO_20260920.md` es la referencia canónica para decisiones, quejas del usuario, soluciones y próximos pasos. `AUDITORIA_REPOSITORIO_20260916.md` registra el alcance y las decisiones de limpieza de esta revisión. `VERIFICACION_PERSONAL.md` describe evidencia automatizada y límites de aceptación.

[G-ESTADO] **0.4.0.dev6** consolidado y verificado; `main` y la rama personal deben apuntar al mismo cierre documental de esta revisión. No hay capa de monkey-patching transitoria.
[L-SIGUIENTE] Ejecutar ACEP-01 a ACEP-12 en el equipo institucional y resolver el conflicto DCE antes de declarar una release candidata.
