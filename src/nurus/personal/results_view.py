"""Pendientes y entregas del trabajo actual."""
from . import ui
from .widgets import ScrollPane
from .current_tools import pending, deliver, export_diagnosis


def build(app):
    pane=ScrollPane(app.pages['Resultados']);pane.pack(fill='both',expand=True)
    app.results_scrollpane=pane;page=pane.body
    ui.Label(page,text='Trabajo actual · pendientes y entrega',font=('Segoe UI',19,'bold')).pack(anchor='w',pady=12)
    tasks=app._tree(page,('Tipo','Registro / producto','Tarea pendiente'))
    tasks.configure(height=12)
    def refresh():
        if app.work:app._capture_observation();app._capture_mail();app._capture_project()
        tasks.delete(*tasks.get_children())
        for task in pending(app.work,app.drafts,app.projects):tasks.insert('','end',values=task)
        app.status.set('Pendientes del trabajo actual actualizados.')
    ui.Button(page,text='Actualizar pendientes',command=lambda:app._guard(refresh)).pack(anchor='w',pady=6)
    ui.Button(page,text='ZIP de productos seleccionados',command=lambda:app._guard(lambda:deliver(app))).pack(anchor='w',pady=6)
    ui.Button(page,text='Exportar diagnóstico de instalación',command=lambda:app._guard(lambda:export_diagnosis(app))).pack(anchor='w',pady=6)
    from .download_link import resume
    app.results_download_button=ui.Button(page,text='Recuperar descarga interrumpida',command=lambda:app._guard(lambda:resume(app)))
    app.results_download_button.pack(anchor='w',pady=6)
    from .work_tools import show_deadlines
    ui.Button(page,text='Vencimientos de informe / egreso proyectado',command=lambda:app._guard(lambda:show_deadlines(app))).pack(anchor='w',pady=6)
    def open_pending(event=None):
        selected=tasks.selection()
        if not selected:return
        kind,identifier,_=tasks.item(selected[0],'values')
        if app.work and any(row.id==identifier for row in app.work.rows):
            app.work_search.set('');app.work_filter.set('Todos');app._apply_work_filter();app.records.selection_set(identifier);app._detail();app.tabs.select(app.pages['Trabajo'])
        elif kind=='Word':
            index=next((i for i,p in enumerate(app.projects) if p.rit==identifier),None)
            if index is not None:app.project_list.selection_set(index);app._select_project();app.tabs.select(app.pages['Resoluciones'])
        else:
            index=next((i for i,d in enumerate(app.drafts) if d.subject==identifier),None)
            if index is not None:app.mail_list.selection_set(index);app._select_mail();app.tabs.select(app.pages['Correos'])
    tasks.bind('<Double-1>',open_pending)
    app.refresh_pending=refresh
