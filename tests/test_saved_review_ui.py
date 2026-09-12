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
