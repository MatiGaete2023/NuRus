"""Metadatos de productos del trabajo actual, sin inferir envíos ni fechas pasadas."""
from datetime import datetime


def receipt(kind, state, *, record_ids=(), **details):
    return dict(kind=kind, state=state, created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
                record_ids=list(record_ids), **details)


def activity_rows(receipts):
    for key,item in reversed(list(receipts.items())):
        day=item.get('created_at')
        try:
            shown=datetime.fromisoformat(day).strftime('%d/%m/%Y %H:%M:%S')
        except (ValueError,TypeError):
            shown='Fecha no registrada'
        kind={'excel':'Excel','word':'Word','draft':'Borrador'}.get(item.get('kind'),item.get('kind','Producto'))
        state={'created':'Guardado en Outlook','saving':'Guardando','uncertain':'Guardado incierto',
               'generated':'Generado'}.get(item.get('state'),item.get('state','Generado'))
        detail=item.get('path') or item.get('subject') or item.get('entry_id') or key
        yield str(key),(shown,kind,state,str(detail))
