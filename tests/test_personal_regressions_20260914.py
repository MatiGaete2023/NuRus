from openpyxl import Workbook

from nurus.personal.config import defaults
from nurus.personal.modalities import modality
from nurus.personal.work import Work


def test_fas_is_family_foster_care_not_ambulatory():
    assert modality('FAS EJEMPLO') == 'FAE'
    assert modality('FAE EJEMPLO') == 'FAE'


def test_reviewed_waiting_sheet_keeps_requested_mode_with_due_date_column(tmp_path):
    book=Workbook();sheet=book.active;sheet.title='Registros'
    sheet.append(['RIT','TRIBUNAL','NOMBRE','RUT','PROGRAMA','T ESPERA','FECHA VENCIMIENTO','OBSERVACION'])
    sheet.append(['X-1-2026','LAJA','Persona Uno','11111111-1','AFT EJEMPLO',45,'30/09/2026','Texto humano'])
    path=tmp_path/'observaciones_modificadas.xlsx';book.save(path)
    work=Work.external(path,defaults(),mode='ESPERA')
    assert work.mode=='ESPERA'
    assert work.rows[0].review['OBSERVACION']=='Texto humano'
