from datetime import date
import customtkinter as ctk
from nurus.personal.config import Configuration
from nurus.personal.app import App
from nurus.personal.work import Work
from test_rus_activity import source


def test_firmas_window_can_review_one_ingreso_at_small_size(tmp_path):
    app=App(Configuration(tmp_path/'config'));app.geometry('1024x650')
    try:
        app.work=Work(app.cfg.data).analyze(source(tmp_path),'ESPERA',as_of=date(2026,10,2));app._show_work()
        app.records.selection_set(app.work.rows[0].id);window=app._open_signed_activity();app.update()
        assert window.winfo_exists()
        assert window.winfo_width()>=800
        window.destroy()
        assert all(not r.review for r in app.work.rows)
    finally:app.destroy()
