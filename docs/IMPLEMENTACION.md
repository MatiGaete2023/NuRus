# Estado operativo del repositorio NuRus

Actualizado: 16 de septiembre de 2026. Rama auditada: `csmp-personal-2026-09-13`. Versión del paquete: **0.4.0.dev6**.

## Alcance actual

El repositorio contiene el núcleo general/histórico de NuRus y la aplicación personal `CSMP Assistant`. El núcleo general no se elimina: mantiene scripts de entrada y cobertura de pruebas propios. Para esta rama, el estado operativo vigente del producto personal se documenta en `IMPLEMENTACION_PERSONAL.md`. Los informes fechados anteriores se conservan como evidencia histórica y no describen automáticamente el comportamiento vigente.

Invariantes: solo Windows para CSMP Assistant; no escribir en RUS/SATURNO; no enviar correos; Outlook solo guarda borradores; el Excel original se conserva; los productos son insumos para revisión humana.

## Estado técnico

- Python soportado: 3.12, 3.13 y 3.14.
- CI: Windows para esta rama, con Actions actuales basadas en Node 24.
- Exportación: copia preservada; captura las ediciones humanas visibles antes de exportar, distingue `REVISADO`/`PENDIENTE` y conserva neutralización de fórmulas.
- Cumplimiento sin cruce utilizable: C-10 no se evalúa y se deja advertencia; el flujo personal continúa sin exigir excepción.
- Resoluciones: seis matrices base Laja/Mulchén; Tomé sigue sin matriz fuente. Una fila visible por tribunal/RIT/tipo; precedencia tipo explícito en `RES` > observación revisada > regla del motor.
- Correos: borradores en lote, sin envío automático, con identidad estable por contenido; las rutas temporales de adjuntos no generan falsos borradores nuevos.
- Arquitectura personal: eliminados los módulos transitorios `runtime_fixes_20260916*`; las correcciones están en los módulos definitivos.

## Documentación

`INDICE_DOCUMENTACION.md` identifica documentos vigentes e históricos. `AUDITORIA_REPOSITORIO_20260916.md` registra el alcance y las decisiones de limpieza de esta revisión. `VERIFICACION_PERSONAL.md` describe evidencia automatizada y límites de aceptación.

[G-ESTADO] Rama personal consolidada en **0.4.0.dev6**, sin capa de monkey-patching transitoria.
[L-SIGUIENTE] Ejecutar la aceptación Office institucional con una copia autorizada y registrar cualquier diferencia reproducible.
