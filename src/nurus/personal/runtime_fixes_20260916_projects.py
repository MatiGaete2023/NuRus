"""Presentación de Resoluciones a nivel de proyecto/caso, no de persona."""
from nurus.rus.columns import normalize
from . import app_base as _app_base

_ORIGINAL_SHOW_WORK = _app_base.App._show_work


def show_work_one_row_per_project(self):
    _ORIGINAL_SHOW_WORK(self)
    seen = set()
    for iid in list(self.words.get_children()):
        values = self.words.item(iid, 'values')
        if len(values) < 3:
            continue
        key = (normalize(values[1]), normalize(values[0]), str(values[2]).strip().upper())
        if key in seen:
            self.words.delete(iid)
        else:
            seen.add(key)
    # El resumen debe describir proyectos/casos visibles, no registros personales.
    if self.work:
        n=len(self.work.rows);exc=sum(r.excluded for r in self.work.rows);obs=sum(bool(r.observation) for r in self.work.rows)
        self.summary.set(f'{n} registros · {obs} propuestas · {exc} excluidos · {len(self.words.get_children())} proyectos posibles')


_app_base.App._show_work = show_work_one_row_per_project
