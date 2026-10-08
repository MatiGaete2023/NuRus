"""Flujo completo ficticio de cuatro modalidades, páginas y fallas recuperables."""
import base64
import hashlib
import html
import json
import threading
from pathlib import Path
import pytest
from perfiles import Selection,selection_profile
from lotes import Batch
from lectura_bitacoras import DiaryRunner,MANIFEST
from test_lotes import CATALOG,FakeBridge,document
from test_vinculos import listing
from csmp_shared import parser

def popup(params,wrong=False):
    from nurus.bitacora_html import HEADERS
    fields={**params,'tipo_popUp':'','RIT_Causa':'X-1-2026','GLS_Nombre':'Persona ficticia',
            'GLS_Centro':'PRM Centro ficticio'}
    if wrong:fields['ID_Ingreso']='999'
    hidden={'HOBS_Centro_':'Texto completo\nSegunda línea','HOBS_Tribunal_':'---','HCOD_Estado_':'6','HFUN_Tribunal_':'','HFLG_Envio_':'1'}
    headers=''.join(f'<td>{h}</td>' for h in HEADERS)
    row=''.join(f'<td>{v}</td>' for v in ['Al Tribunal','Cumplimiento','12/08/2026 10:13','Usuario ficticio','Texto recortado','---','---','---'])+'<td><img id="44"></td>'
    # Los campos completos pertenecen a la tabla, tal como en RUS.
    return (
        f'<html><form name="InformesPpalForm" action="/SITFAWEB/InformesDAction.do">'+
        ''.join(f'<input type="hidden" name="{k}" value="{html.escape(v,quote=True)}">' for k,v in fields.items())+
        f'<table id="TablaInforme"><tr>{headers}</tr><tr>{row}</tr>'+''.join(f'<input type="hidden" name="{k}44" value="{html.escape(v,quote=True)}">' for k,v in hidden.items())+'</table></form></html>')

class Bridge(FakeBridge):
    connected=True
    def __init__(self,wrong=False,missing=False):super().__init__(total=2);self.wrong=wrong;self.missing=missing;self.openings=[]
    def call(self,command,payload=None,timeout=75):
        if command=='search':
            result=super().call(command,payload,timeout)
            profile=selection_profile(self.selection,CATALOG)
            source=base64.b64decode(result['body']).decode()
            start=source.index('<table');end=source.index('</table>',start)+8
            from lxml import etree
            table=listing(court=self.selection.tribunal)
            table.set('id',profile.table_id)
            text=etree.tostring(table,encoding='unicode').replace("'200'",f"'{200+self.number}'")
            if self.missing:text=text.replace('ShowObservaciones','MissingObservaciones')
            # TD encabezado y RUT de la pestaña Espera observados en RUS.
            text=text.replace('<th>','<td>').replace('</th>','</td>').replace('>RUT<','>RUT (-&gt;RCeI)<')
            data=(source[:start]+text+source[end:]).encode()
            result['body']=base64.b64encode(data).decode();return result
        if command=='diary_open':
            self.events.append((command,None));params=payload['params'];self.openings.append(params)
            data=popup(params,self.wrong and params['ID_Ingreso']=='202').encode()
            return {'status':200,'type':'text/html','body':base64.b64encode(data).decode(),'digest':hashlib.sha256(data).hexdigest(),
                    'params':params,'startedAt':'2026-10-08T12:00:00Z'}
        return super().call(command,payload,timeout)

def run(tmp_path,bridge,batch=None,resume=None,cancel=None,emit=None):
    parser()
    return DiaryRunner(bridge,CATALOG,emit or (lambda *a:None),cancel or threading.Event()).run(
        batch or Batch(('49',),('2',),('Cumplimiento',)),tmp_path,resume)

def test_four_modalities_all_courts_and_two_tabs(tmp_path):
    bridge=Bridge();result=run(tmp_path,bridge,Batch(tuple(CATALOG['tribunales']),('1','2','3','4'),('Espera','Cumplimiento')))
    data=json.loads(Path(result['manifest']).read_text(encoding='utf-8'))
    assert result['estado']=='COMPLETA' and len(data['registros'])==32
    assert {p['TIP_Consulta'] for p in bridge.openings}=={'1','2','3','4'}
    assert all(q['paginas']==2 for q in data['consultas'])
    assert set(cmd for cmd,_ in bridge.events)<={'lock','unlock','prepare','search','diary_open'}
    assert bridge.events[-1][0]=='unlock'

def test_same_rit_different_ingresos_and_failed_popup(tmp_path):
    bridge=Bridge(wrong=True);result=run(tmp_path,bridge)
    data=json.loads(Path(result['manifest']).read_text(encoding='utf-8'))
    assert [r['ingreso_id'] for r in data['registros']]==['201','202']
    assert result['leidas']==1 and result['fallidas']==1 and result['estado']=='INCOMPLETA'
    bridge=Bridge();recovered=run(tmp_path,bridge,resume=result['folder'])
    assert recovered['leidas']==2 and len(bridge.openings)==1
    assert bridge.openings[0]['ID_Ingreso']=='202'

def test_missing_link_never_invents_get_and_all_rows_counted(tmp_path):
    bridge=Bridge(missing=True);result=run(tmp_path,bridge)
    data=json.loads(Path(result['manifest']).read_text(encoding='utf-8'))
    assert len(data['registros'])==2 and not bridge.openings
    assert all(r['estado']=='SIN_VINCULO' for r in data['registros'])

def test_cancel_and_resume_keeps_verified_copy(tmp_path):
    cancel=threading.Event()
    def emit(name,value):
        if name=='diary_progress':cancel.set()
    result=run(tmp_path,Bridge(),cancel=cancel,emit=emit)
    assert result['estado']=='CANCELADA' and result['leidas']==1
    bridge=Bridge();result=run(tmp_path,bridge,resume=result['folder'])
    assert result['estado']=='COMPLETA' and len(bridge.openings)==1

def test_modified_file_reloaded_on_retry(tmp_path):
    result=run(tmp_path,Bridge());folder=Path(result['folder'])
    next(folder.glob('*.html')).write_text('cambio',encoding='utf-8')
    bridge=Bridge();result=run(tmp_path,bridge,resume=folder)
    # La copia alterada no se reutiliza ni se sobrescribe silenciosamente.
    assert len(bridge.openings)==1 and result['fallidas']==1

def test_previous_reads_preserved_when_reenumeration_fails(tmp_path):
    result=run(tmp_path,Bridge())
    class FailedListing(Bridge):
        def call(self,command,payload=None,timeout=75):
            if command=='search':
                import motor as m
                raise m.PocError('Listado no disponible')
            return super().call(command,payload,timeout)
    result=run(tmp_path,FailedListing(),resume=result['folder'])
    data=json.loads(Path(result['manifest']).read_text(encoding='utf-8'))
    assert result['estado']=='INCOMPLETA' and len(data['anteriores_no_reenumeradas'])==2
    assert not data['registros']
