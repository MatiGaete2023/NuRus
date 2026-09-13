# Implementación CSMP Assistant personal — 13 de septiembre de 2026

## Resultado y alcance

Versión 0.4.0.dev1. Se implementó el flujo personal en cinco áreas: Trabajo, Correos, Resoluciones, Configuración y Enviados. La entrada es `Abrir_CSMP.bat`; el módulo es `nurus.personal.app`. El flujo normal usa una sesión compartida y una copia de Excel conocida; no solicita aprobar productos ni importar nuevamente el archivo que acaba de generar.

La revisión oficial continúa en RUS. El motor produce propuestas; los campos humanos de la copia son constancias. Generar un Word o guardar un borrador no acredita una gestión realizada ni un correo enviado.

## Decisiones vigentes

- Ante divergencias en observaciones prevalece Asistente v9.1, por instrucción expresa del usuario. Los textos operativos de correo se adaptan del manual CSMP y de la configuración suministrada.
- Las observaciones sugieren actuaciones; no afirman que el programa ya envió correos o remitió proyectos.
- Nunca enviar correo, escribir en RUS/SATURNO ni alterar el Excel original. Solo borradores Outlook; copia obligatoria a ucc_concepcion@pjud.cl, incluso cuando Para queda vacío.
- Mantener los registros excluidos, coloreados. Conservar hojas, fórmulas, estilos, anchos y filtros mediante el exportador nativo de NuRus. La ruta portable de pruebas no acredita fidelidad completa con Office.
- Falta de cruce de Cumplimiento: análisis permitido y exportación mediante excepción documentada; C-10 no se inventa.

## Matriz funcional ejecutada

| Función / fuente | Acción y destino | Objetivo | Evidencia de código |
|---|---|---|---|
| Reglas Asistente | Portar los tres módulos y catálogo | Mantener la decisión de dominio vigente | personal/motor/reglas_*.py |
| Regla, observación y acción | Separar claves de regla, texto y acciones | Editar redacción sin perder correos/proyectos | personal/motor/textos.py; personal/work.py:actions_for |
| Lectura/exportación NuRus | Reutilizar adaptadores con sesión liviana | Procesar .xls/.xlsx/.xlsm y proteger original | personal/work.py; rus/reader.py; services/exports.py |
| Trabajo del Asistente | Adaptar a procesar, exportar y abrir en una acción | Eliminar recargas y aprobaciones técnicas | personal/app.py |
| Creador de Correos | Portar experiencia de edición y configuración | Revisar destinatarios, asunto, cuerpo y adjuntos antes de Save | personal/config.py; personal/outputs.py |
| Contactos y alias | Fuente configurable única, importación Excel | Evitar destinatarios ambiguos o inventados | personal/outputs.py:resolve_contact/import_contacts |
| Resoluciones Asistente | Convertir cinco matrices disponibles a DOCX editables | Mejorar redacción desde Word sin tocar Python | personal/plantillas_word; outputs.py:fill_docx |
| Contador de Correos | Integrar adaptador de consulta y filtros | Exportar Enviados sin rutas personales fijas | personal/app.py; adapters/sent_mail.py |
| Persistencia/aprobaciones NuRus | Retirar del flujo visible; conservar referencia | Reducir pasos sin perder recuperación | personal/work.py:save/load; docs/README_NURUS_DEV7.md |
| Instalación | Entorno separado, Python 3.12–3.14 | Evitar el fallo de comando vacío y coexistir con dev7 | Instalar_CSMP.bat; Abrir_CSMP.bat |
| Estadísticas | Separar propuestas, constancias, Word y borradores | No contar recomendaciones como trabajo realizado | personal/statistics.py |

Las rutas bajo `personal` son relativas a `src/nurus`. El diseño visible sigue las áreas especializadas del Asistente; se reutilizan los adaptadores NuRus existentes. No se ejecutan dos motores para una misma operación. Los archivos antiguos permanecen como referencia, no como un segundo paso obligatorio.

## Reglas y parámetros

El catálogo congelado está en `REFERENCIA_CATALOGO_ASISTENTE.md`. El registro exacto de textos iniciales está en `src/nurus/personal/textos_base.json`; `config.py:defaults` aplica la formulación de propuesta. La matriz de claves, textos, acciones y ubicación está en `MATRIZ_REGLAS_PERSONAL.json`.

| Parámetro | Valor inicial | Fuente / conducta |
|---|---:|---|
| Espera DCE, Laja, Mulchén y Tomé | 30 días | E-05 Asistente |
| Proyecto de ingreso Tomé | 60 días | E-05 Asistente |
| Próxima mayoría | 60 días | E-03/C-02 |
| Oído reciente | 45 días | T-02 |
| Resolución e ingreso reciente | 30 días | E-04/C-03; límites exactos en código |
| Medida próxima a vencer | 45 días | C-05 |
| Informe por vencer | 30 días | I-02 |
| Ficha antigua / reciente / FAE | 180 / 30 / 120 días | C-07/C-08 |

C-10 utiliza identidad completa y la última fila futura válida del cruce, según Asistente. Duplicados discrepantes se advierten. Una hoja válida sin fechas futuras no exige excepción. No se restablece la eliminada C-06 ni se crean informes calculados.

Corrección de integridad: días negativos con egreso futuro no generan una afirmación de medida vencida; se registra incidencia y se omite el fragmento C-04 incompatible. El caso está probado. Se corrigió también el tratamiento de fechas datetime al introducir el reloj fijo para pruebas.

Las acciones se obtienen del identificador emitido: E05 solo correo → consulta al programa; E05 proyecto y correo → consulta + PC_IE; I01 → correo pendiente + PC_INFO sugerido; I02 → correo por vencer. C04/C05 permiten preparar la comunicación de medidas con confirmación del alcance revisado. Generar PC_INFO exige verificar manualmente la procedencia del pide cuenta. Modificar texto no modifica estas decisiones.

## Configuración y datos

La configuración se guarda por usuario bajo LOCALAPPDATA/CSMP_Personal; umbrales, textos, plantillas, contactos y alias se editan desde la interfaz. Escritura atómica y copia .bak antes de reemplazar. Un JSON dañado se informa y no se reemplaza silenciosamente. Las matrices Word se copian al usuario solo si no existen, preservando sus mejoras.

La sesión guarda origen, huella interna, copia producida y recibos. Las filas pueden ordenarse: se reconocen por identificador estable, comprobando su identidad. Si cambia RIT/RUT/nombre/tribunal/programa, se detiene la incorporación para evitar asociar constancias a otra persona. Si se mueve el Excel, Localizar copia sirve para recuperar esa situación excepcional. Correos y Word reutilizan automáticamente la copia habitual.

Un destinatario desconocido o ambiguo deja Para vacío. Direcciones inválidas se rechazan. Los adjuntos por grupo contienen solo los registros correspondientes. Se conservan recibos para impedir repetir un guardado creado o incierto; el estado incierto requiere revisar Outlook.

## Fuentes congeladas

- NuRus dev7: commit e50eee4859fcdced832b52e5177041694d6fd109, árbol db5868e9893c9fb659af591001082b4a6646c45c. La rama histórica se conserva.
- Asistente (1).zip: motor v9.1, catálogo de reglas y resoluciones/generador_resoluciones.py suministrados por el usuario.
- Creador de Correos.py, Contador de Correos.PY y config_correos_csmp.json: aportados por el usuario, utilizados como referencias de flujo y configuración.
- CSMP_2025_Fusionado(2).md: referencia operativa para consultas de espera e informes y comunicaciones informativas.
- Huellas SHA-256 de las fuentes disponibles: FUENTES_PERSONAL.json. El RUS Engine original no estuvo disponible en esta ejecución; no se declara paridad directa con él.

## Verificación y límites

La suite local registra 174 pruebas aprobadas y una omitida antes del cierre; los resultados adicionales y de CI se consignan en VERIFICACION_PERSONAL.md. El .xls real de Cumplimiento proporcionado se analizó: 262 registros y cruce reconocido. Ese análisis no sustituye la aceptación COM/Office.

Se construyó el wheel con recursos JSON y DOCX. Las cinco matrices se renderizaron y revisaron visualmente, una página cada una; no se observó texto recortado. La sustitución conserva párrafos, estilos y tokens divididos entre runs. Esto acredita generación documental, no aprobación judicial.

Pendientes externos: PC_INFO de Laja y matrices de Tomé no figuran entre las cinco fuentes disponibles; la aplicación permite incorporarlas, pero no inventa una matriz alternativa. Falta ejecutar Excel 2010/Outlook clásico, cuenta/firma institucional y medición comparada del ciclo mensual. No se afirma que 174 pruebas demuestren ahorro real de tiempo.

[G-ESTADO]
Objetivo: herramienta personal CSMP con una carga, propuestas y preparación de salidas con control humano.
Confirmado: implementación y 174 pruebas locales; 6/6 trabajos CI aprobados en Windows/Linux 3.12–3.14; paquete y fuentes comprobados.
Limitaciones: aceptación Office y matrices judiciales no suministradas.
[L-SIGUIENTE]
Ejecutar ACEP-01 a ACEP-10 del protocolo institucional y registrar los resultados.
