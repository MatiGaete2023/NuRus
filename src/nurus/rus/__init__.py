"""Lectura y evaluación trazable de las planillas RUS.

El paquete no escribe en SATURNO ni envía comunicaciones.  Produce
resultados revisables, con su procedencia de planilla conservada.
"""

from .models import Mode, SourceReference
from .reader import read_workbook
from .service import evaluate_batch

__all__ = ["Mode", "SourceReference", "evaluate_batch", "read_workbook"]
