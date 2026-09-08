# Implementación de NuRus

Fecha de actualización: 8 de septiembre de 2026. Rama de integración: `implementacion-plan-2026-09-08`. Versión: `0.2.0.dev1`. Base técnica objetivo: Python 3.12, Windows 10, Tkinter/ttk, SQLite local y Outlook Object Model opcional.

## Decisiones cerradas e invariantes

**D01 — Correo electrónico.** NuRus nunca envía correos. Solo puede guardar borradores Outlook para revisión humana previa al envío manual. La ausencia de destinatario es una advertencia y puede conservarse en el borrador; los errores de contenido sí bloquean. El adaptador exige confirmación explícita y usa únicamente `Save()`.

**D02 — Efectos externos.** NuRus no escribe directamente en SATURNO.

**D03 — Trazabilidad.** Una salida derivada de planilla debe conservar referencia al lote aprobado y no recalcular silenciosamente el Excel al generar.

## Implementado en la rama 0.2

### Núcleo RUS y lectura

- Espera, Cumplimiento e Informes usan `nurus.rus` como motor único.
- `read_workbook()` procesa una copia temporal estable y calcula el SHA-256 sobre los mismos bytes.
- Se conserva archivo, hash, hoja, fila física, modalidad, fila de encabezado y época Excel.
- Las columnas ambiguas no se sobrescriben silenciosamente.
- Las filas quedan clasificadas como revisadas, bloqueadas o excluidas; ninguna ausencia de información se convierte en «sin observaciones» sin registrar la incidencia.
- Fechas ISO, ISO con hora y formatos día/mes/año se interpretan explícitamente; los seriales respetan época 1900/1904.

### Persistencia y revisión

- SQLite activa `PRAGMA foreign_keys=ON` en cada conexión.
- `batches` conserva origen real, configuración del análisis, versión del motor, hash del catálogo y hash de la evaluación.
- `review_records` conserva datos, propuesta original, edición, reglas, incidencias, referencias relacionadas y decisión humana.
- Editar o excluir exige motivo.
- Una fila bloqueada no puede aprobarse como limpia; puede excluirse explícitamente con motivo.
- El lote solo se aprueba cuando no quedan filas pendientes/bloqueadas y genera un hash independiente del snapshot final.
- Las plantillas tienen historial de versiones inmutables; la tabla `templates` actúa como puntero a la versión vigente.

### GUI

- La pestaña Trabajo separa «Análisis RUS» de «Comunicación particular».
- Seleccionar un archivo muestra «seleccionado, sin analizar».
- `Analizar archivo` ejecuta lectura/evaluación en un trabajador y actualiza Tkinter desde el hilo principal.
- Un identificador de ejecución invalida resultados antiguos si cambia archivo o modalidad.
- La revisión muestra estado, RIT, tribunal, programa, observación, procedencia, reglas e incidencias.
- Se puede aprobar fila, editar con motivo, excluir, restaurar y congelar el lote completo.
- La generación derivada del snapshot permanece separada hasta completar la fase de productos.

### Windows

- `Instalar_NuRus.bat` crea `.venv` y evita modificar el pandas global.
- `Abrir_NuRus.bat` inicia con el Python del entorno aislado.
- GitHub Actions verifica Python 3.12 en Windows y Linux, `pip check`, compilación y pytest.

## Fases pendientes obligatorias

1. **Productos desde snapshot aprobado (P0/P1).** Construir correo/proyecto de resolución/exportación exclusivamente desde registros aprobados; conservar versión de plantilla y hash del snapshot.
2. **Contactos (P1).** Importación Excel con vista previa, comparación de altas/modificaciones/conflictos y aplicación manual; sin coincidencia aproximada automática.
3. **Exportaciones y proyectos de resolución (P1).** Perfiles aprobados, protección frente a fórmulas, recuperación ante archivo abierto/permisos y trazabilidad de la salida.
4. **Outlook productivo (P1).** Trabajador COM serial, cuenta/carpeta explícitas, prevención de duplicados, `EntryID`/`StoreID` cuando existan y estado por conciliar ante `Save()` incierto. Siempre borradores; nunca envío.
5. **Contador de correos (P1).** Consulta de solo lectura de Enviados, separada del creador de borradores.
6. **Distribución y aceptación (P1/P2).** Matriz completa Windows 10/Excel 2010/Outlook clásico, recuperación, respaldo y paquete limpio sin instalación editable.

## Conflictos y decisiones todavía abiertas

[CONFLICTO_ABIERTO] Política institucional definitiva de CC, adjuntos y criterios de bloqueo por fila/lote. Fuente de cierre: instrucción operativa aprobada. No bloquea lectura y revisión.

[CONFLICTO_ABIERTO] Modelos finales de resolución y criterios de activación. Fuente de cierre: plantillas/oficios vigentes aprobados. No bloquea lectura y revisión.

[CONFLICTO_ABIERTO] Umbrales y textos que representen criterio institucional deben ratificarse con su fuente vigente antes de cambiar reglas. Las pruebas de paridad acreditan comportamiento técnico, no vigencia jurídica u operativa.

## Puerta de aceptación

No declarar NuRus apto para uso productivo hasta que:

- CI Python 3.12 esté verde;
- se ejecute la matriz de `PRUEBAS.md` en Windows 10 con muestras anonimizadas representativas;
- se pruebe un `.xls` BIFF auténtico con `xlrd`;
- el snapshot aprobado genere productos sin recalcular la fuente;
- Outlook solo cree borradores y se compruebe que ninguna ruta ejecuta `Send`;
- existan cero P0 pendientes o estos permanezcan deshabilitados y documentados.
