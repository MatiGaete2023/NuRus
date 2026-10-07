"""Comprobación del ejecutable instalado con configuración temporal aislada."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
import sys
from uuid import uuid4


def check(destination):
    from nurus import __version__
    from nurus.rus.catalog import load_catalog
    from .config import Configuration
    try:from ._build_meta import BUILD_COMMIT,BUILD_VERSION
    except ImportError:BUILD_COMMIT=BUILD_VERSION='unknown'
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
    executable=Path(sys.executable).resolve()
    app_root=executable.parent
    resource_root=Path(personal.__file__).resolve().parent
    resources=[path for path in (resource_root/'plantillas_word').rglob('*.docx') if path.is_file()]
    for package_root in (resource_root,resource_root.parent/'rus',resource_root.parent/'services'):
        if package_root.is_dir():
            resources.extend(path for path in package_root.rglob('*.json') if path.is_file())
    patches=resource_root/'matrix_patches'
    if patches.is_dir():resources.extend(path for path in patches.glob('*.b64') if path.is_file())
    resource_hashes={path.relative_to(app_root).as_posix():sha256(path.read_bytes()).hexdigest()
                     for path in sorted(set(resources))}
    if not getattr(sys,'frozen',False) or not executable.is_file():
        raise ValueError('La comprobación de distribución requiere el ejecutable congelado que se va a entregar.')
    if BUILD_COMMIT=='unknown' or BUILD_VERSION!=__version__:
        raise ValueError('El ejecutable no declara el commit y la versión de su código fuente.')
    exe_hash=sha256(executable.read_bytes()).hexdigest()
    folder=destination.parent/('.csmp-package-check-'+uuid4().hex)
    folder.mkdir()
    app=None
    try:
        app=App(Configuration(folder))
        app.withdraw();app.update()
        for name in ('Trabajo','Correos','Resoluciones','Resultados','Configuración','Enviados'):
            app.tabs.select(app.pages[name]);app.update()
        app._new_manual_mail()
        assert app.work is None and app.drafts[0].options['manual']
        app.subject.set('Prueba aislada de producto manual');app._save_session()
        from .manual_products import ManualStore
        assert ManualStore(folder/'manuales',app.cfg.data).drafts[0].subject=='Prueba aislada de producto manual'
        app._delete_mail()
        if not hasattr(app,'results_bitacora_button'):
            raise ValueError('No se encuentra la importación de bitácoras HAR en Resultados.')
        result={'version':__version__,'source_commit':BUILD_COMMIT,'frozen':True,
                'executable':executable.name,'executable_sha256':exe_hash,
                'resource_sha256':resource_hashes,'pages':list(app.pages),
                'templates':len(templates),'matrix_patches':5,'manual_mail_without_work_verified':True,
                'bitacora_har_button_verified':True,'ok':True}
    finally:
        if app is not None:app.destroy()
        shutil.rmtree(folder)
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
