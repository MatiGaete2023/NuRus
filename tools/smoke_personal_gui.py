"""Prueba de ventana real bajo Xvfb; no inicia Office ni usa archivos del usuario."""
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
        assert len(list(app.template_dir.rglob('*.docx')))==5
        app.geometry('1024x650');app.update_idletasks();app.update()
        print('Cinco pestañas creadas, recursos Word disponibles y ventana redimensionada.')
    finally:app.destroy()
