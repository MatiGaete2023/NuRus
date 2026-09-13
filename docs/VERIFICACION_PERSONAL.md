# Verificación CSMP personal

- Suite local sobre la implementación: **174 aprobadas, 1 omitida**, 13-09-2026, 9,78 segundos. Comando: `python -m pytest -q` con dependencias locales y src en PYTHONPATH.
- Tres flujos verticales, separación texto/acciones, preservación de fórmulas y ancho, exclusiones coloreadas, recuperación de constancias por identidad, umbrales, contradicción de fechas, borrador sin Para y CC obligatorio, configuración dañada, Word con variables entre runs y estadísticas: cubiertos en `tests/test_personal_flow.py`.
- Archivo .xls real de Cumplimiento suministrado: 262 registros reconocidos, cruce disponible. No se incorpora ese archivo ni datos personales al repositorio.
- Cinco matrices DOCX renderizadas con LibreOffice y revisadas visualmente: una página cada una, sin recortes. Las cinco proceden del generador Asistente; falta aprobación institucional del texto.
- Wheel construido con JSON y cinco DOCX; prueba de recursos instalada fuera de src.
- CI configurado para Windows/Linux con Python 3.12, 3.13 y 3.14; incluye prueba de ventana bajo Xvfb. El resultado remoto debe consultarse en Actions sobre el commit de la rama.
- Excel/Outlook institucionales, firma real y ahorro de tiempo: pendientes; véase ACEP-01 a ACEP-10. Las pruebas simuladas no acreditan ejecución Office.
