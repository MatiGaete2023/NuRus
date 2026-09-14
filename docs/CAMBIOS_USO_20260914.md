# Ajustes de uso — 14 de septiembre de 2026

Versión consolidada: **0.4.0.dev3**. Objetivo: preparar Excel, Word y borradores con menos pasos, manteniendo revisión humana y sin escribir en RUS/SATURNO ni enviar correos.

## Cambios consolidados

- Solo Windows; CI en Python 3.12, 3.13 y 3.14.
- Observaciones de gestiones ejecutadas restauradas a “Se remite…” / “Se remite proyecto…”. La matriz documental de reglas se sincroniza con `textos_base.json` y existe una regresión que impide divergencias futuras.
- FAS se clasifica como Familia de acogida.
- La planilla revisada respeta el modo elegido cuando contiene columnas de otros modos.
- Cumplimiento sin cruce utilizable deja advertencia y no evalúa C-10; ya no bloquea ni muestra diálogo de excepción en CSMP Assistant personal.
- Correos: selección de modalidades, editor ampliado, carga de planilla modificada/externa, guardado de todo el lote y adjuntos automáticos con nombre del programa.
- Resoluciones: tipo manual independiente, agrupación tribunal + RIT + tipo, una resolución por grupo y un único Word con salto de página entre proyectos.
- Matrices: seis bases disponibles (Laja y Mulchén). Cinco cuerpos revisados se verifican por SHA-256; PC_INFO Laja se incorporó desde Word antiguo. Tomé sigue pendiente por falta de fuente.
- La revisión de matrices repone correctamente un archivo eliminado aun cuando la revisión ya estaba marcada como aplicada.
- Recursos de matrices divididos en cinco payloads pequeños independientes para evitar corrupción/truncamiento del archivo monolítico anterior.
- `.gitignore` cubre ahora `.venv-csmp`, `dist`, `build` y `*.egg-info` para evitar incorporar entornos o productos locales al repositorio.

## Verificación

La CI comprueba instalación aislada, wheel, dependencias, compilación, suite, cinco parches y seis matrices. Python 3.12 agrega smoke GUI y distribución Windows. El run exacto de cada release se identifica por el SHA del HEAD; no se usa un número de ejecución fijo como fuente única porque quedaría obsoleto al actualizar documentación.

## Límites

No hay matrices de Tomé. La CI no acredita comportamiento real de Excel 2010/Outlook clásico ni calidad jurídica de una resolución concreta; esas verificaciones siguen siendo humanas/institucionales.

[G-ESTADO] Código y documentación alineados para 0.4.0.dev3.
[L-SIGUIENTE] Ejecutar aceptación Office institucional con copias autorizadas.
