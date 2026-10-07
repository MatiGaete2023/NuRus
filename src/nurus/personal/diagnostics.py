"""Identify the exact CSMP installation that is currently running."""
from pathlib import Path
import sys


def installation_info(*,executable=None,personal_module=None,frozen=None,version=None,commit=None):
    import nurus
    import nurus.personal as personal
    executable=Path(executable or sys.executable).resolve()
    personal_module=Path(personal_module or personal.__file__).resolve()
    frozen=bool(getattr(sys,'frozen',False)) if frozen is None else bool(frozen)
    version=version or nurus.__version__
    if commit is None:
        try:from ._build_meta import BUILD_COMMIT
        except ImportError:BUILD_COMMIT='unknown'
        commit=BUILD_COMMIT
    if frozen:origin='EXE congelado'
    elif 'site-packages' in {part.lower() for part in personal_module.parts}:origin='Paquete instalado'
    else:origin='Código fuente'
    return {'version':str(version),'commit':str(commit or 'unknown'),'origin':origin,
            'executable':str(executable),'module':str(personal_module)}


def format_installation_info(info):
    commit=info['commit'][:12] if info['commit'] not in ('','unknown') else 'No declarado'
    return '\n'.join((f"Versión: {info['version']}",f"Commit fuente: {commit}",
        f"Origen: {info['origin']}",f"Ejecutable/intérprete: {info['executable']}",
        f"Módulo CSMP cargado: {info['module']}"))
