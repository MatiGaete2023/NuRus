"""Portable local view preferences; never includes case records or source paths."""
from copy import deepcopy
import json
from pathlib import Path
from uuid import uuid4

TABLES = {
    'records': ('Estado', 'RIT', 'Nombre', 'Tribunal', 'Programa', 'Observación'),
    'words': ('RIT', 'Tribunal', 'Tipo', 'Origen'),
    'sent': ('Fecha', 'Destinatario', 'Asunto'),
}
FILTERS = {
    'work_search': None,
    'work_filter': ('Todos', 'Con aviso', 'Con resolución', 'Excluidos', 'Sin incidencias'),
    'resolution_search': None,
    'resolution_filter': ('Todos', 'Definido en RES', 'Ajustado manualmente', 'Sugerencia automática', 'RES antiguo'),
}
PAGES = ('Trabajo', 'Correos', 'Resoluciones', 'Resultados', 'Configuración', 'Enviados')
MAX_BYTES = 2_000_000


def _keys(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('Estructura de vista incompatible: ' + label)


def _integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('Valor de vista fuera de rango: ' + label)


def validate_state(state):
    _keys(state, ('filters', 'tables', 'font_size', 'geometry', 'page', 'split'), 'vista')
    _keys(state['filters'], FILTERS, 'filtros')
    for key, choices in FILTERS.items():
        value = state['filters'][key]
        if not isinstance(value, str) or len(value) > 500 or (choices and value not in choices):
            raise ValueError('Filtro de vista incompatible: ' + key)
    _integer(state['font_size'], 10, 22, 'fuente')
    if state['page'] not in PAGES:
        raise ValueError('Pestaña de vista desconocida.')
    _keys(state['geometry'], ('width', 'height', 'x', 'y', 'maximized'), 'ventana')
    geometry = state['geometry']
    for key, low, high in (('width', 400, 10000), ('height', 300, 10000), ('x', -50000, 50000), ('y', -50000, 50000)):
        _integer(geometry[key], low, high, key)
    if type(geometry['maximized']) is not bool:
        raise ValueError('Estado de ventana incompatible.')
    _keys(state['split'], ('work_sash_ratio', 'resolution_sash_ratio'), 'separadores')
    for value in state['split'].values():
        if type(value) not in (int, float) or not .1 <= value <= .9:
            raise ValueError('Posición de separador fuera de rango.')
    _keys(state['tables'], TABLES, 'tablas')
    for name, columns in TABLES.items():
        table = state['tables'][name]
        _keys(table, ('visible', 'widths'), name)
        visible = table['visible']
        if (not isinstance(visible, list) or not visible or any(type(col) is not str or col not in columns for col in visible)
                or len(set(visible)) != len(visible)):
            raise ValueError('Columnas visibles incompatibles: ' + name)
        _keys(table['widths'], columns, 'anchos de ' + name)
        for width in table['widths'].values():
            _integer(width, 65, 2000, 'ancho de columna')
    return deepcopy(state)


def fit_geometry(geometry, screen_width, screen_height, minimum=(820, 560)):
    """Keep a portable window reachable on the current primary display."""
    width = min(screen_width, max(min(minimum[0], screen_width), geometry['width']))
    height = min(screen_height, max(min(minimum[1], screen_height), geometry['height']))
    x = max(0, min(geometry['x'], screen_width - width))
    y = max(0, min(geometry['y'], screen_height - height))
    return f'{width}x{height}+{x}+{y}'


def _name(name):
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80:
        raise ValueError('Escribe un nombre de vista de entre 1 y 80 caracteres.')
    return name.strip()


def read_json(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('El archivo de vista supera el tamaño permitido.')
    def distinct(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('El archivo de vista contiene claves repetidas.')
            result[key] = value
        return result
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=distinct)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('El archivo no es una vista JSON válida.') from exc


def _atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8')
    if len(content) > MAX_BYTES:
        raise ValueError('Las preferencias superan el tamaño permitido.')
    temporary = path.with_name(path.name + '.' + uuid4().hex + '.part')
    try:
        with temporary.open('xb') as stream:
            stream.write(content)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class Preferences:
    def __init__(self, directory):
        self.path = Path(directory) / 'vista.json'
        self.data = dict(version=1, current=None, previous=None, presets={})
        if self.path.exists():
            data = read_json(self.path)
            _keys(data, ('version', 'current', 'previous', 'presets'), 'preferencias')
            if type(data['version']) is not int or data['version'] != 1:
                raise ValueError('La versión de las preferencias no es compatible.')
            if not isinstance(data['presets'], dict) or len(data['presets']) > 30:
                raise ValueError('Se admiten hasta 30 vistas guardadas.')
            for key in ('current', 'previous'):
                if data[key] is not None:
                    validate_state(data[key])
            for name, state in data['presets'].items():
                if _name(name) != name:
                    raise ValueError('Nombre de vista incompatible.')
                validate_state(state)
            self.data = deepcopy(data)

    def _commit(self, data):
        _atomic(self.path, data)
        self.data = data

    def remember(self, state, *, keep_previous=False):
        state = validate_state(state)
        data = deepcopy(self.data)
        if state == data['current']:
            return
        if not keep_previous:
            data['previous'] = data['current']
        data['current'] = state
        self._commit(data)

    def save_preset(self, name, state):
        name = _name(name)
        state = validate_state(state)
        data = deepcopy(self.data)
        if name not in data['presets'] and len(data['presets']) >= 30:
            raise ValueError('Se admiten hasta 30 vistas guardadas.')
        data['presets'][name] = state
        self._commit(data)

    def export_preset(self, path, name, state):
        packet = dict(kind='csmp-view', version=1, name=_name(name), state=validate_state(state))
        path = Path(path)
        if path.resolve() == self.path.resolve():
            raise ValueError('Elige un archivo distinto de las preferencias internas.')
        if path.exists():
            raise ValueError('El archivo ya existe; elige un destino nuevo.')
        # Exclusive publication never overwrites a file created concurrently.
        content = json.dumps(packet, ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8')
        with path.open('xb') as stream:
            stream.write(content)
        return path

    def import_preset(self, path):
        packet = read_json(path)
        _keys(packet, ('kind', 'version', 'name', 'state'), 'archivo portable')
        if packet['kind'] != 'csmp-view' or type(packet['version']) is not int or packet['version'] != 1:
            raise ValueError('El archivo no es una vista CSMP compatible.')
        name = _name(packet['name'])
        state = validate_state(packet['state'])
        if name in self.data['presets']:
            raise ValueError('Ya existe una vista con ese nombre; no se sustituyó.')
        self.save_preset(name, state)
        return name
