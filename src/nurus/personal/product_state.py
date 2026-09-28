"""Dependencies of prepared products, independent of their editable text."""
from hashlib import sha256
from pathlib import Path
import json

from nurus.rus.columns import normalize


def fingerprint(work, record_ids, kind):
    ids = set(record_ids)
    rows = getattr(work, 'rows', [])
    mapping = getattr(work, 'mapping', {})

    def group(row):
        fields = ('tribunal', 'programa') if kind.startswith('programa_') else ('tribunal', 'rit')
        return tuple(normalize(row.overrides.get(key, row.values.get(mapping.get(key, ''), ''))) for key in fields)

    groups = {group(row) for row in rows if row.id in ids}
    records=[]
    for row in rows:
        if row.id not in ids and group(row) not in groups:continue
        record={key:getattr(row,key) for key in
                ('id','review','observation','actions','excluded','decisions','overrides','word_overrides')}
        record['values']={key:row.values.get(column,'') for key,column in mapping.items()}
        records.append(record)
    records.sort(key=lambda row: row['id'])
    cfg = getattr(work, 'config', {})
    configuration = {key: cfg.get(key) for key in ('correos', 'contactos', 'aliases', 'firma')}
    payload = {'records': records, 'config': configuration, 'kind': kind, 'ids': sorted(ids)}
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()


def stamp(work, product):
    product.dependency_hash = fingerprint(work, product.record_ids, product.kind)
    if hasattr(product, 'template_hash'):
        product.template_hash = sha256(Path(product.template).read_bytes()).hexdigest()


def stale(work, product):
    expected = getattr(product, 'dependency_hash', '')
    if expected and expected != fingerprint(work, product.record_ids, product.kind):
        return True
    if getattr(product, 'template_hash', ''):
        path = Path(product.template)
        return not path.exists() or sha256(path.read_bytes()).hexdigest() != product.template_hash
    return False


def require_fresh(work, product):
    from .sync import require_current_copy
    require_current_copy(work)
    if stale(work, product):
        raise ValueError('Este producto necesita actualizarse porque cambiaron sus registros o plantilla. '
                         'Prepara nuevamente y revisa los cambios antes de guardar.')

