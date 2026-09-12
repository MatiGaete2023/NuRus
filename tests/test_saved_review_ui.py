from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from nurus.app import NuRusApp


def test_saved_review_uses_remembered_path_without_file_picker(tmp_path, monkeypatch):
    path = tmp_path / "review.xlsx"
    path.touch()
    app = SimpleNamespace(current_batch_id="batch", db=Mock(), import_reviewed_excel=Mock())
    app.db.get_working_workbook.return_value = path
    picker = Mock(side_effect=AssertionError("No debe pedir el archivo otra vez"))
    monkeypatch.setattr("nurus.app.filedialog.askopenfilename", picker)
    monkeypatch.setattr("nurus.app.messagebox.askyesno", lambda *args, **kwargs: True)
    NuRusApp.use_saved_review(app)
    app.import_reviewed_excel.assert_called_once_with(path=path, freeze_when_ready=True)
    picker.assert_not_called()


def test_missing_working_copy_does_not_import_or_guess(tmp_path, monkeypatch):
    app = SimpleNamespace(current_batch_id="batch", db=Mock(), import_reviewed_excel=Mock())
    app.db.get_working_workbook.return_value = tmp_path / "moved.xlsx"
    warning = Mock()
    monkeypatch.setattr("nurus.app.messagebox.showwarning", warning)
    NuRusApp.use_saved_review(app)
    app.import_reviewed_excel.assert_not_called()
    warning.assert_called_once()


def test_cancelled_working_copy_confirmation_does_nothing(tmp_path, monkeypatch):
    path = tmp_path / "review.xlsx"
    path.touch()
    app = SimpleNamespace(current_batch_id="batch", db=Mock(), import_reviewed_excel=Mock())
    app.db.get_working_workbook.return_value = path
    monkeypatch.setattr("nurus.app.messagebox.askyesno", lambda *args, **kwargs: False)
    NuRusApp.use_saved_review(app)
    app.import_reviewed_excel.assert_not_called()


def test_resume_restores_same_batch_without_original_or_reanalysis(tmp_path):
    from test_review_import import _proposal
    db, controller, batch_id, proposal = _proposal(tmp_path)
    batch = db.get_batch(batch_id)
    Path(batch["source_path"]).unlink()
    original_evaluation = batch["evaluation_hash"]
    app = SimpleNamespace(
        analysis_busy=False, io_busy=False, db=db, controller=controller,
        _invalidate_analysis=Mock(), mode_var=Mock(), file_var=Mock(),
        _show_review_rows=Mock(), analysis_status=Mock(), tabs=Mock(), work=object(),
    )
    assert NuRusApp.resume_batch(app, batch_id)
    assert app.current_batch_id == batch_id
    assert app.selected_sheet == "Espera"
    assert db.get_working_workbook(batch_id) == proposal
    assert db.get_batch(batch_id)["evaluation_hash"] == original_evaluation
    assert len(db.list_batches()) == 1
    app._show_review_rows.assert_called_once()
    app.tabs.select.assert_called_once_with(app.work)


def test_resume_does_not_replace_current_work_while_io_busy(monkeypatch):
    app = SimpleNamespace(analysis_busy=False, io_busy=True, db=Mock())
    monkeypatch.setattr("nurus.app.messagebox.showwarning", Mock())
    assert not NuRusApp.resume_batch(app, "batch")
    app.db.get_batch.assert_not_called()
