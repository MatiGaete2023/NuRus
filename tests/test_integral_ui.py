"""Each GUI scenario owns its process and Tcl interpreter, like a CSMP launch."""
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).parents[1]


def run_gui(tmp_path, scenario):
    environment=dict(os.environ,PYTHONPATH=os.pathsep.join([str(ROOT/'src'),str(ROOT/'tests'),*sys.path]))
    script='''
from datetime import date
from pathlib import Path
import sys
from nurus.personal.config import Configuration
from nurus.personal.app import App
from nurus.personal.work import Work
from current_fixture import source
root=Path(sys.argv[1])
app=App(Configuration(root/'config'))
app.geometry('1024x650')
try:
'''+''.join('    '+line+'\n' for line in scenario.splitlines())+'''
finally:
    app.destroy()
'''
    result=subprocess.run([sys.executable,'-c',script,str(tmp_path)],env=environment,
                          capture_output=True,text=True,timeout=45)
    assert result.returncode==0,result.stdout+'\n'+result.stderr


def test_current_results_and_manual_editors_are_reachable(tmp_path):
    run_gui(tmp_path,"""
app.tabs.select(app.pages['Resultados']);app.update()
assert set(app.pages)=={'Trabajo','Correos','Resoluciones','Resultados','Configuración'}
assert app.results_download_button.winfo_exists()
from nurus.personal.manual import open_editor
open_editor(app,'mail');open_editor(app,'word');app.update()
""")


def test_hidden_selection_and_view_preferences_survive_refresh(tmp_path):
    run_gui(tmp_path,"""
app.work=Work(app.cfg.data).analyze(source(root),'ESPERA',as_of=date(2026,10,2));app._show_work()
id=app.work.rows[0].id
app.records.selection_set(id);app.work_search.set('no coincidencia');app._apply_work_filter();app.update()
from nurus.personal.selection import selected_ids
assert id in selected_ids(app,'records')
app._show_work();app.update();from nurus.personal.selection import selected_ids
assert id in selected_ids(app,'records')
app.records.configure(displaycolumns=('Nombre','RIT'));app.work_search.set('');app._apply_work_filter()
assert tuple(app.records['displaycolumns'])==('Nombre','RIT')
""")
