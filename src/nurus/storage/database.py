from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from nurus.domain.models import ProductKind, Template, utc_now


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS templates (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL,
  subject TEXT NOT NULL, body TEXT NOT NULL, allowed_variables TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('draft','published')),
  version INTEGER NOT NULL, updated_at TEXT NOT NULL
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
CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY, batch_id TEXT NOT NULL, kind TEXT NOT NULL, template_id TEXT NOT NULL,
  template_version INTEGER NOT NULL, recipient TEXT NOT NULL, status TEXT NOT NULL,
  subject TEXT NOT NULL, body TEXT NOT NULL, issues TEXT NOT NULL, created_at TEXT NOT NULL,
  FOREIGN KEY(batch_id) REFERENCES batches(id)
);
"""


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA)
        self.seed()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

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
        return [Template(id=r["id"], name=r["name"], kind=ProductKind(r["kind"]), subject=r["subject"], body=r["body"], allowed_variables=tuple(filter(None, r["allowed_variables"].split(","))), status=r["status"], version=r["version"]) for r in rows]

    def save_template(self, template: Template) -> None:
        variables = ",".join(template.allowed_variables)
        with self.connect() as conn:
            conn.execute("""INSERT INTO templates(id,name,kind,subject,body,allowed_variables,status,version,updated_at)
              VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,kind=excluded.kind,
              subject=excluded.subject,body=excluded.body,allowed_variables=excluded.allowed_variables,
              status=excluded.status,version=templates.version+1,updated_at=excluded.updated_at""",
              (template.id, template.name, template.kind.value, template.subject, template.body, variables, template.status, template.version, utc_now()))

    def list_contacts(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM contacts ORDER BY display_name").fetchall()

    def save_contact(self, entity_key: str, display_name: str, email: str, cc: str = "") -> None:
        with self.connect() as conn:
            conn.execute("""INSERT INTO contacts(id,entity_key,display_name,email,cc,active,updated_at)
             VALUES(?,?,?,?,?,?,?) ON CONFLICT(entity_key) DO UPDATE SET display_name=excluded.display_name,
             email=excluded.email,cc=excluded.cc,active=1,updated_at=excluded.updated_at""",
             (entity_key, entity_key, display_name, email, cc, 1, utc_now()))
