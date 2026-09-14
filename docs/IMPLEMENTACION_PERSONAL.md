# Implementación CSMP Assistant personal — 14 de septiembre de 2026

Versión **0.4.0.dev3**. Entrada: `Abrir_CSMP.bat`. Módulo: `nurus.personal.app`. El flujo visible tiene Trabajo, Correos, Resoluciones, Configuración y Enviados.

## Decisiones vigentes

Las observaciones que dejan constancia de una gestión ejecutada —por ejemplo, remitir correo o proyecto— usan redacción de gestión realizada para poder registrarse después en RUS sin reescritura. Las sugerencias sustantivas que forman parte del catálogo (curador, egreso por mayoría, actualización de ficha) conservan su naturaleza de sugerencia. Generar el texto no acredita que la gestión se haya ejecutado.

Ante dudas de reglas prevalece el perfil Asistente vigente. E-05 mantiene el diseño congelado del catálogo: DCE desde 30 días solo correo; Laja/Mulchén desde 30 días proyecto + correo; Tomé 30–59 solo correo y 60+ proyecto + correo.

Cumplimiento sin cruce utilizable no evalúa C-10, deja advertencia y continúa. El flujo personal no solicita ni exige documentar una excepción para exportar.

## Funciones implementadas

Trabajo procesa `.xls/.xlsx/.xlsm`, conserva original, exporta copia y permite actualizar cambios humanos por identidad estable. También puede cargar una planilla modificada/externa y reutilizarla en productos sin volver a ejecutar el motor.

Correos permite seleccionar modalidades, editar vista previa y guardar un borrador o todo el lote. No existe llamada de envío. Destinatarios ambiguos/desconocidos quedan vacíos; la CC institucional se conserva. Los adjuntos automáticos se nombran por programa.

Resoluciones permite escoger `PC_IE`, `PC_INFO` o `NOMENCL`, agrupa por tribunal/RIT/tipo y genera un solo Word con página nueva por proyecto. Varias personas del mismo grupo se integran en un proyecto.

Configuración mantiene umbrales, textos, plantillas, contactos, alias, Outlook y matrices Word bajo `LOCALAPPDATA/CSMP_Personal`. Las escrituras JSON son atómicas y dejan `.bak`.

Enviados consulta Outlook en modo de solo lectura y exporta el resultado; un borrador no se cuenta como enviado.

## Matrices

Inventario base: seis matrices, tres de Laja y tres de Mulchén. Cinco matrices DOCX recibidas el 14-09-2026 se aplican mediante parches de `word/document.xml` verificados por SHA-256; `LAJA/PC_INFO` se incorpora desde la conversión del Word antiguo. La migración es de una sola aplicación, respalda versiones distintas y preserva ediciones manuales posteriores. Si una matriz desaparece, se repone y se aplica la revisión vigente. Tomé continúa pendiente por falta de fuente.

## Verificación y límites

La suite remota se ejecuta en Windows 3.12–3.14. El contrato de release verifica versión, recursos instalados, cinco parches y seis matrices. La aceptación con Excel 2010/Outlook clásico, cuenta institucional y archivos reales autorizados sigue siendo externa a CI.

[G-ESTADO] Implementación personal consolidada en 0.4.0.dev3; no quedan validaciones de excepción de cruce visibles en el flujo personal.
[L-SIGUIENTE] Ejecutar `ACEPTACION_CSMP_PERSONAL.md` en el equipo institucional y registrar resultados.
