# Implementación de NuRus

Fecha: 8 de septiembre de 2026. Base técnica: Python 3.12, Tkinter/ttk, SQLite local y Outlook Object Model opcional.

## Implementado en este cambio

F0: estructura modular, modelo de producto, base SQLite con catálogo versionado, pruebas de regresión iniciales y conservación de datos fuera de la carpeta del programa.

F1: el modelo impide asignar destinatarios por similitud; un correo sin dirección queda bloqueado y visible para completar manualmente. El renderizador valida variables y evita que una plantilla desconocida cambie una decisión del motor.

F2–F5: ventana única con Trabajo, Historial, Plantillas y Contactos; flujo Cargar–Revisar–Generar; editor de plantillas con versión nueva; comunicación particular sin planilla.

## Próximas implementaciones obligatorias antes de uso productivo

1. Migrar los lectores Excel y las reglas revisadas a `adapters/excel` y `services`, preservando fila, hoja y hash de origen.
2. Incorporar tablas `batches` y `products` al flujo de revisión: cada exportación debe usar la copia congelada y no recalcular al generar.
3. Añadir formulario de alta/importación Excel de contactos con comparación explícita y aceptación manual del lote.
4. Completar editor de perfiles de exportación y proyectos de resolución con ejemplos aprobados institucionalmente.
5. Implementar trabajador COM serial, elección de cuenta/carpeta y conciliación de resultados. Nunca enviar; solo guardar borradores después de confirmación explícita.
6. Ejecutar la matriz de `PRUEBAS.md` en Windows 10, Excel 2010 y Outlook clásico institucional antes de distribuir.

## Decisiones pendientes

[CONFLICTO_ABIERTO] Política institucional de CC, adjuntos y bloqueo por fila/lote. Fuente para resolver: instrucción vigente aprobada por la jefatura.

[CONFLICTO_ABIERTO] Catálogo final de textos de resolución y criterios que los activan. Fuente para resolver: modelos y oficios vigentes del CSMP/tribunales.
