# NuRus

Aplicación de escritorio local para preparar, revisar y generar productos del seguimiento de medidas de protección. Integra el análisis de planillas, la elaboración de borradores Outlook y el historial de resultados en una sola ventana.

## Alcance de esta versión

- Flujo único: **Cargar → Revisar → Generar**.
- Catálogo local SQLite de plantillas y contactos, editable desde la interfaz.
- Productos revisables: correo, resolución y exportación CSV.
- Versionado de plantillas: borrador/publicada; las ejecuciones conservan la versión usada.
- Historial local de lotes y productos; no se envía ningún correo.
- Adaptador Outlook aislado. Solo crea borradores cuando se ejecuta expresamente en Windows con Outlook clásico y `pywin32` instalado.

## Requisitos

Python 3.12. Para la interfaz no se necesitan dependencias externas. En Windows, la integración opcional con Outlook clásico requiere `pywin32`.

```powershell
py -3.12 -m pip install -e .[dev]
py -3.12 -m pytest -q
py -3.12 -m nurus.app
```

Los datos se crean en `%LOCALAPPDATA%\\NuRus` en Windows o `~/.local/share/NuRus` en otros sistemas. No instales la base en una carpeta compartida de red.

## Seguridad y operación

No hay envío automático. Un producto sin destinatario permanece revisable y no se intenta crear como borrador Outlook. Los textos de plantilla aceptan únicamente variables declaradas, no HTML libre ni recursos remotos. Antes de habilitar el uso productivo, revisar `docs/IMPLEMENTACION.md` y ejecutar la matriz de `docs/PRUEBAS.md`.
