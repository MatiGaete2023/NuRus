# Resumen de estado — CSMP integral y Descargador · 8 de octubre de 2026

## Objetivo
CSMP Assistant es el producto principal y SITFA Descargador/extensión sus
auxiliares. Las reglas, correos y resoluciones tradicionales pertenecen a Laja,
Mulchén y Tomé. La lectura de bitácoras abarca los tribunales y las cuatro
modalidades disponibles (Ambulatorio, FAE, Residencia, DCE), con selección de
pestañas y paginación. La escritura RUS está aplazada expresamente.

## Evolución, causas y correcciones
1. Se obtuvo lectura local de bitácoras desde HAR y luego recorrido por lotes.
2. El listado no se reconocía con el mismo parser que la descarga normal:
   se ajustó el reconocimiento y el diagnóstico.
3. Se descubrió una extensión más nueva que carecía de diary_open; se integró
   el contrato CSMP–Descargador–extensión dev22 / 2.7.0, incluyendo capacidades,
   retorno comprobado, lectura GET, Excel, PDF y recuperación.
4. En una consulta de doce registros hubo diez bitácoras leídas y dos fallidas
   por diferencias visuales de RIT/nombre pese a coincidir tribunal, causa e
   ingreso. Se identificaron tres controles estrictos: lectura, reutilización
   e importación a CSMP. Dev23 / 2.7.1 unifica la validación: los identificadores
   remotos prevalecen, la diferencia visible genera una advertencia revisable
   y una respuesta de otro ingreso sigue rechazándose.

## Estado de implementación
- Procesamiento Excel, revisión, propuestas, correos borrador y Word: disponibles
  en las líneas CSMP; mantener copia original y supervisión humana.
- Descarga principal y calendarios de informes actual y siguiente: integrados
  en flujo conjunto. No se incluye la consulta de resoluciones firmadas.
- Lectura de bitácoras por lotes: código implementado en rama experimental,
  incluyendo copia íntegra de tabla, análisis hasta cuatro meses y control de
  consultas fallidas; no está acreditada la cobertura remota de todo el historial.
- Guardado de observaciones: no implementado con sesión institucional; no se
  habilita ni se supone fecha real desde una intención local.
- `main` (0.5.0.dev3) y esta rama integral (0.4.0.dev23) no están consolidadas.
  La fusión queda condicionada a la aceptación real de lectura y regresión.

## Comprobación y siguientes acciones
Las pruebas de identidad deben cubrir identidad remota válida con grafía
diferente, identidad remota incorrecta, exportación de advertencias y reintento.
Las CI Windows comprueban CSMP, Descargador, extensión, artefactos y contrato,
pero no sustituyen consulta autenticada real. Verificar la ejecución GitHub
Actions correspondiente al commit publicado antes de usar el nuevo paquete.

Obtener artefacto CSMP-Integral-Windows-dev23 y extensión 2.7.1 de la misma
ejecución. Releer en RUS los dos ingresos previamente fallidos, comparar su
texto con la pantalla y comprobar que las advertencias no desaparecen. Extender
la aceptación a todas las modalidades y pestañas; solo entonces comparar y
consolidar `main` con la rama integral. Mantener inhabilitada la escritura.

Fuentes: `docs/INTEGRACION_COMPLETA_20261008.md`,
`docs/BITACORAS_LOTES_DEV21.md`, `docs/REGISTRO_RECUPERABLE_20261005.md`
y `main/docs/MEJORAS_DISENO_20261007.md`.
