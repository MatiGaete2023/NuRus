# Ajustes de uso - 14 de septiembre de 2026

## Objetivo vigente

Preparar Excel, Word y borradores con menos pasos, como insumos editables. El registro oficial de la gestión reside en RUS.

## Decisiones y cambios

| Observación del usuario | Cambio | Verificación prevista |
|---|---|---|
| Solo Windows | CI exclusivo Windows/Python 3.12–3.14; prueba Tkinter en Windows | Instalación, suite y ventana |
| Restaurar observaciones anteriores | Defaults originales; migración de los textos dev1 sin sobrescribir personalizaciones | Test de migración y reglas |
| Nuevas matrices | Importador ZIP con respaldo y asignación inequívoca | ZIP sintético y DOCX existentes; adjunto real pendiente |
| Un Word y agrupación por RIT | Lote único; tribunal/RIT/tipo; plural e individualización de personas | Test de agrupación, saltos de página y distinto tribunal |
| Modalidades seleccionables | Cuatro casillas, texto del correo y selección de registros | Test de nómina filtrada |
| Elegir tipo de resolución | PC_IE, PC_INFO y NOMENCL asignables por usuario | Proyecto manual sin regla previa |
| No reconoce la planilla | Detección de hojas, encabezados desplazados y alias | Tabla con portada, fila 3, Nombre Menor/NOMBRE CENTRO |
| Espacio para modificar productos | Editores ampliables de observación, correo y resolución; carga directa de planilla modificada | Prueba de ventana y texto editado en DOCX |
| Borradores en lote y adjuntos por programa | Guardar todos, resultados parciales y nombre de programa.xlsx | Save simulado, reintento y nóminas |

## Alcance exacto

- La revisión humana se realiza en RUS y sobre los archivos editables. Se retiraron las casillas de aprobación de proyectos y de alcance de correo; se conserva únicamente la selección de lo que el usuario desea preparar.
- Se conserva el requisito cerrado de documentar la falta de cruce de Cumplimiento y el límite permanente de nunca enviar.
- Los correos pueden prepararse desde una planilla externa sin reglas previas; el usuario escoge el tipo y las modalidades.
- Las ediciones de observación en pantalla afectan los productos de la sesión y su recuperación; no sobrescriben automáticamente el libro original.
- Cada resolución comienza en página nueva. Una resolución extensa puede continuar en otra página. La composición usa el encabezado/pie del primer documento; los cuerpos, tablas e imágenes se incorporan mediante docxcompose. La revisión de matrices con encabezados distintos queda pendiente hasta leer el nuevo ZIP.
- Los grupos usan tribunal, RIT y tipo para evitar fusionar decisiones distintas. Los proyectos plurales requieren la revisión final de redacción habitual.
- Se incorporó docxcompose como dependencia Python, instalada en el entorno aislado. Referencia técnica: https://github.com/4teamwork/docxcompose (README y contrato de Composer).
- No se declara paridad ni incorporación de plantillas no leídas.

## Limitación de esta ejecución

El entorno local informó: exec-server connection attempt failed, timeout de inicialización. No se dispone de terminal ni acceso a los bytes de plantillas_word.zip. Se trabajó sobre el contenido vigente del repositorio; las pruebas se delegan al CI Windows, sin utilizar agentes ni ensayar otros sistemas operativos.

Las matrices nuevas son una dependencia pendiente de lectura, no una aprobación pendiente del usuario.

[G-ESTADO]
Cambios implementados en la rama personal; verificación Windows indicada por Actions.
Pendiente: inspeccionar e integrar plantillas_word.zip; comprobar salida con Office institucional.
[L-SIGUIENTE]
Incorporar las nuevas matrices cuando se restablezca el acceso a los archivos.
