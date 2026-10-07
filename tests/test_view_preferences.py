"""Preferences survive restarts, reject unsafe imports and preserve prior views."""
from copy import deepcopy
import json
from unittest.mock import patch

import pytest

from nurus.personal.view_preferences import Preferences, TABLES, validate_state, fit_geometry


def state():
    return dict(filters=dict(work_search='', work_filter='Todos', resolution_search='', resolution_filter='Todos'),
                tables={name: dict(visible=list(columns), widths={col: 140 for col in columns}) for name, columns in TABLES.items()},
                font_size=13, page='Trabajo', geometry=dict(width=1024, height=650, x=30, y=40, maximized=False),
                split=dict(work_sash_ratio=.4, resolution_sash_ratio=.45))


def test_saved_views_and_previous_state_survive_restart(tmp_path):
    prefs = Preferences(tmp_path)
    first = state()
    prefs.remember(first)
    second = deepcopy(first)
    second['tables']['records']['visible'] = ['Tribunal', 'RIT']
    second['tables']['records']['widths']['RIT'] = 230
    second['font_size'] = 18
    second['filters']['work_filter'] = 'Con aviso'
    prefs.save_preset('Revisión', second)
    prefs.remember(second)
    prefs.remember(second, keep_previous=True)
    loaded = Preferences(tmp_path)
    assert loaded.data['previous'] == first
    assert loaded.data['current'] == second
    assert loaded.data['presets']['Revisión'] == second
    loaded.remember(first)
    assert Preferences(tmp_path).data['previous'] == second


@pytest.mark.parametrize('change', [
    lambda v: v['tables']['records'].update(visible=[]),
    lambda v: v['tables']['records'].update(visible=['RIT', 'RIT']),
    lambda v: v['tables']['records'].update(visible=['RIT', 'ejecutar']),
    lambda v: v['tables']['records']['widths'].update(RIT=-1),
    lambda v: v.update(font_size=True),
    lambda v: v.update(font_size=100),
    lambda v: v.update(page='Tribunal inventado'),
    lambda v: v['filters'].update(work_filter='Guardar en RUS'),
    lambda v: v['split'].update(work_sash_ratio=float('nan')),
    lambda v: v.update(records=[{'rit': 'X-123'}]),
])
def test_invalid_import_never_mutates_existing_preferences(tmp_path, change):
    prefs = Preferences(tmp_path)
    prefs.remember(state())
    original = prefs.path.read_bytes()
    invalid = state()
    change(invalid)
    packet = dict(kind='csmp-view', version=1, name='Otra vista', state=invalid)
    incoming = tmp_path / 'incoming.json'
    incoming.write_text(json.dumps(packet), encoding='utf-8')
    with pytest.raises(ValueError):
        prefs.import_preset(incoming)
    assert prefs.path.read_bytes() == original
    assert prefs.data['presets'] == {}


def test_portable_file_round_trip_does_not_overwrite_named_view(tmp_path):
    source = Preferences(tmp_path / 'one')
    packet = tmp_path / 'portable.json'
    source.export_preset(packet, 'Mi vista', state())
    target = Preferences(tmp_path / 'two')
    assert target.import_preset(packet) == 'Mi vista'
    assert target.data['presets']['Mi vista'] == state()
    original = target.path.read_bytes()
    with pytest.raises(ValueError, match='nombre'):
        target.import_preset(packet)
    assert target.path.read_bytes() == original
    with pytest.raises(ValueError, match='existe'):
        source.export_preset(packet, 'Mi vista', state())


def test_failed_atomic_save_retains_disk_and_memory_state(tmp_path):
    prefs = Preferences(tmp_path)
    prefs.remember(state())
    original = prefs.path.read_bytes()
    current = deepcopy(prefs.data)
    changed = state()
    changed['font_size'] = 18
    with patch('nurus.personal.view_preferences.Path.replace', side_effect=OSError('disk full')):
        with pytest.raises(OSError):
            prefs.remember(changed)
    assert prefs.path.read_bytes() == original
    assert prefs.data == current
    assert not list(tmp_path.glob('*.part'))


def test_offscreen_portable_window_is_reachable_on_smaller_display():
    geometry = dict(width=3000, height=2000, x=-2800, y=5000, maximized=True)
    assert fit_geometry(geometry, 1024, 720) == '1024x720+0+0'
    assert fit_geometry(dict(geometry, width=500, height=350, x=0, y=0), 640, 480) == '640x480+0+0'


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path / 'incoming.json'
    path.write_text('{"kind":"csmp-view","kind":"other"}', encoding='utf-8')
    with pytest.raises(ValueError, match='repetidas'):
        Preferences(tmp_path).import_preset(path)


def test_validated_states_are_owned_copies():
    original = state()
    result = validate_state(original)
    result['tables']['records']['visible'].pop()
    assert result != original
