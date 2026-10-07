"""Comprobación del ejecutable instalado con configuración temporal aislada."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys


def check(destination):
    from nurus import __version__
    from nurus.rus.catalog import load_catalog
    from .config import Configuration
    from .app import App
    from .template_package import _matrix_patches
    import nurus.personal as personal
    import xlrd,win32com.client,openpyxl
    destination=Path(destination).resolve();destination.parent.mkdir(parents=True,exist_ok=True)
    root=Path(personal.__file__).parent
    templates={p.relative_to(root/'plantillas_word').as_posix() for p in (root/'plantillas_word').rglob('*.docx')}
    expected={f'{court}/{kind}.docx' for court in ('LAJA','MULCHEN') for kind in ('NOMENCL','PC_IE','PC_INFO')}
    if templates!=expected:raise ValueError('Faltan matrices Word en el paquete: '+', '.join(sorted(expected-templates)))
    if len(_matrix_patches())!=5:raise ValueError('Faltan revisiones de matrices Word en el paquete.')
    if not load_catalog():raise ValueError('No se encuentra el catálogo de reglas del paquete.')
    with TemporaryDirectory(dir=destination.parent,prefix='csmp-check-') as folder:
        app=App(Configuration(Path(folder)))
        try:
            app.withdraw();app.update()
            for name in ('Trabajo','Correos','Resoluciones','Resultados','Configuración'):
                app.tabs.select(app.pages[name]);app.update()
            result={'version':__version__,'frozen':bool(getattr(sys,'frozen',False)),
                    'pages':list(app.pages),'templates':len(templates),'matrix_patches':5,'ok':True}
        finally:app.destroy()
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
