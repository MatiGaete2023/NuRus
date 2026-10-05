from datetime import date
from openpyxl import load_workbook
import pytest
from nurus.personal.config import defaults
from nurus.personal.work import Work
from nurus.personal.reports import export_management,export_activity
from nurus.personal.rus_activity import mark_reviewed
from test_rus_activity import source


def test_historical_excel_is_never_counted_as_new_registration(tmp_path):
    work=Work(defaults()).analyze(source(tmp_path),'ESPERA',as_of=date(2026,10,2))
    work.rows[0].review={'OBSERVACION':'Constancia histórica','FECHA_OBS':'2026-10-01','TT':1,'CC':1}
    work.receipts={'draft':dict(kind='draft',state='created',created_at='2026-10-02T09:00:00'),
        'uncertain':dict(kind='rus_observation',state='INCIERTA',verified=False,operation_id='u'),
        'verified':dict(kind='rus_observation',state='PENDIENTE_EXCEL',verified=True,new_registration=True,operation_id='op-1',
            registered_at='2026-10-02T10:00:00',remote_entry_id='12',type='Al Tribunal',cc=1,text='Texto guardado')}
    path=export_management([work,work],tmp_path/'gestion.xlsx',date(2026,10,1),date(2026,10,5))
    book=load_workbook(path);counts=dict(book['Resumen'].values)
    assert counts['Observaciones nuevas comprobadas']==1
    assert counts['Constancias históricas del Excel']==1
    assert counts['Nuevas con carga']==1
    assert book['Nuevas comprobadas'].max_row==2
    book.close()
    work.receipts['verified']['cc']=0
    with pytest.raises(ValueError):export_management([work],tmp_path/'wrong.xlsx',date(2026,10,1),date(2026,10,5))


def test_resolution_report_keeps_per_ingreso_and_partial_coverage(tmp_path):
    work=Work(defaults()).analyze(source(tmp_path),'ESPERA',as_of=date(2026,10,2))
    mark_reviewed(work,work.rows[0].id,'firma-1')
    path=export_activity([work,work],tmp_path/'firmas.xlsx');book=load_workbook(path)
    assert book['Firmas por ingreso'].max_row==5
    counts=dict(book['Resumen'].values)
    assert counts['Revisadas para el ingreso']==1 and counts['Por revisar']==3
    assert all(r[4]=='PARCIAL' for r in list(book['Cobertura'].values)[1:])
    book.close()
