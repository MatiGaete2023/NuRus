from __future__ import annotations

from datetime import date

import pytest
from openpyxl import Workbook

from nurus.rus import Mode
from nurus.services.workflow import WorkController
from nurus.storage.database import Database


def _write_compliance(path, *, extra_sheets=()):
    book = Workbook()
    sheet = book.active
    sheet.title = "Cumplimiento"
    sheet.append([
        "DERIVACION", "TRIBUNAL", "NOMBRE", "RIT", "RUT",
        "DIAS DE CUMPLIMIENTO", "DIAS PARA EGRESAR",
    ])
    sheet.append(["PRM Centro", "Juzgado de Laja", "Ana", "C-1", "1-9", 100, 100])
    for name in extra_sheets:
        cross = book.create_sheet(name)
        cross.append([
            "NOMBRE CENTRO", "TRIBUNAL", "NOMBRE MENOR", "RIT", "RUT MENOR",
            "FECHA VENCIMIENTO",
        ])
        cross.append(["PRM Centro", "Juzgado de Laja", "Ana", "C-1", "1-9", "20/09/2026"])
    book.save(path)


def test_missing_cross_sheet_requires_documented_exception_and_freezes_it(tmp_path):
    path = tmp_path / "cumplimiento.xlsx"
    _write_compliance(path)
    db = Database(tmp_path / "nurus.sqlite3")
    controller = WorkController(db)
    batch = controller.analyze(path, Mode.CUMPLIMIENTO, as_of=date(2026, 9, 8))

    assert any(item.startswith("CROSS_SHEET_NOT_SELECTED") for item in batch.warnings)
    with pytest.raises(ValueError, match="excepción documentada"):
        controller.approve_batch(batch.batch_id)
    with pytest.raises(ValueError, match="responsable y motivo"):
        controller.document_missing_cross_sheet_exception(
            batch.batch_id, responsible="", reason=""
        )

    controller.document_missing_cross_sheet_exception(
        batch.batch_id,
        responsible="Matías Gaete",
        reason="La planilla recibida no contiene hoja de cruce; revisión manual autorizada.",
    )
    exception = db.get_batch_exception(batch.batch_id)
    assert exception["code"] == "CROSS_SHEET_NOT_SELECTED"
    assert exception["responsible"] == "Matías Gaete"

    first = controller.approve_batch(batch.batch_id)
    snapshot = db.get_snapshot(batch.batch_id, first)
    assert snapshot["schema_version"] == 2
    assert snapshot["exceptions"] == [{
        "code": "CROSS_SHEET_NOT_SELECTED",
        "responsible": "Matías Gaete",
        "reason": "La planilla recibida no contiene hoja de cruce; revisión manual autorizada.",
        "created_at": exception["created_at"],
    }]

    controller.document_missing_cross_sheet_exception(
        batch.batch_id, responsible="Otra revisión", reason="Motivo actualizado"
    )
    assert db.get_batch(batch.batch_id)["status"] == "review"
    second = controller.approve_batch(batch.batch_id)
    assert second != first
    assert db.get_snapshot(batch.batch_id, first) == snapshot


def test_ambiguous_cross_sheet_cannot_be_approved_by_exception(tmp_path):
    path = tmp_path / "cumplimiento-ambiguo.xlsx"
    _write_compliance(path, extra_sheets=("Cruce A", "Cruce B"))
    db = Database(tmp_path / "nurus.sqlite3")
    batch = WorkController(db).analyze(path, Mode.CUMPLIMIENTO, as_of=date(2026, 9, 8))

    with pytest.raises(ValueError, match="ambigua"):
        db.document_missing_cross_sheet_exception(
            batch.batch_id, responsible="Matías", reason="No corresponde"
        )
