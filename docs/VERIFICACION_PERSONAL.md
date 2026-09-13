# Verificación CSMP personal

- Suite local sobre la implementación: **174 aprobadas, 1 omitida**, 13-09-2026, 9,78 segundos. Comando: `python -m pytest -q` con dependencias locales y src en PYTHONPATH.
- Tres flujos verticales, separación texto/acciones, preservación de fórmulas y ancho, exclusiones coloreadas, recuperación de constancias por identidad, umbrales, contradicción de fechas, borrador sin Para y CC obligatorio, configuración dañada, Word con variables entre runs y estadísticas: cubiertos en `tests/test_personal_flow.py`.
- Archivo .xls real de Cumplimiento suministrado: 262 registros reconocidos, cruce disponible. No se incorpora ese archivo ni datos personales al repositorio.
- Cinco matrices DOCX renderizadas con LibreOffice y revisadas visualmente: una página cada una, sin recortes. Las cinco proceden del generador Asistente; falta aprobación institucional del texto.
- Wheel construido con JSON y cinco DOCX; prueba de recursos instalada fuera de src.
- CI configurado para Windows/Linux con Python 3.12, 3.13 y 3.14; incluye prueba de ventana bajo Xvfb. El resultado remoto debe consultarse en Actions sobre el commit de la rama.
- Excel/Outlook institucionales, firma real y ahorro de tiempo: pendientes; véase ACEP-01 a ACEP-10. Las pruebas simuladas no acreditan ejecución Office.

## Resultado remoto de cierre

Commit de código comprobado: `1cd8e278609a7eea30a256bf787c1ae3d8054c62`.

[GitHub Actions, ejecución 34768182687](https://github.com/MatiGaete2023/NuRus/actions/runs/34768182687): **6/6 trabajos aprobados**, Windows y Linux con Python 3.12, 3.13 y 3.14. La ejecución Windows 3.13 registró 174 aprobadas y una omitida. La prueba de ventana de Linux 3.12 aprobó las cinco pestañas y los recursos Word.

Los 39 archivos publicados fueron comparados mediante su SHA de blob con el contenido local: sin diferencias. ZIP íntegro comprobado mediante CRC, incluye ambos .bat de CSMP y cinco matrices Word. La actualización documental posterior conserva exactamente el código de este commit.
