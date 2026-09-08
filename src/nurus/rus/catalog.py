from __future__ import annotations

import json
from pathlib import Path


class CatalogError(ValueError):
    pass


def default_catalog_path() -> Path:
    return Path(__file__).with_name("textos_observaciones.json")


def load_catalog(path: str | Path | None = None) -> dict[str, dict[str, dict[str, object]]]:
    catalog_path = Path(path) if path else default_catalog_path()
    try:
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CatalogError(f"No se pudo abrir el catálogo: {catalog_path}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"El catálogo no contiene JSON válido: {exc}") from exc
    if not isinstance(raw, dict):
        raise CatalogError("El catálogo debe contener un objeto JSON.")
    return raw


def render(catalog: dict, scope: str, key: str, **values: str) -> str:
    try:
        text = catalog[scope][key]["texto"]
    except (KeyError, TypeError) as exc:
        raise CatalogError(f"Texto no definido: {scope}.{key}") from exc
    try:
        return str(text).format_map(values)
    except KeyError as exc:
        raise CatalogError(f"Falta el campo {exc.args[0]} para {scope}.{key}") from exc
