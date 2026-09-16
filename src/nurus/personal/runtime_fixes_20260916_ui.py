"""Ajustes de interfaz complementarios al flujo revisado del 16-09-2026."""
from . import runtime_fixes_20260916 as fixes
from . import resolutions as _resolutions
from . import app_base as _app_base
from nurus.rus.columns import normalize


def observation_resolution_kind(row):
    """La observación humana discrimina el tipo aun si usa una redacción breve."""
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
    # Cuando el caso ya está marcado para proyecto, estas materias bastan para
    # determinar la matriz; no se exige una fórmula textual exacta.
    if any(part in text for part in ('informe', 'diagnostico', 'diagnostico clinico')):
        return 'PC_INFO'
    if any(part in text for part in ('ingreso efectivo', 'fecha estimada de ingreso', 'ingreso al programa')):
        return 'PC_IE'
    return None


fixes.observation_resolution_kind = observation_resolution_kind
_resolutions.automatic_project_selections = fixes.automatic_project_selections_by_observation

_ORIGINAL_EXPORT_CURRENT = _app_base.App._export_current


def export_current_with_live_edit(self):
    # Exportar equivale a confirmar el contenido que está visible en el editor;
    # no requiere pulsar antes «Aplicar edición» ni cambiar de fila.
    self._capture_observation()
    return _ORIGINAL_EXPORT_CURRENT(self)


_app_base.App._export_current = export_current_with_live_edit
