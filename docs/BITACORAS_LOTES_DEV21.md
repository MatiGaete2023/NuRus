# Lectura por lotes de RUS · CSMP dev21 y Descargador 2.5.0

Actualización del 8 de octubre de 2026. Amplía la importación local de dev20 a un
recorrido desde la sesión de Chrome mediante la extensión del descargador. La
escritura de observaciones queda diferida por indicación del usuario.

## Uso desde CSMP

1. Abre **Resultados** y revisa Desde/Hasta en el apartado **Bitácoras RUS**.
   El análisis admite como máximo los últimos cuatro meses calendario. Este
   período filtra las observaciones analizadas, no las filas que se consultan.
2. Pulsa **Consultar bitácoras en RUS**, elige el nuevo Excel de salida y
   selecciona **SITFA_Descargador.exe 2.5.0** de la actualización.
3. En el descargador, conecta la extensión actualizada con Chrome y RUS abierto.
   Carga las opciones de **Seguimiento**.
4. Selecciona los tribunales disponibles, la pestaña y **Todas las modalidades**
   o una modalidad: Ambulatorio, FAE, Residencia o DCE. Espera y Cumplimiento
   pueden elegirse juntas. Informes admite su filtro de tipo.
5. Pulsa **Leer bitácoras del lote**. Recorre todas las páginas del listado y
   consulta el enlace de observaciones de cada ingreso que puede identificar.
6. Al finalizar, CSMP recibe el control del lote y crea el Excel automáticamente.
   Un resultado incompleto también produce un control visible de sus fallas.

Para una lectura independiente, usa el mismo botón en el descargador y luego
**Resultados → Abrir lote de bitácoras y crear Excel**, eligiendo `bitacoras.json`.
No es necesario iniciar Trabajo, propuestas, correos ni resoluciones.

## Qué revisar en el Excel

- **Lecturas:** todas las filas enumeradas, su tribunal, modalidad, pestaña,
  página, ingreso, resultado, archivo, fecha de captura y huella SHA-256.
- **Consultas:** alcance solicitado y recorrido de cada consulta. Identifica
  consultas fallidas y las que no llegaron a ejecutarse.
- **Resumen y Bitácoras:** última observación del centro dentro del período,
  tipo, CC, posibles reiteraciones y respuestas registradas.
- **Copia íntegra:** los textos completos obtenidos de los campos ocultos de
  la tabla, incluidas las observaciones anteriores al período de análisis.
- **Capturas, Fuentes e Incidencias:** procedencia y límites de la lectura.

**Al Tribunal** equivale a CC=1; **Administrativa** a CC=0. Un tipo desconocido
no se interpreta por suposición. La falta de respuesta en la captura describe
lo que figura en esa tabla; no acredita ausencia de una gestión por otra vía.

## Recuperación

**Cancelar** conserva las copias comprobadas. Conecta Chrome y carga Seguimiento
antes de usar **Reintentar lecturas fallidas…**, eligiendo la carpeta del lote.
Se vuelve a consultar el listado desde la primera página. Se reutilizan las
copias cuyo archivo, huella y contexto siguen siendo válidos; se reintentan
las pendientes o fallidas. Los registros que ya no están en la nueva consulta
no se consultan usando enlaces guardados de una sesión anterior.
Si un registro anterior no se reenumera, se conserva en **Lecturas anteriores**;
esto no acredita que haya desaparecido de RUS, porque la recuperación puede
haber fallado antes de llegar a su página.

Si CSMP cerró antes de generar el libro, **Recuperar Excel de bitácoras** permite
seleccionar `solicitud.json` en su carpeta `intercambio_bitacoras`. Recuperar
una lectura vuelve a exportar con el período y corte originales. También puede
abrirse directamente el `bitacoras.json` del lote y elegir otro período válido.

## Identidad y límites

El cruce usa tribunal + causa RUS + ingreso RUS y comprueba además RIT y persona.
Nunca abre una bitácora construyendo una identidad únicamente desde el RIT.
Las filas sin enlace inequívoco quedan como **SIN_VINCULO**. Esto puede ocurrir
en Egresados si RUS no ofrece Observaciones para ese listado; no se promete
acceso donde no hay un vínculo comprobable.

El estado **COMPLETA** del lote significa que se enumeró el alcance solicitado
y se leyó cada fila vinculable. La cobertura del historial permanece **PARCIAL**:
el contrato observado no acredita otra paginación del historial remoto ni que
la tabla contenga todas las observaciones existentes. Se conserva exactamente
la tabla recibida; no se inventan fechas, respuestas o entradas ausentes.

Los archivos se validan nuevamente antes de exportar. Una copia alterada queda
como fallida. Dos capturas incompatibles del mismo ingreso se rechazan para
evitar mezclar versiones; pueden exportarse como lotes separados.

Las reglas y correos anteriores siguen limitados a Laja, Mulchén y Tomé. La
lectura por lotes utiliza cualquier tribunal disponible en el catálogo real
de Seguimiento. No agrega un endpoint de guardado ni escribe en las bitácoras.
Las capturas HTML, los manifiestos y los Excel se conservan localmente.

## Verificación

Las pruebas locales cubren cuatro modalidades, dos tribunales ficticios, dos
pestañas y dos páginas por consulta, ingresos con el mismo RIT, ausencia de
enlace, respuesta de otro ingreso, cancelación, recuperación, archivos
alterados, exportación íntegra, CC, límites de fechas y devolución a CSMP.
El comando JavaScript real se verifica con un DOM ficticio y rechaza cambios
de tribunal, ingreso, modalidad, pestaña y enlaces duplicados.

El script `descargador/verificar_bitacoras_extension.py` permite comprobar la
extensión en un Chromium aislado con todas las respuestas interceptadas y
ficticias. La aceptación con la sesión real de RUS y muestras de las cuatro
modalidades debe comprobarse por separado; las pruebas locales no equivalen
a una ejecución aceptada por el servidor real.
