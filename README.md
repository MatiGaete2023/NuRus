# CSMP Assistant personal — Windows

Versión **0.4.0.dev4**, actualizada el 14 de septiembre de 2026. Esta rama está orientada exclusivamente a Windows. El asistente prepara insumos editables; el registro oficial de la gestión se realiza en RUS. No escribe en RUS/SATURNO y no envía correos.

## Instalación y actualización

1. Descarga el ZIP de la rama `csmp-personal-2026-09-13` y extrae su contenido.
2. Ejecuta `Instalar_CSMP.bat` y luego `Abrir_CSMP.bat`.
3. Se admite Python 3.12, 3.13 o 3.14. El entorno queda en `.venv-csmp` dentro de la carpeta de la aplicación. No requiere permisos de administrador ni Node.
4. Excel de escritorio y Outlook clásico son necesarios para la ruta completa de uso institucional. La instalación normal puede descargar dependencias Python; si existe `paquetes/`, el instalador usa ese repositorio local.

La configuración del usuario se guarda en `LOCALAPPDATA/CSMP_Personal`. La actualización conserva la configuración y las matrices personalizadas. Las migraciones de textos y matrices dejan respaldo cuando corresponde.

## Flujo de trabajo

En Trabajo selecciona Espera, Cumplimiento o Informes, carga el Excel y pulsa **PROCESAR**. La copia generada se comparte con Correos y Resoluciones. Las observaciones de gestiones ejecutadas usan redacción apta para registrar posteriormente en RUS; que el motor genere ese texto no acredita por sí solo que la gestión haya sido realizada.

Puedes editar la observación en pantalla o cargar una planilla modificada/externa. Se buscan encabezados en todas las hojas hasta la fila 60. Si falta un cruce utilizable en Cumplimiento, C-10 no se evalúa, se deja advertencia y el proceso continúa sin pedir una excepción ni bloquear la exportación.

## Correos

Las modalidades se seleccionan con casillas: Residencial, Ambulatorio, Familia de acogida y DCE. FAS se clasifica como Familia de acogida. Los campos Para, CC, asunto, cuerpo y adjuntos son editables antes de guardar.

**Preparar TODOS los correos necesarios** reúne en una sola operación el correo informativo general correspondiente a la pestaña revisada y todos los correos específicos detectados por las reglas (espera, informes vencidos/por vencer y medidas vencidas/por vencer). `especial` y `proyectos` siguen siendo productos manuales. **Guardar TODOS los borradores** guarda el lote preparado con una sola acción. No existe envío automático. Si no se conoce el destinatario, Para queda vacío. Siempre se incorpora la copia institucional configurada. Las nóminas automáticas se nombran con el programa; si un correo reúne varios programas se crea una nómina por programa.

Las copias nuevas incorporan una columna técnica oculta `NURUS_REGLAS`; al cargar una planilla modificada se recuperan esas reglas y, con ellas, los correos específicos que correspondan. Las copias de versiones anteriores intentan recuperar la misma información desde la hoja oculta `NURUS_TRAZABILIDAD`.

## Resoluciones

El tipo `PC_IE`, `PC_INFO` o `NOMENCL` se puede asignar de forma independiente de la sugerencia del motor. Los proyectos se agrupan por **tribunal + RIT + tipo**. Si hay varias personas en el mismo grupo, se genera un solo proyecto con la individualización correspondiente.

**Generar UN Word** produce un único archivo y cada proyecto comienza en página nueva. Los datos ausentes se marcan como `[COMPLETAR ...]`. Todas las fechas insertadas por el generador de proyectos se escriben íntegramente en palabras, por ejemplo: `catorce de septiembre de dos mil veintiséis`.

### Matrices vigentes

Hay seis matrices base: `LAJA/NOMENCL`, `LAJA/PC_IE`, `LAJA/PC_INFO`, `MULCHEN/NOMENCL`, `MULCHEN/PC_IE` y `MULCHEN/PC_INFO`. Cinco cuerpos DOCX provienen de la revisión del paquete entregado el 14-09-2026 y se verifican por SHA-256; `LAJA/PC_INFO` fue convertida desde el Word antiguo entregado. No hay matrices de Tomé: la aplicación no inventa ni reutiliza una matriz de otro tribunal.

La revisión empaquetada se aplica una sola vez. Si sustituye una matriz existente, se conserva respaldo. Las ediciones manuales posteriores no se pisan en los siguientes inicios. Si una matriz se elimina, la aplicación la repone desde el paquete y vuelve a aplicar el cuerpo vigente.

## Estado de verificación

La CI de esta rama se ejecuta solo en Windows con Python 3.12, 3.13 y 3.14. Verifica instalación, wheel, recursos empaquetados, cinco parches de matrices, seis matrices base, dependencias, compilación y pruebas; Python 3.12 además ejecuta el smoke test de la GUI y construye la distribución Windows.

La validación automática no reemplaza la prueba final con Excel/Outlook institucionales. El estado actual y la clasificación de la documentación están en `docs/IMPLEMENTACION_PERSONAL.md`, `docs/VERIFICACION_PERSONAL.md` y `docs/INDICE_DOCUMENTACION.md`.
