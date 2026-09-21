"""Interfaz CSMP personal.

Único flujo operativo del producto; app_base contiene sus controles compartidos.
"""
from copy import deepcopy
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from .app_base import App as _BaseApp
from .widgets import ScrollPane, NamedChoice
from .mail_controls import alcance_modalidades, selected_court_record_ids
from .modalities import MODALITIES
from .outputs import prepare_drafts, prepare_required_drafts, create_drafts, value
from .resolutions import automatic_project_selections, reviewed_resolution_ids, unique_case_selections
from .statistics import summarize
from .work import Work
from nurus.rus.columns import normalize


class App(_BaseApp):
    def __init__(self,configuration=None):
        super().__init__(configuration=configuration)
        width=min(1180,self.winfo_screenwidth()-60)
        height=min(820,self.winfo_screenheight()-110)
        self.geometry(f'{width}x{height}')
        self.minsize(min(940,width),min(580,height))

    def _mail_page(self):
        page=self.pages['Correos']
        outer=ttk.Panedwindow(page,orient='horizontal');outer.pack(fill='both',expand=True)
        controls=ScrollPane(outer);left=controls.body;right=ttk.Frame(outer)
        self.mail_controls=controls
        outer.add(controls,weight=1);outer.add(right,weight=5)

        mail_cfg=self.cfg.data['correos']
        self.mail_kind=tk.StringVar(value='programa_espera' if 'programa_espera' in mail_cfg['plantillas'] else next(iter(mail_cfg['plantillas'])))
        self.period=tk.StringVar(value=mail_cfg.get('periodo_default') or date.today().strftime('%m/%Y'))

        f_kind=ttk.LabelFrame(left,text='1. Tipo de correo',padding=8);f_kind.pack(fill='x',pady=(0,7))
        self.kind_box=NamedChoice(f_kind,keyvariable=self.mail_kind,names=lambda:{k:v['nombre'] for k,v in self.cfg.data['correos']['plantillas'].items()},state='readonly',width=27)
        self.kind_box.pack(fill='x');self.kind_box.bind('<<ComboboxSelected>>',self._mail_kind_changed)
        self.mail_note=tk.StringVar();ttk.Label(f_kind,textvariable=self.mail_note,wraplength=285).pack(anchor='w',pady=(5,0))

        f_court=ttk.LabelFrame(left,text='2. Tribunal(es)',padding=8);f_court.pack(fill='x',pady=(0,7))
        self.mail_court_keys=list(mail_cfg['tribunales'])
        self.mail_courts=tk.Listbox(f_court,selectmode='extended',exportselection=False,height=max(3,min(6,len(self.mail_court_keys))),font=('Segoe UI',9))
        self.mail_courts.pack(fill='x')
        for key in self.mail_court_keys:self.mail_courts.insert('end',mail_cfg['tribunales'][key].get('nombre',key))
        if self.mail_court_keys:self.mail_courts.selection_set(0,'end')
        court_buttons=ttk.Frame(f_court);court_buttons.pack(fill='x',pady=(5,0))
        ttk.Button(court_buttons,text='Todos',command=self._select_all_mail_courts).pack(side='left',fill='x',expand=True,padx=(0,2))
        ttk.Button(court_buttons,text='Ninguno',command=self._select_no_mail_courts).pack(side='left',fill='x',expand=True,padx=(2,0))

        f_modes=ttk.LabelFrame(left,text='3. Modalidad(es) revisada(s)',padding=8);f_modes.pack(fill='x',pady=(0,7))
        defaults=set(mail_cfg.get('modalidades_default') or MODALITIES.values())
        self.modality_vars={}
        for key,label in MODALITIES.items():
            var=tk.BooleanVar(value=label in defaults);self.modality_vars[key]=var
            short={'RES':'Residencial','AMB':'Ambulatorio','FAE':'Familia de acogida (FAE / FAS)','DCE':'Diagnóstico clínico (DCE)'}[key]
            ttk.Checkbutton(f_modes,text=short,variable=var,command=self._mail_modality_changed).pack(anchor='w',pady=1)
        mode_buttons=ttk.Frame(f_modes);mode_buttons.pack(fill='x',pady=(5,0))
        ttk.Button(mode_buttons,text='Todas',command=self._select_all_mail_modalities).pack(side='left',fill='x',expand=True,padx=(0,2))
        ttk.Button(mode_buttons,text='Ninguna',command=self._select_no_mail_modalities).pack(side='left',fill='x',expand=True,padx=(2,0))
        self.mail_scope=tk.StringVar();ttk.Label(f_modes,textvariable=self.mail_scope,wraplength=285).pack(anchor='w',pady=(5,0))

        f_period=ttk.LabelFrame(left,text='4. Período',padding=8);f_period.pack(fill='x',pady=(0,7))
        ttk.Entry(f_period,textvariable=self.period).pack(fill='x')

        self.manual_mail=tk.BooleanVar()
        ttk.Checkbutton(left,text='Usar solo la selección de Trabajo\n(aplica al tipo seleccionado)',variable=self.manual_mail).pack(anchor='w',pady=(0,7))
        ttk.Button(left,text='Preparar tipo seleccionado',command=lambda:self._guard(self._prepare_mail)).pack(fill='x',pady=2)
        ttk.Button(left,text='Preparar TODOS los correos necesarios',command=lambda:self._guard(self._prepare_all_mail)).pack(fill='x',pady=2)
        ttk.Button(left,text='Cargar planilla modificada / externa',command=lambda:self._guard(self._external)).pack(fill='x',pady=(8,2))

        prepared=ttk.LabelFrame(right,text='Borradores preparados',padding=8);prepared.pack(fill='x',pady=(0,7))
        self.mail_list=tk.Listbox(prepared,exportselection=False,height=5,font=('Segoe UI',9));self.mail_list.pack(fill='x')
        self.mail_list.bind('<<ListboxSelect>>',self._select_mail)

        compose=ttk.LabelFrame(right,text='5. Correo editable antes de guardar en Outlook',padding=8);compose.pack(fill='both',expand=True)
        compose.columnconfigure(1,weight=1);compose.rowconfigure(3,weight=1)
        self.to=tk.StringVar();self.cc=tk.StringVar();self.subject=tk.StringVar();self.attach=tk.StringVar()
        ttk.Label(compose,text='Para:').grid(row=0,column=0,sticky='w',pady=3)
        ttk.Entry(compose,textvariable=self.to).grid(row=0,column=1,sticky='ew',padx=(7,0),pady=3)
        ttk.Label(compose,text='CC:').grid(row=1,column=0,sticky='w',pady=3)
        ttk.Entry(compose,textvariable=self.cc).grid(row=1,column=1,sticky='ew',padx=(7,0),pady=3)
        ttk.Label(compose,text='Asunto:').grid(row=2,column=0,sticky='w',pady=3)
        ttk.Entry(compose,textvariable=self.subject).grid(row=2,column=1,sticky='ew',padx=(7,0),pady=3)
        ttk.Label(compose,text='Cuerpo:').grid(row=3,column=0,sticky='nw',pady=3)
        self.body=ScrolledText(compose,height=14,wrap='word',font=('Segoe UI',10),undo=True);self.body.grid(row=3,column=1,sticky='nsew',padx=(7,0),pady=3)
        ttk.Label(compose,text='Adjuntos:').grid(row=4,column=0,sticky='w',pady=3)
        ttk.Entry(compose,textvariable=self.attach).grid(row=4,column=1,sticky='ew',padx=(7,0),pady=3)

        attach_actions=ttk.Frame(compose);attach_actions.grid(row=5,column=1,sticky='ew',pady=(4,2))
        ttk.Button(attach_actions,text='Agregar a este…',command=self._attachment).pack(side='left')
        ttk.Button(attach_actions,text='Agregar a TODOS…',command=lambda:self._guard(self._attachment_all)).pack(side='left',padx=4)
        ttk.Button(attach_actions,text='Quitar de este',command=self._clear_current_attachments).pack(side='left')

        actions=ttk.Frame(compose);actions.grid(row=6,column=0,columnspan=2,sticky='ew',pady=(8,0))
        ttk.Button(actions,text='Vista previa',command=lambda:self._guard(self._preview_mail)).pack(anchor='w',pady=(0,4))
        save_actions=ttk.Frame(actions);save_actions.pack(fill='x')
        ttk.Button(save_actions,text='Guardar este borrador',command=lambda:self._guard(self._send_draft)).pack(side='right',padx=(4,0))
        self.save_all_button=ttk.Button(save_actions,text='Guardar TODOS los borradores',command=lambda:self._guard(self._send_all))
        self.save_all_button.pack(side='left')

        self._mail_kind_changed();self._mail_modality_changed()

    def _selected_mail_courts(self):
        return [self.mail_court_keys[i] for i in self.mail_courts.curselection() if i<len(self.mail_court_keys)]

    def _select_all_mail_courts(self):
        if self.mail_courts.size():self.mail_courts.selection_set(0,'end')

    def _select_no_mail_courts(self):
        self.mail_courts.selection_clear(0,'end')

    def _selected_mail_modalities(self):
        return [key for key,var in self.modality_vars.items() if var.get()]

    def _select_all_mail_modalities(self):
        for var in self.modality_vars.values():var.set(True)
        self._mail_modality_changed()

    def _select_no_mail_modalities(self):
        for var in self.modality_vars.values():var.set(False)
        self._mail_modality_changed()

    def _mail_modality_changed(self):
        keys=self._selected_mail_modalities() if hasattr(self,'modality_vars') else []
        phrase=alcance_modalidades(keys)
        self.mail_scope.set('Redacción automática: '+phrase+'.' if phrase else 'Sin modalidades seleccionadas.')

    def _mail_kind_changed(self,event=None):
        kind=self.mail_kind.get();tpl=self.cfg.data['correos']['plantillas'].get(kind,{})
        note=tpl.get('nota','')
        requirement='Adjunto: '+tpl.get('adjunto','opcional')+'.'
        mode_note=' Usa modalidades.' if tpl.get('usa_modalidades') else ' No exige modalidades.'
        self.mail_note.set((note+' '+requirement+mode_note).strip())
        self._mail_modality_changed()

    def _mail_selected_ids(self,work,manual=False):
        courts=self._selected_mail_courts()
        if not courts:raise ValueError('Selecciona al menos un tribunal.')
        ids=selected_court_record_ids(work,courts)
        if manual:
            chosen=set(self.records.selection())
            if not chosen:raise ValueError('Selecciona los registros de esta gestión en la pestaña Trabajo.')
            ids=[rid for rid in ids if rid in chosen]
        if not ids:raise ValueError('No hay registros del trabajo que coincidan con los tribunales seleccionados.')
        return ids

    def _sync_mail_config(self,work):
        for key in ('correos','contactos','aliases','cuenta_outlook','firma'):
            work.config[key]=deepcopy(self.cfg.data[key])

    def _display_prepared_drafts(self,drafts,message):
        self.drafts=drafts;self.mail_list.delete(0,'end');self.draft_index=None
        for draft in drafts:self.mail_list.insert('end',draft.subject)
        if drafts:self.mail_list.selection_set(0);self._select_mail()
        else:self._clear_mail_editor()
        self.status.set(message.format(count=len(drafts)))

    def _prepare_mail(self):
        work=self._require_work();self._sync_mail_config(work)
        kind=self.mail_kind.get();tpl=work.config['correos']['plantillas'][kind]
        keys=self._selected_mail_modalities()
        if tpl.get('usa_modalidades') and not keys:raise ValueError('Selecciona al menos una modalidad para este tipo de correo.')
        phrase=alcance_modalidades(keys) if tpl.get('usa_modalidades') else ''
        manual=self.manual_mail.get();selected=self._mail_selected_ids(work,manual=manual)
        modality_keys=keys if tpl.get('usa_modalidades') else None
        period=self.period.get()
        def done(drafts):self._display_prepared_drafts(drafts,'{count} borradores preparados para revisión; todavía no se guardaron en Outlook.')
        self._run('Preparando textos y adjuntos…',lambda:prepare_drafts(work,kind,modalities=phrase,period=period,selected=selected,manual_selection=manual,modality_keys=modality_keys),done)

    def _prepare_all_mail(self):
        work=self._require_work();self._sync_mail_config(work)
        keys=self._selected_mail_modalities()
        if not keys:raise ValueError('Selecciona al menos una modalidad para preparar el conjunto de correos del trabajo.')
        phrase=alcance_modalidades(keys);selected=self._mail_selected_ids(work,manual=False);period=self.period.get()
        def done(drafts):self._display_prepared_drafts(drafts,'{count} correos necesarios preparados: informativo general y gestiones específicas detectadas. Todavía no se guardaron en Outlook.')
        self._run('Preparando todos los correos necesarios del trabajo…',lambda:prepare_required_drafts(work,modalities=phrase,period=period,selected=selected,modality_keys=keys),done)

    def _send_all(self):
        work=self._require_work();self._capture_mail()
        if self.drafts:
            drafts=[replace(draft) for draft in self.drafts]
            def done(result):
                self._save_session()
                self.status.set(f"{result['created']} borradores guardados; {result['skipped']} ya procesados; {len(result['errors'])} incidencias.")
                if result['errors']:messagebox.showwarning('Lote guardado con incidencias','\n'.join(result['errors']))
            self._run('Guardando el lote de borradores en Outlook…',lambda:create_drafts(work,drafts),done)
            return
        self._sync_mail_config(work)
        keys=self._selected_mail_modalities()
        if not keys:raise ValueError('Selecciona al menos una modalidad.')
        selected=self._mail_selected_ids(work,manual=False)
        period=self.period.get();phrase=alcance_modalidades(keys)
        def action():
            drafts=prepare_required_drafts(work,modalities=phrase,period=period,selected=selected,modality_keys=keys)
            return drafts,create_drafts(work,[replace(draft) for draft in drafts])
        def done(payload):
            drafts,result=payload
            self._display_prepared_drafts(drafts,'{count} borradores preparados y procesados para Outlook.')
            self._save_session()
            self.status.set(f"{result['created']} borradores guardados; {result['skipped']} ya existentes; {len(result['errors'])} incidencias.")
            if result['errors']:messagebox.showwarning('Lote guardado con incidencias','\n'.join(result['errors']))
        self._run('Preparando y guardando todos los borradores en Outlook…',action,done)

    def _attachment_all(self):
        self._capture_mail()
        if not self.drafts:raise ValueError('Primero prepara los borradores.')
        paths=filedialog.askopenfilenames(title='Seleccionar adjuntos para todos los borradores')
        if not paths:return
        for draft in self.drafts:
            for path in paths:
                if path not in draft.attachments:draft.attachments.append(path)
        if self.draft_index is not None:self.attach.set('\n'.join(self.drafts[self.draft_index].attachments))
        self.status.set(f'{len(paths)} adjunto(s) incorporado(s) a {len(self.drafts)} borradores.')

    def _clear_current_attachments(self):
        self.attach.set('');self._capture_mail()

    def _preview_mail(self):
        self._capture_mail()
        if self.draft_index is None:raise ValueError('Primero prepara y selecciona un borrador.')
        draft=self.drafts[self.draft_index]
        win=tk.Toplevel(self);win.title('Vista previa del borrador');win.geometry('820x640');win.transient(self)
        text=ScrolledText(win,wrap='word',font=('Segoe UI',10),padx=12,pady=12);text.pack(fill='both',expand=True)
        text.insert('end','PARA: '+draft.to+'\nCC: '+draft.cc+'\nASUNTO: '+draft.subject+'\n\n'+draft.body)
        if draft.attachments:text.insert('end','\n\nADJUNTOS:\n'+'\n'.join('- '+Path(path).name for path in draft.attachments))
        text.configure(state='disabled')

    def _process(self):
        if self.busy:raise ValueError('Hay una operación en curso.')
        path=self.file.get();mode=self.mode.get();sheet=self.sheet.get() or None
        if not Path(path).is_file():raise ValueError('Selecciona un archivo Excel existente.')
        cfg=self.cfg.data
        def done(work):
            self.work=work;self._clear_drafts();self.observation_id=None;self._show_work();self._export_current()
        self._run('Analizando '+mode+'…',lambda:Work(cfg).analyze(path,mode,sheet=sheet),done)

    def _export_current(self):
        self._capture_observation()
        if not self.work:raise ValueError('Primero analiza el archivo.')
        folder=Path(self.folder.get());folder.mkdir(parents=True,exist_ok=True)
        path=folder/(Path(self.work.path).stem+' - revisable '+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+Path(self.work.path).suffix)
        work=self.work
        def done(result):
            self._show_work(reset_projects=False);self._save_session();self.status.set('Excel generado: '+result+' · Disponible en Correos y Resoluciones.')
        self._run('Exportando copia preservada con Excel…',lambda:work.export(path),done)

    def _show_work(self,reset_projects=True):
        if not self.work:return
        self.mode.set(self.work.mode);self.file.set(self.work.path);self.observation_id=None
        self.observation_editor.delete('1.0','end')
        self.records.delete(*self.records.get_children())
        if reset_projects:self.words.delete(*self.words.get_children())
        reviewed_res=reviewed_resolution_ids(self.work)
        fallback_kind=self.manual_word.get() if hasattr(self,'manual_word') else 'PC_IE'
        selections=unique_case_selections(self.work,automatic_project_selections(self.work,fallback_kind))
        by_id={row.id:row for row in self.work.rows}
        for row in self.work.rows:
            state='Excluido' if row.excluded else 'Revisar aviso' if row.warnings else 'Propuesta'
            self.records.insert('','end',iid=row.id,values=(state,value(self.work,row,'rit'),value(self.work,row,'tribunal'),value(self.work,row,'programa'),row.review.get('OBSERVACION',row.observation)),tags=('excluded' if row.excluded else 'warning' if row.warnings else '',))
        for rid,kind in selections if reset_projects else []:
            row=by_id[rid]
            source='Indicado/revisado en archivo (RES)' if reviewed_res is not None else 'Sugerencia automática revisable'
            self.words.insert('','end',iid=rid+'|'+kind,values=(value(self.work,row,'rit'),value(self.work,row,'tribunal'),kind,source))
        n=len(self.work.rows);exc=sum(r.excluded for r in self.work.rows);obs=sum(bool(r.observation) for r in self.work.rows)
        self.summary.set(f'{n} registros · {obs} propuestas · {exc} excluidos · {len(self.words.get_children())} proyectos posibles')
        totals=summarize(self.work)
        if totals['constancias']:self.summary.set(self.summary.get()+f" · {totals['constancias']} constancias con fecha · {totals['con_carga']} con carga")
        self.detail.set('\n'.join(dict.fromkeys(self.work.warnings)))

    @staticmethod
    def _visible_project_key(values):
        return normalize(values[1]),normalize(values[0]),str(values[2]).strip().upper()

    def _existing_project_iid(self,key,exclude=None):
        for iid in self.words.get_children():
            if iid==exclude:continue
            values=self.words.item(iid,'values')
            if len(values)>=3 and self._visible_project_key(values)==key:return iid
        return None

    def _assign_word_type(self):
        selected=list(self.words.selection())
        if not selected:raise ValueError('Selecciona una o más filas concretas de Resoluciones antes de cambiar su tipo.')
        kind=self.manual_word.get();new=[]
        for iid in selected:
            rid=iid.split('|')[0];values=list(self.words.item(iid,'values'));values[2]=kind
            key=self._visible_project_key(values)
            existing=self._existing_project_iid(key,exclude=iid)
            self.words.delete(iid)
            if existing:
                target=existing
            else:
                target=rid+'|'+kind
                if not self.words.exists(target):self.words.insert('','end',iid=target,values=values)
            new.append(target)
        self.words.selection_set(tuple(dict.fromkeys(new)))
        self._clear_projects()
        self.status.set(f'Tipo {kind} aplicado solo a {len(selected)} selección(es).')

    def _add_words(self):
        work=self._require_work();kind=self.manual_word.get();selected=list(self.records.selection())
        if not selected:raise ValueError('Selecciona en Trabajo los registros que quieres agregar manualmente como proyecto.')
        self._clear_projects()
        for rid in selected:
            row=next(r for r in work.rows if r.id==rid)
            if row.excluded:continue
            values=(value(work,row,'rit'),value(work,row,'tribunal'),kind,'Agregado manualmente')
            key=self._visible_project_key(values)
            if self._existing_project_iid(key):continue
            iid=rid+'|'+kind
            if not self.words.exists(iid):self.words.insert('','end',iid=iid,values=values)


def main():
    App().mainloop()


if __name__=='__main__':main()
