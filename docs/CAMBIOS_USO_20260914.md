# Ajustes de uso - 14 de septiembre de 2026

## Objetivo vigente

Preparar Excel, Word y borradores con menos pasos, como insumos editables. El registro oficial de la gestión reside en RUS.

## Decisiones y cambios

| Observación del usuario | Cambio | Verificación |
|---|---|---|
| Solo Windows | CI exclusivo Windows/Python 3.12–3.14; prueba Tkinter en Windows | Instalación, suite y ventana |
| Restaurar observaciones anteriores | Defaults originales; migración de los textos dev1 sin sobrescribir personalizaciones | Test de migración y reglas |
| Nuevas matrices | Cinco matrices actualizadas desde el paquete del usuario; PC_INFO Laja incorporada desde Word antiguo; Tomé pendiente por falta de fuente | Hash del cuerpo XML, apertura DOCX y comparación visual |
| Un Word y agrupación por RIT | Lote único; tribunal/RIT/tipo; plural e individualización de personas | Test de agrupación, saltos de página y distinto tribunal |
| Modalidades seleccionables | Cuatro casillas, texto del correo y selección de registros; FAS se clasifica como Familia de acogida | Test de nómina filtrada |
| Elegir tipo de resolución | PC_IE, PC_INFO y NOMENCL asignables por usuario | Proyecto manual sin regla previa |
| No reconoce la planilla | Detección de hojas, encabezados desplazados y alias; prioridad al modo escogido para planilla revisada | Tabla con portada y columnas mixtas |
| Espacio para modificar productos | Editores ampliables de observación, correo y resolución; carga directa de planilla modificada | Prueba de ventana y texto editado en DOCX |
| Borradores en lote y adjuntos por programa | Guardar todos, resultados parciales y nombre de programa.xlsx | Save simulado, reintento y nóminas |
| Demasiadas validaciones | La ausencia del cruce C-10 en Cumplimiento deja advertencia pero ya no bloquea el producto | Regresión de flujo Cumplimiento |

## Matrices de resoluciones

El archivo `plantillas_word.zip` entregado por el usuario fue inspeccionado. Contiene las versiones revisadas de:

- LAJA/NOMENCL;
- LAJA/PC_IE;
- MULCHEN/NOMENCL;
- MULCHEN/PC_IE;
- MULCHEN/PC_INFO;
- LAJA/PC_INFO en formato Word antiguo, que fue convertido e incorporado previamente.

No contiene matrices de Tomé. Tomé continúa pendiente y ninguna matriz de otro tribunal se reutiliza como sustituto.

Las cinco matrices DOCX revisadas presentan el mismo resultado visible al conservar la estructura DOCX base y sustituir `word/document.xml` por el cuerpo de los archivos entregados. La comprobación local renderizó cada original y cada matriz reconstruida: los cinco pares fueron idénticos píxel por píxel a 120 dpi. Los cuerpos incorporados se almacenan comprimidos y cada uno tiene un SHA-256 esperado que se comprueba al instalar y después de reconstruir el DOCX.

La actualización de matrices se ejecuta una sola vez por revisión. Si el usuario ya tenía una matriz distinta, se conserva una copia de respaldo antes de sustituirla. Una modificación manual posterior queda preservada en siguientes inicios. Si una matriz desaparece, puede reponerse desde el paquete de la aplicación.

## Alcance exacto

- La revisión humana se realiza en RUS y sobre los archivos editables. No hay envío automático de correos.
- Los correos pueden prepararse desde una planilla externa sin reglas previas; el usuario escoge el tipo y las modalidades.
- Las ediciones de observación en pantalla afectan los productos de la sesión y su recuperación; no sobrescriben automáticamente el libro original.
- Cada resolución comienza en página nueva. Una resolución extensa puede continuar en otra página. Los grupos usan tribunal, RIT y tipo para evitar fusionar decisiones distintas.
- Se incorporó docxcompose como dependencia Python para el Word conjunto.
- Cumplimiento sin hoja de cruce no evalúa C-10, deja advertencia y continúa; no exige justificar una excepción para producir el insumo.
- El producto está orientado únicamente a Windows.

[G-ESTADO]
Matrices Laja y Mulchén incorporadas según las fuentes disponibles; Tomé pendiente por falta de matriz fuente. Cambios funcionales y pruebas preparados en la rama personal.

[L-SIGUIENTE]
Ejecutar y comprobar GitHub Actions en Windows 3.12–3.14 sobre el commit final y luego realizar la prueba de uso con Office institucional.
