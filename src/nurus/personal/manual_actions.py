"""Acciones de interfaz sobre productos libres y listas revisadas."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tkinter import messagebox

from .outputs import create_draft
from .manual_products import logical_mail_key,empty_table,table_snapshot


class ManualActions:
    def _save_session(self):
        if not self.busy and hasattr(self,'manual_store'):
            self._capture_mail();self.manual_store.save()
        super()._save_session()

    def _autosave(self):
        if not self.busy:
            try:self._save_session()
            except (ValueError,OSError) as exc:self.status.set('No se pudo guardar la recuperación: '+str(exc))
        self.after(15000,self._autosave)

    def _clear_drafts(self):
        super()._clear_drafts()
        if hasattr(self,'manual_store'):self._display_prepared_drafts([], '{count} correos manuales disponibles.')

    def _new_manual_mail(self):
        self._capture_mail()
        draft=self.manual_store.new_mail()
        source=[d for d in getattr(self,'_draft_scope_source',[]) if not d.options.get('manual')]
        self._display_prepared_drafts(source,'{count} borradores disponibles.')
        self.draft_index=None;self.mail_list.selection_set(self.drafts.index(draft));self._select_mail()
        self.mail_tabs.select(self.mail_compose_tab)
        self.status.set('Correo manual creado. Completa Para, asunto y texto; puedes añadir una nómina o archivos.')

    def _delete_mail(self):
        self._capture_mail()
        if self.draft_index is None:raise ValueError('Selecciona el correo que quieres eliminar de la lista.')
        draft=self.drafts[self.draft_index]
        if draft.options.get('manual'):
            self.manual_store.drafts=[d for d in self.manual_store.drafts if d is not draft and d.key!=draft.key]
            self.manual_store.save()
        else:
            key=logical_mail_key(draft)
            omitted=list(getattr(self.work,'dismissed_mail',[]))
            if key not in omitted:omitted.append(key)
            self.work.dismissed_mail=omitted
        source=[d for d in getattr(self,'_draft_scope_source',[]) if d is not draft and not d.options.get('manual')]
        self.draft_index=None
        self._display_prepared_drafts(source,'{count} borradores disponibles.')
        self._save_session()
        self.status.set('Correo retirado de CSMP. Si ya se guardó en Outlook, esa copia permanece allí.')

    def _restore_mail(self):
        if not self.work:raise ValueError('Carga o recupera el trabajo cuyos correos quieres restaurar.')
        self.work.dismissed_mail=[];self._save_session()
        self.status.set('Omisiones retiradas. Pulsa Preparar tipo o Preparar todos para volver a proponer esos correos.')

    def _mail_context(self,draft):
        if draft.options.get('manual'):
            self.manual_store.config=deepcopy(self.cfg.data);return self.manual_store
        return self._require_work()

    def _send_draft(self):
        self._capture_mail()
        if self.draft_index is None:raise ValueError('Crea o selecciona un borrador antes de guardar.')
        draft=replace(self.drafts[self.draft_index]);context=self._mail_context(draft)
        def done(result):
            self._save_session();self.status.set('Borrador guardado en Outlook. No se envió ningún correo.')
        self._run('Guardando el borrador revisado en Outlook…',lambda:create_draft(context,draft,confirmed=True),done)

    def _send_all(self):
        self._capture_mail()
        if not self.drafts:raise ValueError('Crea o prepara los correos y revísalos antes de guardar el conjunto.')
        if any(d.options.get('pending_table') for d in self.drafts):
            raise ValueError('Hay nóminas pendientes: revisa los registros y genera cada Excel antes de guardar el conjunto.')
        from .outputs import create_drafts
        jobs=[(self._mail_context(d),replace(d)) for d in self.drafts]
        def action():
            total={'created':0,'skipped':0,'errors':[]}
            for context,draft in jobs:
                result=create_drafts(context,[draft])
                for key in ('created','skipped'):total[key]+=result[key]
                total['errors']+=result['errors']
            return total
        def done(result):
            self._save_session()
            self.status.set(f"{result['created']} borradores guardados; {result['skipped']} ya procesados; {len(result['errors'])} incidencias.")
            if result['errors']:messagebox.showwarning('Borradores con incidencias','\n'.join(result['errors']),parent=self)
        self._run('Guardando los borradores revisados en Outlook…',action,done)

    def _review_mail_records(self):
        self._capture_mail()
        if self.draft_index is None:raise ValueError('Selecciona un correo para revisar su nómina.')
        draft=self.drafts[self.draft_index]
        table=draft.options.get('table')
        if not table:
            if draft.options.get('manual'):table=empty_table()
            else:
                from .mail_category import category
                rows=[r for r in self.work.rows if r.id in draft.record_ids]
                table=table_snapshot(self.work,rows,category(self.work.config['correos']['plantillas'].get(draft.kind,{}),draft.kind))
        from .manual_dialogs import records_dialog
        records_dialog(self,draft,table)

    def _manual_resolution(self):
        from .manual_dialogs import resolution_dialog
        resolution_dialog(self)
