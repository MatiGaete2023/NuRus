from dataclasses import replace
from datetime import date
from openpyxl import load_workbook
import pytest

from nurus.personal.bitacoras import Observation,earliest,analyze,cc_for_type,export_audit


TODAY=date(2026,10,5);START=date(2026,6,5)
def entry(id='1',fecha='2026-10-01T09:00:00',**extra):
    values=dict(tribunal_codigo='777',causa_id='100',ingreso_id='200',entry_id=id,fecha=fecha,
      autor='Autor ficticio',tipo='Al Tribunal',etapa='Cumplimiento',texto='Consulta ficticia de un informe pendiente.',
      origen='centro',fuente='captura-1',fila_fuente=1)
    return Observation(**{**values,**extra})


def test_four_calendar_months_and_no_older_fallback():
    assert earliest(date(2026,6,30))==date(2026,2,28)
    with pytest.raises(ValueError):analyze([],date(2026,6,4),TODAY,today=TODAY)
    old=entry(fecha='2026-06-04T15:00:00')
    result=analyze([old],START,TODAY,today=TODAY,coverage='COMPLETA')
    assert result['entries']==[] and result['latest_center']==[]
    at_limit=entry(fecha='2026-06-05T00:00:00')
    assert analyze([at_limit],START,TODAY,today=TODAY)['latest_center']==[at_limit]


def test_last_center_any_author_and_date_ties_kept():
    one=entry();two=entry('2',autor='Otro autor')
    tribunal=entry('3',fecha='2026-10-04T15:00:00',origen='tribunal')
    result=analyze([one,two,tribunal],START,TODAY,today=TODAY)
    assert result['latest_center']==[one,two]
    assert analyze([one,two],START,TODAY,today=TODAY,author='Otro autor')['latest_center']==[two]


def test_type_charge_and_response_uncertainty_are_separate(tmp_path):
    assert cc_for_type('Al Tribunal')==1
    assert cc_for_type('Administrativa')==0
    assert cc_for_type('Comentario con carga') is None
    from nurus.personal.bitacoras import response_state
    assert 'no comprobable' in response_state(entry())
    assert response_state(entry(respuesta_comprobada=True))=='Sin respuesta registrada'
    assert response_state(entry(respuesta_comprobada=True,respuesta='Respuesta ficticia'))=='Respuesta registrada'
    assert 'no exige' in response_state(entry(tipo='Administrativa'))


def test_same_remote_entry_from_two_tabs_counted_once_real_repetitions_kept():
    one=entry();copy=replace(one,fuente='otra-pestaña',fila_fuente=99);repeat=entry('2',fecha='2026-10-02T10:00:00')
    result=analyze([one,copy,repeat],START,TODAY,today=TODAY)
    assert len(result['entries'])==2 and len(result['repeated'])==2
    with pytest.raises(ValueError):analyze([one,replace(copy,texto='Contenido diferente')],START,TODAY,today=TODAY)
    local=replace(one,entry_id='')
    assert len(analyze([local,replace(local,fila_fuente=2)],START,TODAY,today=TODAY)['entries'])==2
    with pytest.raises(ValueError):analyze([one,replace(repeat,ingreso_id='300')],START,TODAY,today=TODAY)


def test_audit_keeps_failed_queries_full_text_and_date_incidence(tmp_path):
    known=entry(texto='=Texto externo\n'+('detalle completo '*150))
    invalid=entry('2',fecha='fecha ilegible')
    queries=[dict(tribunal_codigo='777',causa_id='100',ingreso_id='200',rit='X-1-2026',
        entries=[known,invalid],coverage='COMPLETA'),
        dict(tribunal_codigo='888',causa_id='300',ingreso_id='400',entries=[],coverage='FALLIDA',error='Sesión vencida')]
    path=export_audit(queries,tmp_path/'auditoria.xlsx',START,TODAY,today=TODAY)
    book=load_workbook(path)
    assert book['Resumen'].max_row==3
    assert book['Resumen']['E2'].value=='PARCIAL'
    assert book['Resumen']['E3'].value=='FALLIDA'
    assert book['Bitácoras']['L2'].value==known.texto
    assert book['Bitácoras']['L2'].data_type=='s'
    assert book['Bitácoras']['I2'].value==1
    assert book['Bitácoras']['A2'].border.left.style=='thin'
    assert book['Incidencias'].max_row==4
    book.close()
