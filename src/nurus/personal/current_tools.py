"""Herramientas del trabajo actual: pendientes, revisión, diagnóstico y entrega."""
from pathlib import Path
import json, os, sys, zipfile
from datetime import datetime
from tkinter import messagebox, filedialog
from .outputs import emails, CC, draft_fingerprint
from .product_state import stale
from nurus.services.file_output import write_new_file


def pending(work,drafts,projects):
    tasks=[]
    if work:
        for row in work.rows:
            if row.excluded:continue
            tasks.extend(('Aviso',row.id,str(w)) for w in row.warnings)
            if not row.review and row.observation:tasks.append(('Revisión',row.id,'Revisar observación propuesta'))
    for draft in drafts:
        if not draft.roster_reviewed:tasks.append(('Nómina',draft.subject,'Revisar y generar adjuntos'))
        if not draft.to.strip():tasks.append(('Contacto',draft.subject,'Completar destinatario'))
        if work and stale(work,draft):tasks.append(('Correo',draft.subject,'Actualizar producto'))
        elif work and draft_fingerprint(draft) not in work.receipts:tasks.append(('Correo',draft.subject,'Revisar y guardar borrador'))
    for project in projects:
        if project.review_required or (work and stale(work,project)):tasks.append(('Word',project.rit,'Revisar/actualizar proyecto'))
        elif work and not any(item.get('kind')=='word' and item.get('state')=='generated' and set(project.record_ids).issubset(item.get('record_ids',[])) and item.get('type')==project.kind and Path(item.get('path','')).is_file() for item in work.receipts.values()):tasks.append(('Word',project.rit,'Generar Word revisado'))
    return tasks


def summary(drafts):
    lines=[]
    for draft in drafts:
        to=emails(draft.to);cc=emails(CC+';'+draft.cc)
        if not to:raise ValueError('Completa el destinatario: '+draft.subject)
        if not draft.roster_reviewed:raise ValueError('Revisa primero la nómina de: '+draft.subject)
        if draft.required and not draft.attachments:raise ValueError('Falta adjunto requerido: '+draft.subject)
        if not draft.subject.strip() or not draft.body.strip():raise ValueError('Completa asunto y cuerpo del correo.')
        lines+=['ASUNTO: '+draft.subject,'PARA: '+'; '.join(to),'CC: '+'; '.join(cc),
                'Registros de origen: '+str(len(draft.record_ids))]
        for group in draft.roster:
            lines.append('NÓMINA · '+group['program'])
            lines.extend(' | '.join(row['cells']) for row in group['rows'] if row['include'])
        for attachment in draft.attachments:
            path=Path(attachment)
            if not path.is_file():raise ValueError('Adjunto no disponible: '+str(path))
            lines.append('ADJUNTO: '+str(path)+' · '+str(path.stat().st_size)+' bytes')
        lines+=['CUERPO:\n'+draft.body,'']
    return '\n'.join(lines)


def confirm_drafts(app,drafts):
    import tkinter as tk
    from tkinter import ttk
    content=summary(drafts);accepted=[]
    win=tk.Toplevel(app);win.title('Resumen antes de guardar en Outlook');win.geometry('850x650');win.transient(app)
    text=tk.Text(win,wrap='word');text.pack(fill='both',expand=True,padx=12,pady=12);text.insert('1.0',content);text.configure(state='disabled')
    ttk.Label(win,text='Se crearán borradores en Outlook. Revisa destinatarios, nómina, cuerpo y archivos.').pack()
    ttk.Button(win,text='Confirmar y guardar borradores',command=lambda:(accepted.append(True),win.destroy())).pack(pady=12)
    win.grab_set();app.wait_window(win)
    return bool(accepted)


def diagnosis(app):
    from nurus import __version__
    from importlib.metadata import version,PackageNotFoundError
    result={'producto':'CSMP Windows','version':__version__,'python':sys.version.split()[0],
            'rutas':{'ejecutable':sys.executable,'configuracion':str(app.cfg.directory),'matrices':str(app.template_dir)},
            'plantillas':len(list(app.template_dir.rglob('*.docx'))),'dependencias':{},'office':{}}
    for name in ('pandas','openpyxl','customtkinter','python-docx','pywin32'):
        try:result['dependencias'][name]=version(name)
        except PackageNotFoundError:result['dependencias'][name]='No instalado'
    if os.name=='nt':
        import winreg
        for name in ('Excel.Application','Word.Application','Outlook.Application'):
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,name):result['office'][name]='Registrado'
            except OSError:result['office'][name]='No registrado'
    else:result['office']['estado']='Comprobar en el equipo Windows de destino'
    return result


def export_diagnosis(app):
    path=filedialog.asksaveasfilename(defaultextension='.json',initialfile='Diagnostico_CSMP.json',parent=app)
    if path:write_new_file(Path(path),lambda p:p.write_text(json.dumps(diagnosis(app),ensure_ascii=False,indent=2),encoding='utf-8'));app.status.set('Diagnóstico creado: '+path)


def selected_zip(paths,destination):
    sources=[Path(p).resolve() for p in paths]
    if not sources:raise ValueError('Selecciona productos del trabajo actual.')
    if any(not p.is_file() for p in sources):raise ValueError('Algún producto seleccionado no está disponible.')
    if Path(destination).resolve() in sources:raise ValueError('El ZIP no puede reemplazar un producto seleccionado.')
    def write(target):
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
            for index,path in enumerate(dict.fromkeys(sources),1):archive.write(path,f'{index:03d}_{path.name}')
    write_new_file(Path(destination),write)
    return str(destination)


def deliver(app):
    paths=filedialog.askopenfilenames(title='Selecciona productos del trabajo actual',parent=app)
    if not paths:return
    destination=filedialog.asksaveasfilename(defaultextension='.zip',initialfile='Entrega_CSMP.zip',parent=app)
    if destination:app._run('Preparando entrega…',lambda:selected_zip(paths,destination),lambda p:app.status.set('Entrega creada: '+p))
