"""Prueba de ventana real en Windows; no inicia Office ni usa archivos del usuario."""
from tempfile import TemporaryDirectory
from pathlib import Path
from nurus.personal.config import Configuration
from nurus.personal.app import App

with TemporaryDirectory() as directory:
    app=App(Configuration(Path(directory)))
    try:
        app.update_idletasks();app.update()
        assert len(app.tabs.tabs())==5
        for tab in app.tabs.tabs():
            app.tabs.select(tab);app.update_idletasks();app.update()
            assert app.nametowidget(tab).winfo_ismapped()
        assert app.template_dir.is_dir()
        assert len(list(app.template_dir.rglob('*.docx')))>=5
        assert len(app.modality_vars)==4
        assert all(v.get() for v in app.modality_vars.values())
        assert app.project_editor.winfo_exists()
        assert app.observation_editor.winfo_exists()
        app.geometry('1024x650');app.update_idletasks();app.update()
        print('Cinco pestañas creadas, recursos Word disponibles y ventana redimensionada.')
    finally:app.destroy()
