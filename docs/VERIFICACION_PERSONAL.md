# Verificación vigente — CSMP Assistant personal 0.4.0.dev11

Estado: **CI de dev11 pendiente de cierre**. Esta iteración modifica únicamente experiencia de usuario y documentación; no agrega `.exe` ni cambia los invariantes Office/RUS.

Base previa acreditada: dev10, commit `8546dab08ae9976c2e0f26810e2e49d5fee30ced`, run `35729404913`: Windows Python 3.12/3.13/3.14 success, 256 passed y 1 skipped por versión, smoke CustomTkinter y construcción de distribución Windows correctos.

Dev11 debe comprobar además:
- búsqueda y filtros no destructivos en Trabajo y Resoluciones;
- búsqueda por campos no visibles como nombre y RUT;
- descripciones legibles de PC_IE, PC_INFO y NOMENCL sin cambiar los códigos internos;
- origen visual de resoluciones y ajuste manual;
- barra de contexto persistente;
- acceso a carpeta de salida;
- atajos Ctrl+O, Ctrl+F, F5 y Ctrl+Enter;
- interfaz utilizable a 1024×650, con capturas adicionales de Trabajo y Resoluciones;
- distribución Windows dev11 correctamente referenciada.

La aceptación con Excel 2010 y Outlook institucional sigue definida en `ACEPTACION_CSMP_PERSONAL.md`.
