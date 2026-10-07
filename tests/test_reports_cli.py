from datetime import date
import os
from pathlib import Path
import subprocess
import sys

from openpyxl import load_workbook
import pytest

from nurus.personal.config import defaults
from nurus.personal.work import Work
from test_rus_activity import source


def cli(*arguments):
    root = Path(__file__).parents[1]
    environment = dict(os.environ, PYTHONPATH=os.pathsep.join([str(root/'src'), *sys.path]))
    return subprocess.run([sys.executable, '-m', 'nurus.personal.reports', *map(str, arguments)],
                          env=environment, capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize('kind', ['firmas', 'gestion'])
def test_standalone_report_uses_explicit_period(tmp_path, kind):
    work = Work(defaults()).analyze(source(tmp_path), 'ESPERA', as_of=date(2026, 10, 2))
    work.save(tmp_path/'session')
    target = tmp_path/(kind+'.xlsx')
    result = cli(kind, '--trabajo', tmp_path/'session', '--salida', target,
                 '--desde', '2026-10-01', '--hasta', '2026-10-02')
    assert result.returncode == 0, result.stderr
    book = load_workbook(target)
    try:
        summary = dict(book['Resumen'].values)
        if kind == 'firmas':
            assert summary['Período solicitado desde'] == '2026-10-01'
            assert summary['Período solicitado hasta'] == '2026-10-02'
            assert all('2026-10-01' <= row[4] <= '2026-10-02' for row in list(book['Firmas por ingreso'].values)[1:])
        else:
            assert summary['Desde'] == '2026-10-01'
            assert summary['Hasta'] == '2026-10-02'
    finally:
        book.close()


@pytest.mark.parametrize('kind', ['firmas', 'gestion'])
def test_standalone_report_requires_dates_before_loading_work(tmp_path, kind):
    target = tmp_path/'report.xlsx'
    result = cli(kind, '--trabajo', tmp_path/'absent', '--salida', target)
    assert result.returncode == 2
    assert '--desde' in result.stderr and '--hasta' in result.stderr
    assert 'Traceback' not in result.stderr
    assert not target.exists()


def test_reversed_period_is_explained_before_loading_work(tmp_path):
    target = tmp_path/'report.xlsx'
    result = cli('firmas', '--trabajo', tmp_path/'absent', '--salida', target,
                 '--desde', '2026-10-02', '--hasta', '2026-10-01')
    assert result.returncode == 2
    assert 'Traceback' not in result.stderr
    assert not target.exists()
