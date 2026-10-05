# Prototipos integrales CSMP y descargador — estado del 5 de octubre de 2026

El objetivo completo sigue en ejecución. Esta entrega permite probar el flujo conjunto y las alertas; no acredita todavía lectura ni registro automático de bitácoras en RUS.

## Versiones y ramas

- CSMP: paquete Windows 0.4.0.dev17, con corrección de sintaxis publicada en `experimento/plan-integral-csmp-20261005-dev17-fix`, sobre la base corregida dev14. Configuración de prueba separada en `CSMP_Personal_Prototipo_Integral`.
- Descargador 2.4.0: `experimento/plan-integral-descargador-20261002`, sobre la línea experimental 2.3.1. Configuración separada en `SITFA_Descargador_Integral`.
- El asistente histórico mantiene reglas, correos y proyectos limitados a Laja, Mulchén y Tomé. Las fuentes y alertas admiten todos los tribunales disponibles en la pantalla correspondiente.

## Matriz de los 32 elementos del plan

«Pruebas locales» incluye contratos y recuperación con datos ficticios. Una captura anterior valida la estructura observada, pero no sustituye una ejecución nueva autenticada en RUS.

| ID | Estado del prototipo y evidencia | Trabajo restante para darlo por terminado |
|---|---|---|
| D01 | Catálogo actual, selección múltiple, búsqueda y favoritos conservados; pruebas de interfaz. | Comprobar selección en la sesión actual de RUS. |
| D02 | Principal completa, páginas secuenciales y sin filtro de antigüedad en el flujo conjunto. | Prueba real de Espera/Cumplimiento completos. |
| D03 | Mes actual y siguiente, cambio de año, validación de fechas del XLS. | Descarga real y contraste de los dos calendarios. |
| D04 | Contrato propio de carga, bloques inclusivos de hasta 30 días y período de 60 días ampliable. Las 169 filas de la muestra coinciden celda por celda. | Confirmar criterio temporal y completar cobertura de firmas de trámites antiguos. Actualmente PARCIAL. |
| D05 | Originales, huellas, cantidades, procedencia y cobertura explícita. | Verificar las fuentes nuevas de bitácoras y documentos. |
| D06 | Descarga antes de la siguiente consulta; recuperación por consulta sin repetir las completadas; pruebas de cortes y modificación de archivos. | Prueba de recuperación real con Chrome. |
| D07 | Egresados reconocido con su pestaña observada `tdEgreso`; se mantiene contrato específico. | Consulta/exportación real de Egresados y otras variantes. |
| D08 | Inicio desde CSMP, retorno con huella/modo, solicitudes persistidas, recuperación tras reinicio y ediciones archivadas por solicitud. | Prueba entre ambos ejecutables y RUS; nueva validación de documentos/PDF vinculados. |
| C01 | Botón Descargar y analizar, fases y devolución al trabajo; Recuperar descarga en Resultados evita repetir consulta/análisis tras los cortes probados. | Prueba completa con RUS y ambos paquetes Windows. |
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
- CSMP dev17: regresión local de 459 aprobadas y una omitida; recuperación de descarga, fallos de disco/Excel y preservación de ediciones al cambiar de trabajo. La sintaxis publicada se corrigió en el commit `c3feedd357d4ddf88c5caa946b5d33bd80413fe4`; la rama de prueba es `experimento/plan-integral-csmp-20261005-dev17-fix`.
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

