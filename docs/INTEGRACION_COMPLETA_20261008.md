# Entrega conjunta: CSMP dev23, Descargador y extensión 2.7.1

Actualización del 8 de octubre de 2026. Alcance: leer y copiar bitácoras de
RUS por lotes, devolver el resultado a CSMP y producir el Excel. La escritura
de observaciones continúa aplazada por petición del usuario.

## Qué fallaba y por qué no bastaba cambiar un archivo

La primera ejecución no alcanzaba a enumerar los registros. La corrección
2.5.1 añadió diagnóstico y una lectura del HTML compatible con la descarga
normal. El lote posterior sí enumeró registros con sus vínculos de ingreso,
pero todas sus aperturas fallaban en el comando de la extensión.

La extensión instalada, titulada «2.6.0 Windows · reconstrucción visual de
evidencia», procedía de otra línea de desarrollo: conservaba mejoras del PDF,
pero no contenía `diary_open`. El número más alto no significaba que incluyera
las funciones de bitácoras de la 2.5.1. La revisión contrastó el manifiesto y
el JavaScript instalados con el código de ambos prototipos. No se atribuye el
fallo a que Residencia carezca de registros: la descarga Excel funcionaba.

Se integran ambas líneas en una entrega única. Se conserva el diagnóstico,
la enumeración, los calendarios corregidos, el flujo conjunto y la recuperación;
se incorporan pausa, apariencia, favoritos relativos, presentación de Excel,
UID de calendario estables y manifiesto de integridad del ZIP. El PDF recupera
la selección visual dentro de su iframe. La integración también corrigió una
interferencia: reconstruir los filtros sobrescribía los contadores de página.
Ahora esos contadores siempre se conservan desde la respuesta del servidor.

## Contrato entre todos los componentes

| Componente | Responsabilidad | Control implementado |
| --- | --- | --- |
| CSMP dev23 | Iniciar consulta y exportar Excel | Consulta las capacidades del EXE antes de abrirlo; prefiere el descargador incluido en el mismo paquete |
| Descargador 2.7.1 | Seleccionar alcance, recorrer páginas y copiar ingresos | Comprueba las capacidades de la extensión antes del lote; guarda versión y origen |
| Extensión 2.7.1 | Consultar desde la sesión abierta de Chrome | Acredita conjuntamente lectura, descarga CSMP y PDF; `diary_open` solo permite GET de la bitácora vinculada |
| Copias HTML y bitacoras.json | Conservar texto y control de cada registro | Identidad tribunal + causa + ingreso, SHA-256, estados, fallas y consulta de procedencia |
| Retorno a CSMP | Entregar resultado a la solicitud correcta | Identificador, carpeta propia, SHA-256 y versión/commit del descargador empleado |
| Excel de CSMP | Presentar copias y análisis | Texto completo, CC por tipo de observación, control de lecturas y consultas, errores y versiones visibles |

El contrato exige tres capacidades versión 1: `bitacoras_lectura`,
`descarga_conjunta` y `pdf_seleccion`; además declara `escritura_rus=false`.
Una extensión antigua produce una instrucción concreta de actualización antes
de enumerar. Una respuesta de otra solicitud o de otro EXE se rechaza.
Los lotes anteriores sin metadatos conservan su importación y recuperación.

## Instalación y uso del paquete completo

1. Extraer todo el ZIP en una carpeta nueva. Conservar juntas `CSMP_Integral`,
   `SITFA_Descargador` y `extension`; no mover solo un EXE ni suprimir `_internal`.
2. En Chrome, abrir `chrome://extensions`, activar Modo desarrollador y cargar
   la carpeta `extension` de esta entrega mediante «Cargar descomprimida».
   Si la anterior apunta a otra carpeta, desactivarla para evitar confundirlas.
   Comprobar versión **2.7.1**, cerrar la conexión anterior y recargar RUS.
3. Abrir `Abrir_CSMP.cmd`. En **Resultados → Consultar bitácoras en RUS** elegir
   un período de análisis de hasta cuatro meses y el destino del Excel.
   CSMP abre el descargador incluido y conserva una solicitud recuperable.
4. En Chrome, con RUS abierto, pulsar la extensión y conectar con el código
   que muestra esa nueva ventana del descargador. Cargar las opciones de
   **Seguimiento** desde el descargador.
5. Elegir los tribunales, una o varias modalidades —Residencia, Ambulatorio,
   FAE y DCE— y las pestañas disponibles. Pulsar **Leer bitácoras del lote**.
   La herramienta recorre todas las páginas; una causa con varios ingresos
   conserva sus bitácoras por separado. La pausa se aplica al terminar la
   unidad en curso; Cancelar conserva las copias ya verificadas.
6. Al llegar la respuesta, CSMP genera el Excel elegido. Revisar **Lecturas**
   y **Consultas**, incluso si el lote aparece completo. **Lote** muestra los
   errores globales y las versiones. Un registro FALLIDA o SIN_VINCULO no se
   presenta como una bitácora vacía ni como ausencia de observaciones.
7. Si hubo fallas, usar **Reintentar lecturas fallidas**. Si se cerró CSMP,
   usar **Recuperar Excel de bitácoras** con `solicitud.json`. También se puede
   importar directamente `bitacoras.json` desde Resultados.

«Descargar el lote completo» produce los Excel habituales; «Leer bitácoras»
copia las observaciones. Son operaciones distintas. «Descarga conjunta CSMP»
conserva la principal completa y los informes por vencer del mes actual y
siguiente. La consulta de resoluciones firmadas sigue fuera de ese flujo y
su ausencia no acredita que una causa no tenga movimientos.

## Cómo interpretar el resultado

**Copia íntegra** conserva toda la tabla capturada. El resumen y el análisis
se limitan al período elegido, como máximo cuatro meses calendario. «Al
Tribunal» implica CC=1; «Administrativa» implica CC=0; otros tipos requieren
revisión. El estado de respuesta proviene de los datos disponibles y no
acredita por sí mismo que no existan actuaciones en otra sección de RUS.
Las repeticiones y semejanzas son señales para revisión, no decisiones
automáticas sobre la causa. Una copia acredita la tabla consultada, no que
RUS haya entregado un historial remoto completo.

Las reglas históricas y los correos específicos continúan limitados a Laja,
Mulchén y Tomé. La lectura de bitácoras permite cualquier tribunal disponible
en el formulario y las cuatro modalidades. No se registran observaciones ni
se envían correos durante este recorrido.

## Corrección de identidad visible

En dev23 / 2.7.1, la identidad remota exacta de tribunal, causa, ingreso, etapa
y modalidad sigue siendo obligatoria; también el vínculo desde el listado actual
y la integridad SHA-256. Una diferencia de presentación en RIT o nombre ya no
se confunde con otro ingreso: queda como advertencia visible en **Lecturas** y
**Capturas** del Excel, y se conserva en el manifiesto del lote. El mismo criterio
rige lectura inicial, recuperación e importación a CSMP. Otro ingreso sigue
rechazándose. La corrección no habilita ninguna operación de escritura RUS.

La aceptación real continúa pendiente: releer los dos registros que fallaron,
comparar con la pantalla RUS y validar muestras de las cuatro modalidades y
pestañas. Las pruebas sintéticas no acreditan acceso a RUS institucional.
No se fusiona esta rama con `main` hasta contar con esa aceptación.

## Verificación y mantenimiento

La suite CSMP pasó 545 pruebas, con una omitida. La suite del descargador
cubre calendarios, filtros, vínculos, recuperación, PDF, preferencias, pausa
y productos. La extensión real pasó en Chrome aislado una lectura de 32
bitácoras ficticias —cuatro modalidades, dos tribunales, dos pestañas y dos
páginas— y cinco PDF en cuatro pantallas, seguida de descarga Excel. Todas
las rutas judiciales se simularon: cero consultas reales y cero escrituras.

La distribución se comprueba además con ambos EXE: el descargador genera un
lote ficticio, CSMP verifica el retorno y exporta el Excel; se comprueban
texto completo, CC y bordes. Las pruebas de arranque inspeccionan recursos
incluidos, plantillas y las interfaces. Los informes JSON de verificación
acompañan la entrega. La aceptación con los registros actuales de la sesión
real del usuario sigue siendo necesaria; las pruebas simuladas no la sustituyen.

Para las próximas entregas, `tools/build_integral.ps1` construye y comprueba
las dos aplicaciones juntas. GitHub Actions ejecuta también las pruebas del
descargador, la extensión y el intercambio de los binarios antes de publicar
el artefacto integral. Los cambios de funciones deben actualizar capacidades,
pruebas, guía y distribución en una misma revisión. No se publican HAR,
copias HTML ni resultados con datos reales de causas.

La publicación detectó dos supuestos obsoletos en las pruebas Windows: el
fixture visual no declaraba su hoja y una prueba de preferencias exigía
1050 píxeles de ancho incluso en pantallas de 1024. Se completó el fixture y
se comprobó que el tamaño restaurado respete la pantalla. Pasaron el control
visual local, las cinco pruebas de preferencias y el pipeline independiente
del descargador en GitHub. El comando de CSMP declara explícitamente `tests/`,
coherente con `testpaths`; las dependencias y pruebas del descargador quedan
en su propia fase. Estos ajustes no modifican el código de los EXE verificados.
