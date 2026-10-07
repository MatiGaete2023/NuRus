"""Editores de nóminas y proyectos manuales. No ejecutan reglas del trabajo."""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime,date
from pathlib import Path
from uuid import uuid4
import tkinter as tk
from tkinter import ttk,filedialog
import customtkinter as ctk

from . import ui
from .manual_products import update_table,generate_table,free_resolution,manual_project


def records_dialog(app,draft,source):
    table=deepcopy(source)
    win=ctk.CTkToplevel(app);win.title('Revisar registros antes del adjunto');win.geometry('1040x700');win.transient(app);win.grab_set()
    win.grid_columnconfigure(0,weight=1);win.grid_rowconfigure(1,weight=1)
    ui.Label(win,text='Estos cambios afectan solo a este correo y su Excel adjunto.',wraplength=960).grid(row=0,column=0,sticky='w',padx=15,pady=8)
    pane=ui.Frame(win);pane.grid(row=1,column=0,sticky='nsew',padx=12);pane.grid_columnconfigure(0,weight=1);pane.grid_rowconfigure(0,weight=1)
    cols=['incluir',*map(str,range(len(table['headers'])))]
    tree=ttk.Treeview(pane,columns=cols,show='headings',selectmode='browse',height=8)
    tree.heading('incluir',text='Incluir');tree.column('incluir',width=65,minwidth=65,stretch=False)
    for i,label in enumerate(table['headers']):tree.heading(str(i),text=label);tree.column(str(i),width=150,minwidth=90)
    tree.grid(row=0,column=0,sticky='nsew')
    vertical=ttk.Scrollbar(pane,orient='vertical',command=tree.yview);vertical.grid(row=0,column=1,sticky='ns')
    horizontal=ttk.Scrollbar(pane,orient='horizontal',command=tree.xview);horizontal.grid(row=1,column=0,sticky='ew')
    tree.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set)
    form=ui.Frame(win);form.grid(row=2,column=0,sticky='ew',padx=12,pady=8)
    variables=[tk.StringVar() for _ in table['headers']];included=tk.BooleanVar(value=True);active=[None]
    index={row['id']:row for row in table['records']}
    for i,(label,var) in enumerate(zip(table['headers'],variables)):
        col=(i%2)*2;row=i//2
        form.grid_columnconfigure(col+1,weight=1)
        ui.Label(form,text=label).grid(row=row,column=col,sticky='w',padx=5,pady=3)
        ui.Entry(form,textvariable=var).grid(row=row,column=col+1,sticky='ew',padx=5)
    def draw(row):
        values=['Sí' if row.get('include',True) else 'No',*row['values']]
        if tree.exists(row['id']):tree.item(row['id'],values=values)
        else:tree.insert('','end',iid=row['id'],values=values)
    def flush():
        row=index.get(active[0])
        if row:
            row['values']=[v.get() for v in variables];row['include']=included.get();draw(row)
    def select(event=None):
        selected=tree.selection()
        if not selected:return
        if selected[0]==active[0]:return
        flush();active[0]=selected[0];row=index[active[0]]
        for var,value in zip(variables,row['values']):var.set(value)
        included.set(row.get('include',True))
    tree.bind('<<TreeviewSelect>>',select)
    for row in table['records']:draw(row)
    commands=ui.Frame(win);commands.grid(row=3,column=0,sticky='ew',padx=12,pady=8)
    ui.Checkbutton(commands,text='Incluir esta fila',variable=included,command=flush).pack(side='left')
    def add():
        flush();row={'id':uuid4().hex,'values':['']*len(variables),'base_values':['']*len(variables),'include':True,'group':'Nomina manual','manual_added':True}
        table['records'].append(row);index[row['id']]=row;draw(row);tree.selection_set(row['id']);tree.see(row['id']);select()
    ui.Button(commands,text='Añadir registro',command=lambda:app._guard(add)).pack(side='left',padx=5)
    def finish(generate):
        flush();update_table(draft,table);app.attach.set('\n'.join(draft.attachments));app._save_session()
        win.destroy()
        if not generate:
            app.status.set('Nómina revisada guardada; el Excel sigue pendiente de generación.');return
        directory=Path(app.folder.get()) if app.folder.get() else app.cfg.directory/'salidas'
        def done(paths):
            app.draft_index=None;app._select_mail();app._save_session()
            app.status.set(f'{len(paths)} Excel adjunto(s) generados con los registros revisados. Revisa el correo antes de guardar en Outlook.')
        app._run('Generando la nómina revisada…',lambda:generate_table(draft,directory),done)
    ui.Button(commands,text='Guardar revisión',command=lambda:app._guard(lambda:finish(False))).pack(side='left',padx=5)
    ui.Button(commands,text='Revisar y generar Excel',width=185,command=lambda:app._guard(lambda:finish(True))).pack(side='right')
    ui.Button(commands,text='Cancelar',width=85,fg_color='transparent',border_width=1,command=win.destroy).pack(side='right',padx=5)
    if table['records']:tree.selection_set(table['records'][0]['id']);select()


def resolution_dialog(app):
    from .widgets import ScrollPane
    from .outputs import template_variables,date_in_words
    from .resolutions import Project,generate_projects
    state=deepcopy(app.manual_store.resolution)
    win=ctk.CTkToplevel(app);win.title('Proyecto de resolución manual');win.geometry('1000x740');win.transient(app);win.grab_set()
    win.grid_columnconfigure(0,weight=1);win.grid_rowconfigure(2,weight=1)
    ui.Label(win,text='Completa los datos y revisa el texto. No requiere Excel ni ejecuta las reglas de RUS.',wraplength=930).grid(row=0,column=0,sticky='w',padx=12,pady=8)
    top=ui.Frame(win);top.grid(row=1,column=0,sticky='ew',padx=12);top.grid_columnconfigure(1,weight=1)
    court=tk.StringVar(value=state.get('court',''));rit=tk.StringVar(value=state.get('rit',''))
    matrices={'Texto libre':None,**{p.parent.name+' / '+p.stem:str(p) for p in sorted(app.template_dir.glob('*/*.docx'))}}
    selected=tk.StringVar(value=next((k for k,v in matrices.items() if v==state.get('template') and v),'Texto libre'))
    for row,label,var in [(0,'Tribunal',court),(1,'RIT',rit)]:
        ui.Label(top,text=label).grid(row=row,column=0,sticky='w',padx=5);ui.Entry(top,textvariable=var).grid(row=row,column=1,sticky='ew',padx=5,pady=3)
    ui.Label(top,text='Matriz').grid(row=2,column=0,sticky='w',padx=5)
    selector=ui.Combobox(top,textvariable=selected,values=list(matrices),state='readonly');selector.grid(row=2,column=1,sticky='ew',padx=5,pady=3)
    split=ui.Panedwindow(win,orient='horizontal');split.grid(row=2,column=0,sticky='nsew',padx=12,pady=8)
    fields=ScrollPane(split);split.add(fields,weight=1)
    text=ui.Textbox(split,wrap='word',undo=True);split.add(text,weight=3);text.insert('1.0',state.get('text',''))
    values={};project=[Project(**state['project']) if state.get('project') else None]
    def collect():return {key:var.get() for key,var in values.items()}
    def save():
        app.manual_store.resolution={'court':court.get(),'rit':rit.get(),'template':matrices[selected.get()],
                                     'values':collect(),'text':text.get('1.0','end-1c'),
                                     'project':asdict(project[0]) if project[0] else None}
        app.manual_store.save()
    def load_fields(event=None):
        previous=collect() or state.get('values',{})
        for child in fields.body.winfo_children():child.destroy()
        values.clear();template=matrices[selected.get()]
        if not template:
            ui.Label(fields.body,text='Texto libre: escribe el proyecto completo a la derecha. Se genera un Word sencillo con tribunal y RIT.',wraplength=230).pack(padx=8,pady=8)
            return
        ui.Label(fields.body,text='Completa cada campo antes de cargar el texto de la matriz.',wraplength=230).pack(padx=8,pady=8)
        if not court.get():court.set(Path(template).parent.name)
        for key in sorted(template_variables(template)-{'RIT'}):
            ui.Label(fields.body,text=key.replace('_',' ')).pack(anchor='w',padx=6)
            var=tk.StringVar(value=previous.get(key,date_in_words(date.today()) if key=='FECHA' else ''));values[key]=var
            ui.Entry(fields.body,textvariable=var).pack(fill='x',padx=6,pady=(0,6))
    selector.bind('<<ComboboxSelected>>',load_fields);load_fields()
    actions=ui.Frame(win);actions.grid(row=3,column=0,sticky='ew',padx=12,pady=8)
    def preview():
        template=matrices[selected.get()]
        if not template:raise ValueError('En Texto libre, escribe directamente el proyecto.')
        project[0]=manual_project(template,court.get(),rit.get(),collect())
        text.delete('1.0','end');text.insert('1.0',project[0].text);save()
    def generate():
        template=matrices[selected.get()];body=text.get('1.0','end-1c')
        if not court.get().strip() or not rit.get().strip() or not body.strip():raise ValueError('Completa tribunal, RIT y texto.')
        if template:
            p=project[0]
            if not p or p.template!=template or p.court!=court.get() or p.rit!=rit.get() or p.values!={**collect(),'RIT':rit.get()}:
                raise ValueError('Cambiaste datos de la matriz. Pulsa Cargar texto de matriz y revisa el proyecto antes de generar.')
            p.text=body
        path=filedialog.asksaveasfilename(parent=win,title='Guardar proyecto manual',defaultextension='.docx',filetypes=[('Word','*.docx')],initialfile='Proyecto_manual_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.docx')
        if not path:return
        save()
        if template:result=generate_projects(app.manual_store,[deepcopy(project[0])],path)
        else:result=free_resolution(path,court.get(),rit.get(),body)
        app.status.set('Proyecto manual generado: '+result)
        saved_label.set('Generado: '+Path(result).name)
    ui.Button(actions,text='Cargar texto de matriz',width=175,command=lambda:app._guard(preview)).pack(side='left')
    ui.Button(actions,text='Guardar borrador local',width=165,command=lambda:app._guard(save)).pack(side='left',padx=6)
    ui.Button(actions,text='Generar Word',command=lambda:app._guard(generate)).pack(side='right')
    def close():
        save();win.destroy()
    ui.Button(actions,text='Cerrar',width=80,command=lambda:app._guard(close)).pack(side='right',padx=6)
    saved_label=tk.StringVar();ui.Label(win,textvariable=saved_label,wraplength=920).grid(row=4,column=0,sticky='w',padx=12,pady=4)
    win.protocol('WM_DELETE_WINDOW',lambda:app._guard(close))
