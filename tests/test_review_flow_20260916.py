from copy import deepcopy

from openpyxl import Workbook, load_workbook

from nurus.personal.config import defaults
from nurus.personal.outputs import Draft
from nurus.personal import runtime_fixes_20260916 as fixes
from nurus.personal import runtime_fixes_20260916_ui as ui_fixes
from nurus.personal.resolutions import automatic_project_selections
from nurus.personal.work import Work, Row


def _espera_book(path):
    book = Workbook()
    sheet = book.active
    sheet.title = 'Espera'
    sheet.append(['RIT','TRIBUNAL','NOMBRE','RUT','DERIVACION','T ESPERA','OBSERVACION'])
    sheet.append(['X-1','Jgdo. L. y G. de Mulchén','NNA UNO','11111111-1','AFT PRUEBA',45,'texto previo'])
    book.save(path)


def test_edit_in_work_is_exported_to_visible_observation(tmp_path):
    source = tmp_path/'entrada.xlsx'
    _espera_book(source)
    work = Work(defaults()).analyze(source,'ESPERA',as_of=None)
    row = work.rows[0]
    row.review['OBSERVACION'] = 'observación humana corregida'
    row.review['RES'] = 'PC_IE'
    target = tmp_path/'salida.xlsx'
    work.export(target,backend='portable',reduced_fidelity=True)
    book = load_workbook(target,data_only=False)
    sheet = book['Espera']
    headers = {str(sheet.cell(1,c).value):c for c in range(1,sheet.max_column+1)}
    assert sheet.cell(2,headers['OBSERVACION']).value == 'observación humana corregida'
    assert sheet.cell(2,headers['RES']).value == 'PC_IE'
    assert sheet.cell(2,headers['NURUS_ESTADO_REVISION']).value == 'REVISADO'
    book.close()


def test_unedited_rows_remain_pending_when_another_row_is_reviewed(tmp_path):
    source = tmp_path/'entrada.xlsx'
    _espera_book(source)
    book = load_workbook(source)
    sheet = book['Espera']
    sheet.append(['X-2','Jgdo. L. y G. de Mulchén','NNA DOS','22222222-2','AFT PRUEBA',45,'original dos'])
    book.save(source);book.close()
    work = Work(defaults()).analyze(source,'ESPERA')
    work.rows[0].review['OBSERVACION'] = 'editada uno'
    target = tmp_path/'salida.xlsx'
    work.export(target,backend='portable',reduced_fidelity=True)
    book = load_workbook(target)
    sheet = book['Espera']
    headers = {str(sheet.cell(1,c).value):c for c in range(1,sheet.max_column+1)}
    assert sheet.cell(2,headers['NURUS_ESTADO_REVISION']).value == 'REVISADO'
    assert sheet.cell(3,headers['NURUS_ESTADO_REVISION']).value == 'PENDIENTE'
    assert sheet.cell(3,headers['OBSERVACION']).value == 'original dos'
    book.close()


def test_export_button_captures_live_editor_before_export(monkeypatch):
    calls=[]
    monkeypatch.setattr(ui_fixes,'_ORIGINAL_EXPORT_CURRENT',lambda self:calls.append('export'))
    dummy=type('Dummy',(),{})()
    dummy._capture_observation=lambda:calls.append('capture')
    ui_fixes.export_current_with_live_edit(dummy)
    assert calls==['capture','export']


def test_draft_identity_changes_when_user_edits_content_recipient_or_attachment(tmp_path):
    attachment = tmp_path/'a.txt';attachment.write_text('uno',encoding='utf-8')
    first = Draft('Asunto','Cuerpo','a@example.cl','ucc_concepcion@pjud.cl',[str(attachment)])
    body_edit = deepcopy(first);body_edit.body = 'Cuerpo corregido'
    recipient_edit = deepcopy(first);recipient_edit.to = 'b@example.cl'
    original = fixes._draft_fingerprint(first)
    assert original != fixes._draft_fingerprint(body_edit)
    assert original != fixes._draft_fingerprint(recipient_edit)
    attachment.write_text('dos',encoding='utf-8')
    assert original != fixes._draft_fingerprint(first)


def test_create_draft_replaces_legacy_key_with_reviewed_content_key(monkeypatch,tmp_path):
    attachment=tmp_path/'a.txt';attachment.write_text('contenido',encoding='utf-8')
    draft=Draft('Asunto','Cuerpo editado','','ucc_concepcion@pjud.cl',[str(attachment)],key='legacy-key')
    captured={}
    def fake(work,item,confirmed=False):
        captured['key']=item.key;captured['confirmed']=confirmed;return 'ok'
    monkeypatch.setattr(fixes,'_ORIGINAL_CREATE_DRAFT',fake)
    assert fixes.create_draft_by_content(object(),draft,confirmed=True)=='ok'
    assert captured['confirmed'] is True
    assert captured['key']!='legacy-key'
    assert captured['key']==fixes._draft_fingerprint(draft)


def _row(rid, observation, actions, res=''):
    return Row(
        rid,2,
        {'RIT':'X-1','TRIBUNAL':'Jgdo. L. y G. de Mulchén','NOMBRE':'NNA','RUT':'11111111-1','DERIVACION':'AFT TEST'},
        observation,[],actions,[],False,
        {'RES':res} if res != '' else {},
    )


def _fake_work(rows):
    work = type('W',(),{})()
    work.rows = rows
    work.mapping = {'rit':'RIT','tribunal':'TRIBUNAL','nombre':'NOMBRE','rut':'RUT','programa':'DERIVACION'}
    return work


def test_resolution_type_comes_from_reviewed_observation_when_res_only_marks_case():
    row = _row('r1','Se remite proyecto de resolución pidiendo cuenta respecto del informe de avance.',['PC_IE'],'X')
    selections = automatic_project_selections(_fake_work([row]),'PC_IE')
    assert selections == [('r1','PC_INFO')]


def test_resolution_type_can_use_short_informe_wording():
    row = _row('r1','Informe vencido; corresponde pedir cuenta.',['PC_IE'],'X')
    selections = automatic_project_selections(_fake_work([row]),'PC_IE')
    assert selections == [('r1','PC_INFO')]


def test_resolution_type_explicit_in_res_wins_over_observation():
    row = _row('r1','Se remite proyecto de resolución pidiendo cuenta respecto del ingreso efectivo.',['PC_IE'],'NOMENCL')
    selections = automatic_project_selections(_fake_work([row]),'PC_IE')
    assert selections == [('r1','NOMENCL')]


def test_nomenclatura_can_be_inferred_from_observation():
    row = _row('r1','Corresponde proyecto de nomenclatura para regularizar la causa.',['PC_IE'],'X')
    selections = automatic_project_selections(_fake_work([row]),'PC_IE')
    assert selections == [('r1','NOMENCL')]


class _Words:
    def __init__(self):
        self.data = {
            'a|PC_IE': ['X-1','MULCHEN','PC_IE','auto'],
            'b|PC_IE': ['X-2','MULCHEN','PC_IE','auto'],
        }
        self.selected = ('a|PC_IE',)
    def selection(self): return self.selected
    def item(self,iid,what): return {'values':self.data[iid]}[what]
    def delete(self,iid): self.data.pop(iid)
    def exists(self,iid): return iid in self.data
    def insert(self,parent,where,iid,values): self.data[iid]=list(values)
    def selection_set(self,items): self.selected=tuple(items)


class _List:
    def delete(self,*args): pass


class _Var:
    def get(self): return 'PC_INFO'


class _Status:
    def set(self,value): self.value=value


def test_individual_resolution_type_edit_changes_only_selected_row():
    from nurus.personal.app_base import App
    dummy = type('Dummy',(),{})()
    dummy.words = _Words();dummy.manual_word = _Var();dummy.projects=['old'];dummy.project_index=0;dummy.project_list=_List();dummy.status=_Status()
    App._assign_word_type(dummy)
    assert 'a|PC_INFO' in dummy.words.data
    assert 'b|PC_IE' in dummy.words.data
    assert 'b|PC_INFO' not in dummy.words.data
