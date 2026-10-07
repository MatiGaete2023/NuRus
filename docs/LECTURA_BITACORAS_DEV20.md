# Lectura y copia de bitácoras RUS

Fecha: 7 de octubre de 2026. CSMP 0.4.0.dev20.

## Función disponible

En **Resultados**, sin cargar un trabajo, se pueden seleccionar uno o varios HAR y guardar un Excel nuevo. Los controles propios del período admiten como máximo cuatro meses calendario y parten de ese intervalo. Las reglas de propuestas y correos siguen limitadas a Laja, Mulchén y Tomé. El importador de bitácoras no filtra por esos tribunales: comprueba la identidad remota de cada respuesta y su estructura.

El archivo contiene:

- **Resumen**: última observación del centro dentro del período, cantidades y cobertura.
- **Bitácoras**: entradas del período, respuestas, CC y reiteraciones.
- **Copia íntegra**: todas las entradas de la tabla capturada, incluso las antiguas, con ambos textos completos, autores, fechas, etapa e identificadores.
- **Incidencias**, **Capturas** y **Fuentes HAR**: limitaciones, fecha de captura y procedencia. Los textos extensos de la auditoría usan la hoja y el JSON previstos por el exportador; una copia histórica que exceda el límite de Excel se rechaza antes de crear un archivo recortado.

«Al Tribunal» implica CC=1 y «Administrativa», CC=0. Otros tipos conservan CC desconocido. «---» en el campo de respuesta representa ausencia de respuesta. No se equipara una observación administrativa a un requerimiento sin contestación.

## Evidencia y solución

La captura aportada tiene tres aperturas GET de `IrPopUpInformesAccion.do`, tipo de ventana 12, con el mismo contenido. Una de las capturas adicionales está vacía. La tabla observada tiene 31 entradas; una corresponde al intervalo del 7 de junio al 7 de octubre de 2026. Estos son resultados de una muestra, no cantidades generales del sistema.

La tabla visible recorta los textos. El formulario incluye el texto completo en `HOBS_Centro_<id>` y `HOBS_Tribunal_<id>`. El lector vincula esos campos con el ID de la acción de cada fila. No concatena el texto de la página ni vincula por la posición de los campos ocultos, porque estos están fuera de las filas de datos en el HTML observado.

La respuesta debe coincidir con tribunal, causa, ingreso, etapa y tipo de consulta de la petición. Se verifica el origen, formulario, acción, encabezados, identificadores únicos, fechas y presencia de todos los campos completos. No se ejecutan scripts ni se reproducen peticiones. Cookies y cabeceras de autenticación no se usan. Tres aperturas idénticas generan una sola observación por ID; versiones diferentes del mismo ingreso requieren importación separada para evitar elegir silenciosamente una versión.

## Uso

1. Abrir CSMP dev20 y entrar en **Resultados**.
2. Elegir el período en **Bitácoras RUS desde capturas HAR**.
3. Pulsar **Importar bitácoras HAR y crear Excel**.
4. Seleccionar los HAR que incluyan las respuestas de las ventanas de bitácora.
5. Elegir el destino del Excel. El original no se modifica y un destino existente se rechaza.
6. Revisar **Resumen**, **Bitácoras** y **Copia íntegra**. Consultar **Capturas** para saber cuándo se obtuvo la fuente.

Un HAR sin respuestas recuperables informa un error. Cuando se selecciona junto a otro HAR válido, queda identificado en **Fuentes HAR** sin producir filas inventadas.

## Verificación

49 pruebas focales y de regresión aprobadas: lectura completa, base64, deduplicación, identidades incompatibles, cambios de encabezados, campos ausentes, respuestas truncadas, origen ajeno, cuatro meses calendario, preservación del historial antiguo, texto que comienza con `=`, bordes, análisis existente, productos manuales y devolución a Excel. El ejecutable Windows pasó la comprobación aislada de arranque y presencia del botón de importación. La muestra real se exportó y se contrastaron los 31 textos y respuestas. Excel puede normalizar los saltos CRLF a LF sin perder contenido.

## Lo que sigue pendiente

La tabla de esta captura se recupera íntegramente, pero no acredita paginación ni cobertura completa del servidor. Por eso la cobertura es **PARCIAL** y tiene explicación. No es una consulta en vivo.

Falta validar la apertura desde la selección principal, la búsqueda y resolución inequívoca de cada fila de un Excel, otras pestañas y tribunales y el recorrido automático de un lote. No se declara completada la automatización masiva por tener un lector HAR. La escritura y su devolución de fecha verificada quedan para una fase posterior, según la instrucción del usuario del 7 de octubre.
