# Verificación vigente — CSMP Assistant personal 0.4.0.dev12

Estado de la rama dev12: **CANDIDATA DE EVOLUCIÓN CON CI VERDE; VALIDACIÓN REAL PARCIAL**. Dev11 sigue siendo la última candidata con validación funcional amplia hasta que dev12 complete la validación visual/operativa.

## Verificación dev12

Rama: `ux-observaciones-20260922`. Checkpoint de código verificado tras la corrección visual de Trabajo: `dfa7809505da47f13e2dbdf799ab820de05719a9`, GitHub Actions run `35867829076`, attempt 2: **success** en Windows con Python 3.12, 3.13 y 3.14; **273 passed, 1 skipped** por versión. Python 3.12 aprobó además el smoke CustomTkinter y la construcción de la distribución ZIP dev12. La primera ejecución 3.12 agotó el límite de 8 minutos sin fallo de aserción; la repetición aislada terminó correctamente. No se atribuye a dev12 la evidencia funcional amplia de dev11.

## Evidencia automatizada

Checkpoint UX dev11: `291c3929fbda63a336a1b04f6d402a7eb84236d0`, GitHub Actions run `35733322467`, Windows Python 3.12/3.13/3.14 en success.

Hotfix Excel RES: `b6c9d84b79b416dd7fc5fb9911a9ffe521934ac9`, GitHub Actions run `35737408005`, Windows Python 3.12/3.13/3.14 en success, **260 passed, 1 skipped** por versión. Python 3.12 aprobó además smoke CustomTkinter y construcción de la distribución Windows dev11.

El hotfix elimina la dependencia de `Application.International` al configurar la lista RES nativa de Excel; usa una hoja técnica oculta y el nombre `NURUS_RES_TIPOS`. La regresión cubre expresamente el escenario COM que produjo `'tuple' object is not callable` en Excel real.

## Evidencia de uso real — 23 de septiembre de 2026

La revisión visual de Trabajo confirmó una fricción de dev12: el detalle de causa repetía la observación y reducía excesivamente el editor. Se corrigió en `dfa7809505da47f13e2dbdf799ab820de05719a9` compactando el detalle solo en Trabajo y priorizando el espacio del editor. Falta comprobar visualmente esta corrección en el PC del usuario.

## Evidencia de uso real — 22 de septiembre de 2026

El usuario confirmó funcionamiento satisfactorio de:
- procesamiento y modificación del Excel;
- desplegable y clasificación `RES`;
- generación de proyectos de resolución;
- creación y edición de borradores de correo;
- modificación de parámetros/configuración.

Esta prueba ocurrió después del hotfix RES. Por ello dev11 pasa de prototipo abierto a **candidata funcional congelada**.

## Límites

No se considera todavía versión 1.0 estable. Continúan pendientes los casos específicos no confirmados en la prueba real y registrados en `ACEPTACION_CSMP_PERSONAL.md`, la decisión DCE, matrices Tomé y una breve etapa de uso cotidiano para detectar fricciones. El producto no envía correos y no escribe en RUS/SATURNO.
