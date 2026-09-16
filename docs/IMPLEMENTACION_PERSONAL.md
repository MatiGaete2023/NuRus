# Implementación CSMP Assistant personal — 16 de septiembre de 2026

Versión **0.4.0.dev6**. Entrada: `Abrir_CSMP.bat`. Módulo: `nurus.personal.app`. El flujo visible tiene Trabajo, Correos, Resoluciones, Configuración y Enviados.

## Decisiones vigentes

Las observaciones que dejan constancia de una gestión ejecutada —por ejemplo, remitir correo o proyecto— usan redacción de gestión realizada para poder registrarse después en RUS sin reescritura. Las sugerencias sustantivas que forman parte del catálogo (curador, egreso por mayoría, actualización de ficha) conservan su naturaleza de sugerencia. Generar el texto no acredita que la gestión se haya ejecutado.

Ante dudas de reglas prevalece el perfil Asistente vigente. E-05 mantiene el diseño congelado del catálogo: DCE desde 30 días solo correo; Laja/Mulchén desde 30 días proyecto + correo; Tomé 30–59 solo correo y 60+ proyecto + correo.

Cumplimiento sin cruce utilizable no evalúa C-10, deja advertencia y continúa. El flujo personal no solicita ni exige documentar una excepción para exportar.

## Trabajo y exportación

Trabajo procesa `.xls/.xlsx/.xlsm`, conserva el original, exporta copia y permite actualizar cambios humanos por identidad estable. También puede cargar una planilla modificada/externa y reutilizarla en productos sin volver a ejecutar el motor.

La exportación captura automáticamente la observación visible antes de generar la copia. Si existe revisión humana, solo las filas efectivamente modificadas se marcan `REVISADO`; las restantes se marcan `PENDIENTE`. Los campos `OBSERVACION`, `FECHA_OBS`, `TT`, `CC` y `RES` se escriben desde la revisión sin borrar valores originales no modificados. La protección contra fórmulas iniciadas por `=`, `+`, `-` o `@` se mantiene.

Las exportaciones incluyen `NURUS_REGLAS` como columna técnica oculta. `Work.external` la usa para restaurar reglas y acciones después de editar/reabrir la planilla; si no existe, intenta recuperar reglas desde `NURUS_TRAZABILIDAD`.

## Correos

Correos permite seleccionar tribunal y modalidades, editar Para/CC/asunto/cuerpo/adjuntos y guardar un borrador o todo el lote. **Preparar TODOS los correos necesarios** construye el informativo general de la pestaña y cada comunicación específica respaldada por acciones del motor: `programa_espera`, `programa_vencido`, `programa_por_vencer` y `medidas`. Los productos `especial` y `proyectos` permanecen manuales.

**Guardar TODOS los borradores** funciona tanto con un lote ya preparado como sin vista previa previa: en este último caso prepara y guarda el conjunto necesario. No existe llamada de envío. Destinatarios ambiguos/desconocidos quedan vacíos; la CC institucional se conserva.

La deduplicación ya no depende de filas + asunto ni de la ruta temporal de los adjuntos. La clave se calcula desde destinatarios efectivos, CC, asunto, cuerpo, obligatoriedad y pares nombre/hash de adjunto. Dos nóminas idénticas generadas bajo directorios UUID distintos conservan la misma identidad; una modificación real cambia la clave.

## Resoluciones

Los tipos son `PC_IE`, `PC_INFO` y `NOMENCL`. La precedencia es: tipo explícito en `RES`; tipo inferido desde observación humana revisada; acción del motor; y solo para un caso expresamente marcado sin datos suficientes, tipo manual de respaldo.

Cuando `RES` no fue utilizado, una observación aislada no crea un proyecto nuevo: debe existir una acción de resolución del motor. La vista se deduplica antes de llegar a la interfaz y muestra una sola fila por tribunal + RIT + tipo. Cambiar el tipo exige seleccionar explícitamente la fila o filas concretas; no seleccionar nada no modifica el conjunto completo.

`prepare_projects` sigue expandiendo la fila representativa a todas las personas de la misma causa. Varias personas del mismo tribunal/RIT/tipo se integran en un solo proyecto y cada NNA queda junto a su propia cédula. Se genera un único Word con página nueva por proyecto. `FECHA` y `FECHA_RESOLUCION` se renderizan totalmente en palabras.

## Arquitectura y limpieza 0.4.0.dev6

Las correcciones que inicialmente estaban en cuatro módulos `runtime_fixes_20260916*` se integraron directamente en `work.py`, `outputs.py`, `resolutions.py`, `app.py` y `services/exports.py`. `nurus.personal.__init__` vuelve a ser declarativo y no altera funciones de otros módulos mediante importaciones con efectos secundarios.

Se eliminaron imports y funciones privadas sin uso detectado en los módulos intervenidos y se añadió un contrato de higiene que impide volver a versionar la capa `runtime_fixes_*`, `__pycache__`, `.pyc`, `.pyo`, `.DS_Store` o `Thumbs.db`.

El núcleo general de NuRus se conserva porque mantiene entrada `nurus`, pruebas y componentes compartidos. La documentación histórica también se conserva, pero está clasificada como histórica en `INDICE_DOCUMENTACION.md`.

## Matrices

Inventario base: seis matrices, tres de Laja y tres de Mulchén. Cinco matrices DOCX recibidas el 14-09-2026 se aplican mediante parches de `word/document.xml` verificados por SHA-256; `LAJA/PC_INFO` se incorpora desde la conversión del Word antiguo. Tomé continúa pendiente por falta de fuente y no se sustituye con matrices de otro tribunal.

## Verificación y límites

La suite remota se ejecuta en Windows 3.12–3.14. El contrato de release verifica versión, recursos instalados, cinco parches, seis matrices, ausencia de la capa transitoria y consistencia de la distribución dev6. La aceptación con Excel 2010/Outlook clásico, cuenta institucional y archivos reales autorizados sigue siendo externa a CI.

[G-ESTADO] Implementación personal consolidada en **0.4.0.dev6**.
[L-SIGUIENTE] Ejecutar `ACEPTACION_CSMP_PERSONAL.md` en el equipo institucional y registrar resultados.
