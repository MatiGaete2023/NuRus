import os
from pathlib import Path
import subprocess
import sys


def run_gui(tmp_path, scenario):
    root = Path(__file__).parents[1]
    environment = dict(os.environ, PYTHONPATH=os.pathsep.join([str(root/'src'), str(root/'tests'), *sys.path]))
    script = '''
from pathlib import Path
import sys
from nurus.personal.config import Configuration
from nurus.personal.app import App
root=Path(sys.argv[1])
app=App(Configuration(root/'config'))
try:
''' + ''.join('    '+line+'\n' for line in scenario.splitlines()) + '''
finally:
    app.destroy()
'''
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path)], env=environment,
                            capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stdout+'\n'+result.stderr


def test_layout_filters_and_previous_view_survive_restart(tmp_path):
    run_gui(tmp_path, '''
app.geometry('1024x650')
app.update()
controller=app.view_preferences
initial=controller.capture()
changed=controller.capture()
changed['tables']['records']['visible']=['Tribunal','RIT','Nombre']
changed['tables']['records']['widths']['RIT']=230
changed['filters']['work_filter']='Con aviso'
changed['font_size']=18
changed['geometry'].update(width=1050,height=620)
controller.apply(changed)
app.update()
controller.save_current()
assert controller.store.data['previous']==initial
''')
    run_gui(tmp_path, '''
app.update()
controller=app.view_preferences
initial=controller.store.data['previous']
assert tuple(app.records.cget('displaycolumns'))==('Tribunal','RIT','Nombre')
assert app.records.column('RIT','width')==230
assert app.work_filter.get()=='Con aviso'
assert controller.font_size==18
expected=f'{min(1050,app.winfo_screenwidth())}x{min(620,app.winfo_screenheight())}'
assert app.geometry().split('+')[0]==expected,app.geometry()
controller.restore_previous()
assert tuple(app.records.cget('displaycolumns'))==tuple(initial['tables']['records']['visible'])
assert controller.font_size==initial['font_size']
assert controller.store.data['previous']['font_size']==18
''')


def test_hidden_record_selection_is_preserved_by_view_application(tmp_path):
    run_gui(tmp_path, '''
app.update()
app.records.insert('', 'end', iid='selected', values=('','X-123','Persona','','',''))
app.records.insert('', 'end', iid='other', values=('','X-456','Otra persona','','',''))
app._work_all_iids=['selected','other']
app.records.selection_set('selected')
changed=app.view_preferences.capture()
changed['filters']['work_search']='Otra persona'
app.view_preferences.apply(changed)
assert app._selected_work_ids()==('selected',)
assert 'selected' not in app.records.get_children()
changed['filters']['work_search']=''
app.view_preferences.apply(changed)
assert app.records.selection()==('selected',)
assert 'selected' in app.records.get_children()
''')


def test_invalid_preset_changes_no_widget(tmp_path):
    run_gui(tmp_path, '''
app.update()
before=app.view_preferences.capture()
broken=app.view_preferences.capture()
broken['tables']['records']['visible']=['invalid']
try:
    app.view_preferences.apply(broken)
except ValueError:
    pass
else:
    raise AssertionError('Invalid preset accepted')
assert app.view_preferences.capture()==before
assert not app.view_preferences.store.path.exists()
''')


def test_close_persists_view_without_an_active_case(tmp_path):
    run_gui(tmp_path, '''
app.update()
app.records.column('RIT',width=270,stretch=False)
app.work_filter.set('Con aviso')
app.destroy=lambda:None
app._close()
assert app.view_preferences.store.path.is_file()
from nurus.personal.view_preferences import Preferences
saved=Preferences(app.cfg.directory).data['current']
assert saved['tables']['records']['widths']['RIT']==270
assert saved['filters']['work_filter']=='Con aviso'
''')


def test_hidden_selection_survives_session_capture_and_restore(tmp_path):
    run_gui(tmp_path, '''
from datetime import date
from nurus.personal.work import Work
from nurus.personal.session import capture,restore
from test_rus_activity import source
app.work=Work(app.cfg.data).analyze(source(root),'ESPERA',as_of=date(2026,10,2))
app._show_work()
rid=app.work.rows[0].id
app.records.selection_set(rid)
app.work_search.set('This search hides all rows')
assert not app.records.get_children()
capture(app)
assert app.work.session['preferences']['records']==[rid]
app._hidden_work_selection=set()
restore(app)
app.work_search.set('')
assert app.records.selection()==(rid,)
''')
