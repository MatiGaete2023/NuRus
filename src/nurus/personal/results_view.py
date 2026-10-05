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
