"""Correcciones de flujo personal verificadas el 16-09-2026.

Se cargan al importar ``nurus.personal`` para mantener una única ruta de ejecución
sin reescribir los módulos históricos. Cada corrección está cubierta por regresión.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import json

from nurus.rus.columns import normalize
from nurus.rus.rules import tribunal
from nurus.services.exports import _export_preserved_payload
from nurus.services import exports as _exports

from . import outputs as _outputs
from . import resolutions as _resolutions
from .mail_controls import alcance_modalidades
from .outputs import value
from .work import Work as _Work


def _explicit(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _human_reviewed(row):
    """Distingue una edición humana real de columnas técnicas reimportadas vacías."""
    review = row.review or {}
    if 'OBSERVACION' in review and str(review.get('OBSERVACION', '')) != str(row.observation or ''):
        return True
    return any(_explicit(review.get(key)) for key in ('FECHA_OBS', 'TT', 'CC', 'RES'))


def _review_value(row, key, fallback=''):
    if key in (row.review or {}):
        return row.review.get(key, '')
    return fallback


def export_reviewed_work(self, destination, *, backend='native', reduced_fidelity=False):
    """Exporta las ediciones de la ventana Trabajo sin convertir el original en fuente mutable.

    Si todavía no existe edición humana, conserva la salida de propuesta. Si existe
    al menos una edición, solo las filas realmente revisadas escriben OBSERVACION,
    FECHA_OBS, TT, CC y RES en la copia resultante; las restantes quedan PENDIENTES.
    """
    reviewed = {row.id: _human_reviewed(row) for row in self.rows}
    reviewed_stage = any(reviewed.values())
    batch = {
        'source_name': Path(self.path).name,
        'source_path': self.path,
        'source_hash': self.source_hash,
        'primary_sheet': self.sheet,
        'header_row': self.header,
        'mode': self.mode,
        'export_stage': 'reviewed' if reviewed_stage else 'proposal',
    }
    records = []
    for row in self.rows:
        is_reviewed = reviewed[row.id]
        records.append({
            'record_id': row.id,
            'source_sheet': self.sheet,
            'source_row': row.source_row,
            'source_hash': self.source_hash,
            'decision': 'excluded' if row.excluded else ('approved' if is_reviewed else 'pending'),
            'evaluation_status': 'blocked' if row.warnings else 'reviewed',
            'edit_reason': '; '.join(row.warnings),
            'edited_observation': _review_value(row, 'OBSERVACION', row.observation),
            'rule_ids_json': json.dumps(row.rules),
            'rus_recorded': bool(is_reviewed and not row.excluded),
            'review_date': _review_value(row, 'FECHA_OBS'),
            'tt_value': _review_value(row, 'TT'),
            'workload_value': _review_value(row, 'CC'),
            'resolution_value': _review_value(row, 'RES'),
        })
    result = _export_preserved_payload(
        self.content,
        {'batch': batch, 'records': records, 'exceptions': [self.exception] if self.exception else []},
        destination,
        backend=backend,
        allow_reduced_fidelity=reduced_fidelity,
    )
    self.output = str(result.path)
    self.output_hash = sha256(Path(self.output).read_bytes()).hexdigest()
    return self.output


def annotation_values(record, stage):
    if record['decision'] == 'excluded':
        state = 'EXCLUIDO'
    elif stage == 'proposal' and record['evaluation_status'] == 'blocked':
        state = 'REQUIERE_REVISION'
    elif stage == 'proposal':
        state = 'PROPUESTA'
    elif record['decision'] == 'approved':
        state = 'REVISADO'
    else:
        state = 'PENDIENTE'
    return str(record['edited_observation']), state


def _draft_fingerprint(draft):
    attachments = []
    for item in draft.attachments:
        path = Path(item)
        digest = sha256(path.read_bytes()).hexdigest() if path.is_file() else 'MISSING'
        attachments.append((str(path.resolve()), digest))
    payload = {
        'to': str(draft.to or '').strip(),
        'cc': str(draft.cc or '').strip(),
        'subject': str(draft.subject or ''),
        'body': str(draft.body or ''),
        'attachments': attachments,
    }
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


_ORIGINAL_CREATE_DRAFT = _outputs.create_draft
_ORIGINAL_CREATE_DRAFTS = _outputs.create_drafts


def create_draft_by_content(work, draft, *, confirmed=False):
    """La deduplicación considera el borrador realmente revisado, no solo filas+asunto."""
    draft.key = _draft_fingerprint(draft)
    return _ORIGINAL_CREATE_DRAFT(work, draft, confirmed=confirmed)


def create_drafts_by_content(work, drafts):
    for draft in drafts:
        draft.key = _draft_fingerprint(draft)
    return _ORIGINAL_CREATE_DRAFTS(work, drafts)


def observation_resolution_kind(row):
    """Clasifica el tipo desde la observación humana antes de usar la sugerencia del motor."""
    review = row.review or {}
    text = normalize(review.get('OBSERVACION', row.observation) or '')
    if not text:
        return None
    if 'nomencl' in text:
        return 'NOMENCL'
    if 'pc info' in text:
        return 'PC_INFO'
    if 'pc ie' in text:
        return 'PC_IE'
    project_cue = any(part in text for part in ('proyecto de resolucion', 'proyecto resolucion', 'pidiendo cuenta', 'pedir cuenta'))
    if project_cue and any(part in text for part in ('informe', 'diagnostico', 'informe de avance')):
        return 'PC_INFO'
    if project_cue and any(part in text for part in ('ingreso efectivo', 'fecha estimada de ingreso', 'ingreso al programa')):
        return 'PC_IE'
    return None


def automatic_project_selections_by_observation(work, fallback_kind='PC_IE'):
    """Respeta RES y usa la observación revisada para escoger PC_IE/PC_INFO/NOMENCL."""
    reviewed = _resolutions.reviewed_resolution_ids(work)
    result = []
    if reviewed is None:
        for row in work.rows:
            if row.excluded:
                continue
            suggested = [kind for kind in row.actions if kind in _resolutions.KINDS]
            if not suggested:
                continue
            observed = observation_resolution_kind(row)
            kinds = [observed] if observed else suggested
            for kind in kinds:
                if kind in _resolutions.KINDS:
                    result.append((row.id, kind))
        return result

    case_kinds = OrderedDict()
    for row in work.rows:
        if row.id not in reviewed or row.excluded:
            continue
        explicit = _resolutions.resolution_kind(row.review.get('RES'))
        observed = observation_resolution_kind(row)
        actions = [kind for kind in row.actions if kind in _resolutions.KINDS]
        kinds = [explicit] if explicit else ([observed] if observed else actions)
        if not kinds:
            kinds = [fallback_kind]
        bucket = case_kinds.setdefault(_resolutions._case_key(work, row), [])
        for kind in kinds:
            if kind and kind not in bucket:
                bucket.append(kind)
    for row in work.rows:
        if row.excluded:
            continue
        for kind in case_kinds.get(_resolutions._case_key(work, row), []):
            result.append((row.id, kind))
    return result


def _install():
    # Exportación visible de ediciones humanas.
    _Work.export = export_reviewed_work
    _exports._annotation_values = annotation_values

    # Borradores: una edición de Para/CC/Asunto/Cuerpo/Adjunto produce una nueva
    # identidad y no queda bloqueada por un borrador de una versión anterior.
    _outputs.create_draft = create_draft_by_content
    _outputs.create_drafts = create_drafts_by_content

    # Resoluciones: tipo derivado de la observación revisada cuando RES no lo dice.
    _resolutions.automatic_project_selections = automatic_project_selections_by_observation

    # Importamos la base después de parchear outputs/resolutions para que sus aliases
    # locales apunten a las funciones corregidas.
    from . import app_base as _app_base

    def assign_word_type_individually(self):
        selected = list(self.words.selection())
        if not selected:
            raise ValueError('Selecciona una o más filas concretas de Resoluciones antes de cambiar su tipo.')
        kind = self.manual_word.get()
        new = []
        for iid in selected:
            rid = iid.split('|')[0]
            values = list(self.words.item(iid, 'values'))
            values[2] = kind
            self.words.delete(iid)
            target = rid + '|' + kind
            if not self.words.exists(target):
                self.words.insert('', 'end', iid=target, values=values)
            new.append(target)
        self.words.selection_set(new)
        self.projects = []
        self.project_index = None
        self.project_list.delete(0, 'end')
        self.status.set(f'Tipo {kind} aplicado solo a {len(new)} selección(es).')

    def send_all_or_prepare(self):
        work = self._require_work()
        self._capture_mail()
        if self.drafts:
            drafts = [replace(draft) for draft in self.drafts]
            def done(result):
                self._save_session()
                self.status.set(f"{result['created']} borradores guardados; {result['skipped']} ya procesados; {len(result['errors'])} incidencias.")
                if result['errors']:
                    from tkinter import messagebox
                    messagebox.showwarning('Lote guardado con incidencias', '\n'.join(result['errors']))
            self._run('Guardando el lote de borradores en Outlook…', lambda: _outputs.create_drafts(work, drafts), done)
            return

        # Si aún no se preparó vista previa, el mismo botón prepara y guarda el lote,
        # equivalente al creador de correos independiente. El clic es la confirmación.
        if not all(hasattr(self, name) for name in ('_sync_mail_config', '_selected_mail_modalities', '_mail_selected_ids')):
            raise ValueError('Primero prepara los borradores.')
        self._sync_mail_config(work)
        keys = self._selected_mail_modalities()
        if not keys:
            raise ValueError('Selecciona al menos una modalidad.')
        selected = self._mail_selected_ids(work, manual=False)
        period = self.period.get()
        phrase = alcance_modalidades(keys)

        def action():
            drafts = _outputs.prepare_required_drafts(
                work,
                modalities=phrase,
                period=period,
                selected=selected,
                modality_keys=keys,
            )
            result = _outputs.create_drafts(work, [replace(draft) for draft in drafts])
            return drafts, result

        def done(payload):
            drafts, result = payload
            if hasattr(self, '_display_prepared_drafts'):
                self._display_prepared_drafts(drafts, '{count} borradores preparados y procesados para Outlook.')
            self._save_session()
            self.status.set(f"{result['created']} borradores guardados; {result['skipped']} ya existentes; {len(result['errors'])} incidencias.")
            if result['errors']:
                from tkinter import messagebox
                messagebox.showwarning('Lote guardado con incidencias', '\n'.join(result['errors']))

        self._run('Preparando y guardando todos los borradores en Outlook…', action, done)

    _app_base.App._assign_word_type = assign_word_type_individually
    _app_base.App._send_all = send_all_or_prepare


_install()
