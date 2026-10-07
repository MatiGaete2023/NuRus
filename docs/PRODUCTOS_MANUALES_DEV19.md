# CSMP dev19: productos manuales y revisión de nóminas

## Funciones incorporadas

**Correos → Nuevo manual** crea un borrador sin Excel ni análisis previo. Para, CC, asunto, texto y archivos se editan en el editor habitual. Puede incorporar una nómina escrita manualmente. El guardado en Outlook conserva la cuenta configurada y la copia institucional; siempre guarda borradores, sin enviar.

**Registros incluidos → Revisar registros / generar Excel** abre una tabla y sus campos. Seleccionar otra fila conserva la edición en el diálogo; Incluir esta fila permite omitirla, y Añadir registro incorpora otra. Cancelar descarta los cambios de ese diálogo. Guardar revisión conserva las correcciones pendientes; Revisar y generar Excel crea el adjunto con bordes, filtro, texto literal y cabeceras congeladas. Ningún Excel automático se genera antes de revisar la nómina en la interfaz. Los cambios afectan solo a este correo y su adjunto. El original RUS y el trabajo principal se conservan.

Al preparar de nuevo un correo se mantienen sus correcciones por identidad de registro, pero se exige otra revisión y generación del adjunto. Se conserva la procedencia y el control de cambios del producto. Los programas mantienen sus archivos separados. Antes de Guardar todos, todas las nóminas pendientes deben revisarse; el botón no crea y guarda silenciosamente un conjunto sin revisión.

**Eliminar correo** retira el borrador seleccionado de CSMP. Para los sugeridos, la omisión se guarda con el trabajo y se respeta al volver a prepararlos. **Restaurar omitidos** permite volver a proponerlos al preparar. Si ya existe una copia en Outlook, esa copia permanece; la acción no borra correo externo ni adjuntos guardados. Los manuales se eliminan de la biblioteca local de productos manuales.

**Resoluciones → Nuevo manual** abre un editor independiente. Texto libre permite escribir un proyecto para cualquier tribunal con tribunal, RIT y cuerpo. Puede utilizar una matriz existente del tribunal y tipo correctos: completa los campos, Cargar texto de matriz, revisa/editas el texto y Generar Word. Cambiar datos después de preparar exige cargar y revisar nuevamente la matriz. Un archivo existente no se sobrescribe. Las matrices instaladas de base son Laja y Mulchén; no se inventa una matriz de Tomé ni se reutiliza la de otro tribunal.

Los correos manuales, sus ediciones, los recibos de Outlook y el último proyecto manual se conservan en `manuales/productos_manuales.json` bajo la configuración de CSMP Integral. Cambiar el Excel de Trabajo no elimina los manuales. La recuperación de la descarga y de las sesiones anteriores se conserva.

## Otras mejoras recomendadas

| Mejora | Ubicación | Implementación propuesta |
| --- | --- | --- |
| Biblioteca buscable de productos manuales | CSMP | Guardar varios proyectos por tribunal/RIT, fecha, título y estado; recuperar sin reconstruir el análisis. |
| Plantillas favoritas para correo libre | CSMP | Elegir plantilla y completar variables explícitas; generar vista previa y dejar Para editable. |
| Duplicar manual para otra gestión | CSMP | Copia con identidad nueva, sin recibos de Outlook, y adjuntos que requieren revisión. |
| Resumen final antes de Outlook | CSMP | Comparar cantidades incluidas/omitidas, destinatarios y archivos con el borrador revisado. |
| Perfiles con fechas relativas | Descargador | Ampliar favoritos con mes actual/siguiente y filtros explícitos, sin guardar sesión ni filtros privados. |
| Lista de verificación de fuentes | Descargador | Resumen legible de consultas, páginas, períodos y compatibilidad, enlazando cada original. |
| Revisar bitácoras para todos los tribunales | Módulo separado RUS | Leer identidad del ingreso, recuperar observaciones hasta cuatro meses y exportar evidencias. |
| Registrar propuestas en bitácora | Módulo separado RUS | Validar tribunal/RIT/persona/centro, previsualizar cada texto, guardar y comprobar recibo; Al Tribunal = CC 1. |
| Resoluciones firmadas | Investigación separada | Validar navegación de Carga y fechas en vivo antes de ofrecer alertas; queda fuera de la descarga conjunta actual. |

Las reglas, comunicaciones automáticas y proyectos históricos siguen limitados a Laja, Mulchén y Tomé. Un producto libre no amplía esas reglas. Las propuestas de bitácoras y firmas no se presentan como funciones verificadas en vivo.

## Verificación

Pruebas con datos ficticios: creación de manuales sin Excel, recuperación y prevención de duplicados, edición de nómina sin alterar la fuente, texto seguro frente a fórmulas, omisiones persistentes, campos/matriz del tribunal correcto y preservación de los flujos anteriores. Outlook se simula en pruebas; ningún correo real se crea durante la validación.
