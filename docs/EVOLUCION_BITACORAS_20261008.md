# Continuación del desarrollo: lectura y copia de bitácoras

Este documento complementa la memoria entregada el 6 de octubre y conserva la
separación entre Descargador y CSMP Integral. No sustituye los antecedentes ni
atribuye aceptación real a pruebas locales.

## Decisiones y solicitudes que cambiaron el alcance

1. La auditoría inicial de NuRus se orientaba a errores y experiencia de usuario.
   La indicación posterior «estamos usando el csmp como prototipo final, más que
   el nurus» fijó CSMP personal Windows como producto de trabajo.
2. La precisión «reglas, correos, etc, es solo respecto de los 3 primeros
   tribunales» conservó Laja, Mulchén y Tomé para las reglas históricas. La
   revisión de bitácoras e ingreso de observaciones debía admitir todos los
   tribunales disponibles, mediante selección explícita.
3. «Preocúpate de la lectura y copia de las bitácoras, la escritura quedará
   para después» separó el objetivo inmediato de lectura del registro oficial.
   Por esa razón esta entrega no conecta el motor de recibos con un guardado RUS.
4. Dev20, publicado el 7 de octubre, implementó la lectura de capturas HAR y el
   Excel de textos completos. Permitió comprobar la estructura observada, pero
   no recorría automáticamente los registros de una modalidad.
5. «Realiza ese flujo no solo en ambulatorio sino en fae, residencia y dce»
   extendió el recorrido solicitado a las cuatro modalidades. La continuación
   del 8 de octubre termina su implementación en Descargador 2.5.0 y CSMP dev21.
   El momento exacto del cambio de alcance es esa instrucción; no se dispone de
   una hora verificable del mensaje y no se inventa una.

## Descargador

Se reutiliza su catálogo autenticado, selección de filtros, transporte Chrome,
validación de contexto y recorrido por páginas. El lote crea una consulta por
combinación de tribunal, modalidad y pestaña. Sus controles de página rechazan
la vuelta a una página anterior o el cambio de total/consulta entre páginas.

Los enlaces literales `ShowObservaciones` y `ShowHistoria` permiten comprobar
tribunal, causa e ingreso desde cada fila. Se reconoce también el encabezado
RUT de Espera y las tablas con encabezados TD. Una fila sin vínculo no se abre
con una consulta inventada a partir del RIT y queda registrada como incidente.

El nuevo comando `diary_open` recupera únicamente el popup tipo 12 que existe
en la respuesta actual del listado. La extensión verifica modalidad, tribunal,
pestaña y argumentos del enlace antes del GET. El parser común comprueba los
identificadores de la respuesta, la tabla y los campos completos por entrada.
Se guarda localmente una copia HTML y su huella, con control JSON por fila.

La cancelación y el reintento utilizan ese control. Se reenumera el listado;
las copias íntegras comprobadas se reutilizan y las fallas se reintentan. Los
resultados anteriores que no se reenumeran siguen documentados aparte. Ningún
endpoint de registro de observaciones se incorpora a esta actualización.

## CSMP Integral

Resultados permite lanzar el flujo sin preparar Trabajo ni correos. Conserva
la solicitud y el período, recibe el manifiesto del descargador, verifica su
ubicación, identificador y SHA-256 y crea el Excel. La operación puede
recuperarse después del cierre de CSMP. También admite importar un lote local.

El período es de hasta cuatro meses calendario. **Copia íntegra** conserva la
tabla obtenida, aunque tenga entradas anteriores. El criterio explícito del
usuario se aplica al tipo de observación: Al Tribunal significa CC=1. La hoja
Lecturas incluye cada fila y Consultas identifica alcances incompletos, incluso
si no se llegó a obtener ningún registro de una consulta.

## Problemas encontrados y soluciones

- La lectura anterior dependía de capturas abiertas manualmente. Se conecta
  ahora el recorrido del descargador con la exportación comprobada de CSMP.
- Un encabezado TD/RUT de Espera podía impedir reconocer vínculos. Se amplía
  la identificación sin relajar la comprobación de causa e ingreso.
- El HTML sin declaración de codificación podía alterar encabezados con tildes.
  La lectura de filas usa UTF-8 antes de interpretar la tabla.
- Un archivo de bitácora de otro ingreso podía contaminar el resultado. Se
  rechaza y se conserva la falla en el control; se continúa con otros registros.
- La cancelación podía dejar trabajo perdido o la recuperación podía omitir
  lecturas anteriores. Se escribe el control después de cada resultado y se
  conserva la procedencia de las filas no reenumeradas.
- El nuevo parser debía incluirse en el EXE y ser compatible con el descargador.
  Se coloca en un módulo común mínimo, sin cargar el motor ni la interfaz de
  CSMP, y se prueba su inclusión en la verificación del paquete congelado.
- La versión y varios documentos seguían mostrando dev17. Se actualizan las
  portadas, nombres de distribución y metadatos conservando la evidencia antigua.

## Producto solicitado y límite del producto entregado

El código ahora ofrece selección universal y recorrido por páginas para las
cuatro modalidades, copia, análisis local, Excel y recuperación. Conserva las
funciones anteriores. La escritura sigue aplazada expresamente. La tabla
capturada no acredita un historial remoto completo y una pestaña sin enlace
de observaciones no puede leerse inventando un vínculo.

Las pruebas con datos ficticios y el arranque del ejecutable se documentan en
la entrega. La prueba adicional de Chromium aislado requiere descargar ese
navegador; el intento local agotó el tiempo de conexión al servidor de descarga.
El JavaScript real sí se comprobó con DOM ficticio y rechazo de contextos ajenos.
La aceptación con una sesión RUS real, particularmente muestras de FAE,
Residencia y DCE, sigue siendo una validación externa distinta de estas pruebas.

Fuentes: las solicitudes citadas; [contrato dev20](LECTURA_BITACORAS_DEV20.md);
[guía dev21](BITACORAS_LOTES_DEV21.md); implementación de `bitacora_html.py`,
`personal/bitacora_lote.py`, `personal/bitacora_link.py`,
`descargador/lectura_bitacoras.py` y `descargador/extension/pagina.js`. Los HAR
aportados fundamentan la estructura observada y permanecen locales; no se
publican capturas ni registros reales en GitHub.
