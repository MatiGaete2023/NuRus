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
            if kind=='firmas':return export_activity(works,path,a,b)
            return export_management(works,path,a,b)
        app._run('Generando informe…',action,lambda p:app.status.set('Informe creado: '+p))
    ui.Button(page,text='Informe de firmas y revisiones',width=280,command=lambda:app._guard(lambda:generate('firmas'))).pack(anchor='w',pady=8)
    ui.Button(page,text='Informe de gestión del período',width=280,command=lambda:app._guard(lambda:generate('gestion'))).pack(anchor='w',pady=8)
    def recover_download():
        from .download_link import resume
        resume(app)
    app.results_download_button=ui.Button(page,text='Recuperar descarga',width=280,
                                         command=lambda:app._guard(recover_download))
    app.results_download_button.pack(anchor='w',pady=8)
    from .bitacoras import earliest
    diary_start=tk.StringVar(value=earliest(date.today()).isoformat())
    diary_end=tk.StringVar(value=date.today().isoformat())
    def import_diary():
        from .bitacora_har import import_har, export_har_audit
        from .bitacoras import validate_period
        chosen=filedialog.askopenfilenames(title='Capturas HAR de bitácoras RUS',filetypes=[('Captura de red','*.har')])
        if not chosen:return
        a,b=date.fromisoformat(diary_start.get()),date.fromisoformat(diary_end.get())
        validate_period(a,b)
        destination=filedialog.asksaveasfilename(defaultextension='.xlsx',initialfile='Bitacoras_RUS.xlsx')
        if not destination:return
        app._run('Leyendo los textos completos de las bitácoras…',
                 lambda:export_har_audit(import_har(chosen),destination,a,b),
                 lambda path:app.status.set('Bitácoras de la captura exportadas: '+path))
    ui.Label(page,text='Bitácoras RUS · lectura por lotes',font=('Segoe UI',16,'bold')).pack(anchor='w',pady=(16,4))
    ui.Label(page,text='Exporta los textos completos, respuestas, reiteraciones y CC. El análisis abarca hasta '
             'cuatro meses; Copia íntegra conserva toda la tabla capturada. Puedes consultar RUS con el descargador '
             'para Ambulatorio, FAE, Residencia y DCE, o importar capturas locales.',
             wraplength=770,text_color=ui.MUTED).pack(fill='x',pady=4)
    diary_bar=ui.Frame(page);diary_bar.pack(fill='x',pady=6)
    for title,var in [('Desde · año-mes-día',diary_start),('Hasta · año-mes-día',diary_end)]:
        ui.Label(diary_bar,text=title).pack(side='left',padx=5)
        ui.Entry(diary_bar,textvariable=var,width=14).pack(side='left',padx=5)
    app.results_bitacora_button=ui.Button(page,text='Importar bitácoras HAR y crear Excel',width=280,
                                         command=lambda:app._guard(import_diary))
    app.results_bitacora_button.pack(anchor='w',pady=8)
    def live_diary():
        from .bitacora_link import start
        start(app,date.fromisoformat(diary_start.get()),date.fromisoformat(diary_end.get()))
    app.results_bitacora_live_button=ui.Button(page,text='Consultar bitácoras en RUS',width=280,
        command=lambda:app._guard(live_diary))
    app.results_bitacora_live_button.pack(anchor='w',pady=8)
    def recover_diary():
        from .bitacora_link import recover
        recover(app)
    ui.Button(page,text='Recuperar Excel de bitácoras',width=280,
        command=lambda:app._guard(recover_diary)).pack(anchor='w',pady=8)
    def open_diary_lot():
        from .bitacora_lote import export_lote
        source=filedialog.askopenfilename(title='Lote del descargador: bitacoras.json',filetypes=[('Control de bitácoras','bitacoras.json')])
        if not source:return
        destination=filedialog.asksaveasfilename(defaultextension='.xlsx',initialfile='Bitacoras_RUS.xlsx')
        if not destination:return
        a,b=date.fromisoformat(diary_start.get()),date.fromisoformat(diary_end.get())
        app._run('Exportando el lote de bitácoras…',lambda:export_lote(source,destination,a,b),
            lambda p:app.status.set('Excel de bitácoras creado: '+str(p)))
    ui.Button(page,text='Abrir lote de bitácoras y crear Excel',width=280,
        command=lambda:app._guard(open_diary_lot)).pack(anchor='w',pady=8)
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
        source=work.path
        path=filedialog.asksaveasfilename(defaultextension=Path(source).suffix,
                                         initialfile=Path(source).stem+'_registro'+Path(source).suffix)
        if not path:return
        from .registration_excel import receipts_for_source
        def show_receipts(choices):
            import customtkinter as ctk
            window=ctk.CTkToplevel(app);window.title('Elegir recibos para devolver a Excel')
            window.geometry('1120x680');window.minsize(900,560);window.transient(app);window.grab_set()
            body=ui.Frame(window);body.pack(fill='both',expand=True,padx=14,pady=14)
            ui.Label(body,text='Selecciona las operaciones comprobadas que corresponden a este Excel.',
                     font=('Segoe UI',16,'bold')).pack(anchor='w',pady=(0,4))
            ui.Label(body,text='Solo aparecen recibos del mismo archivo de origen (SHA-256), con el mismo ingreso y texto. '
                     'Puedes elegir varias filas; las identidades repetidas producen un conflicto y no se crea la copia.',
                     wraplength=1040,text_color=ui.MUTED).pack(anchor='w',pady=(0,8))
            columns=('operacion','fecha','estado','tribunal','rit','ingreso','tipo','cc','excel')
            tree=ui.Treeview(body,columns=columns,show='headings',selectmode='extended',height=9)
            titles={'operacion':'Operación','fecha':'Fecha RUS','estado':'Estado','tribunal':'Tribunal',
                    'rit':'RIT','ingreso':'Ingreso','tipo':'Tipo','cc':'CC RUS','excel':'Fecha / CC actual'}
            widths={'operacion':118,'fecha':130,'estado':135,'tribunal':180,'rit':125,
                    'ingreso':100,'tipo':135,'cc':75,'excel':145}
            for column in columns:
                tree.heading(column,text=titles[column]);tree.column(column,width=widths[column],stretch=column in ('tribunal','tipo'))
            y=ui.Scrollbar(body,orient='vertical',command=tree.yview)
            x=ui.Scrollbar(body,orient='horizontal',command=tree.xview)
            tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
            tree.pack(side='top',fill='both',expand=True);y.place(in_=tree,relx=1.0,rely=0,relheight=1.0,anchor='ne')
            x.pack(fill='x')
            for choice in choices:
                registered=choice['registered_at'].replace('T',' ')
                values=(choice['operation_id'],registered,choice['state'],choice['tribunal'],choice['rit'],
                        choice['ingreso_id'],choice['type'],choice['cc'],
                        f"{choice['excel_date'] or '—'} / {choice['excel_cc'] if choice['excel_cc'] not in (None,'') else '—'}")
                tree.insert('', 'end', iid=choice['operation_id'], values=values)
            ui.Label(body,text='Texto exacto del recibo seleccionado',text_color=ui.MUTED).pack(anchor='w',pady=(8,2))
            preview=ui.Textbox(body,height=5,wrap='word');preview.pack(fill='x',pady=(0,8));preview.configure(state='disabled')
            def update_preview(_event=None):
                selected=tree.selection();value=''
                if selected:
                    item=next((item for item in choices if item['operation_id']==selected[0]),None)
                    if item:value=item['text']
                preview.configure(state='normal');preview.delete('1.0','end');preview.insert('1.0',value);preview.configure(state='disabled')
            tree.bind('<<TreeviewSelect>>',update_preview)
            buttons=ui.Frame(body);buttons.pack(fill='x')
            state=ui.Label(buttons,text=(f'{len(choices)} recibo(s) coinciden con el libro.' if choices else
                'No hay recibos comprobados para este archivo e ingreso.'),text_color=ui.MUTED)
            state.pack(side='left',padx=(0,8))
            def reconcile_selected():
                selected=tree.selection()
                if not selected:
                    state.configure(text='Selecciona al menos un recibo.',text_color='#f0b35a');return
                window.grab_release();window.destroy()
                from .registration_excel import reconcile_excel
                app._run('Devolviendo recibos seleccionados a una copia…',
                         lambda:reconcile_excel(store,source,path,mode=work.mode,sheet=work.sheet,
                                                operation_ids=list(selected)),
                         lambda p:app.status.set('Copia creada con los recibos seleccionados: '+p))
            ui.Button(buttons,text='Cancelar',command=window.destroy).pack(side='right',padx=5)
            ui.Button(buttons,text='Crear copia con selección',command=reconcile_selected,
                      state='normal' if choices else 'disabled').pack(side='right',padx=5)
        app._run('Buscando recibos comprobados para este Excel…',
                 lambda:receipts_for_source(store,source,mode=work.mode,sheet=work.sheet),show_receipts)
    ui.Label(page,text='Recibos de registro: estas opciones no envían observaciones a RUS.',
             text_color=ui.MUTED).pack(anchor='w',pady=(16,4))
    ui.Button(page,text='Informe de operaciones de registro',width=280,
              command=lambda:app._guard(export_operations)).pack(anchor='w',pady=5)
    app.results_return_button=ui.Button(page,text='Recuperar devolución de fechas a Excel',width=280,
                                       command=lambda:app._guard(return_dates))
    app.results_return_button.pack(anchor='w',pady=5)
