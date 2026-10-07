# Estado de ejecución del plan Luna

Fecha: 6 de octubre de 2026
Alcance: prototipos CSMP (producto) y SITFA Descargador (auxiliar), Windows local.

## Avance comprobado

| Elementos | Estado | Resultado |
|---|---|---|
| L0 | Hecho | Descargador 2.4.0 y CSMP 0.4.0.dev17 tienen ZIP con checksum SHA-256 externo, manifiesto de archivos y proof ligado a commit/recursos. CSMP se extrajo y abrió desde la carpeta de entrega; el proof cotejó el EXE extraído con el EXE probado. El manifiesto de cada paquete indica su commit exacto; los companions `.sha256` guardan el hash externo del ZIP. |
| L1–L2 | Hechos | Descargador valida las 23 columnas y conserva identidad estable de firmas; CSMP lee/reconcilia revisiones antiguas de forma inequívoca. |
| L3–L5 | Hechos | El período elegido limita el informe de firmas; el retorno a Excel permite seleccionar recibos verificados; la búsqueda de reiteraciones no omite textos separados alfabéticamente y avisa si alcanza el límite. |
| L6A | Hecho | Cobertura reconoce `COMPLETA`, `VACIA_COMPROBADA`, `PARCIAL`, `FALLIDA` y `NO_CONSULTADA`. Una cobertura vacía con filas de observaciones o firmas se rechaza. |
| L6B | Revisado | La identidad remota exige tribunal, causa, ingreso, persona, centro, RIT y vínculo desde respuesta actual. RIT y fila local no autorizan escritura. |
| L6C–L6D | Parcial / evidencia externa pendiente | La elección de pantalla/modalidad no acredita acciones de bitácora. El puente valida el contexto en pruebas sintéticas; no se pudo observar una sesión RUS activa desde esta corrida. No se declara capacidad de lectura o escritura. |
| L7A–L7B | Bloqueados para integración real | Hay contratos de análisis y calendario, pero falta validar selectores, paginación, fechas, identificadores y fin de lectura en una sesión RUS vigente. |
| L7C–L7F | Parcial / L7F hecho | El exportador de bitácora conserva coberturas, errores y textos largos mediante Excel + JSON íntegro con hash. Sin lector conectado, no obtiene bitácoras RUS por sí mismo ni aparece como consulta automática en Resultados. |
| L7D–L7E | Pendientes | No se habilitaron vistas automáticas de bitácora o calendario sin lector RUS comprobado. |
| L8A | Salvaguarda hecha; contrato real pendiente | Se eliminó el límite supuesto de 2.000 caracteres. La preparación de una intención ahora exige que el límite UTF-16 haya sido observado/configurado; sin él, la operación se detiene. El formulario real no se pudo capturar. |
| L8B–L8C | Bloqueados para integración real | Vista previa contra estado reciente, escritura y readback requieren primero bitácora/formulario reales y una sesión comprobable. No hay POST ni guardado automático habilitado. |
| L9 | Bloqueado | No se marca fecha de gestión ni CC en el Excel a partir de intenciones locales. El retorno a Excel sigue condicionado a recibo RUS comprobado. |
| L10A–L10D | Revisados | Se conserva el flujo conjunto, períodos, cruce por tribunal/RIT, estados parciales, copias de Excel y bordes. No se recrearon funciones existentes ni se detectó una nueva brecha que justificara otro cambio aquí. |
| L11A | Hecho | La interfaz ya no promete lectura/registro en tribunales sin reglas históricas ni adapter RUS habilitado. |
| L11B–L11D | Pendientes | Exportación conectada, confirmación visual de lote y bandeja de recuperación esperan el contrato real de lectura/escritura y readback. |
| L11E | Hecho en dev18 | Configuración → Básico → Vista guarda y restaura filtros, columnas visibles/orden, anchos, fuente de tablas/editores y geometría; JSON portable validado y vista anterior persistente. Se conservan selecciones ocultas también en la sesión del trabajo. |
| L11F | Revisado para F02–F05 | Consolidación/comparación y CSV/ZIP/ICS son accesibles en Resultados del Descargador; firmas y gestión por período en Resultados de CSMP. Corregida la utilidad CLI de firmas para exigir y aplicar fechas. ICS distingue vencimiento de informe y egreso proyectado y declara lote incompleto. La consulta masiva de bitácoras (F01) permanece pendiente del lector real. |
| L11G | Hecho | Configuración → Avanzado → Diagnóstico informa versión, commit, origen y rutas del ejecutable/intérprete y módulo CSMP realmente cargado. |
| L12–L13 | Hechos al cerrar esta entrega | Manual y estado del plan se alinean con capacidades comprobadas; la verificación del ZIP final se anota con hash, commit y prueba de arranque. |

## Contratos y límites que conserva CSMP

- Las reglas históricas de propuestas, correos y matrices siguen limitadas a Laja, Mulchén y Tomé. La selección de otro tribunal no activa esas reglas.
- Las bitácoras y registros para cualquier tribunal siguen apagados hasta verificar el contrato de esa pantalla en RUS. `Al Tribunal` implica CC=1; `Administrativa`, CC=0; tipo desconocido detiene la operación.
- El máximo de revisión de bitácora sigue siendo cuatro meses calendario. Actividad solo cuenta resoluciones firmadas y no invalidadas; la cobertura temporal de carga no se da por completa mientras su filtro no se confirme.
- El informe de carga conserva el tribunal de sus filas aunque el encabezado diga «Concepción». Informes por vencer comprende mes actual y siguiente.
- Excel original y borradores se mantienen locales; no se envían correos ni se repite un guardado incierto a ciegas.

## Validación y limitaciones

- CSMP, pruebas focales de bitácora/firma, identidad, registro y diagnóstico: **65 aprobadas**.
- Suite CSMP completa en este Windows: **470 aprobadas, 1 omitida y 16 fallidas por `WinError 5` al escribir/limpiar `%TEMP%`**. Las trazas mostraron errores de ACL en operaciones temporales de Word, Outlook y exportación; no se interpretan como fallos funcionales. Los flujos pertinentes también tienen pruebas focales aprobadas.
- Descargador: L1 tuvo 10 aprobadas y una omitida por el entorno; L2 y empaquetado tuvieron sus pruebas focales aprobadas. Una repetición amplia posterior encontró carpetas de test residuales sin permisos accesibles; no se cuenta esa corrida como aprobación de suite.
- Windows: el EXE final se abre después de extraer y se cotejan proof, SHA-256, recursos, manifiesto y CRC del ZIP. Esto prueba apertura local; no prueba conexión institucional RUS.
- Chrome aparece como «Tu Chrome» mediante la extensión conectada, pero las operaciones de acceso a pestañas agotan el tiempo de espera aunque RUS está abierto. Por eso L6D–L9 y las vistas dependientes siguen pendientes de evidencia real. No se reutilizaron cookies ni HAR como credenciales.

## Continuación local — dev18 / Descargador 2.4.1

Se cerró L11E y se auditó el acceso de las utilidades existentes L11F. Pruebas nuevas y regresión local: 42 aprobadas y una fallida por el error de permisos de `%TEMP%` al preparar matrices Word; los cinco escenarios nuevos de vista y los 16 contratos de preferencias pasaron. Informes CLI y regresión de períodos: 9 aprobadas. Semántica ICS: 3 aprobadas. Los escenarios de reinicio usan procesos separados para evitar reutilizar el intérprete Tcl.

Commits: `674eb12` (preferencias validadas), `fc98ae7` (controles y selección oculta), `2ce97c2` (fechas de informes CLI), `672122a` (Descargador, semántica ICS). La nueva compilación debe verificarse sobre su EXE exacto; los hashes dev17 anteriores son evidencia de la entrega anterior.

## Commits de CSMP añadidos en esta ejecución

- `7e43b203` — valida esquema de informe de carga (Descargador).
- `442784ad` — identidad estable de firma (Descargador).
- `90d2b034` — lectura dual segura de revisiones heredadas.
- `9b5e2df` — aplica rango al informe de firmas.
- `7f9fabbc` — selección explícita de recibos para Excel.
- `f75295db` — búsqueda ampliada de reiteraciones.
- `dc46229` — conserva textos extensos de auditoría.
- `b32c95a` — muestra capacidades verificadas en UI.
- `8697209` — requiere límite observado del formulario RUS.
- `12223e9` — distingue consulta vacía verificada de cobertura desconocida.
- `2975bfe` — muestra instalación efectiva en Diagnóstico.
