# CSMP Assistant personal - Windows

Versión **0.4.0.dev2**, actualización de uso del 14 de septiembre de 2026. El asistente genera insumos editables; el registro oficial de la gestión se realiza en RUS.

## Instalar o actualizar

1. Descarga el ZIP de la rama csmp-personal-2026-09-13 y extrae su contenido.
2. Ejecuta **Instalar_CSMP.bat**, luego **Abrir_CSMP.bat**.
3. Se utiliza Python 3.12, 3.13 o 3.14 en el entorno separado .venv-csmp. Excel de escritorio y Outlook clásico deben estar instalados en Windows. No se requieren permisos de administrador ni Node.
4. El instalador incorpora también docxcompose para unir los proyectos Word. Con instalación offline, agrega esta dependencia y las demás ruedas a la carpeta paquetes. La instalación normal descarga paquetes Python; no se cambian controles institucionales.

La configuración personal y sus matrices se conservan. La actualización restituye automáticamente los textos predeterminados de dev1 que se habían convertido a “Se sugiere…”, dejando respaldo y preservando las redacciones personalizadas.

## Flujo directo

Selecciona el Excel y pulsa PROCESAR. Abre la copia, registra la gestión en RUS cuando corresponda y ajusta la constancia en Excel. Correos y Resoluciones comparten esa copia.

Las observaciones vuelven a usar la redacción de gestión realizada del Asistente, conforme a la instrucción del usuario. Que el motor produzca ese texto no acredita que la gestión ya se ejecutó: se utiliza para el registro posterior en RUS.

Puedes editar la observación del registro en el área inferior de Trabajo. Esa edición se usa en los productos de la sesión; no escribe automáticamente en el original. También puedes cargar una planilla modificada desde Trabajo, Correos o Resoluciones, sin pasar otra vez por el motor. Se buscan encabezados en todas las hojas, hasta la fila 60; solo se solicita elegir hoja si hay más de una tabla reconocida y no se distingue la correspondiente.

Los excluidos siguen presentes y coloreados en el Excel del motor. La excepción documentada de Cumplimiento se mantiene si falta la hoja cruzada.

## Correos

Marca las modalidades con casillas: Residencial, Ambulatorio, Familia de acogida y DCE. Prepara los borradores y edita Para, CC, asunto, cuerpo o adjuntos en el panel ampliable.

**Guardar TODOS los borradores** guarda el lote con una sola acción. Puedes guardar solo el correo visible si lo prefieres. No hay aprobación por correo ni envío automático. Para desconocido queda vacío; siempre se agrega copia a ucc_concepcion@pjud.cl.

Las nóminas automáticas se nombran con el programa, por ejemplo AFT EJEMPLO.xlsx. Si un correo reúne varios programas, se adjunta una nómina por programa. Los caracteres no admitidos por Windows se sustituyen por guion bajo. Las subcarpetas internas evitan colisiones sin cambiar el nombre del adjunto.

Si parte del lote falla, se conservan los borradores creados. Al reintentar se omiten los ya guardados y los guardados inciertos, para evitar duplicados.

## Resoluciones

Elige PC_IE, PC_INFO o NOMENCL y aplica el tipo a los registros que quieras, con independencia de la sugerencia del motor. Si no hay sugerencias, el tipo elegido permite preparar desde los registros externos.

Preparar / actualizar proyectos agrupa por **tribunal + RIT + tipo**. Personas con nombres/RUT distintos de un mismo grupo quedan en un único proyecto con individualización y ajustes de plural. Proyectos de distinto tipo o tribunal se mantienen separados.

Edita el texto en el panel derecho y pulsa **Generar UN Word**. El archivo reúne el lote y cada proyecto comienza en página nueva. Si un proyecto es demasiado largo, puede ocupar más de una página; no se recorta información para forzarlo. Los datos que falten se marcan [COMPLETAR ...] para editarlos sin un interrogatorio previo.

Las matrices se editan desde Configuración. Puedes incorporar un DOCX indicando tribunal/tipo o importar un ZIP organizado como LAJA/PC_IE.docx, MULCHEN/PC_INFO.docx, etc. Se respalda cada matriz reemplazada. Los archivos sin identificación inequívoca se informan para asignarlos; no se asume una matriz judicial.

## Enviados y estadísticas

Enviados consulta Outlook en modo de solo lectura y exporta el resultado. El resumen diferencia constancias, borradores guardados, proyectos y archivos Word. Un borrador nunca se cuenta como correo enviado.

## Estado y verificación

Consulta [Cambios del 14 de septiembre](docs/CAMBIOS_USO_20260914.md) y GitHub Actions sobre el commit instalado. Las pruebas de compatibilidad se ejecutan únicamente en Windows con Python 3.12–3.14. La prueba con Excel/Outlook institucionales sigue siendo necesaria.

El ZIP de nuevas matrices adjuntado en la conversación aún no pudo inspeccionarse por indisponibilidad del entorno de archivos. Por ello esta actualización conserva las cinco matrices previamente incorporadas y añade el importador de paquetes. No se afirma haber integrado las nuevas ni las de Tomé.
