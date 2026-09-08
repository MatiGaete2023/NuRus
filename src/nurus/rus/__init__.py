"""Lectura y evaluación trazable de las planillas RUS.

El paquete no escribe en SATURNO ni envía comunicaciones. Produce resultados
revisables con procedencia de archivo, hash, hoja y fila.
"""

from .models import EvaluationBatch, EvaluationStatus, Mode, SourceReference
from .reader import WorkbookReadError, read_workbook
from .service import evaluate_batch

__all__ = [
    "EvaluationBatch",
    "EvaluationStatus",
    "Mode",
    "SourceReference",
    "WorkbookReadError",
    "evaluate_batch",
    "read_workbook",
]
