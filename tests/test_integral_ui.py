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
from test_rus_activity import source
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


def test_firmas_window_can_review_one_ingreso_at_small_size(tmp_path):
    run_gui(tmp_path,'''
app.work=Work(app.cfg.data).analyze(source(root),'ESPERA',as_of=date(2026,10,2))
app._show_work()
app.records.selection_set(app.work.rows[0].id)
window=app._open_signed_activity()
app.update()
assert window.winfo_exists()
assert window.winfo_width()>=800
window.destroy()
assert all(not row.review for row in app.work.rows)
''')


def test_results_return_is_reachable_at_small_windows_size(tmp_path):
    run_gui(tmp_path,'''
app.tabs.select(app.pages['Resultados'])
app.update()
canvas=app.results_scrollpane.body._parent_canvas
canvas.yview_moveto(1)
app.update()
for button in (app.results_return_button,app.results_download_button):
    assert button.winfo_ismapped()
    assert button.winfo_rooty()>=app.winfo_rooty()
    assert button.winfo_rooty()+button.winfo_height()<=app.winfo_rooty()+app.winfo_height()
''')
