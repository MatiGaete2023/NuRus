# CSMP Assistant personal

Una carga de Excel para analizar Espera, Cumplimiento o Informes, abrir una copia preservada y preparar Word y borradores desde el mismo trabajo.

Versión 0.4.0.dev1. La aceptación del flujo completo en Excel y Outlook institucionales sigue siendo necesaria; no se declara validación productiva.

## Instalar y abrir

1. Extrae el ZIP completo en una carpeta donde puedas escribir, por ejemplo Documentos\CSMP.
2. Ejecuta **Instalar_CSMP.bat**. Reutiliza Python 3.12, 3.13 o 3.14; crea un entorno separado `.venv-csmp`. No pide cambiar políticas ni privilegios de administrador.
3. Ejecuta **Abrir_CSMP.bat**. Usa este acceso para la interfaz nueva.

Se requieren Windows, Excel de escritorio, Outlook clásico y Python compatible. La instalación descarga dependencias salvo que la carpeta `paquetes` contenga sus ruedas institucionales. Sin acceso a ese repositorio de paquetes, solicita el conjunto offline; no se modifican proxy ni controles institucionales. No requiere Node ni servicios de IA externos.

## Trabajo habitual

Selecciona modo y archivo y pulsa **PROCESAR**. La salida aparece en la carpeta indicada; **Abrir Excel** abre esa copia. Se preservan hojas y contenido original y se agregan campos de propuesta/revisión. Los excluidos permanecen coloreados.

La observación oficial se registra manualmente en RUS. Si corriges OBSERVACION, FECHA_OBS, TT, CC o RES en la copia, guarda Excel y usa **Actualizar cambios**; Correos y Resoluciones también consultan la misma copia. No necesitas volver a seleccionarla. Los campos de identidad deben conservarse aunque ordenes las filas.

Si falta el cruce de Cumplimiento, se conserva el análisis y se pide el motivo de la excepción antes de exportar. Si falla Excel, puedes reintentar la exportación sin repetir el análisis.

## Correos

Preparar vista previa arma textos y adjuntos por destinatario desde el trabajo activo. Edita Para, CC, asunto, cuerpo y adjuntos; **Guardar borrador revisado** solo guarda en Outlook. Para puede quedar vacío. La copia a ucc_concepcion@pjud.cl se incorpora siempre. La cuenta se selecciona en Configuración; se carga su firma al abrir el borrador.

Los informativos que afirman revisión realizada requieren indicar las modalidades y confirmar ese alcance. Los registros externos se cargan una sola vez; selecciónalos en Trabajo y usa la opción de gestión particular.

## Resoluciones y configuración

Selecciona proyectos, verifica su procedencia y genera Word. Las cinco plantillas disponibles proceden del Asistente y se copian al directorio del usuario para editarlas en Word. Las matrices no disponibles se informan como pendientes. Incorpóralas desde Configuración: carpetas LAJA, MULCHEN y TOME; nombres PC_IE.docx, PC_INFO.docx, NOMENCL.docx; variables como {{RIT}}, {{NOMBRE}}, {{RUT}}, {{PROGRAMA}}, {{FECHA}}.

Configuración permite editar umbrales, textos, plantillas de correo, contactos, alias, cuenta y CC adicional. Las reglas iniciales son las del Asistente por instrucción del usuario; las observaciones proponen actuaciones y no afirman que ya se enviaron correos.

Enviados es de solo lectura: fechas, filtros textuales, total y exportación. Un borrador no se cuenta como correo enviado. El resumen de constancias utiliza la información humana de FECHA_OBS, TT y CC, diferenciándola de las propuestas.

## Documentación y pruebas

- [Estado, decisiones y trazabilidad de implementación](docs/IMPLEMENTACION_PERSONAL.md).
- [Protocolo de aceptación institucional](docs/ACEPTACION_CSMP_PERSONAL.md).
- [Referencia conservada del prototipo anterior](docs/README_NURUS_DEV7.md).

Pruebas: `python -m pytest -q`. Entrada nueva: `python -m nurus.personal.app`. La interfaz anterior conserva su módulo de referencia, pero no es el acceso recomendado para este paquete.
