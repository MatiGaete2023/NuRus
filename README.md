# CSMP Assistant personal — Windows

Versión **0.4.0.dev6**, actualizada el 16 de septiembre de 2026. Esta rama está orientada exclusivamente a Windows. El asistente prepara insumos editables; el registro oficial de la gestión se realiza en RUS. No escribe en RUS/SATURNO y no envía correos.

## Instalación y actualización

1. Descarga el ZIP de la rama `csmp-personal-2026-09-13` y extrae su contenido.
2. Ejecuta `Instalar_CSMP.bat` y luego `Abrir_CSMP.bat`.
3. Se admite Python 3.12, 3.13 o 3.14. El entorno queda en `.venv-csmp` dentro de la carpeta de la aplicación. No requiere permisos de administrador ni Node.
4. Excel de escritorio y Outlook clásico son necesarios para la ruta completa de uso institucional. La instalación normal puede descargar dependencias Python; si existe `paquetes/`, el instalador usa ese repositorio local.

La configuración del usuario se guarda en `LOCALAPPDATA/CSMP_Personal`. La actualización conserva la configuración y las matrices personalizadas. Las migraciones de textos y matrices dejan respaldo cuando corresponde.

## Flujo de trabajo

En Trabajo selecciona Espera, Cumplimiento o Informes, carga el Excel y pulsa **PROCESAR**. La copia generada se comparte con Correos y Resoluciones. Las observaciones de gestiones ejecutadas usan redacción apta para registrar posteriormente en RUS; que el motor genere ese texto no acredita por sí solo que la gestión haya sido realizada.

Puedes editar la observación directamente en la ventana. Al exportar se captura automáticamente el contenido visible aunque no hayas pulsado antes **Aplicar edición**. Si existe revisión humana, las filas modificadas quedan `REVISADO`; las no modificadas quedan `PENDIENTE`. Se exportan `OBSERVACION`, `FECHA_OBS`, `TT`, `CC` y `RES` sin borrar valores existentes que no fueron editados. La neutralización de fórmulas de Excel se conserva.

También puedes cargar una planilla modificada/externa. Se buscan encabezados en todas las hojas hasta la fila 60. Si falta un cruce utilizable en Cumplimiento, C-10 no se evalúa, se deja advertencia y el proceso continúa sin pedir una excepción ni bloquear la exportación.

## Correos

Las modalidades se seleccionan con casillas: Residencial, Ambulatorio, Familia de acogida y DCE. FAS se clasifica como Familia de acogida. Los campos Para, CC, asunto, cuerpo y adjuntos son editables antes de guardar.

**Preparar TODOS los correos necesarios** reúne el correo informativo general correspondiente a la pestaña revisada y todos los correos específicos detectados por las reglas. **Guardar TODOS los borradores** puede guardar un lote ya preparado o, si todavía no existe vista previa, preparar y guardar el conjunto necesario en una sola acción. No existe envío automático. Si no se conoce el destinatario, Para queda vacío. Siempre se incorpora la copia institucional configurada.

La identidad de un borrador depende de destinatarios efectivos, CC, asunto, cuerpo y contenido de los adjuntos. La ruta temporal de una nómina no forma parte de esa identidad: volver a preparar el mismo correo en otra carpeta UUID no habilita un duplicado, pero una edición real sí genera una identidad distinta.

Las copias nuevas incorporan una columna técnica oculta `NURUS_REGLAS`; al cargar una planilla modificada se recuperan esas reglas y, con ellas, los correos específicos que correspondan. Las copias anteriores intentan recuperar la misma información desde `NURUS_TRAZABILIDAD`.

## Resoluciones

Los proyectos se agrupan por **tribunal + RIT + tipo** y la lista muestra una sola fila por ese grupo. El tipo se determina con esta precedencia: tipo explícito en `RES` (`PC_IE`, `PC_INFO` o `NOMENCL`), observación humana revisada, acción del motor y, solo para un caso expresamente marcado sin información suficiente, el tipo manual de respaldo.

Una mención a informe/diagnóstico discrimina `PC_INFO`; ingreso efectivo/fecha estimada de ingreso discrimina `PC_IE`; nomenclatura discrimina `NOMENCL`. Si `RES` no fue utilizado, una observación por sí sola no crea un proyecto: debe existir una acción de resolución del motor. Para cambiar el tipo manualmente debes seleccionar de forma explícita la fila o filas concretas; no seleccionar nada ya no equivale a modificar todos los proyectos.

Si hay varias personas en el mismo RIT y tipo, se genera un solo proyecto y cada NNA queda individualizado junto a su propia cédula. **Generar UN Word** produce un único archivo y cada proyecto comienza en página nueva. Los datos ausentes se marcan como `[COMPLETAR ...]`. Las fechas insertadas por el generador se escriben íntegramente en palabras.

### Matrices vigentes

Hay seis matrices base: `LAJA/NOMENCL`, `LAJA/PC_IE`, `LAJA/PC_INFO`, `MULCHEN/NOMENCL`, `MULCHEN/PC_IE` y `MULCHEN/PC_INFO`. Cinco cuerpos DOCX provienen de la revisión del paquete entregado el 14-09-2026 y se verifican por SHA-256; `LAJA/PC_INFO` fue convertida desde el Word antiguo entregado. No hay matrices de Tomé: la aplicación no inventa ni reutiliza una matriz de otro tribunal.

## Arquitectura y mantenimiento

La versión 0.4.0.dev6 eliminó los cuatro módulos transitorios `runtime_fixes_20260916*`. Las correcciones quedaron incorporadas en los módulos definitivos, por lo que importar `nurus.personal` ya no modifica otros módulos mediante monkey-patching. El núcleo general de NuRus y sus ejecutables históricos se mantienen porque conservan una ruta de entrada y cobertura de pruebas propia; los documentos históricos se mantienen para trazabilidad.

## Estado de verificación

La CI de esta rama se ejecuta en Windows con Python 3.12, 3.13 y 3.14. Verifica instalación, wheel, recursos empaquetados, cinco parches de matrices, seis matrices base, dependencias, compilación, pruebas y contratos de higiene del repositorio; Python 3.12 además ejecuta el smoke de la GUI y construye la distribución Windows `CSMP-Windows-dev6`.

La validación automática no reemplaza la prueba final con Excel/Outlook institucionales. Consulta `docs/IMPLEMENTACION_PERSONAL.md`, `docs/VERIFICACION_PERSONAL.md`, `docs/AUDITORIA_REPOSITORIO_20260916.md` y `docs/INDICE_DOCUMENTACION.md`.
