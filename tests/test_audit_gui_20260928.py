"""Real isolated windows: no Office invocation and no personal files."""
import os
from dataclasses import asdict

import pytest

pytestmark=pytest.mark.skipif(os.name!='nt',reason='Windows GUI contract')


def test_full_session_and_contextual_fields_recover(tmp_path):
    from nurus.personal.app import App
    from nurus.personal.config import Configuration, BASE
    from nurus.personal.outputs import prepare_drafts
    from nurus.personal.resolutions import prepare_projects, automatic_project_selections
    from test_audit_integrity_20260928 import source
    work=source(tmp_path/'original.xlsx')
    cfg=Configuration(tmp_path/'profile')
    app=App(cfg)
    try:
        app.work=work
        app._show_work()
        app.records.selection_set(work.rows[0].id);app._detail()
        form=app.record_form
        form.review['FECHA_OBS'].set('28/09/2026')
        form.review['TT'].set('0');form.review['CC'].set('1')
        form.resolution.set('NOMENCL')
        form.word['DURACION'].set('noventa días')
        form.capture()
        app._show_work()
        drafts=prepare_drafts(work,'programa_espera')
        app._display_prepared_drafts(drafts,'{count} preparados')
        app.body.insert('end','\nEdición personal del correo')
        projects,errors=prepare_projects(work,automatic_project_selections(work),BASE/'plantillas_word')
        assert not errors
        app.projects=projects;app.project_list.delete(0,'end')
        for p in projects:app.project_list.insert('end',p.rit)
        app.project_list.selection_set(0);app._select_project()
        app.project_editor.insert('end','\nEdición personal del proyecto')
        app._save_session()
        expected_drafts=[asdict(item) for item in app.drafts]
        expected_projects=[asdict(item) for item in app.projects]
    finally:app.destroy()
    reopened=App(cfg)
    try:
        reopened._continue_resume()
        assert [asdict(item) for item in reopened.drafts]==expected_drafts
        assert [asdict(item) for item in reopened.projects]==expected_projects
        row=reopened.work.rows[0]
        assert row.review['TT']==0 and row.review['CC']==1
        assert row.word_overrides['DURACION']=='noventa días'
        assert (row.id,'NOMENCL') in automatic_project_selections(reopened.work)
    finally:reopened.destroy()


@pytest.mark.parametrize('size',['1024x650','1180x820'])
def test_editors_and_actions_fit_without_detail_overlap(tmp_path,size):
    # Each launch owns its Tcl interpreter, like a real application process.
    import subprocess
    import sys
    environment=dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
    script='from pathlib import Path; import sys; from test_audit_gui_20260928 import _layout_probe; _layout_probe(Path(sys.argv[1]),sys.argv[2])'
    result=subprocess.run([sys.executable,'-c',script,str(tmp_path),size],env=environment,capture_output=True,text=True,timeout=45)
    assert result.returncode==0,result.stdout+'\n'+result.stderr


def _layout_probe(tmp_path,size):
    from nurus.personal.app import App
    from nurus.personal.config import Configuration
    from nurus.personal.outputs import Draft
    from test_audit_integrity_20260928 import source
    app=App(Configuration(tmp_path/'profile'))
    try:
        app.work=source(tmp_path/'original.xlsx')
        app._show_work();app.geometry(size)
        app.tabs.select(app.pages['Trabajo'])
        app.update_idletasks();app.update()
        app.records.selection_set(app.work.rows[0].id);app._detail()
        app.update_idletasks();app.update()
        assert app.observation_editor.winfo_ismapped()
        assert app.observation_editor.winfo_height()>=120
        app.tabs.select(app.pages['Correos'])
        app._display_prepared_drafts([Draft('Asunto','Texto\n'*40,program='Programa')],'{count} preparados')
        app.update_idletasks();app.update()
        assert app.body.winfo_height()>=120
        for widget in (app.body,app.save_all_button):
            assert widget.winfo_rooty()+widget.winfo_height()<=app.winfo_rooty()+app.winfo_height()
    finally:app.destroy()

