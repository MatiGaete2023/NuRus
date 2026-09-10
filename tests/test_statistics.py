from datetime import date

from openpyxl import load_workbook

from nurus.services.statistics import ReviewStatistics, export_review_statistics


def test_statistics_export_keeps_raw_administrative_values(tmp_path):
    stats = ReviewStatistics(
        start=date(2026, 9, 1), end=date(2026, 9, 30),
        total_records=8, reviewed_in_period=5, excluded=1,
        outside_period=1, missing_or_invalid_date=1, observations_changed=2,
        tt_values=(("Sí", 3), ("(vacío)", 2)),
        workload_values=(("Con carga", 4), ("Sin carga", 1)),
        resolution_values=(("No", 5),),
    )
    path = export_review_statistics(stats, tmp_path / "estadisticas.xlsx")
    book = load_workbook(path)
    assert dict(book["Resumen"].values)["Revisados en período"] == 5
    assert dict(book["CC"].values)["Con carga"] == 4
    assert dict(book["TT"].values)["Sí"] == 3
