# Protocolo de aceptación real de lectura de bitácoras — CSMP dev23 / SITFA 2.7.1

**Estado:** PENDIENTE DE EJECUCIÓN EN RUS REAL. No confundir CI verde con aceptación de datos institucionales.

**Versión congelada para prueba:** commit `f2809581db486b78eff5f1b267a38609e9d23adf`.
Artefacto `CSMP-Integral-Windows-dev23` de
https://github.com/MatiGaete2023/NuRus/actions/runs/37811441614.
Extensión `2.7.1` de la carpeta `extension` dentro del mismo artefacto.
No mezclar componentes de entregas ni usar un EXE independiente de otra rama.

## 1. Preparación y contrato

1. Extraer todo el ZIP en una carpeta nueva y conservar juntas `CSMP_Integral`,
   `SITFA_Descargador` y `extension`.
2. Deshabilitar la extensión antigua de Chrome. Cargar como descomprimida la
   carpeta `extension` de esta misma entrega y comprobar versión `2.7.1`.
3. Cerrar cualquier conexión previa, volver a abrir RUS con sesión propia y
   conectar usando el código del Descargador. No copiar credenciales ni HAR
   con cookies al repositorio.
4. Iniciar consulta desde **CSMP → Resultados → Consultar bitácoras en RUS**,
   y comprobar que reconoce el Descargador y capacidades `bitacoras_lectura`,
   `descarga_conjunta`, `pdf_seleccion`, así como `escritura_rus=false`.
5. Confirmar que los Excel habituales del Descargador se siguen produciendo
   independientemente de las copias HTML de bitácoras.

## 2. Relectura de los dos casos que fallaron

Seleccionar el mismo tribunal, modalidad y pestaña en que se observaron los
dos fallos anteriores (12 enumerados / 10 leídos / 2 fallidos). Mantener una
copia local del lote original para comparar, sin publicarla.

Para cada ingreso antes fallido registrar localmente:

| Comprobación | Aceptación |
| --- | --- |
| Tribunal, ID de causa e ID de ingreso | Coinciden exactamente con el vínculo y la captura; no se sustituyen por RIT |
| RIT y nombre visibles | Si difieren en formato, queda advertencia explícita; no se descarta ingreso remoto válido |
| Estado de la lectura | `LEIDA`, con archivo HTML existente y SHA-256 comprobable |
| Tabla RUS frente a copia íntegra | Igual número de filas, fechas, tipos, etapas, autores y textos completos de centro/tribunal |
| Análisis y hojas de Excel | «Copia íntegra», «Lecturas», «Consultas» y «Capturas» reflejan la captura, sin ocultar advertencias |
| Recuperación | Reintentar no pierde lecturas comprobadas ni las duplica indebidamente |
| Caso de identidad incorrecta | Un `ID_Ingreso` remoto diferente continúa en `FALLIDA`; nunca se acepta por coincidencia de RIT/nombre |

No publicar nombres de NNA, RUN, textos de observaciones, copias HTML
institucionales ni capturas con datos personales en GitHub.

## 3. Ampliación de muestra

Con los dos casos aprobados, probar al menos una selección no vacía de cada
modalidad: **Ambulatorio, FAE, Residencia y DCE**. Cubrir **Espera** y
**Cumplimiento** donde la interfaz permita esas combinaciones, y comprobar
paginación (>1 página donde exista). Si una combinación no ofrece datos o
pestaña, registrarlo como «SIN DATOS/NO DISPONIBLE» y no como validada.

Incluir reintento de una falla recuperable, cancelación y conservación de
copias verificadas. Verificar que `SIN_VINCULO`, `FALLIDA` y consulta no
ejecutada no se interpreten como ausencia de observaciones.

## 4. Acta mínima de aceptación (completar localmente)

- Fecha y hora de prueba: PENDIENTE
- Equipo/Windows/Chrome: PENDIENTE
- Artefacto, commit y versiones verificadas: PENDIENTE
- Dos fallos anteriores: 0 de 2 acreditados en esta etapa
- Filas cotejadas contra RUS / discrepancias: PENDIENTE
- Modalidades verificadas: 0 de 4 acreditadas en esta etapa
- Pestañas y paginación: PENDIENTE
- Compatibilidad CSMP ↔ Descargador ↔ extensión en sesión real: PENDIENTE
- Resultado global: **NO ACEPTADO TODAVÍA**
- Observaciones o errores reproducibles: PENDIENTE

## 5. Puerta de integración con main

`main` y `experimento/plan-integral-csmp-20261002` están divergidas. El
comparador GitHub del 8-10-2026 identifica 10 commits de la integral no
incluidos en main, 36 de main no incluidos en la integral y 153 archivos de
diferencia. Estos números son fotografía del momento, no cifras permanentes.

Solo después de completar y aprobar el acta real:
1. Revisar por archivo la colisión de versiones, flujos, instaladores,
   reglas de negocio, GUI, Excel y CI, preservando funciones de ambas ramas.
2. Integrar en una rama candidata distinta; compilar ambos EXE y extensión
   desde ese mismo commit; ejecutar toda la CI.
3. Hacer una segunda prueba de regresión real antes de fusionar `main`.
4. Mantener deshabilitada la escritura de observaciones en RUS en todo momento.

**Prohibición de inferencias:** CI verde, datos ficticios o 10/12 lecturas
anteriores no acreditan que hoy se lean bien las dos bitácoras restantes.
