# Protocolo de la línea integral — 0.4.0.dev17

**Prototipo 0.4.0.dev17 · 5 de octubre de 2026.** Conserva la base corregida dev14, el flujo conjunto y las alertas. Añade diario recuperable y conciliación de fechas con Excel. El adaptador real de bitácoras y registro sigue pendiente; la interfaz todavía no escribe observaciones en RUS. Véanse REGISTRO_RECUPERABLE_20261005.md y ESTADO_PLAN_INTEGRAL_20261005.md. Las secciones anteriores a este avance se conservan como antecedentes, no como aceptación de las funciones nuevas.


La evidencia automática actual está en [CORRECCION_ADJUNTOS_20260930.md](CORRECCION_ADJUNTOS_20260930.md).
La aceptación institucional del 22-09 que sigue se conserva como evidencia de
dev11. Las comprobaciones de Office pendientes no se convierten en aprobadas por
las pruebas simuladas de dev14.

# Aceptación histórica — CSMP Assistant personal 0.4.0.dev12

Estado al 22 de septiembre de 2026: **VALIDACIÓN FUNCIONAL REAL DEL FLUJO PRINCIPAL SATISFACTORIA**. El usuario confirmó funcionamiento en procesamiento/modificación del Excel, RES categórico, generación de resoluciones, creación y edición de borradores de correo y modificación de parámetros. Las pruebas institucionales específicas que no fueron verificadas expresamente permanecen pendientes.

Responsable: usuario principal. Fecha: 22-09-2026. Commit base probado: `f67af0998640223344cc9af653f80b8334a82fe6`.

## Dev12 — aceptación pendiente

La validación real registrada abajo corresponde a dev11 y constituye la línea base que dev12 no debe romper. Dev12 requiere nueva prueba visual/operativa de paneles de detalle, siguiente incidencia, comparación antes/después, configuración Básico/Avanzado, reanudación explícita y redacciones actualizadas. Hasta entonces no sustituye a dev11 en `main`.

## Validación funcional real del 22 de septiembre de 2026

El usuario informó una prueba satisfactoria del flujo real: procesamiento del Excel y modificación de su contenido, selector RES categórico, creación de proyectos de resolución, creación y modificación de borradores de correo y modificación de parámetros/configuración. El fallo COM detectado previamente al configurar RES (`'tuple' object is not callable`) fue corregido y el mismo flujo volvió a funcionar en Excel real. Esta evidencia justifica congelar dev11 como **candidata funcional**, pero no convierte automáticamente en aprobadas las pruebas ACEP que requieren condiciones específicas no reportadas (duplicados Outlook, Enviados, Cumplimiento con/sin cruce, matrices faltantes, reinicio, medición de tiempos, etc.).

| ID | Acción | Criterio de aceptación | Resultado / evidencia |
|---|---|---|---|
| ACEP-01 | Instalar y abrir | Abre cinco áreas sin privilegios administrativos; registra Python 3.12–3.14 | Pendiente |
| ACEP-02 | Procesar Espera | Copia abre sin reparación; cantidad y observaciones esperadas; original intacto | **OK funcional 22-09** — procesamiento Excel real confirmado tras hotfix RES |
| ACEP-03 | Editar en Trabajo y exportar directamente | Sin pulsar antes “Aplicar edición”, la copia contiene la observación visible; fila editada `REVISADO`, filas intactas `PENDIENTE`; TT/CC/RES previos no se borran; `RES` nuevo ofrece desplegable PC_IE/PC_INFO/NOMENCL | **OK funcional 22-09** — modificación del Excel y RES confirmadas |
| ACEP-04 | Cumplimiento con y sin cruce | Con cruce: C-10 según fuente; sin cruce: advertencia, sin C-10 y sin diálogo de excepción/bloqueo | Pendiente |
| ACEP-05 | Editar planilla y actualizar | Cambios asociados por identidad; Correos/Word reutilizan la copia sin nueva carga | **OK funcional 22-09** — cambios Excel reutilizados en productos |
| ACEP-06 | Preparar correos | **Preparar TODOS** incluye informativo general + comunicaciones específicas; modalidades correctas; Para puede quedar vacío; CC institucional; nómina por programa y sin excluidos | **OK funcional 22-09** — creación y edición de correos confirmadas; casos de borde siguen cubiertos por CI |
| ACEP-07 | Guardar lote de borradores | Todos quedan en Borradores, ninguno en Enviados; repetir preparación idéntica no duplica aunque cambie la carpeta temporal del adjunto; editar cuerpo/destinatario sí produce versión nueva | Pendiente |
| ACEP-08 | Clasificar resoluciones | `PC_IE`, `PC_INFO` o `NOMENCL` en RES prevalece y aparece como `Definido en RES`; un valor RES desconocido se advierte sin generar tipo; marcas antiguas 1/X siguen legibles; una observación sin acción ni RES no crea proyecto | **OK funcional 22-09** — RES categórico y reconocimiento confirmados |
| ACEP-09 | Editar resoluciones una a una | Lista con una fila por tribunal/RIT/tipo; cambiar tipo afecta solo selección explícita; no seleccionar nada no modifica todos | Pendiente |
| ACEP-10 | Generar Word Laja/Mulchén | Un Word; una resolución por grupo tribunal/RIT/tipo; varios NNA junto a su cédula; saltos de página; fechas en palabras | **OK funcional 22-09** — creación de resoluciones confirmada |
| ACEP-11 | Matrices | Seis matrices Laja/Mulchén disponibles; Tomé se informa como faltante sin sustituto automático | Pendiente |
| ACEP-12 | Enal trabajo; Recuperar descarga en Resultados evita repetir consulta/análisis tras los cortes probados. | Prueba completa con RUS y ambos paquetes Windows. |
| C02 | Hoja auxiliar de dos meses con orden de fuentes, fechas e identidad completa; RUT solo se completa mediante coincidencia inequívoca. | Validación real del calendario y cobertura; reforzar aceptación de auxiliares externos. |
| C03 | Firmas por código de tribunal–RIT, informes por identidad completa y guardas de productos para tres tribunales. | Contraste real y calendario individual de estado. |
| C04 | Cuatro columnas, detalle y colores; probado con Excel de escritorio. | Completar criterio de cobertura y comparación con última revisión del centro. |
| C05 | Ficha de firmas y apertura de originales; vínculos reales de ingreso/persona/centro extraídos de la respuesta capturada. | Apertura y comprobación de causa, calendario y bitácora en RUS. |
| C06 | Pendiente de lector del calendario individual. | Contrato real, todos los informes, estados y contradicciones. |
| C07 | Servicio común probado: máximo cuatro meses, última entrada del centro de cualquier autor, fechas empatadas y sin retroceso a entradas antiguas. | Conectar y verificar el lector real de bitácoras. |
| C08 | Servicio probado: CC por tipo, respuestas desconocidas separadas, reiteraciones y deduplicación por ID remoto. | Lectura de textos completos, respuestas y paginación reales. |
| C09 | Intención del texto efectivo del Excel, identidad/contexto y guardado único probados con adaptador ficticio. | Completar el adaptador real, campos y contrato de guardar/releer en RUS. |
| C10 | Diario SQLite, recuperación sin reenvío y devolución por ingreso a una copia; conflictos y cortes probados con datos ficticios. | Prueba real RUS y aceptación del paquete dev16; devolución nativa verificada en XLS/XLSX/XLSM. |
| C11 | Pendiente de bandeja de seguimiento conjunta. | Integrar firmas, bitácoras, respuestas y siguientes comprobaciones. |
| C12 | Edición, contactos, matrices y configuración de la base preservadas. | Auditar y completar presets, columnas y preferencias avanzadas aún ausentes. |
| C13 | Historial y búsqueda existentes preservados; revisión de firma persistente por ingreso real entre descargas. | Separar texto consultado/guardado y ampliar búsqueda de gestiones nuevas. |
| C14 | Paquete dev16 comprobado después de extraerlo, con seis matrices Word; descargador/extensión 2.4.0 comprobados. dev17 añade devolución recuperable. | Paquete dev17, recuperación conjunta real y aceptación completa. |
| F01 | Exportador común de auditoría con resumen, historial, incidencias, textos y bordes; pruebas con consultas fallidas. | Conexión real, selección de tribunales/pestañas y acceso de usuario independiente. |
| F02 | Consolidación, conversión y comparación de la línea experimental conservadas. | Validación de los nuevos esquemas de fuentes y prueba de usuario. |
| F03 | Informe por período y varios trabajos en Resultados; separa historial del Excel, productos locales y observaciones nuevas comprobadas. | Alimentarlo con recibos reales de C10 y completar alcance/autores. |
| F04 | Informe de firmas por ingreso y cobertura, con revisiones locales y deduplicación de sesiones repetidas. | Cobertura completa, última revisión del centro y prueba de usuario. |
| F05 | CSV, ZIP e ICS de la base experimental conservados. | Validar significado de fechas de nuevas fuentes. |
| B01 | Catálogos dinámicos y contratos por pantalla. | Capacidades reales de ventanas y registro por pestaña/etapa. |
| B02 | IDs remotos vinculados por identidad completa; revisión persistente solo cuando el vínculo está comprobado. | Revalidación al abrir y escribir en RUS. |
| B03 | Puente/extensión existentes y contratos de carga ampliados. | Servicios compartidos de lectura y registro de ventanas. |
| B04 | Fuentes y cobertura explícita; no se afirma ausencia de movimientos a partir de carga parcial. | Criterio temporal de carga y cobertura/paginación de bitácoras. |
| B05 | Intención persistida antes de enviar; estados y transiciones atómicas; recuperación consulta sin volver a guardar. | Completar y validar evidencia real de RUS y recuperación del flujo completo. |

## Pruebas verificadas

- CSMP dev16: 443 pruebas aprobadas y una omitida en Windows, con Python 3.12, 3.13 y 3.14. La omitida corresponde a una condición de plataforma; no es prueba pendiente de registro RUS. CI del código: https://github.com/MatiGaete2023/NuRus/actions/runs/37348807233.
- CSMP dev17: regresión local de 459 aprobadas y una omitida; recuperación de descarga, fallos de disco/Excel y preservación de ediciones al cambiar de trabajo. Pendiente contraste del nuevo CI y del paquete final.
- Descargador: 111 pruebas aprobadas antes de añadir la comprobación de arranque del paquete; ésta se ejecuta además sobre el ejecutable real.
- Excel de escritorio: original intacto, tres ingresos conservados, cuatro columnas de actividad, colores azul/ámbar, bordes y formato original, TT/CC/FECHA_OBS vacíos.
- Captura real de carga: 169 filas, comparación completa de sus 23 celdas y multiplicidad; 168 firmas válidas, 13 posteriores a la fecha consultada.
- Vínculos de ingreso: los tres registros de Cumplimiento de la captura entregada tienen IDs consistentes de causa, ingreso, persona y centro.
- Análisis de bitácoras: pruebas de cuatro meses calendario, última entrada, autores, empates, carga, respuesta incierta, reiteraciones, textos completos e incidencias.

Estas comprobaciones no equivalen a un registro real en RUS. La conexión de Chrome falló al inventariar pestañas; el usuario indicó que puede reconectarlo y abrir RUS. Falta verificar esa reconexión y los contratos de las ventanas.

## Siguiente tramo

1. Probar el flujo completo con los ejecutables y la extensión publicados; el arranque aislado y los recursos empaquetados ya están verificados.
2. Comprobar bitácora/calendario/historia de la sesión RUS y completar el lector común, la ficha y la auditoría independiente.
3. Implementar recibos, registro exacto y devolución a Excel; validar un caso que el usuario elija expresamente antes del lote.
4. Completar bandeja, configuración avanzada y variantes; ejecutar la aceptación de los 32 elementos y de los paquetes finales.

## Avance posterior: recibos y conciliación dev16

El diario conserva la intención antes del envío y consulta después de un corte sin repetir el guardado. La conciliación identifica el ingreso real aunque se reordenen las filas, utiliza la fecha comprobada y conserva TT/RES. Una entrada idéntica del mismo autor y día se reutiliza sin enviar ni contar otra gestión. Las pruebas locales emplearon un adaptador ficticio de RUS.

La devolución nativa se comprobó en XLS, XLSX y XLSM, con original intacto, fórmulas, formatos y otras hojas conservados. Las 443 pruebas del código publicado aprobaron en las tres versiones Windows. El ejecutable dev16 incluye seis matrices Word, cinco revisiones y seis páginas; se comprobó su arranque también después de extraer el ZIP.

El adaptador real sigue pendiente: esta entrega no acredita ni realiza escritura judicial desde la interfaz. Véase REGISTRO_RECUPERABLE_20261005.md. Los paquetes dev15 anteriores permanecen conservados.
