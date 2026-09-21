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
        # Las acciones deben estar dentro de la ventana a tamaño de PC institucional.
        app.tabs.select(app.pages['Correos']);app.update_idletasks();app.update()
        button=app.save_all_button
        assert button.winfo_ismapped()
        assert button.winfo_rootx()+button.winfo_width() <= app.winfo_rootx()+app.winfo_width()
        assert button.winfo_rooty()+button.winfo_height() <= app.winfo_rooty()+app.winfo_height()
        assert app.body.winfo_height() >= 100
        app.mail_controls.canvas.yview_moveto(1);app.update()
        assert app.mail_controls.canvas.yview()[1] >= .99
        # Nombres legibles, identidad interna estable y guardado al cambiar de plantilla.
        before=app.tpl_key.get();app.tpl_body.insert('end','\nPrueba de edición conservada.')
        other=next(k for k in app.cfg.data['correos']['plantillas'] if k!=before)
        app.tpl_key.set(other);app._load_tpl()
        assert app.cfg.data['correos']['plantillas'][before]['cuerpo'].endswith('Prueba de edición conservada.')
        app.tpl_key.set(before);app._load_tpl()
        assert app.tpl_body.get('1.0','end-1c').endswith('Prueba de edición conservada.')
        assert app.kind_box.get()==app.cfg.data['correos']['plantillas'][app.mail_kind.get()]['nombre']
        print('Cinco pestañas; botones visibles a 1024x650; cuerpo editable >=100px; scroll y guardado de plantillas OK.')
    finally:app.destroy()
