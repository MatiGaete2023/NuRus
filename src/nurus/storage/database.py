from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Mapping
from uuid import uuid4

from nurus.domain.models import Product, ProductKind, Template, utc_now
from nurus.rus.models import EvaluationBatch, SourceReference


SCHEMA = """
CREATE TABLE IF NOT EXISTS workbook_sources (
  hash TEXT PRIMARY KEY, content BLOB NOT NULL, size INTEGER NOT NULL,
  created_at TEXT NOT NULL, CHECK(length(content)=size)
);
CREATE TRIGGER IF NOT EXISTS source_no_update BEFORE UPDATE ON workbook_sources
BEGIN SELECT RAISE(ABORT, 'Origen inmutable'); END;
CREATE TRIGGER IF NOT EXISTS source_no_delete BEFORE DELETE ON workbook_sources
BEGIN SELECT RAISE(ABORT, 'Origen inmutable'); END;
CREATE TABLE IF NOT EXISTS batch_exceptions (
  batch_id TEXT PRIMARY KEY REFERENCES batches(id) ON DELETE CASCADE,
  code TEXT NOT NULL, responsible TEXT NOT NULL, reason TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approved_snapshots (
  hash TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batches(id),
  payload TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS snapshot_no_update BEFORE UPDATE ON approved_snapshots
BEGIN SELECT RAISE(ABORT, 'Snapshot inmutable'); END;
CREATE TRIGGER IF NOT EXISTS snapshot_no_delete BEFORE DELETE ON approved_snapshots
BEGIN SELECT RAISE(ABORT, 'Snapshot inmutable'); END;
CREATE TABLE IF NOT EXISTS templates (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL,
  subject TEXT NOT NULL, body TEXT NOT NULL, allowed_variables TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('draft','published')),
  version INTEGER NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS template_versions (
  template_id TEXT NOT NULL, version INTEGER NOT NULL, name TEXT NOT NULL,
  kind TEXT NOT NULL, subject TEXT NOT NULL, body TEXT NOT NULL,
  allowed_variables TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('draft','published')),
  created_at TEXT NOT NULL,
  PRIMARY KEY(template_id, version)
);
CREATE TABLE IF NOT EXISTS contacts (
  id TEXT PRIMARY KEY, entity_key TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL,
  email TEXT NOT NULL, cc TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS batches (
  id TEXT PRIMARY KEY, source_name TEXT NOT NULL, source_hash TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS review_records (
  batch_id TEXT NOT NULL,
  record_id TEXT NOT NULL,
  source_sheet TEXT NOT NULL,
  source_row INTEGER NOT NULL,
  source_hash TEXT NOT NULL,
  values_json TEXT NOT NULL,
  original_observation TEXT NOT NULL,
  edited_observation TEXT NOT NULL,
  rule_ids_json TEXT NOT NULL,
  issues_json TEXT NOT NULL,
  related_sources_json TEXT NOT NULL,
  evaluation_status TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('pending','approved','excluded','blocked')),
  edit_reason TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL,
  PRIMARY KEY(batch_id, record_id),
  FOREIGN KEY(batch_id) REFERENCES batches(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY, batch_id TEXT NOT NULL, kind TEXT NOT NULL, template_id TEXT NOT NULL,
  template_version INTEGER NOT NULL, recipient TEXT NOT NULL, status TEXT NOT NULL,
  subject TEXT NOT NULL, body TEXT NOT NULL, issues TEXT NOT NULL, created_at TEXT NOT NULL,
  FOREIGN KEY(batch_id) REFERENCES batches(id)
);
"""


_BATCH_COLUMNS = {
    "mode": "TEXT NOT NULL DEFAULT 'MANUAL'",
    "source_path": "TEXT NOT NULL DEFAULT ''",
    "primary_sheet": "TEXT NOT NULL DEFAULT ''",
    "cross_sheet": "TEXT NOT NULL DEFAULT ''",
    "header_row": "INTEGER NOT NULL DEFAULT 1",
    "excel_epoch": "TEXT NOT NULL DEFAULT '1900'",
    "as_of": "TEXT NOT NULL DEFAULT ''",
    "engine_version": "TEXT NOT NULL DEFAULT ''",
    "catalog_hash": "TEXT NOT NULL DEFAULT ''",
    "column_mapping": "TEXT NOT NULL DEFAULT '{}'",
    "warnings": "TEXT NOT NULL DEFAULT '[]'",
    "evaluation_hash": "TEXT NOT NULL DEFAULT ''",
    "snapshot_hash": "TEXT NOT NULL DEFAULT ''",
    "status": "TEXT NOT NULL DEFAULT 'review'",
    "approved_at": "TEXT NOT NULL DEFAULT ''",
}

_PRODUCT_COLUMNS = {
    "cc": "TEXT NOT NULL DEFAULT ''",
    "context": "TEXT NOT NULL DEFAULT '{}'",
    "warnings": "TEXT NOT NULL DEFAULT '[]'",
    "source_snapshot_hash": "TEXT NOT NULL DEFAULT ''",
}


def _json_safe(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _json(value: object) -> str:
    return json.dumps(_json_safe(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _source_dict(source: SourceReference) -> dict[str, object]:
    return {
        "workbook_name": source.workbook_name,
        "workbook_sha256": source.workbook_sha256,
        "sheet_name": source.sheet_name,
        "row_number": source.row_number,
    }


def _evaluation_payload(batch: EvaluationBatch) -> dict[str, object]:
    return {
        "batch_id": batch.batch_id,
        "mode": batch.mode.value,
        "as_of": batch.as_of.isoformat(),
        "workbook_name": batch.workbook_name,
        "workbook_sha256": batch.workbook_sha256,
        "primary_sheet": batch.primary_sheet,
        "cross_sheet": batch.cross_sheet,
        "header_row": batch.header_row,
        "excel_epoch": batch.excel_epoch,
        "engine_version": batch.engine_version,
        "catalog_sha256": batch.catalog_sha256,
        "column_mapping": dict(batch.column_mapping),
        "warnings": list(batch.warnings),
        "evaluations": [
            {
                "record_id": item.record_id,
                "source": _source_dict(item.source),
                "values": dict(item.values),
                "observation": item.observation,
                "rule_ids": list(item.rule_ids),
                "issues": [
                    {"code": issue.code, "message": issue.message, "source": _source_dict(issue.source)}
                    for issue in item.issues
                ],
                "related_sources": [_source_dict(source) for source in item.related_sources],
                "status": item.status.value,
            }
            for item in batch.evaluations
        ],
    }


def _digest_payload(payload: object) -> str:
    return sha256(_json(payload).encode("utf-8")).hexdigest()


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.migration_backup = None
        if path.exists() and path.stat().st_size:
            with sqlite3.connect(path) as source:
                version = source.execute("PRAGMA user_version").fetchone()[0]
                if version > 5:
                    raise ValueError("Base de una versión posterior: no se permite degradarla.")
                if version < 5:
                    backup = path.with_name(path.name + f".pre-v5-{uuid4().hex}.bak")
                    with sqlite3.connect(backup) as destination:
                        source.backup(destination)
                    self.migration_backup = backup
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            self._migrate(conn)
        self.seed()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _ensure_columns(conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")

    def _migrate(self, conn: sqlite3.Connection) -> None:
        self._ensure_columns(conn, "batches", _BATCH_COLUMNS)
        self._ensure_columns(conn, "products", _PRODUCT_COLUMNS)
        # Las instalaciones 0.1 guardaban solo la última versión. Se conserva como
        # versión histórica inicial sin reconstruir información inexistente.
        conn.execute(
            """INSERT OR IGNORE INTO template_versions(
                   template_id,version,name,kind,subject,body,allowed_variables,status,created_at)
               SELECT id,version,name,kind,subject,body,allowed_variables,status,updated_at
               FROM templates"""
        )
        conn.execute("PRAGMA user_version = 5")

    def foreign_keys_enabled(self) -> bool:
        with self.connect() as conn:
            return bool(conn.execute("PRAGMA foreign_keys").fetchone()[0])

    def seed(self) -> None:
        if self.list_templates():
            return
        self.save_template(Template(
            id="email-ingreso", name="Consulta de ingreso", kind=ProductKind.EMAIL,
            subject="Ingreso efectivo · {TRIBUNAL}",
            body="Sres. {PROGRAMA}:\n\nSe solicita informar la fecha estimada de ingreso de los registros incluidos.\n\n{TABLA_REGISTROS}",
            allowed_variables=("TRIBUNAL", "PROGRAMA", "TABLA_REGISTROS"), status="published",
        ))
        self.save_template(Template(
            id="resolucion-base", name="Proyecto de resolución", kind=ProductKind.RESOLUTION,
            subject="", body="{TRIBUNAL}, {FECHA_CORTE}\n\nVistos los antecedentes, téngase presente {OBSERVACION}.",
            allowed_variables=("TRIBUNAL", "FECHA_CORTE", "OBSERVACION"), status="published",
        ))

    def list_templates(self) -> list[Template]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM templates ORDER BY kind, name").fetchall()
        return [
            Template(
                id=row["id"], name=row["name"], kind=ProductKind(row["kind"]),
                subject=row["subject"], body=row["body"],
                allowed_variables=tuple(filter(None, row["allowed_variables"].split(","))),
                status=row["status"], version=row["version"],
            )
            for row in rows
        ]

    def list_template_versions(self, template_id: str) -> list[Template]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM template_versions WHERE template_id=? ORDER BY version",
                (template_id,),
            ).fetchall()
        return [
            Template(
                id=row["template_id"], name=row["name"], kind=ProductKind(row["kind"]),
                subject=row["subject"], body=row["body"],
                allowed_variables=tuple(filter(None, row["allowed_variables"].split(","))),
                status=row["status"], version=row["version"],
            )
            for row in rows
        ]

    def save_template(self, template: Template) -> Template:
        variables = ",".join(template.allowed_variables)
        now = utc_now()
        with self.connect() as conn:
            current = conn.execute(
                "SELECT COALESCE(MAX(version),0) FROM template_versions WHERE template_id=?",
                (template.id,),
            ).fetchone()[0]
            version = int(current) + 1 if current else max(1, int(template.version))
            conn.execute(
                """INSERT INTO template_versions(
                       template_id,version,name,kind,subject,body,allowed_variables,status,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (template.id, version, template.name, template.kind.value, template.subject,
                 template.body, variables, template.status, now),
            )
            conn.execute(
                """INSERT INTO templates(id,name,kind,subject,body,allowed_variables,status,version,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET name=excluded.name,kind=excluded.kind,
                   subject=excluded.subject,body=excluded.body,allowed_variables=excluded.allowed_variables,
                   status=excluded.status,version=excluded.version,updated_at=excluded.updated_at""",
                (template.id, template.name, template.kind.value, template.subject, template.body,
                 variables, template.status, version, now),
            )
        return Template(
            id=template.id, name=template.name, kind=template.kind, subject=template.subject,
            body=template.body, allowed_variables=template.allowed_variables,
            status=template.status, version=version,
        )

    def list_contacts(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM contacts ORDER BY display_name").fetchall()

    def save_contact(self, entity_key: str, display_name: str, email: str, cc: str = "") -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO contacts(id,entity_key,display_name,email,cc,active,updated_at)
                   VALUES(?,?,?,?,?,?,?) ON CONFLICT(entity_key) DO UPDATE SET
                   display_name=excluded.display_name,email=excluded.email,cc=excluded.cc,
                   active=1,updated_at=excluded.updated_at""",
                (entity_key, entity_key, display_name, email, cc, 1, utc_now()),
            )

    def save_evaluation_batch(self, batch: EvaluationBatch, *, source_bytes: bytes | None = None) -> str:
        """Persiste exactamente la evaluación recibida; no recalcula reglas."""
        if source_bytes is not None:
            if not isinstance(source_bytes, bytes) or not source_bytes:
                raise ValueError("El origen debe contener bytes inmutables no vacíos.")
            if sha256(source_bytes).hexdigest() != batch.workbook_sha256:
                raise ValueError("Los bytes de origen no coinciden con el hash del lote.")
        payload = _evaluation_payload(batch)
        evaluation_hash = _digest_payload(payload)
        now = utc_now()
        with self.connect() as conn:
            if source_bytes is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO workbook_sources(hash,content,size,created_at) VALUES(?,?,?,?)",
                    (batch.workbook_sha256, source_bytes, len(source_bytes), now),
                )
                stored = conn.execute(
                    "SELECT content FROM workbook_sources WHERE hash=?", (batch.workbook_sha256,)
                ).fetchone()
                if bytes(stored["content"]) != source_bytes:
                    raise ValueError("El origen almacenado no coincide con los bytes importados.")
            conn.execute(
                """INSERT INTO batches(
                       id,source_name,source_hash,created_at,mode,source_path,primary_sheet,
                       cross_sheet,header_row,excel_epoch,as_of,engine_version,catalog_hash,
                       column_mapping,warnings,evaluation_hash,snapshot_hash,status,approved_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (batch.batch_id, batch.workbook_name or "Sin nombre", batch.workbook_sha256,
                 now, batch.mode.value, batch.source_path, batch.primary_sheet, batch.cross_sheet,
                 batch.header_row, batch.excel_epoch, batch.as_of.isoformat(), batch.engine_version,
                 batch.catalog_sha256, _json(dict(batch.column_mapping)), _json(batch.warnings),
                 evaluation_hash, "", "review", ""),
            )
            for item in batch.evaluations:
                if item.status.value == "excluded":
                    decision = "excluded"
                elif item.status.value == "blocked":
                    decision = "blocked"
                else:
                    decision = "pending"
                conn.execute(
                    """INSERT INTO review_records(
                           batch_id,record_id,source_sheet,source_row,source_hash,values_json,
                           original_observation,edited_observation,rule_ids_json,issues_json,
                           related_sources_json,evaluation_status,decision,edit_reason,updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (batch.batch_id, item.record_id, item.source.sheet_name, item.source.row_number,
                     item.source.workbook_sha256, _json(dict(item.values)), item.observation,
                     item.observation, _json(item.rule_ids),
                     _json([{"code": issue.code, "message": issue.message,
                             "source": _source_dict(issue.source)} for issue in item.issues]),
                     _json([_source_dict(source) for source in item.related_sources]),
                     item.status.value, decision, "", now),
                )
        return evaluation_hash

    def document_missing_cross_sheet_exception(
        self, batch_id: str, *, responsible: str, reason: str
    ) -> None:
        """Registra una excepción humana antes de aprobar Cumplimiento sin hoja de cruce."""
        responsible = responsible.strip()
        reason = reason.strip()
        if not responsible or not reason:
            raise ValueError("La excepción requiere responsable y motivo.")
        with self.connect() as conn:
            batch = conn.execute("SELECT * FROM batches WHERE id=?", (batch_id,)).fetchone()
            if batch is None:
                raise KeyError("Lote no encontrado.")
            warnings = json.loads(batch["warnings"] or "[]")
            missing_cross = any(
                str(item).startswith("CROSS_SHEET_NOT_SELECTED") for item in warnings
            )
            ambiguous_cross = any(
                str(item).startswith(("CROSS_SHEET_AMBIGUOUS", "CROSS_MAPPING_AMBIGUOUS"))
                for item in warnings
            )
            if batch["mode"] != "CUMPLIMIENTO" or not missing_cross:
                raise ValueError("Este lote no requiere excepción por ausencia de hoja de cruce.")
            if ambiguous_cross:
                raise ValueError(
                    "La hoja de cruce es ambigua; selecciónala o corrige su mapeo antes de aprobar."
                )
            conn.execute(
                """INSERT INTO batch_exceptions(batch_id,code,responsible,reason,created_at)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(batch_id) DO UPDATE SET
                   code=excluded.code,responsible=excluded.responsible,
                   reason=excluded.reason,created_at=excluded.created_at""",
                (batch_id, "CROSS_SHEET_NOT_SELECTED", responsible, reason, utc_now()),
            )
            conn.execute(
                "UPDATE batches SET status='review',snapshot_hash='',approved_at='' WHERE id=?",
                (batch_id,),
            )

    def get_batch_exception(self, batch_id: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM batch_exceptions WHERE batch_id=?", (batch_id,)
            ).fetchone()

    def get_original_workbook(self, batch_id: str, *, snapshot_hash: str = "") -> bytes:
        """Recupera bytes verificados; nunca relee la ruta externa como sustituto."""
        if snapshot_hash:
            digest = self.get_snapshot(batch_id, snapshot_hash)["batch"]["source_hash"]
        else:
            batch = self.get_batch(batch_id)
            if batch is None:
                raise KeyError("Lote no encontrado.")
            digest = batch["source_hash"]
        with self.connect() as conn:
            row = conn.execute(
                "SELECT content,size FROM workbook_sources WHERE hash=?", (digest,)
            ).fetchone()
        if row is None:
            raise ValueError("No se conservan bytes originales para este lote; vuelve a importarlo.")
        content = bytes(row["content"])
        if len(content) != row["size"] or sha256(content).hexdigest() != digest:
            raise ValueError("El origen almacenado no coincide con su hash o tamaño.")
        return content

    def get_batch(self, batch_id: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM batches WHERE id=?", (batch_id,)).fetchone()

    def list_review_records(self, batch_id: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM review_records WHERE batch_id=? ORDER BY source_sheet,source_row",
                (batch_id,),
            ).fetchall()

    def set_record_decision(
        self,
        batch_id: str,
        record_id: str,
        decision: str,
        *,
        observation: str | None = None,
        reason: str = "",
    ) -> None:
        if decision not in {"pending", "approved", "excluded"}:
            raise ValueError("Decisión de revisión no válida.")
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM review_records WHERE batch_id=? AND record_id=?",
                (batch_id, record_id),
            ).fetchone()
            if row is None:
                raise KeyError("Registro de revisión no encontrado.")
            if row["evaluation_status"] == "blocked" and decision == "approved":
                raise ValueError("Una fila bloqueada no puede aprobarse sin corregir la causa.")
            new_observation = row["edited_observation"] if observation is None else observation.strip()
            changed = new_observation != row["original_observation"]
            if (changed or decision == "excluded") and not reason.strip():
                raise ValueError("La edición o exclusión requiere un motivo de revisión.")
            conn.execute(
                """UPDATE review_records SET decision=?,edited_observation=?,edit_reason=?,updated_at=?
                   WHERE batch_id=? AND record_id=?""",
                (decision, new_observation, reason.strip(), utc_now(), batch_id, record_id),
            )
            conn.execute(
                "UPDATE batches SET status='review',snapshot_hash='',approved_at='' WHERE id=?",
                (batch_id,),
            )

    def restore_record(self, batch_id: str, record_id: str) -> None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT evaluation_status,original_observation FROM review_records WHERE batch_id=? AND record_id=?",
                (batch_id, record_id),
            ).fetchone()
            if row is None:
                raise KeyError("Registro de revisión no encontrado.")
            decision = "excluded" if row["evaluation_status"] == "excluded" else (
                "blocked" if row["evaluation_status"] == "blocked" else "pending"
            )
            conn.execute(
                """UPDATE review_records SET decision=?,edited_observation=original_observation,
                   edit_reason='',updated_at=? WHERE batch_id=? AND record_id=?""",
                (decision, utc_now(), batch_id, record_id),
            )
            conn.execute(
                "UPDATE batches SET status='review',snapshot_hash='',approved_at='' WHERE id=?",
                (batch_id,),
            )

    def approve_batch(self, batch_id: str) -> str:
        """Aprueba filas y persiste el snapshot en una única transacción."""
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            batch = conn.execute("SELECT * FROM batches WHERE id=?", (batch_id,)).fetchone()
            if batch is None:
                raise KeyError("Lote no encontrado.")
            warnings = json.loads(batch["warnings"] or "[]")
            exception = conn.execute(
                "SELECT * FROM batch_exceptions WHERE batch_id=?", (batch_id,)
            ).fetchone()
            missing_cross = batch["mode"] == "CUMPLIMIENTO" and any(
                str(item).startswith("CROSS_SHEET_NOT_SELECTED") for item in warnings
            )
            ambiguous_cross = any(
                str(item).startswith(("CROSS_SHEET_AMBIGUOUS", "CROSS_MAPPING_AMBIGUOUS"))
                for item in warnings
            )
            rows = conn.execute(
                "SELECT * FROM review_records WHERE batch_id=? ORDER BY source_sheet,source_row",
                (batch_id,),
            ).fetchall()
            if not rows:
                raise ValueError("El lote no contiene registros revisables.")
            blocked = [r for r in rows if r["decision"] == "blocked"
                       or (r["evaluation_status"] == "blocked" and r["decision"] != "excluded")]
            if blocked:
                pending = sum(r["decision"] == "pending" for r in rows)
                message = f"Quedan {len(blocked)} filas bloqueadas que requieren revisión individual."
                if pending:
                    message += f" Las {pending} filas sin incidencias se aprobarán juntas cuando se apruebe el lote."
                raise ValueError(message)
            if missing_cross and ambiguous_cross:
                raise ValueError(
                    "La hoja de cruce es ambigua; no puede aprobarse mediante excepción."
                )
            if missing_cross and exception is None:
                raise ValueError(
                    "Cumplimiento requiere una excepción documentada por ausencia de hoja de cruce."
                )
            now = utc_now()
            conn.execute(
                "UPDATE review_records SET decision='approved',updated_at=? WHERE batch_id=? AND decision='pending'",
                (now, batch_id),
            )
            rows = conn.execute(
                "SELECT * FROM review_records WHERE batch_id=? ORDER BY source_sheet,source_row",
                (batch_id,),
            ).fetchall()
            exceptions = []
            if exception is not None:
                exceptions.append({
                    "code": exception["code"],
                    "responsible": exception["responsible"],
                    "reason": exception["reason"],
                    "created_at": exception["created_at"],
                })
            snapshot = {
                "schema_version": 2,
                "batch": {k: batch[k] for k in batch.keys()
                          if k not in {"status", "snapshot_hash", "approved_at"}},
                "records": [{k: r[k] for k in r.keys() if k != "updated_at"} for r in rows],
                "exceptions": exceptions,
            }
            digest = _digest_payload(snapshot)
            conn.execute(
                "INSERT OR IGNORE INTO approved_snapshots(hash,batch_id,payload,created_at) VALUES(?,?,?,?)",
                (digest, batch_id, _json(snapshot), now),
            )
            # La fecha corresponde al snapshot, incluso al aprobarlo nuevamente.
            frozen = conn.execute("SELECT created_at FROM approved_snapshots WHERE hash=?", (digest,)).fetchone()
            conn.execute(
                "UPDATE batches SET status='approved',snapshot_hash=?,approved_at=? WHERE id=?",
                (digest, frozen["created_at"], batch_id),
            )
        return digest

    def get_snapshot(self, batch_id: str, snapshot_hash: str = "") -> dict:
        """Lee evidencia histórica; nunca reconstruye un snapshot ausente."""
        with self.connect() as conn:
            if not snapshot_hash:
                batch = conn.execute("SELECT status,snapshot_hash FROM batches WHERE id=?", (batch_id,)).fetchone()
                if batch is None or batch["status"] != "approved" or not batch["snapshot_hash"]:
                    raise ValueError("Se requiere un lote aprobado y congelado.")
                snapshot_hash = batch["snapshot_hash"]
            row = conn.execute(
                "SELECT payload,created_at FROM approved_snapshots WHERE hash=? AND batch_id=?",
                (snapshot_hash, batch_id),
            ).fetchone()
            if row is None:
                raise ValueError("No existe snapshot histórico guardado; revisa y aprueba nuevamente el lote.")
            payload = json.loads(row["payload"])
            if _digest_payload(payload) != snapshot_hash:
                raise ValueError("El contenido del snapshot no coincide con su hash.")
            payload["batch"].update(snapshot_hash=snapshot_hash, status="approved", approved_at=row["created_at"])
            return payload

    def record_product(self, product: Product, source_name: str = "Comunicación particular") -> None:
        """Registra una copia preparada; nunca crea ni envía elementos Outlook."""
        now = utc_now()
        batch_id = product.batch_id
        snapshot_hash = ""
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            if batch_id:
                batch = conn.execute("SELECT * FROM batches WHERE id=?", (batch_id,)).fetchone()
                if batch is None:
                    raise ValueError("El producto referencia un lote inexistente.")
                if batch["status"] != "approved":
                    raise ValueError("El lote debe estar aprobado antes de preparar productos.")
                snapshot_hash = product.source_snapshot_hash
                if not snapshot_hash or snapshot_hash != batch["snapshot_hash"]:
                    raise ValueError("La vista previa no corresponde al snapshot vigente; prepara nuevamente el producto.")
                if not conn.execute("SELECT 1 FROM approved_snapshots WHERE hash=? AND batch_id=?", (snapshot_hash, batch_id)).fetchone():
                    raise ValueError("El producto requiere un snapshot histórico guardado.")
            else:
                batch_id = str(uuid4())
                conn.execute(
                    """INSERT INTO batches(id,source_name,source_hash,created_at,mode,status,approved_at)
                       VALUES(?,?,?,?,?,?,?)""",
                    (batch_id, source_name, "manual", now, "MANUAL", "approved", now),
                )
            conn.execute(
                """INSERT INTO products(
                       id,batch_id,kind,template_id,template_version,recipient,status,subject,body,
                       issues,created_at,cc,context,warnings,source_snapshot_hash)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (product.id, batch_id, product.kind.value, product.template.id,
                 product.template.version, product.recipient, product.status.value,
                 product.rendered_subject, product.rendered_body, _json(product.issues), now,
                 product.cc, _json(product.context), _json(getattr(product, "warnings", [])),
                 snapshot_hash),
            )

    def list_products(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                """SELECT p.*, b.source_name FROM products p JOIN batches b ON b.id=p.batch_id
                   ORDER BY p.created_at DESC LIMIT 100"""
            ).fetchall()
