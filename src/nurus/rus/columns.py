from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode()
    text = re.sub(r"[-().]+", " ", text.lower().strip())
    return re.sub(r"\s+", " ", text)


COMMON: dict[str, tuple[str, ...]] = {
    "programa": ("DERIVACION", "DERIVACIÓN", "PROGRAMA", "NOMBRE CENTRO"),
    "tribunal": ("TRIBUNAL",),
    "nombre": ("NOMBRE", "NOMBRE COMPLETO", "NOMBRE MENOR"),
    "nacimiento": ("FEC. NACIMIENTO", "FEC.NACIMIENTO", "FECHA NACIMIENTO", "FEC NACIMIENTO"),
    "curador": ("CURADOR", "CURADOR AD LITEM", "CURADOR AD-LITEM", "CURADOR AD LITEM.", "CUR. AD LITEM", "CURADOR/A AD LITEM", "CURADOR/A AD-LITEM"),
    "oido": ("FEC. OIDO", "FEC.OIDO", "FEC OIDO", "FECHAOIDO", "FEC. OÍDO", "FEC.OÍDO"),
    "resolucion": ("FEC. RESOLUCIÓN", "FEC.RESOLUCIÓN", "FEC. RESOLUCION", "FEC.RESOLUCION", "FECHA RESOLUCION", "FEC RESOLUCION"),
    "prox_aud": ("PROXS. AUDS.", "PROXS AUDS", "PROX AUD", "PROXIMA AUDIENCIA", "PRÓXIMA AUDIENCIA", "PROX. AUD.", "PROX. AUDS."),
    "rit": ("RIT",),
    "rut": ("RUT", "RUT MENOR", "RUT NNA", "RUT LITIGANTE"),
}

MODE_COLUMNS: dict[Mode | str, dict[str, tuple[str, ...]]] = {
    "ESPERA": {"espera": ("T ESPERA", "T_ESPERA", "DIAS_ESPERA", "TESPERA", "DÍAS DE ESPERA", "DIAS DE ESPERA")},
    "CUMPLIMIENTO": {
        "dias_cumpl": ("DIAS DE CUMPLIMIENTO", "DÍAS DE CUMPLIMIENTO", "DIAS CUMPLIMIENTO"),
        "dias_egresar": ("DIAS PARA EGRESAR", "DÍAS PARA EGRESAR", "DIAS EGRESAR"),
        "ingreso": ("FEC.INGRESO EFECTIVO", "FEC. INGRESO EFECTIVO", "FEC INGRESO EFECTIVO"),
        "egreso_proy": ("FEC.EGRESO PROYECTADO", "FEC. EGRESO PROYECTADO", "FEC EGRESO PROYECTADO"),
        "ficha_fae": ("FEC.ACT.F.FAE", "FEC. ACT. F. FAE", "FEC ACT F FAE", "FEC.ACT.F.FAE/FAS", "FEC. ACT. F. FAE/FAS"),
        "ficha_ind": ("FEC.ACT.F.INDIVIDUAL", "FEC. ACT. F. INDIVIDUAL", "FEC ACT F INDIVIDUAL"),
    },
    "INFORMES": {
        "vencimiento": ("FECHA VENCIMIENTO", "FEC.VENCIMIENTO", "FEC. VENCIMIENTO"),
        "ingreso": ("FEC.INGRESO EFECTIVO", "FEC. INGRESO EFECTIVO", "FECHA INGRESO"),
    },
}

H2_COLUMNS: dict[str, tuple[str, ...]] = {
    "rit": ("RIT",), "rut": ("RUT MENOR", "RUT"), "nombre": ("NOMBRE MENOR", "NOMBRE"),
    "tribunal": ("TRIBUNAL",), "programa": ("NOMBRE CENTRO", "DERIVACION", "DERIVACIÓN"),
    "vencimiento": ("FECHA VENCIMIENTO", "FEC.VENCIMIENTO", "FEC. VENCIMIENTO"),
}


def map_columns(headers: Iterable[str], mode: str) -> dict[str, str]:
    by_normalized = {normalize(header): str(header) for header in headers}
    aliases = {**COMMON, **MODE_COLUMNS[mode]}
    return {key: by_normalized[normalize(alias)] for key, names in aliases.items() for alias in names if normalize(alias) in by_normalized}


def map_cross_columns(headers: Iterable[str]) -> dict[str, str]:
    by_normalized = {normalize(header): str(header) for header in headers}
    return {key: by_normalized[normalize(alias)] for key, names in H2_COLUMNS.items() for alias in names if normalize(alias) in by_normalized}


def has_full_cross_mapping(headers: Iterable[str]) -> bool:
    return set(map_cross_columns(headers)) == set(H2_COLUMNS)
