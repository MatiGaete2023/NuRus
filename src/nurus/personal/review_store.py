"""Revisiones locales por ingreso real; no atribuye gestiones a RUS."""
from hashlib import sha256
import json
from pathlib import Path
import re

from .config import atomic_json


def identity(work, row):
    # Los vínculos provienen de la respuesta que originó el Excel. Las correcciones
    # del editor no cambian el destino ni trasladan la revisión a otra persona.
    values = row.values
    keys = ('SITFA_TRIBUNAL_CODIGO', 'SITFA_CAUSA_RUS', 'SITFA_INGRESO_RUS',
            'SITFA_PERSONA_RUS', 'SITFA_CENTRO_RUS')
    parts = tuple(str(values.get(k, '') or '') for k in keys)
    verified = values.get('SITFA_VINCULO_ESTADO') == 'Vinculado desde respuesta actual'
    if verified and all(re.fullmatch(r'\d{1,20}', value) for value in parts):
        namespace = ('rus', *parts)
        kind = 'ingreso_real'
    else:
        # Sin vínculo comprobado se conserva la sesión, pero nunca se hereda la
        # revisión mediante RIT/nombre ni entre descargas distintas.
        namespace = ('fuente', work.source_hash, row.id)
        kind = 'solo_esta_fuente'
    return sha256(json.dumps(namespace).encode()).hexdigest(), kind


class ReviewStore:
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        if not self.path.exists():
            return {'version': 1, 'ingresos': {}}
        if self.path.stat().st_size > 8 * 1024 * 1024:
            raise ValueError('El archivo de revisiones excede el límite de lectura.')
        data = json.loads(self.path.read_text(encoding='utf-8'))
        if data.get('version') != 1 or not isinstance(data.get('ingresos'), dict):
            raise ValueError('El archivo de revisiones no tiene un formato compatible.')
        for key, value in data['ingresos'].items():
            if not re.fullmatch('[0-9a-f]{64}', key) or not isinstance(value, dict):
                raise ValueError('Hay una revisión local inválida.')
            if not isinstance(value.get('firmas'), dict):
                raise ValueError('Falta el detalle de una revisión local.')
        return data

    def remember(self, work, row, fingerprint, timestamp):
        data = self.read()
        key, kind = identity(work, row)
        item = data['ingresos'].setdefault(key, {'alcance': kind, 'firmas': {}})
        item['firmas'][fingerprint] = timestamp
        atomic_json(self.path, data)


def bind(work, path):
    store = ReviewStore(path)
    data = store.read()
    entries = data['ingresos']
    work.review_store_path = str(store.path)
    for row in work.rows:
        key, _ = identity(work, row)
        saved = entries.get(key, {}).get('firmas', {})
        work.activity_reviewed.setdefault(row.id, {}).update(saved)
    from .rus_activity import attach
    attach(work)
    # Promote only an exact, unique alias from a verified intake. Keep the old
    # hash in the same store entry because it cannot be reconstructed later.
    from .rus_activity import _legacy_alias_matches
    changed=False
    for row in work.rows:
        key, kind = identity(work, row)
        if kind!='ingreso_real':continue
        item=entries.get(key)
        if not item or not isinstance(item.get('firmas'),dict):continue
        signatures=work.signed_activity.get(row.id,{}).get('firmas',[])
        for fingerprint,legacy in _legacy_alias_matches(signatures).items():
            if legacy in item['firmas'] and fingerprint not in item['firmas']:
                item['firmas'][fingerprint]=item['firmas'][legacy];changed=True
    if changed:
        try:atomic_json(store.path,data)
        except OSError:
            warnings=getattr(work,'warnings',None)
            if isinstance(warnings,list):warnings.append('No se pudo guardar la nueva huella de una revisión heredada; se conserva la anterior y la coincidencia actual solo se usa en esta sesión.')
