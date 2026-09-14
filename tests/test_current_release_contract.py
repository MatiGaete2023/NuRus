from pathlib import Path
import tomllib
import nurus

ROOT=Path(__file__).parents[1]

def test_release_version_and_current_docs_are_aligned():
    project=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))
    assert project['project']['version']==nurus.__version__=='0.4.0.dev5'
    current_docs=[
        ROOT/'README.md', ROOT/'docs/IMPLEMENTACION.md', ROOT/'docs/IMPLEMENTACION_PERSONAL.md',
        ROOT/'docs/CAMBIOS_USO_20260914.md', ROOT/'docs/VERIFICACION_PERSONAL.md',
        ROOT/'docs/ACEPTACION_CSMP_PERSONAL.md', ROOT/'docs/INDICE_DOCUMENTACION.md',
    ]
    for path in current_docs:
        text=path.read_text(encoding='utf-8')
        assert '0.4.0.dev5' in text, path
    readme=current_docs[0].read_text(encoding='utf-8')
    assert 'Windows/Linux' not in readme
    personal=(ROOT/'docs/IMPLEMENTACION_PERSONAL.md').read_text(encoding='utf-8')
    assert 'excepción documentada' not in personal.lower()
    assert 'Pendientes externos: PC_INFO de Laja' not in personal

def test_gitignore_covers_local_csmp_environment_and_build_outputs():
    entries=set((ROOT/'.gitignore').read_text(encoding='utf-8').splitlines())
    assert {'.venv-csmp/','dist/','build/','*.egg-info/'} <= entries
