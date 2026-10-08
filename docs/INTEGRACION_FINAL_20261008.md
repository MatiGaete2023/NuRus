# CSMP 0.5.0.dev4 + SITFA Descargador 2.7.1 — integración de bitácoras
Actualizado el 8 de octubre de 2026.

## Producto y alcance
La rama `feat/consolidacion-bitacoras-20261008` parte de la versión 0.5.0.dev3
de `main`; conserva Trabajo, Correos, Resoluciones, Resultados, Configuración,
nóminas editables, Word y correo manual, preparación de borradores y recuperación.
Incorpora el lector, parser compartido, importación HAR, análisis y exportación
de bitácoras RUS de la rama experimental `f2809581`, junto al Descargador y
extensión 2.7.1.

Acceso: **Resultados → Más acciones → Bitácoras RUS**. Controles:
Consultar bitácoras (Chrome autenticado), recuperar consulta, importar HAR y
abrir `bitacoras.json`. Se elige el rango de análisis (hasta cuatro meses);
«Copia íntegra» contiene el texto de las observaciones de la tabla recuperada.
No existe envío de correo ni escritura de observaciones en este recorrido.

## Identidad, límites e integridad
Se coteja tribunal, causa e ingreso RUS, más contexto de etapa y modalidad.
Las diferencias visuales de nombre/RIT producen advertencias sin mezclar
ingresos; una identidad remota incompatible se rechaza. El control de lecturas
preserva errores, consultas fallidas y hash SHA-256; no presenta un fallo como
una bitácora vacía. Un HTML visible no acredita por sí solo todo el historial
que pudiera tener el servidor.

## Distribución y aceptación
Los workflows verifican CSMP 0.5.0.dev4, Descargador/extensión 2.7.1,
pruebas de identidad y recuperación, y construyen un paquete Windows conjunto.
La ejecución exacta de CI determina si está aprobado: este documento no
presume resultados de pruebas aún no realizadas.

Para usar lectura en lote, descargar **CSMP-Descargador-Integral-dev4** desde
GitHub Actions del commit aprobado. Extraer completo en carpeta nueva.
Desactivar extensiones antiguas y cargar la carpeta `extension` que viaja
con los dos EXE. El instalador individual de CSMP es un producto separado.

## Verificación institucional pendiente
Reabrir las dos bitácoras que anteriormente fallaron (10 de 12 consultadas),
contrastar RIT visible, nombre, texto completo, fecha, tipo y CC con RUS.
Extender a Residencia, Ambulatorio, FAE y DCE, pestañas, paginación,
interrupción y reintento. Nunca publicar HAR ni datos de NNA en el repositorio.
No se habilita escritura RUS ni se modifica SATURNO.

## Separación de líneas
`main` y `experimento/plan-integral-csmp-20261002` quedan intactas.
La consolidación de código está en una rama de integración; su promoción
exige resultados de CI y aceptación con sesión RUS real.
