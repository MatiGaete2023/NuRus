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
        from .bitacora_lote import import_lote
        from .bitacora_link import verify_reply
        assert app.results_bitacora_live_button.winfo_exists()
        result={'version':__version__,'source_commit':BUILD_COMMIT,'frozen':True,
                'executable':executable.name,'executable_sha256':exe_hash,
                'resource_sha256':resource_hashes,'pages':list(app.pages),
                'templates':len(templates),'matrix_patches':5,'manual_mail_without_work_verified':True,
                'bitacora_har_button_verified':True,'bitacora_lote_button_verified':True,'ok':True}
    finally:
        if app is not None:app.destroy()
        shutil.rmtree(folder)
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')


def check_integral(destination,downloader):
    """Ejecuta ambos binarios y el retorno/exportación reales con un lote ficticio."""
    from datetime import date
    import subprocess,tempfile
    from types import SimpleNamespace
    import openpyxl
    from nurus import __version__
    from .integral_contract import validate,bundled_downloader,choose
    from .bitacora_link import finish,write
    from .bitacoras import earliest
    destination=Path(destination).resolve();destination.parent.mkdir(parents=True,exist_ok=True)
    downloader=Path(downloader or bundled_downloader()).resolve()
    if not getattr(sys,'frozen',False):raise ValueError('Esta prueba requiere los ejecutables Windows entregados.')
    with tempfile.TemporaryDirectory(prefix='integracion-ficticia-',dir=destination.parent) as temp:
        folder=Path(temp);lot=folder/'lotes';lot.mkdir()
        capabilities=validate([str(downloader)],folder)
        app=SimpleNamespace(cfg=SimpleNamespace(directory=folder,data={},save=lambda data:None))
        selected=choose(app)
        if Path(selected[0]).resolve()!=downloader:raise ValueError('CSMP no eligió el descargador del mismo paquete.')
        result=subprocess.run([str(downloader),'--generar-lote-prueba',str(lot)],timeout=60,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode:raise ValueError('No se generó el lote ficticio con el descargador entregado.')
        reply=json.loads((lot/'prueba.json').read_text(encoding='utf-8'))
        today=date.today();request={'id':'ficticio','folder':str(folder),'desde':earliest(today).isoformat(),
            'hasta':today.isoformat(),'corte':today.isoformat(),'destino':str(folder/'Bitacoras.xlsx'),
            'descargador':capabilities,'estado':'PENDIENTE'}
        write(folder/'respuesta.json',{**reply,'id':request['id']})
        app=SimpleNamespace(_run=lambda text,action,done:done(action()),status=SimpleNamespace(set=lambda text:None))
        finish(app,request)
        if request['estado']!='EXPORTADA':raise ValueError('CSMP no completó el retorno del lote.')
        book=openpyxl.load_workbook(request['archivo'])
        try:
            assert book['Copia íntegra']['M2'].value=='Texto completo'
            assert book['Copia íntegra']['K2'].value==1
            assert book['Copia íntegra']['M2'].border.left.style=='thin'
            assert book['Lecturas']['K2'].value=='LEIDA'
            assert book['Consultas']['D2'].value=='ENUMERADA'
            sheets=book.sheetnames
        finally:book.close()
        proof={'ok':True,'datos':'ficticios','csmp_version':__version__,'descargador':capabilities,
            'csmp_exe_sha256':sha256(Path(sys.executable).read_bytes()).hexdigest(),
            'descargador_exe_sha256':sha256(downloader.read_bytes()).hexdigest(),
            'seleccion_descargador_del_paquete':True,'retorno_lote_verificado':True,'excel_generado_por_csmp':True,'texto_completo':True,
            'cc_al_tribunal_1':True,'bordes':True,'hojas':sheets,'peticiones_reales_rus':0,'escrituras_rus':0}
    write(destination,proof)
