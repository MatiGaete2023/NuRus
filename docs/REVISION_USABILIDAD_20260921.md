# Revisión de CSMP Assistant — 21 de septiembre de 2026

Versión: **0.4.0.dev7** de CSMP Assistant personal (no corresponde al antiguo NuRus dev7).
Base contrastada: `e64594b73946c6c7a6f13563b7d7b9f4fd27c0fe`, coincidente con main y la rama personal al inicio.

## Resultado y alcance

Se conserva el Asistente y sus cinco áreas. Se corrigen errores de preparación y se facilita mantener textos y matrices. No se reconstruye el motor ni se cambian umbrales, contactos o matrices judiciales por inferencia. Windows es el único destino. No hay dependencias nuevas respecto de dev6.

| Hallazgo en dev6 | Cambio aplicado | Objetivo / evidencia de verificación |
|---|---|---|
| Una plantilla particular creada en Configuración no posee acción del motor y podía producir cero borradores | El filtro de acciones se aplica solo a los tipos automáticos conocidos; las plantillas personales usan el alcance seleccionado | Permitir comunicaciones configurables; regresión con plantilla nueva y fila sin acciones |
| `draft_fingerprint()` validaba direcciones fuera del manejo de errores del lote | Cada validación queda dentro del manejo individual; se informa el fallo y se continúa | Un destinatario incorrecto no impide guardar otros borradores; prueba de reintento sin duplicados |
| Cambiar de plantilla/regla descartaba el editor sin guardar | Se guardan cambios válidos al cambiar o cerrar; un cambio inválido permanece en el editor y mantiene la selección anterior | Evitar pérdida de redacción; prueba de persistencia y error de variables |
| Los nombres editables de plantillas no se mostraban en Correos | Selectores con nombre legible e ID interno estable; nombres repetidos se distinguen por ID | Hacer útil el nombre configurado, sin romper reglas ni migraciones |
| Ventana mínima de 1040×700 y barra lateral larga | Tamaño inicial ajustado a pantalla, panel desplazable, casillas breves y acciones distribuidas | Controles accesibles en pantalla reducida; prueba Windows a 1024×650 |
| Umbrales poco explicativos y variables escritas de memoria | Etiquetas operativas e inserción de variables; editores con scroll y deshacer | Cambiar contenido sin Python ni recordar marcadores |
| Incorporar Word pedía escribir tribunal y código en dos diálogos | Selectores de tribunal/tipo, apertura directa en Word y reemplazo validado | Editar la matriz concreta con menos pasos; no inventar Tomé |
| Cambiar selección después de preparar Word podía generar la selección anterior | Se vuelve a preparar al variar la selección; se conservan ediciones de proyectos con datos iguales | Generar lo seleccionado actualmente |
| Accesos antiguos podían iniciar otra interfaz | Los dos BAT antiguos y el comando `nurus` remiten al Asistente | Un solo producto visible; conservación interna de dependencias compartidas |

Referencias de implementación: `src/nurus/personal/outputs.py`, `app.py`, `app_base.py`, `widgets.py`, `config.py`; regresiones en `tests/test_personal_usability_20260921.py` y `tools/smoke_personal_gui.py`.

## Uso después de actualizar

Instala con `Instalar_CSMP.bat` y abre con `Abrir_CSMP.bat`. No se requieren nuevas dependencias, otra versión de Python ni privilegios administrativos respecto de dev6. Los nombres anteriores son accesos de compatibilidad, no otra línea de producto.

En Configuración puedes cambiar umbrales, advertencias, textos, asuntos/cuerpos, contactos y alias. Los umbrales y observaciones rigen el próximo análisis: no reescriben una revisión humana existente. Los cambios de plantilla de correo rigen nuevas preparaciones, no un borrador ya editado. Las variables entre llaves deben conservarse cuando la validación de la observación lo exige. Los botones de guardar siguen disponibles y el cambio de selección guarda automáticamente textos válidos.

En Word y Outlook, escoge tribunal y tipo antes de abrir o reemplazar la matriz. El cuerpo del proyecto también sigue editable en Resoluciones. La selección determina el lote, un único Word agrupa tribunal/RIT/tipo y cada proyecto comienza en página nueva. El trabajo humano sigue realizándose fuera del Asistente; no se agregan aprobaciones para obtener insumos.

## Límites y pendientes materiales

- **C01 DCE:** permanece la divergencia documental >40 días frente a vencimiento; no se cambia la regla vigente.
- **Tomé:** siguen faltando matrices fuente. No se reutilizan otros tribunales.
- **Office institucional:** siguen pendientes ACEP-01 a ACEP-12. CI Windows no prueba Excel 2010, la cuenta ni la firma institucional.
- La revisión es dirigida a fricciones comprobables, no una certificación de ausencia de todo error. El ahorro de tiempo debe medirse en el mismo lote real.
- Se mantienen módulos internos `nurus` por dependencia y compatibilidad. Se retira su experiencia separada de los accesos distribuidos; borrar el núcleo compartido rompería lectura/exportación y no aporta ahorro al usuario.
- Las ediciones manuales de proyectos solo se reutilizan al volver a preparar si los datos del grupo no cambiaron; cambios simultáneos de planilla y redacción requieren revisar el nuevo proyecto.

## Verificación

Prevista: suite completa en Windows con Python 3.12, 3.13 y 3.14; prueba real Tkinter de botones visibles, editor, scroll y guardado de configuración; construcción del paquete y del ZIP. Los resultados y commit se incorporan al cerrar la ejecución.

[G-ESTADO]
Cambios de dev7 implementados desde dev6; comprobación Windows pendiente.
Decisión vigente: desarrollar exclusivamente CSMP Assistant personal.
[L-SIGUIENTE]
Completar CI Windows y registrar resultados antes de integrar en main.
