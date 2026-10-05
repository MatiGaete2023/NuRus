"""Funciones independientes accesibles sin preparar propuestas ni correos."""
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from . import ui
from .work import Work
from .reports import export_activity,export_management


def build(app):
    page=app.pages['Resultados']
    from .widgets import ScrollPane
    app.results_scrollpane=ScrollPane(page)
    app.results_scrollpane.pack(fill='both',expand=True)
    page=app.results_scrollpane.body
    ui.Label(page,text='Informes de uno o varios trabajos',font=('Segoe UI',19,'bold')).pack(anchor='w',pady=10)
    ui.Label(page,text='Las revisiones locales, las constancias del Excel y los registros comprobados en RUS se muestran por separado.',
             wraplength=770,text_color=ui.MUTED).pack(fill='x',pady=8)
    include=tk.BooleanVar(value=True);files=[];scope=tk.StringVar(value='Trabajo actual')
    ui.Checkbutton(page,text='Incluir el trabajo actual',variable=include).pack(anchor='w',pady=6)
    def choose():
        chosen=filedialog.askopenfilenames(title='Selecciona trabajo.json de las sesiones guardadas',filetypes=[('Sesión CSMP','trabajo.json')])
        if chosen:files[:]=[Path(p).parent for p in chosen];scope.set(f'{len(files)} sesiones adicionales')
    ui.Button(page,text='Elegir sesiones guardadas',command=choose).pack(anchor='w',pady=5)
    ui.Label(page,textvariable=scope).pack(anchor='w',pady=4)
    bar=ui.Frame(page);bar.pack(fill='x',pady=12)
    start=tk.StringVar(value=date.today().replace(day=1).isoformat());end=tk.StringVar(value=date.today().isoformat())
    for title,var in [('Desde · año-mes-día',start),('Hasta · año-mes-día',end)]:
        ui.Label(bar,text=title).pack(side='left',padx=5);ui.Entry(bar,textvariable=var,width=14).pack(side='left',padx=5)
    def generate(kind):
        current=app.work if include.get() else None
        if current:app._save_session()
        if not current and not files:raise ValueError('Incluye el trabajo actual o selecciona sesiones guardadas.')
        a,b=date.fromisoformat(start.get()),date.fromisoformat(end.get())
        path=filedialog.asksaveasfilename(defaultextension='.xlsx',initialfile='Informe_'+kind+'.xlsx')
        if not path:return
        def action():
            works=([current] if current else [])+[Work.load(folder) for folder in files]
            if kind=='firmas':return export_activity(works,path)
            return export_management(works,path,a,b)
        app._run('Generando informe…',action,lambda p:app.status.set('Informe creado: '+p))
    ui.Button(page,text='Informe de firmas y revisiones',width=280,command=lambda:app._guard(lambda:generate('firmas'))).pack(anchor='w',pady=8)
    ui.Button(page,text='Informe de gestión del período',width=280,command=lambda:app._guard(lambda:generate('gestion'))).pack(anchor='w',pady=8)
    def journal():
        from .registration import Journal
        path=app.cfg.directory/'registro_observaciones.sqlite'
        if not path.is_file():raise ValueError('Todavía no hay un diario de operaciones de registro en este prototipo.')
        return Journal(path)
    def export_operations():
        store=journal()
        path=filedialog.asksaveasfilename(defaultextension='.xlsx',initialfile='Operaciones_registro.xlsx')
        if not path:return
        from .registration import export_journal
        app._run('Exportando operaciones de registro…',lambda:export_journal(store,path),
                 lambda p:app.status.set('Informe creado: '+p))
    def return_dates():
        store=journal();work=app._require_work()
        source=work.output or work.path
        path=filedialog.asksaveasfilename(defaultextension=Path(source).suffix,
                                         initialfile=Path(source).stem+'_registro'+Path(source).suffix)
        if not path:return
        from .registration_excel import reconcile_excel
        app._run('Devolviendo fechas de registros comprobados…',
                 lambda:reconcile_excel(store,source,path,mode=work.mode,sheet=work.sheet),
                 lambda p:app.status.set('Copia creada con fechas comprobadas: '+p))
    ui.Label(page,text='Recibos de registro: estas opciones no envían observaciones a RUS.',
             text_color=ui.MUTED).pack(anchor='w',pady=(16,4))
    ui.Button(page,text='Informe de operaciones de registro',width=280,
              command=lambda:app._guard(export_operations)).pack(anchor='w',pady=5)
    app.results_return_button=ui.Button(page,text='Recuperar devolución de fechas a Excel',width=280,
                                       command=lambda:app._guard(return_dates))
    app.results_return_button.pack(anchor='w',pady=5)
