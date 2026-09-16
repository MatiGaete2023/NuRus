"""Conserva la neutralización de fórmulas al exportar observaciones revisadas."""
from nurus.services import exports as _exports


def annotation_values_safe(record, stage):
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
    return str(_exports._safe_cell(record['edited_observation'])), state


_exports._annotation_values = annotation_values_safe
