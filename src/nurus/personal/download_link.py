"""Lanzamiento del descargador y retorno comprobado de un flujo completo."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
from uuid import uuid4
from tkinter import filedialog


def verify_reply(path):
    path=Path(path)
    if path.stat().st_size>64_000:raise ValueError('La respuesta del descargador excede el tamaño permitido.')
    data=json.loads(path.read_text(encoding='utf-8'));source=Path(data['archivo']).resolve()
    if source.suffix.lower()!='.xlsx' or not source.is_file() or source.stat().st_size>80*1024*1024:raise ValueError('El resultado no es un libro disponible.')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=data.get('sha256'):raise ValueError('El libro cambió después de la descarga.')
    if data.get('modo') not in ('ESPERA','CUMPLIMIENTO'):raise ValueError('Modo de retorno no reconocido.')
    return source,data['modo']


def start(app):
    mode=app.mode.get()
    if mode not in ('ESPERA','CUMPLIMIENTO'):raise ValueError('Selecciona Espera o Cumplimiento para el flujo conjunto.')
    executable=app.cfg.data.get('descargador_integral','')
    if not executable or not Path(executable).is_file():
        executable=filedialog.askopenfilename(parent=app,title='Elegir el descargador de este prototipo',filetypes=[('Descargador Windows','*.exe'),('Descargador Python','descargador.py')])
        if not executable:return
        app.cfg.data['descargador_integral']=executable;app.cfg.save(app.cfg.data)
    folder=app.cfg.directory/'intercambio';folder.mkdir(parents=True,exist_ok=True)
    reply=folder/(uuid4().hex+'.json')
    command=([sys.executable,executable] if Path(executable).suffix.lower()=='.py' else [executable])
    command+=['--csmp-reply',str(reply),'--modo',mode,'--destino',app.folder.get()]
    process=subprocess.Popen(command,cwd=str(Path(executable).parent),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    app.status.set('Descargador abierto. Selecciona tribunales/modalidades y pulsa Descarga conjunta CSMP.')
    def poll():
        if not app.winfo_exists():return
        if reply.exists():
            def receive():
                source,returned_mode=verify_reply(reply)
                if app.work:app._capture_observation();app._save_session()
                app.file.set(str(source));app.mode.set(returned_mode);app.sheet.set(returned_mode);app._process()
            if app.busy:app.after(600,poll)
            else:app._guard(receive)
            return
        if process.poll() is not None:
            app.status.set('Descargador cerrado sin un libro nuevo. Los trabajos existentes se conservan.');return
        app.after(600,poll)
    app.after(600,poll)
