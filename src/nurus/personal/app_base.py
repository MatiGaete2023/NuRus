"""Interfaz personal CSMP: una carga, propuestas y preparación de salidas."""
from pathlib import Path
from datetime import date, datetime
from dataclasses import replace
from copy import deepcopy
import os
import queue
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

from .config import Configuration, PARAMETER_LABELS, VARIABLES
from .widgets import ScrollPane, NamedChoice
from .work import Work
from .outputs import create_draft, import_contacts
from .resolutions import KINDS, prepare_projects, generate_projects, automatic_project_selections
from .importing import SheetChoice
from nurus.rus.reader import list_workbook_sheets
from nurus.adapters.sent_mail import count_sent_mail, export_sent_report

class App(tk.Tk):
    def __init__(self,configuration=None):
        super().__init__()
        self.title('CSMP Assistant personal');self.geometry('1120x720');self.minsize(820,560)
        self.cfg=configuration or Configuration()
        self.work=None;self.drafts=[];self.draft_index=None;self.report=None;self.busy=False
        self.projects=[];self.project_index=None;self.last_word='';self.observation_id=None
        self.events=queue.Queue()
        self.template_dir=self.cfg.directory/'plantillas_word'
        self.template_dir.mkdir(parents=True,exist_ok=True)
        self._install_templates()
        self.status=tk.StringVar(value='Selecciona un Excel para comenzar.')
        ttk.Label(self,text='CSMP Assistant',font=('Segoe UI',20,'bold')).pack(anchor='w',padx=14,pady=(10,0))
        ttk.Label(self,text='Propuestas para revisión humana · Correos solo como borradores').pack(anchor='w',padx=14)
        self.tabs=ttk.Notebook(self);self.tabs.pack(fill='both',expand=True,padx=12,pady=10)
        self.pages={}
        for name in ('Trabajo','Correos','Resoluciones','Configuración','Enviados'):
            frame=ttk.Frame(self.tabs,padding=10);self.tabs.add(frame,text=name);self.pages[name]=frame
        self._work_page();self._mail_page();self._word_page();self._config_page();self._sent_page()
        ttk.Label(self,textvariable=self.status,wraplength=1050).pack(fill='x',padx=12,pady=5)
        self.protocol('WM_DELETE_WINDOW',self._close)
        self.after(100,self._poll)
        saved=self.cfg.directory/'sesion/trabajo.json'
        if saved.exists():
            try:self.work=Work.load(saved.parent);self._show_work();self.status.set('Trabajo anterior recuperado. Su copia Excel sigue disponible.')
            except Exception as exc:self.status.set('No se pudo recuperar el trabajo anterior: '+str(exc))

    def _install_templates(self):
        source=Path(__file__).parent/'plantillas_word'
        if source.exists():
            for path in source.rglob('*.docx'):
                dst=self.template_dir/path.relative_to(source);dst.parent.mkdir(parents=True,exist_ok=True)
                if not dst.exists():shutil.copyfile(path,dst)

    def _run(self,label,action,done=None):
        if self.busy:messagebox.showinfo('En curso','Espera a que termine la operación actual.');return
        self.busy=True;self.status.set(label)
        def worker():
            try:self.events.put((True,action(),done))
            except Exception as exc:self.events.put((False,exc,None))
        threading.Thread(target=worker,daemon=True).start()

    def _poll(self):
        try:
            while True:
                ok,result,done=self.events.get_nowait();self.busy=False
                if ok:
                    self.status.set('Operación terminada.')
                    if done:
                        try:done(result)
                        except Exception as exc:
                            self.status.set(str(exc));messagebox.showerror('No se completó la operación',str(exc))
                else:
                    if isinstance(result,SheetChoice):
                        self._choose_external_sheet(result.names)
                    else:
                        self.status.set(str(result));messagebox.showerror('No se completó la operación',str(result))
                    self._save_session()
        except queue.Empty:pass
        self.after(100,self._poll)

    def _save_session(self):
        self._capture_observation()
        if self.work and not self.busy:
            try:self.work.save(self.cfg.directory/'sesion')
            except OSError as exc:self.status.set('No se pudo guardar la recuperación: '+str(exc))

    def _close(self):
        if self.busy:messagebox.showinfo('Operación en curso','Espera a que termine antes de cerrar.');return
        try:
            self._save_text(notify=False);self._save_tpl(notify=False)
        except ValueError as exc:
            messagebox.showerror('Configuración pendiente',str(exc));return
        self._save_session();self.destroy()

    def _require_work(self):
        if self.busy:raise ValueError('Hay una operación en curso.')
        self._capture_observation()
        if not self.work or not self.work.output:raise ValueError('Procesa primero el Excel; se compartirá automáticamente con esta pestaña.')
        return self.work

    def _guard(self,action):
        try:
            if self.busy:raise ValueError('Espera a que termine la operación actual.')
            action()
        except Exception as exc:messagebox.showerror('Revisa los datos',str(exc))

    def _open(self,path):
        if not Path(path).exists():raise ValueError('No se encuentra el archivo o carpeta: '+str(path))
        if os.name=='nt':os.startfile(str(path))
        else:messagebox.showinfo('Archivo disponible',str(path))

    @staticmethod
    def _field(parent,label,variable,row,width=65):
        ttk.Label(parent,text=label).grid(row=row,column=0,sticky='w',pady=3)
        entry=ttk.Entry(parent,textvariable=variable,width=width);entry.grid(row=row,column=1,sticky='ew',padx=6,pady=3)
        parent.columnconfigure(1,weight=1);return entry

    @staticmethod
    def _tree(parent,columns):
        frame=ttk.Frame(parent);frame.pack(fill='both',expand=True,pady=8)
        tree=ttk.Treeview(frame,columns=columns,show='headings',selectmode='extended')
        for col in columns:tree.heading(col,text=col);tree.column(col,width=140,stretch=True)
        y=ttk.Scrollbar(frame,orient='vertical',command=tree.yview);x=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview)
        tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        tree.grid(row=0,column=0,sticky='nsew');y.grid(row=0,column=1,sticky='ns');x.grid(row=1,column=0,sticky='ew')
        frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1);return tree

    def _work_page(self):
        page=self.pages['Trabajo'];top=ttk.Frame(page);top.pack(fill='x')
        self.mode=tk.StringVar(value='ESPERA');self.file=tk.StringVar();self.sheet=tk.StringVar()
        self.folder=tk.StringVar(value=str(self.cfg.directory/'salidas'))
        mode_box=ttk.Combobox(top,textvariable=self.mode,values=['ESPERA','CUMPLIMIENTO','INFORMES'],state='readonly',width=20)
        mode_box.grid(row=0,column=0,pady=5)
        mode_box.bind('<<ComboboxSelected>>',self._mode_changed)
        self._field(top,'Archivo',self.file,1)
        ttk.Button(top,text='Buscar',command=self._choose).grid(row=1,column=2)
        ttk.Label(top,text='Hoja (automática si está vacía)').grid(row=2,column=0,sticky='w')
        self.sheet_box=ttk.Combobox(top,textvariable=self.sheet,state='readonly');self.sheet_box.grid(row=2,column=1,sticky='ew',padx=6)
        self._field(top,'Carpeta de salida',self.folder,3)
        ttk.Button(top,text='Cambiar',command=lambda:self._select_folder(self.folder)).grid(row=3,column=2)
        buttons=ttk.Frame(page);buttons.pack(fill='x',pady=5)
        extra=ttk.Frame(page);extra.pack(fill='x')
        ttk.Button(buttons,text='PROCESAR',command=lambda:self._guard(self._process)).pack(side='left',padx=3)
        ttk.Button(buttons,text='Abrir Excel',command=lambda:self._guard(lambda:self._open(self._require_work().output))).pack(side='left',padx=3)
        ttk.Button(buttons,text='Actualizar cambios',command=lambda:self._guard(self._refresh)).pack(side='left',padx=3)
        ttk.Button(extra,text='Localizar copia movida',command=lambda:self._guard(self._locate)).pack(side='left',padx=3)
        ttk.Button(extra,text='Exportar copia con mis cambios',command=lambda:self._guard(lambda:self._export_current())).pack(side='left',padx=3)
        self.summary=tk.StringVar();ttk.Label(page,textvariable=self.summary).pack(anchor='w')
        ttk.Button(page,text='Exportar resumen de constancias',command=lambda:self._guard(self._export_statistics)).pack(anchor='w')
        split=ttk.Panedwindow(page,orient='vertical');split.pack(fill='both',expand=True)
        table=ttk.Frame(split);edit=ttk.Frame(split);split.add(table,weight=3);split.add(edit,weight=2)
        self.records=self._tree(table,('Estado','RIT','Tribunal','Programa','Observación'))
        self.records.column('Observación',width=520);self.records.tag_configure('excluded',background='#fff2cc');self.records.tag_configure('warning',background='#fde9d9')
        self.records.bind('<<TreeviewSelect>>',self._detail)
        self.detail=tk.StringVar();ttk.Label(edit,textvariable=self.detail,wraplength=1000).pack(fill='x')
        ttk.Label(edit,text='Observación editable del registro seleccionado (se incorpora a los productos)').pack(anchor='w')
        self.observation_editor=ScrolledText(edit,wrap='word',height=5,font=('Segoe UI',10),undo=True);self.observation_editor.pack(fill='both',expand=True)
        ttk.Button(edit,text='Aplicar edición',command=lambda:self._guard(self._apply_observation)).pack(anchor='e')
        ttk.Button(extra,text='Cargar planilla modificada',command=lambda:self._guard(self._external)).pack(side='left')

    def _select_folder(self,var):
        path=filedialog.askdirectory()
        if path:var.set(path)

    def _mode_changed(self,event=None):
        # Una hoja seleccionada para otro modo no debe anular la detección automática.
        self.sheet.set('')

    def _choose(self):
        if self.busy:return
        path=filedialog.askopenfilename(filetypes=[('Excel','*.xls *.xlsx *.xlsm')])
        if path:
            self.file.set(path);self.sheet.set('')
            self._run('Leyendo nombres de hojas…',lambda:list_workbook_sheets(path),lambda names:self.sheet_box.configure(values=['',*names]))

    def _capture_observation(self):
        if self.observation_id and self.work:
            row=next((r for r in self.work.rows if r.id==self.observation_id),None)
            if row:
                text=self.observation_editor.get('1.0','end-1c')
                if text!=row.review.get('OBSERVACION',row.observation):
                    row.review['OBSERVACION']=text
                    if self.records.exists(row.id):self.records.set(row.id,'Observación',text)

    def _apply_observation(self):
        self._capture_observation();self._save_session()
        self.status.set('Edición incorporada a esta sesión y a sus productos.')

    def _detail(self,event=None):
        self._capture_observation()
        if self.work and self.records.selection():
            row=next(r for r in self.work.rows if r.id==self.records.selection()[0])
            self.observation_id=row.id
            self.detail.set('; '.join(row.warnings))
            self.observation_editor.delete('1.0','end');self.observation_editor.insert('1.0',row.review.get('OBSERVACION',row.observation))

    def _refresh(self):
        work=self._require_work()
        def done(result):
            if result:
                self._clear_drafts();self._show_work()
            self._save_session();self.status.set('Cambios incorporados. Prepara los correos y proyectos con los datos actualizados.' if result else 'La copia no ha cambiado.')
        self._run('Incorporando cambios de la copia…',work.refresh,done)

    def _export_statistics(self):
        from .statistics import export_summary
        work=self._require_work();path=filedialog.asksaveasfilename(defaultextension='.xlsx',initialfile='Resumen_constancias.xlsx')
        if path:self._run('Generando resumen de constancias…',lambda:export_summary(work,path),lambda p:(self._save_session(),self.status.set('Resumen exportado: '+p)))

    def _locate(self):
        work=self._require_work();path=filedialog.askopenfilename(filetypes=[('Excel','*.xls *.xlsx *.xlsm')])
        if path:
            old=work.output
            def relocate():
                work.output=path
                try:return work.refresh()
                except Exception:
                    work.output=old
                    raise
            def done(changed):
                if changed:
                    self._clear_drafts();self._show_work()
                self._save_session()
                self.status.set('Copia localizada. Cambios incorporados; prepara los productos actualizados.' if changed else 'Copia localizada; los productos preparados se conservan.')
            self._run('Comprobando copia localizada…',relocate,done)

    def _external(self):
        path=filedialog.askopenfilename(filetypes=[('Excel','*.xlsx *.xls *.xlsm')])
        if path:self._load_external(path)

    def _load_external(self,path,sheet=None):
        self.pending_external=path
        cfg=self.cfg.data;mode=self.mode.get()
        def done(work):
            self.work=work;self._clear_drafts();self.observation_id=None
            self._show_work();self._save_session();self.manual_mail.set(False)
            self.status.set(f'{len(work.rows)} registros incorporados desde {work.sheet}, fila {work.header}. Ya disponibles para todos los productos.')
        self._run('Reconociendo hojas, encabezados y observaciones…',lambda:Work.external(path,cfg,mode,sheet=sheet),done)

    def _choose_external_sheet(self,names):
        window=tk.Toplevel(self);window.title('Elegir tabla del libro');window.transient(self)
        ttk.Label(window,text='Hay varias tablas reconocidas. Elige la que necesitas:').pack(padx=15,pady=10)
        selected=tk.StringVar(value=names[0])
        ttk.Combobox(window,textvariable=selected,values=names,state='readonly',width=45).pack(padx=15)
        def apply():
            name=selected.get();window.destroy();self._load_external(self.pending_external,name)
        ttk.Button(window,text='Usar hoja',command=apply).pack(pady=15)

    def _clear_drafts(self):
        self.drafts=[];self.draft_index=None;self.mail_list.delete(0,'end')
        self._clear_mail_editor();self._clear_projects()

    def _clear_projects(self):
        self.projects=[];self.project_index=None
        self.project_list.delete(0,'end');self.project_editor.delete('1.0','end')
        self._prepared_selection=None
        self.last_word=''

    def _clear_mail_editor(self):
        for variable in (self.to,self.cc,self.subject,self.attach):variable.set('')
        self.body.delete('1.0','end')

    def _capture_mail(self):
        if self.draft_index is not None:
            d=self.drafts[self.draft_index];d.to=self.to.get();d.cc=self.cc.get();d.subject=self.subject.get();d.body=self.body.get('1.0','end-1c');d.attachments=[p for p in self.attach.get().split('\n') if p]

    def _select_mail(self,event=None):
        self._capture_mail()
        if not self.mail_list.curselection():return
        self.draft_index=self.mail_list.curselection()[0];d=self.drafts[self.draft_index]
        self.to.set(d.to);self.cc.set(d.cc);self.subject.set(d.subject);self.body.delete('1.0','end');self.body.insert('1.0',d.body);self.attach.set('\n'.join(d.attachments))

    def _attachment(self):
        paths=filedialog.askopenfilenames()
        if paths:self.attach.set('\n'.join([p for p in self.attach.get().split('\n') if p]+list(paths)))

    def _send_draft(self):
        work=self._require_work();self._capture_mail()
        if self.draft_index is None:raise ValueError('Primero prepara una vista previa.')
        draft=replace(self.drafts[self.draft_index])
        self._run('Guardando únicamente un borrador en Outlook…',lambda:create_draft(work,draft,confirmed=True),lambda r:(self._save_session(),self.status.set('Borrador guardado en Outlook. No se envió ningún correo.')))

    def _word_page(self):
        page=self.pages['Resoluciones']
        actions=ttk.Frame(page);actions.pack(fill='x')
        self.manual_word=tk.StringVar(value='PC_IE')
        ttk.Label(actions,text='Tipo:').pack(side='left')
        ttk.Combobox(actions,textvariable=self.manual_word,values=list(KINDS),state='readonly',width=14).pack(side='left',padx=6)
        ttk.Button(actions,text='Aplicar tipo a la selección',command=lambda:self._guard(self._assign_word_type)).pack(side='left')
        ttk.Button(actions,text='Agregar desde Trabajo',command=lambda:self._guard(self._add_words)).pack(side='left',padx=4)
        ttk.Button(actions,text='Cargar planilla modificada',command=lambda:self._guard(self._external)).pack(side='right')
        actions2=ttk.Frame(page);actions2.pack(fill='x',pady=5)
        ttk.Button(actions2,text='Seleccionar todos',command=lambda:self.words.selection_set(self.words.get_children())).pack(side='left')
        ttk.Button(actions2,text='Preparar / actualizar proyectos',command=lambda:self._guard(self._prepare_words)).pack(side='left',padx=5)
        ttk.Button(actions2,text='Generar UN Word',command=lambda:self._guard(self._generate_words)).pack(side='right')
        ttk.Button(actions2,text='Abrir Word generado',command=lambda:self._guard(lambda:self._open(self.last_word))).pack(side='right',padx=5)
        split=ttk.Panedwindow(page,orient='horizontal');split.pack(fill='both',expand=True)
        left=ttk.Frame(split);right=ttk.Frame(split);split.add(left,weight=2);split.add(right,weight=3)
        self.words=self._tree(left,('RIT','Tribunal','Tipo','Revisión'))
        self.project_list=tk.Listbox(left,height=5,exportselection=False);self.project_list.pack(fill='x')
        self.project_list.bind('<<ListboxSelect>>',self._select_project)
        ttk.Label(right,text='Proyecto editable. Los datos ausentes quedan como [COMPLETAR ...].').pack(anchor='w')
        self.project_editor=ScrolledText(right,wrap='word',height=18,font=('Segoe UI',11),undo=True);self.project_editor.pack(fill='both',expand=True)

    def _capture_project(self):
        if self.project_index is not None and self.project_index<len(self.projects):
            self.projects[self.project_index].text=self.project_editor.get('1.0','end-1c')

    def _select_project(self,event=None):
        self._capture_project()
        if self.project_list.curselection():
            self.project_index=self.project_list.curselection()[0]
            self.project_editor.delete('1.0','end');self.project_editor.insert('1.0',self.projects[self.project_index].text)

    def _prepare_words(self,then_generate=False):
        work=self._require_work()
        self._capture_project()
        edits={(p.court,p.rit,p.kind):(p.values,p.text) for p in self.projects if p.text!=p.original_text}
        selected=list(self.words.selection()) or list(self.words.get_children())
        if not selected:
            selections=automatic_project_selections(work,self.manual_word.get())
            if not selections:
                raise ValueError('No hay proyectos indicados. Si la planilla usa RES, solo se generan los marcados allí; para agregar otro caso, selecciónalo en Trabajo y usa Agregar desde Trabajo.')
        else:
            selections=[item.split('|') for item in selected]
        def done(result):
            self.projects,errors=result;self.project_index=None;self.project_list.delete(0,'end')
            self.project_editor.delete('1.0','end')
            self._prepared_selection=tuple(selected)
            for p in self.projects:
                previous=edits.get((p.court,p.rit,p.kind))
                if previous and previous[0]==p.values:p.text=previous[1]
            for p in self.projects:self.project_list.insert('end',p.rit+' · '+p.kind+' · '+str(len(p.record_ids))+' registros')
            if self.projects:self.project_list.selection_set(0);self._select_project()
            self.status.set(f'{len(self.projects)} proyectos agrupados; {len(errors)} matrices pendientes.')
            if errors:messagebox.showwarning('Matrices pendientes','\n'.join(errors))
            if then_generate and self.projects:self._generate_words()
        self._run('Agrupando proyectos por tribunal, RIT y tipo…',lambda:prepare_projects(work,selections,self.template_dir),done)

    def _generate_words(self):
        work=self._require_work()
        selected=tuple(self.words.selection() or self.words.get_children())
        if not self.projects or selected!=getattr(self,'_prepared_selection',None):self._prepare_words(then_generate=True);return
        self._capture_project()
        path=Path(work.output).parent/('Resoluciones_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.docx')
        projects=deepcopy(self.projects)
        def done(result):
            self.last_word=result;self._save_session();self.status.set('Word conjunto generado: '+result)
        self._run('Generando un Word con los proyectos…',lambda:generate_projects(work,projects,path),done)

    def _config_page(self):
        page=self.pages['Configuración'];nb=ttk.Notebook(page);nb.pack(fill='both',expand=True)
        params_scroll=ScrollPane(nb);nb.add(params_scroll,text='Reglas y umbrales');params=params_scroll.body
        self.param_vars={}
        for i,(key,number) in enumerate(self.cfg.data['umbrales'].items()):
            var=tk.StringVar(value=str(number));self.param_vars[key]=var
            ttk.Label(params,text=PARAMETER_LABELS[key]+' (días)').grid(row=i//2,column=(i%2)*2,sticky='w',padx=8,pady=4)
            ttk.Entry(params,textvariable=var,width=8).grid(row=i//2,column=(i%2)*2+1)
        ttk.Button(params,text='Guardar umbrales',command=lambda:self._guard(self._save_params)).grid(row=8,column=0,pady=12)
        self.disabled={}
        for i,key in enumerate(['COMUN.CURADOR','COMUN.OIDO','COMUN.PROX_AUDIENCIA','COMUN.PROXIMA_MAYORIA']):
            v=tk.BooleanVar(value=key not in self.cfg.data['desactivadas']);self.disabled[key]=v
            ttk.Checkbutton(params,text='Advertir '+key.split('.')[1].replace('_',' ').lower(),variable=v).grid(row=9+i,column=0,columnspan=4,sticky='w')
        texts=ttk.Frame(nb,padding=8);nb.add(texts,text='Observaciones')
        keys=[s+'.'+k for s,d in self.cfg.data['textos'].items() if not s.startswith('_') for k in d]
        self.text_key=tk.StringVar(value=keys[0]);box=ttk.Combobox(texts,textvariable=self.text_key,values=keys,state='readonly',width=55);box.pack(anchor='w');box.bind('<<ComboboxSelected>>',self._load_text)
        self.text_variable=tk.StringVar();self.text_variables=ttk.Combobox(texts,textvariable=self.text_variable,state='readonly',width=28);self.text_variables.pack(anchor='w',pady=3)
        ttk.Button(texts,text='Insertar variable en el texto',command=lambda:self.text_editor.insert('insert',self.text_variable.get())).pack(anchor='w')
        self.text_editor=ScrolledText(texts,wrap='word',undo=True,font=('Segoe UI',11));self.text_editor.pack(fill='both',expand=True,pady=6)
        ttk.Button(texts,text='Guardar texto · También se guarda al cambiar de regla',command=lambda:self._guard(self._save_text)).pack(anchor='w');self._load_text()
        mail=ttk.Frame(nb,padding=8);nb.add(mail,text='Plantillas correo')
        self.tpl_key=tk.StringVar(value='espera');box=NamedChoice(mail,keyvariable=self.tpl_key,names=lambda:{k:v['nombre'] for k,v in self.cfg.data['correos']['plantillas'].items()},state='readonly',width=35);box.grid(row=0,column=0);box.bind('<<ComboboxSelected>>',self._load_tpl)
        self.tpl_name=tk.StringVar();self.tpl_subject=tk.StringVar();self.tpl_req=tk.BooleanVar();self.tpl_modes=tk.BooleanVar()
        self._field(mail,'Nombre',self.tpl_name,1);self._field(mail,'Asunto',self.tpl_subject,2)
        self.tpl_body=ScrolledText(mail,wrap='word',height=7,undo=True,font=('Segoe UI',11));self.tpl_body.grid(row=3,column=0,columnspan=2,sticky='nsew');mail.rowconfigure(3,weight=1)
        ttk.Checkbutton(mail,text='Adjunto obligatorio',variable=self.tpl_req).grid(row=4,column=0)
        ttk.Checkbutton(mail,text='Usa modalidades',variable=self.tpl_modes).grid(row=4,column=1)
        ttk.Button(mail,text='Guardar plantilla',command=lambda:self._guard(self._save_tpl)).grid(row=5,column=0)
        self.tpl_variable=tk.StringVar(value='{TRIBUNAL}')
        variable_bar=ttk.Frame(mail);variable_bar.grid(row=6,column=0,columnspan=2,sticky='ew',pady=5)
        ttk.Combobox(variable_bar,textvariable=self.tpl_variable,values=['{'+v+'}' for v in sorted(VARIABLES)],state='readonly',width=24).pack(side='left')
        ttk.Button(variable_bar,text='Insertar en cuerpo',command=lambda:self.tpl_body.insert('insert',self.tpl_variable.get())).pack(side='left',padx=4)
        ttk.Label(mail,text='Los cambios se guardan también al cambiar de plantilla o cerrar.').grid(row=7,column=0,columnspan=2,sticky='w')
        self.tpl_box=box
        ttk.Button(mail,text='Nueva plantilla',command=lambda:self._guard(self._new_tpl)).grid(row=5,column=1,sticky='w');self._load_tpl()
        contacts=ttk.Frame(nb,padding=8);nb.add(contacts,text='Contactos y alias')
        self.contact_name=tk.StringVar();self.contact_mail=tk.StringVar();self.contact_alias=tk.StringVar()
        self._field(contacts,'Programa / tribunal',self.contact_name,0);self._field(contacts,'Correos (; separados)',self.contact_mail,1);self._field(contacts,'Alias opcional',self.contact_alias,2)
        ttk.Button(contacts,text='Guardar contacto',command=lambda:self._guard(self._save_contact)).grid(row=3,column=0)
        ttk.Button(contacts,text='Importar catastro Excel',command=lambda:self._guard(self._import_contacts)).grid(row=3,column=1,sticky='w')
        self.contact_list=tk.Listbox(contacts,exportselection=False);self.contact_list.grid(row=4,column=0,columnspan=2,sticky='nsew');contacts.rowconfigure(4,weight=1)
        self.contact_list.bind('<<ListboxSelect>>',self._select_contact)
        ttk.Button(contacts,text='Eliminar contacto seleccionado',command=lambda:self._guard(self._delete_contact)).grid(row=5,column=0)
        self._list_contacts()
        office=ttk.Frame(nb,padding=8);nb.add(office,text='Word y Outlook')
        self.account=tk.StringVar(value=self.cfg.data.get('cuenta_outlook',''));self.signature=tk.StringVar(value=self.cfg.data.get('firma',''));self.additional=tk.StringVar(value=self.cfg.data['correos'].get('cc_adicional',''))
        self._field(office,'Cuenta Outlook (vacío: predeterminada)',self.account,0);self._field(office,'Firma de texto adicional',self.signature,1);self._field(office,'CC adicional',self.additional,2)
        ttk.Label(office,text='Copia institucional siempre incluida: ucc_concepcion@pjud.cl').grid(row=3,column=0,columnspan=2,sticky='w',pady=10)
        ttk.Button(office,text='Guardar Outlook',command=lambda:self._guard(self._save_office)).grid(row=4,column=0)
        ttk.Button(office,text='Abrir plantillas Word',command=lambda:self._guard(lambda:self._open(self.template_dir))).grid(row=5,column=0,pady=12)
        self.word_court=tk.StringVar(value='LAJA');self.word_kind=tk.StringVar(value='PC_IE')
        matrix=ttk.Frame(office);matrix.grid(row=8,column=0,columnspan=2,sticky='w',pady=5)
        ttk.Combobox(matrix,textvariable=self.word_court,values=['LAJA','MULCHEN','TOME'],state='readonly',width=12).pack(side='left')
        ttk.Combobox(matrix,textvariable=self.word_kind,values=list(KINDS),state='readonly',width=12).pack(side='left',padx=4)
        ttk.Button(matrix,text='Editar matriz en Word',command=lambda:self._guard(lambda:self._open(self.template_dir/self.word_court.get()/(self.word_kind.get()+'.docx')))).pack(side='left')
        ttk.Button(matrix,text='Reemplazar matriz…',command=lambda:self._guard(self._import_word)).pack(side='left',padx=4)
        ttk.Button(office,text='Importar paquete de plantillas ZIP',command=lambda:self._guard(self._import_templates_zip)).grid(row=7,column=0,pady=8)
        ttk.Label(office,text='Carpetas LAJA, MULCHEN y TOME; tipos PC_IE.docx, PC_INFO.docx y NOMENCL.docx.',wraplength=640).grid(row=6,column=0,columnspan=2,sticky='w')

    def _save_params(self):
        from copy import deepcopy
        cfg=deepcopy(self.cfg.data)
        cfg['umbrales']={k:int(v.get()) for k,v in self.param_vars.items()}
        hidden=[key for key in cfg['desactivadas'] if key not in self.disabled]
        cfg['desactivadas']=hidden+[key for key,var in self.disabled.items() if not var.get()]
        self.cfg.save(cfg)
        self.status.set('Parámetros guardados. Se aplicarán al próximo análisis; el trabajo actual conserva su perfil.')

    def _save_before_switch(self, attribute, variable, save):
        previous=getattr(self,attribute,None)
        if previous and previous!=variable.get():
            try:save(notify=False)
            except ValueError as exc:
                variable.set(previous)
                messagebox.showerror('No se guardó el cambio',str(exc))
                return False
        return True

    def _load_text(self,event=None):
        if not self._save_before_switch('_editing_text_key',self.text_key,self._save_text):return
        self._editing_text_key=self.text_key.get()
        s,k=self._editing_text_key.split('.')
        text=self.cfg.data['textos'][s][k]['texto']
        self.text_editor.delete('1.0','end');self.text_editor.insert('1.0',text);self.text_editor.edit_reset()
        from string import Formatter
        fields=sorted({'{'+f+'}' for _,f,_,_ in Formatter().parse(text) if f})
        self.text_variables.configure(values=fields);self.text_variable.set(fields[0] if fields else '')

    def _save_text(self,notify=True):
        key=getattr(self,'_editing_text_key',None)
        if not key:return
        cfg=deepcopy(self.cfg.data);s,k=key.split('.')
        text=self.text_editor.get('1.0','end-1c')
        if text!=cfg['textos'][s][k]['texto']:
            cfg['textos'][s][k]['texto']=text;self.cfg.save(cfg)
        if notify:self.status.set('Texto guardado para próximos análisis; la revisión actual se conserva.')

    def _load_tpl(self,event=None):
        if not self._save_before_switch('_editing_tpl_key',self.tpl_key,self._save_tpl):return
        self._editing_tpl_key=self.tpl_key.get()
        tpl=self.cfg.data['correos']['plantillas'][self._editing_tpl_key]
        self.tpl_name.set(tpl['nombre']);self.tpl_subject.set(tpl['asunto'])
        self.tpl_body.delete('1.0','end');self.tpl_body.insert('1.0',tpl['cuerpo']);self.tpl_body.edit_reset()
        self.tpl_req.set(tpl['adjunto']=='obligatorio');self.tpl_modes.set(tpl.get('usa_modalidades',False))

    def _save_tpl(self,notify=True):
        key=getattr(self,'_editing_tpl_key',None)
        if not key:return
        cfg=deepcopy(self.cfg.data);tpl=cfg['correos']['plantillas'][key]
        tpl.update(nombre=self.tpl_name.get().strip(),asunto=self.tpl_subject.get(),cuerpo=self.tpl_body.get('1.0','end-1c'),adjunto='obligatorio' if self.tpl_req.get() else 'opcional',usa_modalidades=self.tpl_modes.get())
        if not tpl['nombre']:raise ValueError('La plantilla necesita un nombre.')
        if cfg!=self.cfg.data:self.cfg.save(cfg)
        keys=list(cfg['correos']['plantillas'])
        self.tpl_box.configure(values=keys);self.kind_box.configure(values=keys)
        if notify:self.status.set('Plantilla guardada; se aplica al preparar correos nuevos.')

    def _new_tpl(self):
        from copy import deepcopy
        from uuid import uuid4
        self._save_tpl(notify=False)
        name=simpledialog.askstring('Nueva plantilla','Nombre de la comunicación:')
        if not name:return
        cfg=deepcopy(self.cfg.data);key='particular_'+uuid4().hex[:6]
        cfg['correos']['plantillas'][key]={'nombre':name,'asunto':name+' — {TRIBUNAL}','cuerpo':'Buen día:\n\n\nAtentamente,','adjunto':'opcional','usa_modalidades':False}
        self.cfg.save(cfg);keys=list(cfg['correos']['plantillas']);self.tpl_box.configure(values=keys);self.kind_box.configure(values=keys);self.tpl_key.set(key);self._load_tpl()

    def _list_contacts(self):
        self.contact_list.delete(0,'end')
        for k in self.cfg.data['correos']['tribunales']:self.contact_list.insert('end','Tribunal: '+k)
        for k in sorted(self.cfg.data['contactos']):self.contact_list.insert('end',k)

    def _select_contact(self,event=None):
        if self.contact_list.curselection():
            k=self.contact_list.get(self.contact_list.curselection()[0]);self.contact_name.set(k);self.contact_alias.set('')
            self.contact_mail.set('; '.join(self.cfg.data['correos']['tribunales'][k.split(': ',1)[1]]['para']) if k.startswith('Tribunal: ') else self.cfg.data['contactos'][k])

    def _save_contact(self):
        from copy import deepcopy
        from .config import emails
        cfg=deepcopy(self.cfg.data);name=self.contact_name.get().strip();mail='; '.join(emails(self.contact_mail.get()))
        if not name:raise ValueError('Indica un nombre.')
        if name.startswith('Tribunal: '):cfg['correos']['tribunales'][name.split(': ',1)[1]]['para']=emails(mail)
        else:
            cfg['contactos'][name]=mail
            if self.contact_alias.get().strip():cfg['aliases'][self.contact_alias.get().strip()]=name
        self.cfg.save(cfg);self._list_contacts()

    def _delete_contact(self):
        from copy import deepcopy
        name=self.contact_name.get();cfg=deepcopy(self.cfg.data)
        if name.startswith('Tribunal: '):cfg['correos']['tribunales'][name.split(': ',1)[1]]['para']=[]
        else:
            cfg['contactos'].pop(name,None);cfg['aliases']={k:v for k,v in cfg['aliases'].items() if v!=name}
        self.cfg.save(cfg);self._list_contacts()

    def _import_contacts(self):
        path=filedialog.askopenfilename(filetypes=[('Excel','*.xlsx *.xls')])
        if not path:return
        from copy import deepcopy
        cfg=deepcopy(self.cfg.data);contacts,conflicts=import_contacts(cfg,path);cfg['contactos']=contacts;self.cfg.save(cfg);self._list_contacts()
        messagebox.showinfo('Catastro incorporado',f'{len(contacts)} contactos disponibles.'+('\nNo se sustituyeron coincidencias conflictivas:\n'+'\n'.join(conflicts) if conflicts else ''))

    def _save_office(self):
        from copy import deepcopy
        cfg=deepcopy(self.cfg.data);cfg['cuenta_outlook']=self.account.get().strip();cfg['firma']=self.signature.get();cfg['correos']['cc_adicional']=self.additional.get();self.cfg.save(cfg);self.status.set('Configuración de Outlook guardada.')

    def _import_templates_zip(self):
        from .template_package import import_templates
        path=filedialog.askopenfilename(filetypes=[('Paquete Word','*.zip')])
        if not path:return
        result=import_templates(path,self.template_dir)
        self.status.set(f"{len(result['imported'])} matrices importadas; {len(result['unmatched'])} archivos sin identificación automática.")
        if result['unmatched']:messagebox.showinfo('Asignación pendiente','Estos archivos deben incorporarse indicando tribunal y tipo:\n'+'\n'.join(result['unmatched']))

    def _import_word(self):
        court=self.word_court.get();kind=self.word_kind.get()
        if court not in ('LAJA','MULCHEN','TOME') or kind not in ('PC_IE','PC_INFO','NOMENCL'):return
        path=filedialog.askopenfilename(filetypes=[('Word','*.docx')])
        if not path:return
        from docx import Document
        Document(path)  # Verificar antes de reemplazar la matriz vigente.
        target=self.template_dir/court/(kind+'.docx');target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():shutil.copyfile(target,target.with_suffix('.bak.docx'))
        shutil.copyfile(path,target);self.status.set('Plantilla incorporada: '+str(target))

    def _sent_page(self):
        page=self.pages['Enviados'];top=ttk.Frame(page);top.pack(fill='x')
        self.start=tk.StringVar(value=date.today().replace(day=1).isoformat());self.end=tk.StringVar(value=date.today().isoformat());self.search=tk.StringVar();self.sent_court=tk.StringVar();self.sent_type=tk.StringVar()
        self._field(top,'Desde (AAAA-MM-DD)',self.start,0);self._field(top,'Hasta',self.end,1);self._field(top,'Tribunal / texto',self.sent_court,2);self._field(top,'Tipo / asunto',self.sent_type,3);self._field(top,'Buscar',self.search,4)
        ttk.Button(top,text='Consultar Outlook',command=lambda:self._guard(self._sent_query)).grid(row=5,column=0)
        ttk.Button(top,text='Filtrar resultado',command=self._filter_sent).grid(row=5,column=1,sticky='w')
        ttk.Button(top,text='Exportar Excel',command=lambda:self._guard(self._export_sent)).grid(row=5,column=1,sticky='e')
        self.sent=self._tree(page,('Fecha','Destinatario','Asunto'))

    def _sent_query(self):
        start=date.fromisoformat(self.start.get());end=date.fromisoformat(self.end.get());account=self.cfg.data.get('cuenta_outlook') or None
        def done(report):self.report=report;self._filter_sent()
        self._run('Consultando Enviados (solo lectura)…',lambda:count_sent_mail(start,end,account_key=account),done)

    def _filter_sent(self):
        if not self.report:return
        from nurus.rus.columns import normalize
        terms=[normalize(s.get()) for s in (self.sent_court,self.sent_type,self.search) if s.get().strip()]
        self.filtered=tuple(r for r in self.report.rows if all(t in normalize(r['Asunto']+' '+r['Destinatario']) for t in terms))
        self.sent.delete(*self.sent.get_children())
        for row in self.filtered:self.sent.insert('','end',values=(row['Fecha de envío'],row['Destinatario'],row['Asunto']))
        self.status.set(f'{len(self.filtered)} correos coinciden · {self.report.errors} errores de lectura · Consulta limitada: {"sí" if self.report.truncated else "no"}. Filtros por texto, no clasificación acreditada.')

    def _export_sent(self):
        if not self.report:raise ValueError('Primero consulta Enviados.')
        path=filedialog.asksaveasfilename(defaultextension='.xlsx',initialfile='Correos_enviados.xlsx')
        if path:export_sent_report(replace(self.report,rows=self.filtered),path);self.status.set('Reporte de Enviados exportado: '+path)

def main():
    """Compatibilidad: el módulo base nunca inicia una variante del producto."""
    from .app import main as personal_main
    personal_main()

if __name__=='__main__':main()
