from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
from zipfile import ZipFile
import json
import pytest
from openpyxl import Workbook,load_workbook
from docx import Document
from nurus.personal.config import defaults,Configuration,BASE,CC
from nurus.personal.work import Work
from nurus.personal.importing import SheetChoice
from nurus.personal.outputs import prepare_drafts,create_drafts,Draft
from nurus.personal.resolutions import prepare_projects,generate_projects,replace_paragraph
from nurus.personal.template_package import import_templates

def external(tmp_path,rows=None):
    book=Workbook();book.active.title='Portada';book.active['A1']='REPORTE'
    sheet=book.create_sheet('Registros');sheet.append(['Reporte mensual']);sheet.append([])
    sheet.append(['RIT','TRIBUNAL','NOMBRE MENOR','RUT MENOR','NOMBRE CENTRO','Observaciones','FECHA_OBS','TT','CC'])
    for row in rows or [
        ['X-1-2026','LAJA','Persona Uno','11111111-1','AFT EJEMPLO','Se remite proyecto.','2026-09-14',1,0],
        ['X-1-2026','LAJA','Persona Dos','22222222-2','AFT EJEMPLO','Texto humano.','2026-09-14',1,1],
        ['X-2-2026','LAJA','Persona Tres','33333333-3','FAE EJEMPLO','Constancia.','2026-09-14',1,0],
    ]:sheet.append(row)
    path=tmp_path/'revisado.xlsx';book.save(path)
    return Work.external(path,defaults())

def test_headers_offset_other_sheet_aliases_and_human_review(tmp_path):
    work=external(tmp_path)
    assert work.sheet=='Registros' and work.header==3 and len(work.rows)==3
    assert work.rows[1].review['OBSERVACION']=='Texto humano.'
    assert work.rows[1].review['CC']==1
    book=load_workbook(work.output);book['Registros']['F5']='Edición posterior';book.save(work.output)
    assert work.refresh()
    assert work.rows[1].review['OBSERVACION']=='Edición posterior'

def test_multiple_tables_request_only_actual_sheet_choice(tmp_path):
    work=external(tmp_path);book=load_workbook(work.output);book.copy_worksheet(book['Registros']).title='Otra';book.save(work.output)
    with pytest.raises(SheetChoice):Work.external(work.output,defaults())
    assert Work.external(work.output,defaults(),sheet='Otra').sheet=='Otra'

def test_modalities_filter_and_program_attachment_names(tmp_path):
    work=external(tmp_path)
    drafts=prepare_drafts(work,'programa_espera',modality_keys=['FAE'])
    assert len(drafts)==1
    assert Path(drafts[0].attachments[0]).name=='FAE EJEMPLO.xlsx'
    sheet=load_workbook(drafts[0].attachments[0]).active
    assert sheet.max_row==2 and sheet['D2'].value=='Persona Tres'
    all_drafts=prepare_drafts(work,'programa_espera')
    assert len(all_drafts)==2

def test_batch_save_empty_to_and_partial_failure_do_not_duplicate(tmp_path,monkeypatch):
    work=external(tmp_path);seen=[]
    def save(product,**kwargs):
        seen.append(product)
        if product.rendered_subject=='Falla':raise ValueError('Error de prueba')
        return SimpleNamespace(entry_id='e',store_id='s')
    monkeypatch.setattr('nurus.personal.outputs.save_draft',save)
    drafts=[Draft('Uno','Texto',key='a'),Draft('Falla','Texto',key='b'),Draft('Tres','Texto',key='c')]
    result=create_drafts(work,drafts)
    assert result['created']==2 and len(result['errors'])==1 and all(CC in p.cc for p in seen)
    assert seen[0].recipient==''
    again=create_drafts(work,drafts)
    assert again['created']==0 and again['skipped']==2 and len(seen)==4

def test_migration_restores_old_defaults_and_preserves_customizations(tmp_path):
    conf=Configuration(tmp_path/'config');cfg=deepcopy(conf.data);cfg.pop('revision_textos',None)
    original=cfg['textos']['ESPERA']['E05_PROYECTO_Y_CORREO']['texto']
    cfg['textos']['ESPERA']['E05_PROYECTO_Y_CORREO']['texto']=original.replace('Se remite proyecto de resolución','Se sugiere preparar proyecto de resolución').replace('se remite correo electrónico','se sugiere remitir correo electrónico').replace('Se remite correo electrónico','Se sugiere remitir correo electrónico')
    cfg['textos']['ESPERA']['E05_SOLO_CORREO']['texto']='Mi texto personalizado.'
    conf.save(cfg);updated=Configuration(conf.directory)
    assert updated.data['textos']['ESPERA']['E05_PROYECTO_Y_CORREO']['texto']==original
    assert updated.data['textos']['ESPERA']['E05_SOLO_CORREO']['texto']=='Mi texto personalizado.'
    assert updated.path.with_suffix('.bak').exists()

def test_single_word_groups_people_and_starts_next_project_on_new_page(tmp_path):
    work=external(tmp_path)
    projects,errors=prepare_projects(work,[(r.id,'PC_IE') for r in work.rows],BASE/'plantillas_word')
    assert not errors and len(projects)==2
    assert len(projects[0].record_ids)==2
    assert 'Persona Uno' in projects[0].text and 'Persona Dos' in projects[0].text
    assert '11111111-1' in projects[0].text and '22222222-2' in projects[0].text
    projects[0].text+='\nPárrafo incorporado por el usuario.'
    path=tmp_path/'Resoluciones.docx';generate_projects(work,projects,path)
    doc=Document(path);text='\n'.join(p.text for p in doc.paragraphs)
    assert 'Párrafo incorporado por el usuario.' in text
    assert text.count('RIT: X-1-2026')==1
    assert text.count('RIT: X-2-2026')==1
    assert 'w:type="page"' in doc.element.xml
    assert len(list(tmp_path.glob('*.docx')))==1

def test_manual_type_and_missing_data_produce_editable_project(tmp_path):
    work=external(tmp_path)
    projects,errors=prepare_projects(work,[(work.rows[0].id,'NOMENCL')],BASE/'plantillas_word')
    assert not errors and projects[0].kind=='NOMENCL'
    assert '[COMPLETAR NOMENCLATURA]' in projects[0].text

def test_same_rit_different_court_does_not_merge(tmp_path):
    work=external(tmp_path);work.rows[1].values[work.mapping['tribunal']]='MULCHEN'
    projects,errors=prepare_projects(work,[(r.id,'PC_IE') for r in work.rows[:2]],BASE/'plantillas_word')
    assert not errors and len(projects)==2

def test_edit_preserves_unchanged_bold_runs():
    doc=Document();p=doc.add_paragraph();p.add_run('RIT: ').bold=True;p.add_run('X-1')
    replace_paragraph(p,'RIT: X-2')
    assert p.text=='RIT: X-2' and p.runs[0].bold

def test_zip_import_known_names_preserves_backup_and_rejects_ambiguous(tmp_path):
    package=tmp_path/'matrices.zip';source=BASE/'plantillas_word/LAJA/PC_IE.docx'
    with ZipFile(package,'w') as z:
        z.write(source,'plantillas_word/LAJA/PC_IE.docx')
        z.write(source,'sin_identificar.docx')
    directory=tmp_path/'matrices';result=import_templates(package,directory)
    assert len(result['imported'])==1 and result['unmatched']==['sin_identificar.docx']
    import_templates(package,directory)
    assert (directory/'LAJA/PC_IE.bak.docx').exists()

def test_summary_counts_one_document_and_two_projects(tmp_path):
    from nurus.personal.statistics import summarize
    work=external(tmp_path);projects,_=prepare_projects(work,[(r.id,'PC_IE') for r in work.rows],BASE/'plantillas_word')
    generate_projects(work,projects,tmp_path/'lote.docx')
    counts=summarize(work)
    assert counts['word_generados']==1 and counts['proyectos_generados']==2
