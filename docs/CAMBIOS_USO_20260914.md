# Ajustes de uso — 14–16 de septiembre de 2026

Versión consolidada vigente: **0.4.0.dev6**. Objetivo: preparar Excel, Word y borradores con menos pasos, manteniendo revisión humana y sin escribir en RUS/SATURNO ni enviar correos.

## Cambios consolidados previos

- Solo Windows; CI en Python 3.12, 3.13 y 3.14.
- Observaciones de gestiones ejecutadas restauradas a “Se remite…” / “Se remite proyecto…”. La matriz documental de reglas se sincroniza con `textos_base.json`.
- FAS se clasifica como Familia de acogida.
- Cumplimiento sin cruce utilizable deja advertencia y no evalúa C-10; no bloquea ni muestra diálogo de excepción en el flujo personal vigente.
- Correos: selección de modalidades, editor ampliado, carga de planilla modificada/externa, preparación integral y adjuntos automáticos con nombre del programa.
- Outlook: el Inspector usado para insertar firma se cierra después de guardar; no existe llamada de envío.
- Las planillas exportadas conservan `NURUS_REGLAS`; las copias anteriores pueden recuperar reglas desde `NURUS_TRAZABILIDAD`.
- Resoluciones: agrupación tribunal + RIT + tipo, un Word y una resolución por grupo, fechas en palabras, prevalencia de `RES`, correspondencia nombre/cédula y orden determinista.
- Matrices: seis bases Laja/Mulchén, cinco cuerpos revisados verificados por SHA-256 y reposición de matriz eliminada. Tomé sigue pendiente por falta de fuente.

## Consolidación del 16-09 — dev6

- Se eliminan los cuatro módulos transitorios `runtime_fixes_20260916*`. Sus comportamientos pasan a módulos definitivos; importar `nurus.personal` deja de producir monkey-patching.
- Trabajo captura la observación visible al exportar. Las filas editadas quedan `REVISADO`; las restantes `PENDIENTE`. Los campos técnicos existentes que no fueron modificados se preservan.
- Se mantiene la neutralización de fórmulas de Excel para observaciones que comienzan con caracteres interpretables como fórmula.
- La identidad de borradores pasa a contenido efectivo: Para, CC, asunto, cuerpo, obligatoriedad y nombre/hash de adjuntos. La ruta UUID temporal deja de formar parte de la identidad.
- **Guardar TODOS** puede preparar y guardar el lote si todavía no existe una vista previa preparada.
- Resoluciones usa precedencia tipo explícito en `RES` > observación revisada > acción del motor. Una observación sin RES ni acción de proyecto no crea por sí sola una resolución.
- La deduplicación tribunal/RIT/tipo se ejecuta antes de poblar la interfaz, no como limpieza visual posterior.
- Cambiar el tipo requiere una selección explícita y solo afecta esas filas. Agregar manualmente evita duplicar un proyecto ya visible para la misma causa/tipo.
- Se eliminan imports privados sin uso en los módulos de resoluciones/trabajo intervenidos y la función privada `_excel_column_name` sin referencias del exportador.
- Se agrega contrato de higiene de repositorio para impedir reaparición de `runtime_fixes_*` y basura generada común.
- Workflow actualizado a acciones actuales con runtime Node 24; distribución renombrada `CSMP-Windows-dev6`.

## Verificación

La CI comprueba instalación aislada, wheel, dependencias, compilación, suite, recursos, cinco parches y seis matrices. Python 3.12 agrega smoke GUI y distribución Windows. El run exacto se identifica por el SHA del HEAD.

## Límites y conflicto abierto

No hay matrices de Tomé. La CI no acredita comportamiento real de Excel 2010/Outlook clásico ni calidad jurídica de una resolución concreta; esas verificaciones siguen siendo humanas/institucionales.

[CONFLICTO_ABIERTO] El Manual de Funciones CSMP 2025 indica, para DCE en Informes, pedir cuenta de informes pendientes de entrega de más de 40 días. El motor vigente clasifica como `I01_VENCIDO_DCE` cualquier informe DCE cuya fecha de vencimiento ya pasó. No se modifica esta regla en esta auditoría porque requiere resolver la fuente operativa vigente antes de alterar producción.

[G-ESTADO] Código y documentación alineados para **0.4.0.dev6**.
[L-SIGUIENTE] Ejecutar aceptación Office institucional con copias autorizadas y resolver el conflicto de umbral DCE contra la instrucción operativa vigente.
