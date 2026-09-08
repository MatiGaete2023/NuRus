# NuRus

Aplicación de escritorio local para analizar y revisar planillas del seguimiento de medidas de protección con trazabilidad y control humano.

**Versión de esta rama:** `0.2.0.dev1`. No está aprobada todavía para uso productivo.

## Invariante de correo

**NuRus nunca envía correos electrónicos.** La integración Outlook solo puede guardar borradores mediante `Save()`, después de una confirmación explícita. El destinatario puede quedar vacío para completarlo durante la revisión humana. No existe una ruta automática de envío.

## Disponible actualmente

- Motor RUS único para **Espera, Cumplimiento e Informes**.
- Lectura de una copia estable del Excel; el SHA-256 corresponde a los mismos bytes procesados.
- Soporte `.xlsx`/`.xlsm` mediante `openpyxl` y `.xls` mediante el extra `xlrd`.
- Procedencia por archivo, SHA-256, hoja y fila física.
- Detección visible de columnas ambiguas y de filas bloqueadas.
- GUI: seleccionar archivo no equivale a analizar; botón **Analizar archivo** ejecuta lector y reglas fuera del hilo de Tkinter.
- Vista de revisión por fila con RIT, tribunal, programa, observación, reglas e incidencias.
- Aprobación, edición con motivo, exclusión con motivo y restauración de propuesta.
- Snapshot SHA-256 del lote aprobado; los productos posteriores deben usar ese snapshot y no recalcular la planilla.
- SQLite local con claves foráneas activas, lote/origen persistente y versiones inmutables de plantillas.
- Comunicación particular sin planilla RUS.
- Adaptador Outlook aislado para **guardar borradores únicamente**. Todavía no está conectado a la GUI productiva.

## Pendiente antes de uso productivo

- Preparar correos, proyectos de resolución y exportaciones exclusivamente desde snapshots aprobados.
- Importación de contactos con vista previa, comparación y aceptación manual.
- Perfiles de exportación y modelos de resolución aprobados.
- Integración Outlook serial con selección de cuenta/carpeta, prevención de duplicados y conciliación de `Save()` incierto.
- Contador de correos enviados de solo lectura.
- Matriz completa de pruebas en Windows 10, Excel 2010 y Outlook clásico institucional.
- Paquete final de distribución; el `.exe` se evaluará después de estabilizar el flujo.

## Instalación recomendada en Windows

La instalación debe quedar aislada del Python general del equipo.

1. Descarga o clona el repositorio en una carpeta estable.
2. Ejecuta `Instalar_NuRus.bat`.
3. Después abre con doble clic `Abrir_NuRus.bat`.

El instalador crea `.venv` y usa ese Python para NuRus; no modifica políticas de Windows ni desactiva controles institucionales.

Instalación manual equivalente desde `cmd`:

```cmd
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[excel-legacy,outlook]"
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m nurus.app
```

Para desarrollo y pruebas:

```cmd
.venv\Scripts\python.exe -m pip install -e ".[dev,excel-legacy,outlook]"
.venv\Scripts\python.exe -m pytest -q
```

## Datos locales

La base de trabajo se crea en `%LOCALAPPDATA%\NuRus` en Windows o `~/.local/share/NuRus` en otros sistemas. No debe instalarse en una carpeta compartida de red ni subirse a GitHub con información de NNA.

## Seguridad y aceptación

NuRus no escribe en SATURNO y no envía correos. Cualquier función no cubierta por la matriz de `docs/PRUEBAS.md` debe permanecer deshabilitada o identificada como no validada. El estado técnico y los pendientes se mantienen en `docs/IMPLEMENTACION.md`.
