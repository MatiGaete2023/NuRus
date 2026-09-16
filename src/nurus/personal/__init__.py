"""CSMP personal: un trabajo compartido, revisión humana y solo borradores."""

# Correcciones operativas de la rama personal. Se cargan antes de la interfaz para
# que Work, salidas, resoluciones y aliases importados por app_base usen la misma
# implementación verificada.
from . import runtime_fixes_20260916 as _runtime_fixes_20260916  # noqa: F401,E402
from . import runtime_fixes_20260916_ui as _runtime_fixes_20260916_ui  # noqa: F401,E402
from . import runtime_fixes_20260916_projects as _runtime_fixes_20260916_projects  # noqa: F401,E402
