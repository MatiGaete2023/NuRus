from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Mapping


class Mode(StrEnum):
    ESPERA = "ESPERA"
    CUMPLIMIENTO = "CUMPLIMIENTO"
    INFORMES = "INFORMES"


@dataclass(frozen=True)
class SourceReference:
    """Ubicación verificable de una fila en el libro que la originó."""

    workbook_name: str
    workbook_sha256: str
    sheet_name: str
    row_number: int


@dataclass(frozen=True)
class SourceRecord:
    values: Mapping[str, object]
    source: SourceReference


@dataclass(frozen=True)
class ReadBatch:
    mode: Mode
    records: tuple[SourceRecord, ...]
    cross_records: tuple[SourceRecord, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    source: SourceReference


@dataclass(frozen=True)
class Evaluation:
    source: SourceReference
    observation: str
    rule_ids: tuple[str, ...]
    issues: tuple[Issue, ...] = ()
    related_sources: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class EvaluationBatch:
    mode: Mode
    as_of: date
    evaluations: tuple[Evaluation, ...]
    warnings: tuple[str, ...] = ()

