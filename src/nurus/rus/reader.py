from __future__ import annotations

import hashlib
from pathlib import Path

from .columns import has_full_cross_mapping
from .models import Mode, ReadBatch, SourceRecord, SourceReference

_ALLOWED_SUFFIXES = {".xls", ".xlsx", ".xlsm"}


class WorkbookReadError(ValueError):
    pass


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _engine(path: Path) -> str:
    if path.suffix.lower() == ".xls":
        return "xlrd"
    return "openpyxl"


def _records(frame, path: Path, digest: str, sheet_name: str) -> tuple[SourceRecord, ...]:
    cleaned = frame.dropna(how="all").fillna("")
    cleaned.columns = [str(header).strip() for header in cleaned.columns]
    return tuple(
        SourceRecord(
            values={str(key): value for key, value in row.items()},
            source=SourceReference(path.name, digest, sheet_name, int(index) + 2),
        )
        for index, row in cleaned.iterrows()
    )


def _sheet_by_name(names: list[str], requested: str) -> str:
    matches = [name for name in names if name.strip().casefold() == requested.strip().casefold()]
    if len(matches) != 1:
        raise WorkbookReadError(f"No existe una hoja única llamada {requested!r}.")
    return matches[0]


def read_workbook(path: str | Path, mode: Mode | str, *, sheet_name: str | None = None, cross_sheet_name: str | None = None) -> ReadBatch:
    """Lee un libro local sin modificarlo y asigna procedencia a cada fila.

    Para Cumplimiento, el cruce se acepta solo si la hoja secundaria se indica
    explícitamente, se llama ``Hoja2`` o hay una única hoja con las columnas
    requeridas. Nunca se toma simplemente la segunda pestaña del libro.
    """
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - depende de instalación
        raise WorkbookReadError("Falta pandas; instala las dependencias de NuRus.") from exc

    selected_mode = Mode(mode)
    source = Path(path).expanduser()
    if not source.is_file():
        raise WorkbookReadError(f"Archivo no encontrado: {source}")
    if source.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise WorkbookReadError("Solo se admiten archivos .xls, .xlsx y .xlsm.")
    digest = _hash_file(source)
    try:
        workbook = pd.ExcelFile(source, engine=_engine(source))
    except ImportError as exc:
        dependency = "xlrd" if source.suffix.lower() == ".xls" else "openpyxl"
        raise WorkbookReadError(f"No se puede leer {source.suffix}: instala {dependency}.") from exc
    except Exception as exc:
        raise WorkbookReadError(f"No se pudo abrir el libro: {exc}") from exc

    with workbook:
        names = list(workbook.sheet_names)
        if not names:
            raise WorkbookReadError("El libro no contiene hojas.")
        if sheet_name:
            primary_name = _sheet_by_name(names, sheet_name)
        elif selected_mode is Mode.CUMPLIMIENTO and any(name.strip().casefold() == "cumplimiento" for name in names):
            primary_name = _sheet_by_name(names, "cumplimiento")
        else:
            primary_name = names[0]
        primary = _records(pd.read_excel(workbook, sheet_name=primary_name), source, digest, primary_name)

        warnings: list[str] = []
        cross: tuple[SourceRecord, ...] = ()
        if selected_mode is Mode.CUMPLIMIENTO:
            other_names = [name for name in names if name != primary_name]
            chosen: str | None = None
            if cross_sheet_name:
                chosen = _sheet_by_name(other_names, cross_sheet_name)
            else:
                named = [name for name in other_names if name.strip().casefold() == "hoja2"]
                if len(named) == 1:
                    chosen = named[0]
                else:
                    candidates = []
                    for name in other_names:
                        candidate = pd.read_excel(workbook, sheet_name=name)
                        if has_full_cross_mapping(candidate.columns):
                            candidates.append(name)
                    if len(candidates) == 1:
                        chosen = candidates[0]
                    elif len(candidates) > 1:
                        warnings.append("CROSS_SHEET_AMBIGUOUS: indique la hoja de cruce explícitamente.")
            if chosen:
                cross = _records(pd.read_excel(workbook, sheet_name=chosen), source, digest, chosen)
            elif other_names:
                warnings.append("CROSS_SHEET_NOT_SELECTED: C-10 no se evaluará sin una hoja de cruce identificable.")
    return ReadBatch(selected_mode, primary, cross, tuple(warnings))
