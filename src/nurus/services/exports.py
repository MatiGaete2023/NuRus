from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from nurus.storage.database import Database


class ExportError(ValueError):
    pass


@dataclass(frozen=True)
class ExportResult:
    path: Path
    sha256: str
    row_count: int


def _safe_cell(value: object) -> object:
    if not isinstance(value, str):
        return value
    if value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _snapshot_rows(db: Database, batch_id: str) -> tuple[object, list[dict[str, object]]]:
    batch = db.get_batch(batch_id)
    if batch is None:
        raise ExportError("Lote no encontrado.")
    if batch["status"] != "approved" or not batch["snapshot_hash"]:
        raise ExportError("Solo se puede exportar un lote aprobado y congelado.")
    rows: list[dict[str, object]] = []
    for item in db.list_review_records(batch_id):
        if item["decision"] != "approved":
            continue
        values = json.loads(item["values_json"])
        values["NURUS_OBSERVACION"] = item["edited_observation"]
        values["NURUS_HOJA_ORIGEN"] = item["source_sheet"]
        values["NURUS_FILA_ORIGEN"] = item["source_row"]
        values["NURUS_HASH_ORIGEN"] = item["source_hash"]
        rows.append(values)
    if not rows:
        raise ExportError("El lote no contiene registros aprobados exportables.")
    return batch, rows


def _headers(rows: list[dict[str, object]]) -> list[str]:
    result: list[str] = []
    for row in rows:
        for key in row:
            if key not in result:
                result.append(key)
    return result


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_review_snapshot(
    db: Database,
    batch_id: str,
    destination: str | Path,
    *,
    overwrite: bool = False,
) -> ExportResult:
    """Exporta una copia revisada; jamás modifica el Excel fuente."""
    target = Path(destination).expanduser().resolve()
    if target.suffix.lower() not in {".xlsx", ".csv"}:
        raise ExportError("La exportación debe ser .xlsx o .csv.")
    if target.exists() and not overwrite:
        raise ExportError("El archivo de destino ya existe; confirma un nombre distinto o sobrescritura.")
    target.parent.mkdir(parents=True, exist_ok=True)

    batch, rows = _snapshot_rows(db, batch_id)
    headers = _headers(rows)
    suffix = target.suffix.lower()
    temp_path: Path | None = None
    try:
        if suffix == ".xlsx":
            from openpyxl import Workbook

            handle = tempfile.NamedTemporaryFile(
                prefix=target.stem + ".", suffix=".tmp.xlsx", dir=target.parent, delete=False
            )
            handle.close()
            temp_path = Path(handle.name)
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Revision"
            sheet.append(headers)
            for row in rows:
                sheet.append([_safe_cell(row.get(header, "")) for header in headers])
            trace = workbook.create_sheet("Trazabilidad")
            trace.append(["CAMPO", "VALOR"])
            for key, value in [
                ("batch_id", batch["id"]),
                ("snapshot_hash", batch["snapshot_hash"]),
                ("source_name", batch["source_name"]),
                ("source_hash", batch["source_hash"]),
                ("mode", batch["mode"]),
                ("as_of", batch["as_of"]),
                ("engine_version", batch["engine_version"]),
                ("catalog_hash", batch["catalog_hash"]),
            ]:
                trace.append([key, value])
            trace.sheet_state = "hidden"
            workbook.save(temp_path)
        else:
            handle = tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8-sig", newline="", prefix=target.stem + ".",
                suffix=".tmp.csv", dir=target.parent, delete=False
            )
            temp_path = Path(handle.name)
            with handle:
                writer = csv.writer(handle, delimiter=";", quoting=csv.QUOTE_MINIMAL)
                writer.writerow(headers)
                for row in rows:
                    writer.writerow([_safe_cell(row.get(header, "")) for header in headers])
        os.replace(temp_path, target)
        temp_path = None
    except OSError as exc:
        raise ExportError(f"No se pudo escribir la exportación: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    return ExportResult(target, _hash(target), len(rows))
