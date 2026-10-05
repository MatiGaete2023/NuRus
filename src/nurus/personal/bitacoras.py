"""Análisis común de bitácoras: hechos consultados, sin proponer ni registrar texto."""
from calendar import monthrange
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from difflib import SequenceMatcher

from nurus.rus.columns import normalize


def earliest(today):
    month=today.year*12+today.month-1-4
    year,zero=divmod(month,12)
    return date(year,zero+1,min(today.day,monthrange(year,zero+1)[1]))


def validate_period(start,end,today=None):
    today=today or date.today()
    if not isinstance(start,date) or not isinstance(end,date) or start>end or end>today or start<earliest(today):
        raise ValueError('Las bitácoras admiten hasta los últimos cuatro meses calendario, sin fechas futuras.')


def cc_for_type(kind):
    key=normalize(kind)
    if key==normalize('Al Tribunal'):return 1
    if key==normalize('Administrativa'):return 0
    return None


@dataclass(frozen=True)
class Observation:
    tribunal_codigo: str
    causa_id: str
    ingreso_id: str
    entry_id: str
    fecha: str
    autor: str
    tipo: str
    etapa: str
    texto: str
    origen: str = 'desconocido'
    respuesta: str = ''
    fecha_respuesta: str = ''
    respuesta_comprobada: bool = False
    fuente: str = ''
    fila_fuente: int = 0
    rit: str = ''
    tribunal: str = ''
    persona: str = ''
    centro: str = ''

    def moment(self):
        try:return datetime.fromisoformat(self.fecha)
        except (TypeError,ValueError):return None

    def identity(self):
        base=(self.tribunal_codigo,self.causa_id,self.ingreso_id)
        if not all(base):raise ValueError('Una entrada carece de identidad de causa o ingreso.')
        if self.entry_id:return (*base,'remota',self.entry_id)
        if not self.fuente or self.fila_fuente<1:
            raise ValueError('Una entrada sin ID remoto necesita fuente y posición comprobables.')
        return (*base,'fuente',self.fuente,self.fila_fuente)


def deduplicate(entries):
    result={}
    for entry in entries:
        key=entry.identity()
        if key in result:
            old=result[key]
            facts=('fecha','autor','tipo','etapa','texto','origen','respuesta','fecha_respuesta','respuesta_comprobada')
            if any(getattr(old,k)!=getattr(entry,k) for k in facts):
                raise ValueError('Dos extracciones contienen datos distintos para una misma entrada de bitácora.')
        else:result[key]=entry
    return list(result.values())


def response_state(entry):
    if cc_for_type(entry.tipo)==0:return 'Administrativa; no exige respuesta del tribunal'
    if cc_for_type(entry.tipo) is None:return 'Tipo pendiente de clasificación'
    if not entry.respuesta_comprobada:return 'Respuesta no comprobable con esta lectura'
    return 'Respuesta registrada' if entry.respuesta.strip() else 'Sin respuesta registrada'


def analyze(entries,start,end,*,today=None,author=None,coverage='PARCIAL'):
    validate_period(start,end,today)
    if coverage not in ('COMPLETA','PARCIAL','FALLIDA','NO_CONSULTADA'):raise ValueError('Cobertura de bitácora desconocida.')
    complete=deduplicate(entries);invalid=[];current=[]
    if len({(e.tribunal_codigo,e.causa_id,e.ingreso_id) for e in complete})>1:
        raise ValueError('Analiza cada ingreso por separado para no mezclar sus observaciones.')
    for entry in complete:
        moment=entry.moment()
        if moment is None:invalid.append(entry);continue
        if start<=moment.date()<=end and (not author or normalize(entry.autor)==normalize(author)):current.append(entry)
    if invalid and coverage=='COMPLETA':coverage='PARCIAL'
    groups=defaultdict(list)
    for entry in current:
        if entry.texto.strip():groups[normalize(entry.texto)].append(entry)
    repeated={e.identity() for items in groups.values() if len(items)>1 for e in items}
    possible=set();texts=sorted(groups)
    for i,text in enumerate(texts):
        if len(text)<30:continue
        for other in texts[i+1:i+6]:
            if len(other)>=30 and SequenceMatcher(None,text,other,autojunk=False).ratio()>=.92:
                possible.update(e.identity() for e in (*groups[text],*groups[other]))
    center=[e for e in current if e.origen=='centro']
    # Ordenar fechas con y sin hora/zona sin inventar una zona del servidor.
    def key(e):return e.moment().replace(tzinfo=None)
    latest=[]
    if center:
        last=max(key(e) for e in center);latest=[e for e in center if key(e)==last]
    return {'entries':current,'latest_center':latest,'coverage':coverage,'invalid_dates':invalid,
            'unknown_origin':sum(e.origen=='desconocido' for e in current),
            'repeated':repeated,'possible_repeated':possible,'start':start.isoformat(),'end':end.isoformat()}


def export_audit(queries,destination,start,end,*,today=None,author=None):
    """Queries contiene cada ingreso, incluso vacío/fallido: nunca desaparece del resumen."""
    from .reports import _book
    validate_period(start,end,today);history=[];summary=[];issues=[]
    for query in queries:
        entries=query.get('entries',[])
        result=analyze(entries,start,end,today=today,author=author,coverage=query.get('coverage','NO_CONSULTADA'))
        identity=(query.get('tribunal_codigo',''),query.get('causa_id',''),query.get('ingreso_id',''))
        if not all(identity):raise ValueError('La consulta de bitácora no identifica su ingreso.')
        if any((e.tribunal_codigo,e.causa_id,e.ingreso_id)!=identity for e in entries):
            raise ValueError('El contenido de una bitácora no pertenece a su ingreso solicitado.')
        recent=result['entries'];last=result['latest_center']
        latest_text='\n\n'.join(e.texto for e in last)
        summary.append([*identity,query.get('rit',''),result['coverage'],start.isoformat(),end.isoformat(),len(recent),
            last[0].fecha if last else '',latest_text,'Empate de fecha; conservar todas' if len(last)>1 else '',
            sum(cc_for_type(e.tipo)==1 for e in recent),sum(cc_for_type(e.tipo)==0 for e in recent),
            result['unknown_origin'],'Última del centro pendiente de comprobar' if result['unknown_origin'] or result['invalid_dates'] else ''])
        for entry in recent:
            history.append([*identity,entry.rit,entry.entry_id,entry.fecha,entry.autor,entry.tipo,cc_for_type(entry.tipo),
                entry.etapa,entry.origen,entry.texto,response_state(entry),entry.respuesta,entry.fecha_respuesta,
                entry.identity() in result['repeated'],entry.identity() in result['possible_repeated'],entry.fuente])
        for entry in result['invalid_dates']:issues.append([*identity,entry.entry_id,'Fecha ilegible',entry.fecha])
        if result['coverage']!='COMPLETA':issues.append([*identity,'','Lectura '+result['coverage'].lower(),query.get('error','')])
    return _book([
        ('Resumen',('Tribunal código','Causa RUS','Ingreso RUS','RIT','Cobertura','Desde','Hasta','Entradas recientes',
          'Última fecha centro','Texto','Ambigüedad','Con carga','Administrativas','Origen desconocido','Detalle'),summary),
        ('Bitácoras',('Tribunal código','Causa RUS','Ingreso RUS','RIT','Entrada RUS','Fecha','Autor','Tipo','CC','Etapa',
          'Origen','Texto','Estado respuesta','Respuesta','Fecha respuesta','Texto reiterado','Posible reiteración','Fuente'),history),
        ('Incidencias',('Tribunal código','Causa RUS','Ingreso RUS','Entrada RUS','Motivo','Detalle'),issues)],destination)
