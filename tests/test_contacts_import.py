from __future__ import annotations

import pytest
from openpyxl import Workbook

from nurus.services.contacts import (
    ContactImportError,
    apply_contact_preview,
    preview_contact_import,
    resolve_contact_exact,
)
from nurus.storage.database import Database


def _write(path, headers, rows):
    book = Workbook()
    sheet = book.active
    sheet.title = "Contactos"
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    book.save(path)


def test_contact_import_is_previewed_and_applies_only_accepted_rows(tmp_path):
    path = tmp_path / "contactos.xlsx"
    _write(
        path,
        ["PROGRAMA", "CORREO", "CC", "ALIAS"],
        [
            ["PRM Norte", "norte@example.test", "copia@example.test", "Norte PRM; PRM N"],
            ["PRM Sur", "sur@example.test", "", "Sur PRM"],
        ],
    )
    db = Database(tmp_path / "nurus.sqlite3")

    preview = preview_contact_import(db, path)
    assert [item.action for item in preview.changes] == ["add", "add"]
    assert not preview.conflicts

    count = apply_contact_preview(db, preview, {preview.changes[0].entity_key})
    assert count == 1
    assert len(db.list_contacts()) == 1

    direct = resolve_contact_exact(db, "PRM Norte")
    alias = resolve_contact_exact(db, "Norte PRM")
    similar = resolve_contact_exact(db, "Norte PR")
    assert direct is not None and direct["email"] == "norte@example.test"
    assert alias is not None and alias["email"] == "norte@example.test"
    assert similar is None


def test_existing_contact_is_reported_as_update_not_silently_replaced(tmp_path):
    path = tmp_path / "contactos.xlsx"
    db = Database(tmp_path / "nurus.sqlite3")
    db.save_contact("prm norte", "PRM Norte", "old@example.test")
    _write(path, ["PROGRAMA", "CORREO"], [["PRM Norte", "new@example.test"]])

    preview = preview_contact_import(db, path)
    change = preview.changes[0]
    assert change.action == "update"
    assert change.existing_email == "old@example.test"
    assert change.email == "new@example.test"
    assert db.list_contacts()[0]["email"] == "old@example.test"


def test_ambiguous_entity_columns_require_explicit_correction(tmp_path):
    path = tmp_path / "contactos.xlsx"
    _write(
        path,
        ["PROGRAMA", "NOMBRE CENTRO", "CORREO"],
        [["PRM Norte", "PRM Norte", "norte@example.test"]],
    )
    db = Database(tmp_path / "nurus.sqlite3")
    with pytest.raises(ContactImportError, match="Columnas ambiguas"):
        preview_contact_import(db, path)


def test_invalid_email_is_conflict_and_cannot_be_applied(tmp_path):
    path = tmp_path / "contactos.xlsx"
    _write(path, ["PROGRAMA", "CORREO"], [["PRM Norte", "correo-invalido"]])
    db = Database(tmp_path / "nurus.sqlite3")

    preview = preview_contact_import(db, path)
    change = preview.changes[0]
    assert change.action == "conflict"
    assert "sintaxis inválida" in change.issue
    with pytest.raises(ContactImportError):
        apply_contact_preview(db, preview, {change.entity_key})
