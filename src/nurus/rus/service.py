from __future__ import annotations

from datetime import date

from .catalog import load_catalog
from .columns import H2_COLUMNS, map_columns, map_cross_columns
from .models import Evaluation, EvaluationBatch, Mode, ReadBatch, SourceRecord
from .rules import as_date, evaluate_compliance, evaluate_reports, evaluate_waiting, match_key


def _cross_index(records: tuple[SourceRecord, ...], as_of: date) -> tuple[dict[tuple[str, ...], SourceRecord], list[str]]:
    """Replica el cruce histórico: cinco campos y última fila válida.

    La referencia completa de la fila secundaria se conserva, en vez de
    perderse al reducir el cruce a una fecha.
    """
    if not records:
        return {}, []
    columns = map_cross_columns(records[0].values.keys())
    missing = set(H2_COLUMNS) - set(columns)
    if missing:
        return {}, [f"CROSS_MAPPING_MISSING: faltan {', '.join(sorted(missing))}; C-10 no se evaluará."]
    index: dict[tuple[str, ...], SourceRecord] = {}
    for record in records:
        due = as_date(record.values.get(columns["vencimiento"]))
        if not due or due <= as_of:
            continue
        key = match_key(record.values, columns)
        if key and key[0]:
            index[key] = record
    return index, []


def evaluate_batch(batch: ReadBatch, *, as_of: date | None = None, catalog_path: str | None = None) -> EvaluationBatch:
    """Evalúa un lote de forma determinista y sin producir efectos externos."""
    today = as_of or date.today()
    catalog = load_catalog(catalog_path)
    if not batch.records:
        return EvaluationBatch(batch.mode, today, (), batch.warnings)
    columns = map_columns(batch.records[0].values.keys(), batch.mode.value)
    warnings = list(batch.warnings)
    required = {"programa", "tribunal"}
    if not required <= set(columns):
        warnings.append("REQUIRED_COLUMNS_MISSING: faltan DERIVACION/PROGRAMA o TRIBUNAL; no se evaluó el lote.")
        return EvaluationBatch(batch.mode, today, (), tuple(warnings))
    cross: dict[tuple[str, ...], SourceRecord] = {}
    if batch.mode is Mode.CUMPLIMIENTO:
        cross, cross_warnings = _cross_index(batch.cross_records, today)
        warnings.extend(cross_warnings)

    evaluations: list[Evaluation] = []
    for record in batch.records:
        related = ()
        if batch.mode is Mode.ESPERA:
            observation, rule_ids, issues = evaluate_waiting(record, columns, catalog, today)
        elif batch.mode is Mode.INFORMES:
            observation, rule_ids, issues = evaluate_reports(record, columns, catalog, today)
        else:
            key = match_key(record.values, columns)
            cross_record = cross.get(key) if key else None
            cross_due = as_date(cross_record.values[map_cross_columns(cross_record.values.keys())["vencimiento"]]) if cross_record else None
            if cross_record:
                related = (cross_record.source,)
            observation, rule_ids, issues = evaluate_compliance(record, columns, catalog, today, cross_due)
        evaluations.append(Evaluation(record.source, observation, rule_ids, issues, related))
    return EvaluationBatch(batch.mode, today, tuple(evaluations), tuple(warnings))
