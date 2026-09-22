# UX y observaciones dev12 — 22 de septiembre de 2026

Producto: **CSMP Assistant personal 0.4.0.dev12**. Rama de desarrollo: `ux-observaciones-20260922`.

## Objetivo

Aplicar una mejora UX acotada y las redacciones de observaciones aprobadas sin rediseñar el motor, sin alterar umbrales sustantivos y sin ampliar el producto hacia multiusuario, nube o servicios externos.

## Cambios funcionales

- Panel de detalle reutilizable en Trabajo, Correos y Resoluciones con datos disponibles de la causa y productos relacionados.
- Navegación Anterior/Siguiente incidencia basada exclusivamente en `Row.warnings`.
- Comparación original/final para observación, correo y proyecto Word; se oculta cuando no existe edición.
- Jerarquía de acciones: Actualizar desde Excel, Guardar borradores y Generar Word como acciones primarias; las demás permanecen disponibles.
- Éxitos y operación en curso se informan en la barra de estado; errores, decisiones y riesgos mantienen diálogos.
- Configuración se divide visualmente en Básico y Avanzado sin cambiar el formato persistido.
- Reanudación del último trabajo reutiliza `sesion/trabajo.json`; ya no se activa silenciosamente al iniciar y exige Continuar.
- Tooltips mínimos para `PC_IE`, `PC_INFO` y `NOMENCL`.
- `Enviados` conserva su implementación y se presenta al usuario como Historial.

## Observaciones y RES

Los catálogos activos `personal/textos_base.json` y `rus/textos_observaciones.json` quedan sincronizados con las redacciones aprobadas. La migración `revision_textos=3` reemplaza solamente textos que aún coinciden exactamente con el valor predeterminado anterior y conserva personalizaciones.

En Cumplimiento se elimina el prefijo genérico «Medida revisada.» cuando existe un hallazgo concreto. La composición prioriza estado principal, luego hitos procesales (oído/audiencia) y finalmente sugerencias como curador/fichas.

`INFORMES.I01_VENCIDO_GENERAL` e `I01_VENCIDO_DCE` mantienen la asociación estructurada a `PC_INFO`. `I02_*` continúa generando solo correo preventivo. No se deduce `PC_INFO` desde palabras de la observación.

## Lo que no cambia

No cambian los umbrales, modalidades, criterios de mayoría de edad, reglas de fichas, criterios de espera ni reglas de cruce. Se conservan Excel original intacto, copia revisable, RES categórico y legado, validación nativa Excel, Word, borradores Outlook, revisión humana, Windows y Python 3.12–3.14.

No se agrega SQLite, dashboard, gráficos, usuarios/roles, nube, API externa, IA, plugins, PySide6, Electron, C#, `.exe`, instalador ni actualización automática.

## Conflicto abierto

El conflicto histórico DCE/Informes permanece sin modificación: el manual documentado exige más de 40 días para pedir cuenta, mientras el motor vigente clasifica el informe como vencido desde que pasa la fecha. Dev12 no cambia ese umbral porque esta evolución autorizó redacción y `PC_INFO`, no reglas temporales sustantivas.

## Pruebas

Se agregan regresiones para textos exactos, sincronización de catálogos, migración sin sobrescribir personalizaciones, `PC_INFO` de vencidos, ausencia de `PC_INFO` por vencer, orden de composición, detalle de causa, incidencias, comparación, productos, reanudación y jerarquía UX.

La evidencia de CI y el SHA final se incorporan en `VERIFICACION_PERSONAL.md` cuando la rama quede verde.

## Validación real pendiente

La CI no acredita ergonomía real ni integración con Excel 2010/Outlook institucional. Antes de integrar a `main` deben probarse visualmente la navegación de incidencias, los paneles, las comparaciones, la recuperación de sesión y el flujo habitual completo.
