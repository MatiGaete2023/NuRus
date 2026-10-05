"""Ficha local de firmas; la revisión se atribuye solo al ingreso elegido."""
from tkinter import messagebox
import customtkinter as ctk
from . import ui
from .rus_activity import mark_reviewed


def show(app):
    if app.busy:raise ValueError('Hay una operación en curso.')
    app._capture_observation();work=app.work;selected=app.records.selection()
    if work is None:raise ValueError('Analiza el libro antes de revisar sus firmas.')
    if len(selected)!=1:raise ValueError('Selecciona un ingreso para revisar sus firmas.')
    rid=selected[0];entry=work.signed_activity.get(rid)
    if not entry:raise ValueError('Este trabajo no tiene fuentes de firmas. Utiliza Descargar y analizar.')
    win=ctk.CTkToplevel(app);win.title('Resoluciones firmadas · ingreso seleccionado');win.geometry('880x580');win.transient(app)
    ui.Label(win,text=entry['valores']['DETALLE'],wraplength=800).pack(fill='x',padx=12,pady=10)
    tree=app._tree(win,('Firma','Hora','Trámite','Estado'))
    for index,signature in enumerate(entry['firmas']):
        reviewed=signature['huella'] in work.activity_reviewed.get(rid,{})
        tree.insert('','end',iid=str(index),values=(signature['firma'],signature['hora'],signature['tramite'],'Revisada' if reviewed else 'Por revisar'))
    def record():
        chosen=tree.selection()
        if len(chosen)!=1:return
        signature=entry['firmas'][int(chosen[0])];mark_reviewed(work,rid,signature['huella'])
        values=list(tree.item(chosen[0],'values'));values[-1]='Revisada';tree.item(chosen[0],values=values)
        app._save_session();app._show_work(reset_projects=False)
        app.status.set('Firma revisada para este ingreso. Exporta la copia actual para actualizar sus alertas.')
    ui.Button(win,text='Marcar revisada para este ingreso',command=lambda:app._guard(record)).pack(pady=12)
    return win
