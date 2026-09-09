from hashlib import sha256

import pytest
from openpyxl import Workbook

from nurus.rus.models import Mode
from nurus.rus.reader import read_workbook, WorkbookReadError


def make_book(path, names):
    book = Workbook()
    book.remove(book.active)
    for name in names:
        sheet = book.create_sheet(name)
        sheet.append(["RIT", "TRIBUNAL", "DERIVACION"])
        sheet.append(["X-1", "Juzgado de Laja", "PRM Prueba"])
    book.save(path)


@pytest.mark.parametrize("mode,title", [
    (Mode.ESPERA, "Espera"),
    (Mode.CUMPLIMIENTO, "Cumplimiento"),
    (Mode.INFORMES, "Informes"),
])
def test_mode_selects_its_sheet_and_preserves_source(tmp_path, mode, title):
    path = tmp_path / "multi.xlsx"
    make_book(path, ["OB", "Espera", "Cumplimiento", "Informes", "Medidas vencidas"])
    original = path.read_bytes()
    result = read_workbook(path, mode)
    assert result.primary_sheet == title
    assert result.records[0].source.sheet_name == title
    assert result.records[0].source.row_number == 2
    assert result.workbook_sha256 == sha256(original).hexdigest()
    assert path.read_bytes() == original


def test_unnamed_multisheet_requires_explicit_selection(tmp_path):
    path = tmp_path / "unknown.xlsx"
    make_book(path, ["Primera", "Segunda"])
    with pytest.raises(WorkbookReadError, match="explícitamente"):
        read_workbook(path, Mode.ESPERA)
    assert read_workbook(path, Mode.ESPERA, sheet_name="Segunda").primary_sheet == "Segunda"


@pytest.mark.parametrize("name", ["OB", "Medidas vencidas"])
def test_excluded_sheet_cannot_be_explicit_primary(tmp_path, name):
    path = tmp_path / "excluded.xlsx"
    make_book(path, [name])
    with pytest.raises(WorkbookReadError, match="no se procesan"):
        read_workbook(path, Mode.ESPERA, sheet_name=name)


def test_single_unnamed_sheet_remains_supported(tmp_path):
    path = tmp_path / "single.xlsx"
    make_book(path, ["Hoja1"])
    assert read_workbook(path, Mode.ESPERA).primary_sheet == "Hoja1"


def test_autodetects_displaced_header_and_preserves_physical_rows(tmp_path):
    path = tmp_path / "displaced.xlsx"
    book = Workbook()
    sheet = book.active
    sheet.title = "informe_1"
    for _ in range(13):
        sheet.append(["REPORTE DE CUMPLIMIENTO"])
    sheet.append([
        "RIT", "TRIBUNAL", "RUT", "NOMBRE", "DERIVACIÓN",
        "DÍAS DE CUMPLIMIENTO", "DÍAS PARA EGRESAR",
    ])
    sheet.append([
        "X-1-2026", "Jgdo. L. y G. de Laja", "11.111.111-1", "NNA Prueba",
        "PRM Prueba", 120, 60,
    ])
    book.save(path)

    result = read_workbook(path, Mode.CUMPLIMIENTO)

    assert result.header_row == 14
    assert result.records[0].source.sheet_name == "informe_1"
    assert result.records[0].source.row_number == 15
    assert result.column_mapping["programa"] == "DERIVACIÓN"
    assert result.column_mapping["dias_cumpl"] == "DÍAS DE CUMPLIMIENTO"
    assert any(item.startswith("HEADER_ROW_AUTODETECTED") for item in result.warnings)
