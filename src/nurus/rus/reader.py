from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from .columns import ColumnMappingError, has_full_cross_mapping, map_columns, map_cross_columns, normalize
from .models import Mode, ReadBatch, SourceRecord, SourceReference

_ALLOWED_SUFFIXES = {".xls", ".xlsx", ".xlsm"}


class WorkbookReadError(ValueError):
    pass


def _snapshot_file(path: Path, *, max_file_size_bytes: int | None = None) -> tuple[Path, str]:
    if max_file_size_bytes is not None and path.stat().st_size > max_file_size_bytes:
        raise WorkbookReadError(
            f"El archivo supera el límite configurado de {max_file_size_bytes} bytes."
        )
    digest = hashlib.sha256()
    temp_path: Path | None = None
    try:
        with path.open("rb") as source, tempfile.NamedTemporaryFile(
            suffix=path.suffix, delete=False
        ) as target:
            temp_path = Path(target.name)
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
                target.write(chunk)
        return temp_path, digest.hexdigest()
    except OSError as exc:
        if temp_path:
            temp_path.unlink(missing_ok=True)
        raise WorkbookReadError(f"No se pudo crear una copia estable del archivo: {exc}") from exc


def _engine(path: Path) -> str:
    return "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"


def _is_empty(value: object) -> bool:
    if value is None:
        return True
    text = str(value).strip().casefold()
    return text in {"", "nan", "nat", "none"}


def _records(frame, source_name: str, digest: str, sheet_name: str, header_row: int) -> tuple[SourceRecord, ...]:
    frame = frame.copy()
    frame.columns = [str(header).strip() for header in frame.columns]
    records: list[SourceRecord] = []
    for index, row in frame.iterrows():
        values = {str(key): value for key, value in row.items()}
        if all(_is_empty(value) for value in values.values()):
            continue
        records.append(
            SourceRecord(
                values=values,
                source=SourceReference(
                    source_name,
                    digest,
                    sheet_name,
                    header_row + int(index) + 1,
                ),
            )
        )
    return tuple(records)


def _sheet_by_name(names: list[str], requested: str) -> str:
    matches = [name for name in names if name.strip().casefold() == requested.strip().casefold()]
    if len(matches) != 1:
        raise WorkbookReadError(f"No existe una hoja única llamada {requested!r}.")
    return matches[0]


def _headers(pd, workbook, sheet_name: str, header_row: int) -> list[str]:
    try:
        raw = pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            header=None,
            nrows=header_row,
            dtype=object,
            keep_default_na=False,
        )
    except Exception as exc:
        raise WorkbookReadError(f"No se pudieron leer los encabezados de {sheet_name!r}: {exc}") from exc
    if raw.empty or len(raw.index) < header_row:
        raise WorkbookReadError(
            f"La hoja {sheet_name!r} no contiene la fila de encabezado {header_row}."
        )
    values = [str(value).strip() for value in raw.iloc[header_row - 1].tolist()]
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for header in values:
        normalized = normalize(header)
        if not normalized:
            continue
        if normalized in seen:
            duplicates.extend([seen[normalized], header])
        else:
            seen[normalized] = header
    if duplicates:
        unique = list(dict.fromkeys(duplicates))
        raise WorkbookReadError(
            f"Encabezados duplicados o equivalentes en {sheet_name!r}: {', '.join(unique)}."
        )
    return values


def _read_sheet(pd, workbook, sheet_name: str, header_row: int):
    try:
        return pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            header=header_row - 1,
            dtype=object,
            keep_default_na=False,
        )
    except Exception as exc:
        raise WorkbookReadError(f"No se pudo leer la hoja {sheet_name!r}: {exc}") from exc


def _excel_epoch(workbook) -> str:
    book = getattr(workbook, "book", None)
    datemode = getattr(book, "datemode", None)
    if datemode == 1:
        return "1904"
    epoch = getattr(book, "epoch", None)
    if getattr(epoch, "year", None) == 1904:
        return "1904"
    return "1900"


def read_workbook(
    path: str | Path,
    mode: Mode | str,
    *,
    sheet_name: str | None = None,
    cross_sheet_name: str | None = None,
    header_row: int = 1,
    max_file_size_bytes: int | None = None,
) -> ReadBatch:
    """Lee una copia estable del libro y conserva procedencia física de cada fila.

    `header_row` es 1-based. No se modifica el archivo original ni se ejecutan macros.
    La copia temporal garantiza que el SHA-256 corresponde a los mismos bytes
    procesados por pandas.
    """
    if header_row < 1:
        raise WorkbookReadError("header_row debe ser mayor o igual a 1.")
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover
        raise WorkbookReadError("Falta pandas; instala las dependencias de NuRus.") from exc

    selected_mode = Mode(mode)
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise WorkbookReadError(f"Archivo no encontrado: {source}")
    if source.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise WorkbookReadError("Solo se admiten archivos .xls, .xlsx y .xlsm.")

    snapshot, digest = _snapshot_file(source, max_file_size_bytes=max_file_size_bytes)
    try:
        try:
            workbook = pd.ExcelFile(snapshot, engine=_engine(source))
        except ImportError as exc:
            dependency = "xlrd" if source.suffix.lower() == ".xls" else "openpyxl"
            raise WorkbookReadError(
                f"No se puede leer {source.suffix}: instala {dependency}."
            ) from exc
        except Exception as exc:
            raise WorkbookReadError(f"No se pudo abrir el libro: {exc}") from exc

        with workbook:
            names = list(workbook.sheet_names)
            if not names:
                raise WorkbookReadError("El libro no contiene hojas.")
            if sheet_name:
                primary_name = _sheet_by_name(names, sheet_name)
            elif selected_mode is Mode.CUMPLIMIENTO and any(
                name.strip().casefold() == "cumplimiento" for name in names
            ):
                primary_name = _sheet_by_name(names, "cumplimiento")
            else:
                primary_name = names[0]

            primary_headers = _headers(pd, workbook, primary_name, header_row)
            try:
                primary_mapping = map_columns(primary_headers, selected_mode)
            except ColumnMappingError as exc:
                raise WorkbookReadError(str(exc)) from exc
            primary = _records(
                _read_sheet(pd, workbook, primary_name, header_row),
                source.name,
                digest,
                primary_name,
                header_row,
            )

            warnings: list[str] = []
            cross: tuple[SourceRecord, ...] = ()
            cross_mapping: dict[str, str] = {}
            chosen = ""
            if selected_mode is Mode.CUMPLIMIENTO:
                other_names = [name for name in names if name != primary_name]
                if cross_sheet_name:
                    chosen = _sheet_by_name(other_names, cross_sheet_name)
                else:
                    named = [
                        name
                        for name in other_names
                        if name.strip().casefold() == "hoja2"
                    ]
                    if len(named) == 1:
                        chosen = named[0]
                    else:
                        candidates: list[str] = []
                        for name in other_names:
                            try:
                                headers = _headers(pd, workbook, name, header_row)
                            except WorkbookReadError:
                                continue
                            if has_full_cross_mapping(headers):
                                candidates.append(name)
                        if len(candidates) == 1:
                            chosen = candidates[0]
                        elif len(candidates) > 1:
                            warnings.append(
                                "CROSS_SHEET_AMBIGUOUS: indique la hoja de cruce explícitamente."
                            )
                if chosen:
                    cross_headers = _headers(pd, workbook, chosen, header_row)
                    try:
                        cross_mapping = map_cross_columns(cross_headers)
                    except ColumnMappingError as exc:
                        warnings.append(f"CROSS_MAPPING_AMBIGUOUS: {exc}")
                        chosen = ""
                    if chosen:
                        cross = _records(
                            _read_sheet(pd, workbook, chosen, header_row),
                            source.name,
                            digest,
                            chosen,
                            header_row,
                        )
                if not chosen:
                    warnings.append(
                        "CROSS_SHEET_NOT_SELECTED: C-10 no se evaluará sin una hoja de cruce identificable."
                    )

            return ReadBatch(
                mode=selected_mode,
                records=primary,
                cross_records=cross,
                warnings=tuple(dict.fromkeys(warnings)),
                source_path=str(source),
                workbook_name=source.name,
                workbook_sha256=digest,
                primary_sheet=primary_name,
                cross_sheet=chosen,
                header_row=header_row,
                excel_epoch=_excel_epoch(workbook),
                column_mapping=primary_mapping,
                cross_mapping=cross_mapping,
            )
    finally:
        try:
            os.unlink(snapshot)
        except OSError:
            pass
