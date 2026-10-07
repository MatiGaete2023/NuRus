"""Lectura local de capturas RUS. No reproduce peticiones ni guarda en el sitio."""
import base64
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlsplit

from lxml import html
from nurus.rus.columns import normalize
from .bitacoras import Observation, export_audit, cc_for_type, response_state, EXCEL_CELL_TEXT_LIMIT, _utf16_units

ORIGIN = 'https://familia.pjud.cl'
POPUP_PATH = '/SITFAWEB/IrPopUpInformesAccion.do'
HEADERS = ('Tipo Observación', 'Etapa', 'Fecha Centro', 'Usuario Centro',
           'Observación Centro', 'Fecha Tribunal', 'Usuario Tribunal',
           'Observación Tribunal', 'Acción')
IDENTITY_FIELDS = ('COD_Tribunal', 'CRR_IdCausa', 'ID_Ingreso', 'COD_Etapa', 'TIP_Consulta')
FULL_FIELDS = ('HOBS_Centro_', 'HOBS_Tribunal_', 'HCOD_Estado_', 'HFUN_Tribunal_', 'HFLG_Envio_')


def _date(text, *, optional=False):
    text = text.strip()
    if optional and text in ('', '---'): return ''
    for pattern in ('%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y'):
        try: return datetime.strptime(text, pattern).isoformat()
        except ValueError: pass
    raise ValueError('La captura contiene una fecha de bitácora ilegible.')


def _one_input(form, name):
    found = form.xpath('.//input[@name=$name]', name=name)
    if len(found) != 1: raise ValueError('Campo ausente o repetido en bitácora: '+name)
    return found[0].get('value', '')


def read_popup(text, params, *, source='', captured_at=''):
    """Vincula cada fila con sus campos ocultos por ID, nunca por posición."""
    if params.get('tipo_popUp') != '12': raise ValueError('La captura no corresponde a una bitácora RUS.')
    # RUS añade scripts después de </html> en esta ventana.
    if not re.search(r'</html\s*>', text, re.I):
        raise ValueError('La respuesta HTML está incompleta.')
    document = html.fromstring(text)
    forms = document.xpath('//form[@name="InformesPpalForm"]')
    if len(forms) != 1: raise ValueError('No se encontró el formulario de bitácora; comprueba la sesión.')
    form = forms[0]
    action = urlsplit(form.get('action', ''))
    if (action.path != '/SITFAWEB/InformesDAction.do' or
            (action.netloc and f'{action.scheme}://{action.netloc}' != ORIGIN)):
        raise ValueError('El formulario de bitácora no tiene el destino esperado.')
    context = {key: _one_input(form, key) for key in IDENTITY_FIELDS}
    for key, value in context.items():
        if not value or value != params.get(key):
            raise ValueError('La respuesta no corresponde al ingreso solicitado: '+key)
    for key in IDENTITY_FIELDS[:4]:
        if not context[key].isdigit() or int(context[key]) <= 0:
            raise ValueError('Identidad remota inválida: '+key)
    kind = _one_input(form, 'tipo_popUp')
    if kind not in ('', '12'): raise ValueError('El tipo de ventana no corresponde a bitácora.')
    tables = form.xpath('.//table[@id="TablaInforme"]')
    if len(tables) != 1: raise ValueError('La captura no contiene una tabla de bitácora única.')
    table = tables[0]; rows = table.xpath('.//tr')
    if not rows or tuple(normalize(' '.join(c.text_content().split())) for c in rows[0].xpath('./td|./th')) != tuple(map(normalize, HEADERS)):
        raise ValueError('Cambió la estructura de la tabla de bitácora.')
    hidden = {}
    for field in table.xpath('.//input'):
        name = field.get('name', '')
        if not name.startswith(FULL_FIELDS): continue
        if field.get('type', '').lower() != 'hidden' or name in hidden:
            raise ValueError('Campo de texto completo inválido o repetido.')
        hidden[name] = field.get('value', '')
    base = {'tribunal_codigo': context['COD_Tribunal'], 'causa_id': context['CRR_IdCausa'],
            'ingreso_id': context['ID_Ingreso'], 'rit': _one_input(form, 'RIT_Causa'),
            'persona': _one_input(form, 'GLS_Nombre'), 'centro': _one_input(form, 'GLS_Centro')}
    entries = []; ids = set(); used = set(); warnings = []; row_metadata = []
    for number, row in enumerate(rows[1:], 1):
        cells = row.xpath('./td')
        if len(cells) != len(HEADERS): raise ValueError('Fila de bitácora incompleta.')
        values = [' '.join(cell.text_content().split()) for cell in cells]
        actions = cells[-1].xpath('.//img[@id]')
        entry_ids = {field.get('id') for field in actions}
        if len(entry_ids) != 1: raise ValueError('No se puede vincular la fila con su observación.')
        entry_id = entry_ids.pop()
        if not entry_id.isdigit() or int(entry_id) <= 0 or entry_id in ids:
            raise ValueError('La tabla contiene una identidad de observación inválida o repetida.')
        ids.add(entry_id)
        names = [prefix+entry_id for prefix in FULL_FIELDS]
        if any(name not in hidden for name in names):
            raise ValueError('Falta el texto completo o metadatos de una observación.')
        used.update(names)
        center, response, state, tribunal_user, send = [hidden[name] for name in names]
        if response.strip() == '---': response = ''
        response_date = _date(values[5], optional=True)
        if bool(response.strip()) != bool(response_date):
            warnings.append('Entrada '+entry_id+': respuesta y fecha del tribunal no concuerdan.')
        entries.append(Observation(**base, entry_id=entry_id, fecha=_date(values[2]), autor=values[3],
            tipo=values[0], etapa=values[1], texto=center, origen='centro', respuesta=response,
            fecha_respuesta=response_date, respuesta_comprobada=True, fuente=source, fila_fuente=number))
        row_metadata.append({'entry_id': entry_id, 'state': state, 'send_to_tribunal': send,
                             'tribunal_user': tribunal_user})
    if set(hidden) != used: raise ValueError('Hay textos ocultos sin una fila correspondiente.')
    # Una captura no acredita la cobertura actual del sitio ni una consulta completa de otros ingresos.
    return {**base, 'entries': entries, 'coverage': 'PARCIAL', 'captured_at': captured_at,
            'stage_code': context['COD_Etapa'], 'source': source, 'row_metadata': row_metadata,
            'warnings': warnings, 'html_sha256': sha256(text.encode('utf-8')).hexdigest(),
            'captures': 1, 'error': 'Tabla recuperada de una captura HAR. No es una consulta en vivo ni acredita cobertura del servidor.'}


def import_har(paths):
    """Importa varias capturas. No accede a cookies, cabeceras de sesión ni red."""
    queries = {}; sources = []
    for path in map(Path, paths):
        raw = path.read_bytes(); document = json.loads(raw.decode('utf-8-sig'))
        records = document.get('log', {}).get('entries', [])
        if not isinstance(records, list): raise ValueError('HAR sin lista de peticiones válida.')
        found = 0
        for number, record in enumerate(records):
            request = record.get('request', {}); url = urlsplit(request.get('url', ''))
            if url.path != POPUP_PATH: continue
            if f'{url.scheme}://{url.netloc}' != ORIGIN or request.get('method') != 'GET':
                raise ValueError('Origen o método inesperado para la apertura de bitácora.')
            pairs = parse_qsl(url.query, keep_blank_values=True)
            params = dict(pairs)
            if len(params) != len(pairs): raise ValueError('La consulta tiene parámetros repetidos.')
            if params.get('tipo_popUp') != '12': continue
            response = record.get('response', {})
            if response.get('status') != 200: raise ValueError('Una apertura de bitácora no respondió correctamente.')
            content = response.get('content', {}); text = content.get('text', '')
            encoding = content.get('encoding')
            if encoding == 'base64': text = base64.b64decode(text, validate=True).decode('utf-8-sig')
            elif encoding: raise ValueError('Codificación HAR desconocida.')
            capture_time = record.get('startedDateTime', '')
            try: datetime.fromisoformat(capture_time.replace('Z', '+00:00'))
            except (ValueError, AttributeError): raise ValueError('La apertura no identifica la fecha de la captura.')
            query = read_popup(text, params, source=f'{path.name} / respuesta {number}', captured_at=capture_time)
            found += 1
            key = tuple(query[k] for k in ('tribunal_codigo', 'causa_id', 'ingreso_id'))
            if key in queries:
                old = queries[key]
                if old['html_sha256'] != query['html_sha256']:
                    raise ValueError('Dos capturas del mismo ingreso difieren. Importa por separado para comparar las versiones.')
                old['captures'] += 1
            else: queries[key] = query
        sources.append({'file': path.name, 'sha256': sha256(raw).hexdigest(), 'requests': len(records),
                        'openings': found, 'detail': '' if found else 'Sin respuestas de bitácora recuperables.'})
    if not queries: raise ValueError('No hay respuestas de bitácora recuperables en los HAR seleccionados.')
    return {'queries': list(queries.values()), 'sources': sources}


def export_har_audit(capture, destination, start, end, *, today=None):
    sources = [(s['file'], s['sha256'], s['requests'], s['openings'], s['detail']) for s in capture['sources']]
    provenance = []; copy_rows = []
    for query in capture['queries']:
        provenance.append([query['tribunal_codigo'], query['causa_id'], query['ingreso_id'], query['rit'],
            query['persona'], query['centro'], query['stage_code'], query['captured_at'], query['captures'],
            len(query['entries']), query['html_sha256'], query['error'], '\n'.join(query['warnings'])])
        for entry, meta in zip(query['entries'], query['row_metadata']):
            if any(_utf16_units(text)>EXCEL_CELL_TEXT_LIMIT for text in (entry.texto,entry.respuesta)):
                raise ValueError('Un texto excede el límite de celda de Excel; no se generará una copia recortada.')
            copy_rows.append([entry.tribunal_codigo,entry.causa_id,entry.ingreso_id,entry.rit,entry.persona,
                entry.centro,entry.entry_id,entry.fecha,entry.autor,entry.tipo,cc_for_type(entry.tipo),entry.etapa,
                entry.texto,entry.fecha_respuesta,meta['tribunal_user'],entry.respuesta,response_state(entry),
                meta['state'],meta['send_to_tribunal'],query['captured_at']])
    return export_audit(capture['queries'], destination, start, end, today=today, extra_sheets=[
        ('Copia íntegra', ('Tribunal código','Causa RUS','Ingreso RUS','RIT','Persona','Centro','Entrada RUS',
         'Fecha centro','Usuario centro','Tipo','CC','Etapa','Texto centro','Fecha tribunal','Usuario tribunal',
         'Texto tribunal','Estado respuesta','Estado RUS código','HFLG_Envio RUS','Fecha captura'),copy_rows),
        ('Capturas', ('Tribunal código', 'Causa RUS', 'Ingreso RUS', 'RIT', 'Persona', 'Centro',
         'Etapa código', 'Fecha captura', 'Aperturas idénticas', 'Entradas tabla capturada', 'SHA-256 HTML',
         'Alcance', 'Advertencias'), provenance),
        ('Fuentes HAR', ('Archivo', 'SHA-256', 'Peticiones', 'Aperturas', 'Detalle'), sources)])
