from io import BytesIO
from types import SimpleNamespace

from openpyxl import Workbook

from nurus.personal import review_store
from nurus.personal.review_store import ReviewStore, bind, identity as intake_identity
from nurus.personal.rus_activity import _reviews_with_legacy_aliases
from nurus.personal.rus_activity import attach, mark_reviewed


def signature(fingerprint, alias, *, ambiguous=False):
    status = "huella_compuesta_ambigua_sin_id_remoto" if ambiguous else "huella_compuesta_local_sin_id_remoto"
    return {"huella": fingerprint, "identidad": f"{status};huella_legacy={alias}"}


def test_exact_unique_legacy_alias_is_dual_read_without_deleting_old_flag():
    old = "a" * 64 + ":1"
    reviewed = {old: "2026-10-01T09:00:00-03:00"}
    merged = _reviews_with_legacy_aliases([signature("stable:1", old)], reviewed)
    assert merged == {old: reviewed[old], "stable:1": reviewed[old]}
    assert reviewed == {old: "2026-10-01T09:00:00-03:00"}


def test_unmatched_legacy_hash_is_preserved_but_not_guessed_onto_changed_row():
    old = "b" * 64 + ":1"
    current = "c" * 64 + ":1"
    reviewed = {old: "2026-10-01T09:00:00-03:00"}
    merged = _reviews_with_legacy_aliases([signature("stable:1", current)], reviewed)
    assert merged == reviewed


def test_repeated_or_ambiguous_signatures_keep_multiplicity_without_alias_transfer():
    alias = "d" * 64 + ":1"
    reviewed = {alias: "2026-10-01T09:00:00-03:00"}
    candidates = [signature("stable:1", alias, ambiguous=True), signature("stable:2", alias, ambiguous=True)]
    merged = _reviews_with_legacy_aliases(candidates, reviewed)
    assert len(candidates) == 2
    assert merged == reviewed


def test_same_legacy_alias_cannot_be_assigned_to_two_current_fingerprints():
    alias = "e" * 64 + ":1"
    reviewed = {alias: "2026-10-01T09:00:00-03:00"}
    candidates = [signature("stable:1", alias), signature("stable:2", alias)]
    assert _reviews_with_legacy_aliases(candidates, reviewed) == reviewed


def work_with_sources(signatures, reviewed):
    book = Workbook()
    details = book.active
    details.title = "Resoluciones firmadas"
    details.append(("tribunal_codigo", "tribunal", "rit", "tramite", "firma", "hora", "documento", "identidad", "huella"))
    for item in signatures:
        details.append(("777", "Tribunal ficticio", "X-1-2026", "Resolución ficticia", "2026-10-01", "09:30", "DOC", item["identidad"], item["huella"]))
    coverage = book.create_sheet("SITFA_COBERTURA")
    coverage.append(("tribunal_codigo", "desde", "hasta", "estado", "criterio_temporal", "sin_coincidencias"))
    coverage.append(("777", "2026-09-01", "2026-10-31", "PARCIAL", "consulta", "Sin coincidencias en informes"))
    stream = BytesIO()
    book.save(stream)
    book.close()
    row = SimpleNamespace(id="registro-1", values={"RIT": "X-1-2026", "TRIBUNAL": "Tribunal ficticio", "SITFA_TRIBUNAL_CODIGO": "777",
        "SITFA_CAUSA_RUS": "101", "SITFA_INGRESO_RUS": "201", "SITFA_PERSONA_RUS": "301", "SITFA_CENTRO_RUS": "401",
        "SITFA_VINCULO_ESTADO": "Vinculado desde respuesta actual"})
    return SimpleNamespace(content=stream.getvalue(), rows=[row], mapping={"rit": "RIT", "tribunal": "TRIBUNAL"},
        activity_reviewed={"registro-1": dict(reviewed)}, warnings=[])


def test_attach_dual_reads_exact_legacy_alias_and_preserves_both_keys():
    old = "f" * 64 + ":1"
    work = work_with_sources([signature("stable:1", old)], {old: "2026-10-01T09:00:00-03:00"})
    attach(work)
    assert work.signed_activity["registro-1"]["pendientes"] == 0
    assert work.activity_reviewed["registro-1"] == {old: "2026-10-01T09:00:00-03:00", "stable:1": "2026-10-01T09:00:00-03:00"}


def test_attach_keeps_changed_legacy_hash_unresolved_and_does_not_drop_it():
    old = "1" * 64 + ":1"
    current = "2" * 64 + ":1"
    work = work_with_sources([signature("stable:1", current)], {old: "2026-10-01T09:00:00-03:00"})
    attach(work)
    assert work.signed_activity["registro-1"]["pendientes"] == 1
    assert work.activity_reviewed["registro-1"] == {old: "2026-10-01T09:00:00-03:00"}
    assert "Revisiones heredadas sin vínculo seguro: 1" in work.signed_activity["registro-1"]["valores"]["DETALLE"]


def test_ambiguous_multiplicity_stays_pending_after_source_order_changes():
    first = signature("stable:1", "a" * 64 + ":1", ambiguous=True)
    second = signature("stable:2", "b" * 64 + ":1", ambiguous=True)
    for ordered in ([first, second], [second, first]):
        work = work_with_sources(ordered, {"stable:1": "2026-10-01T09:00:00-03:00"})
        attach(work)
        entry = work.signed_activity["registro-1"]
        assert len(entry["firmas"]) == 2
        assert entry["pendientes"] == 2
        assert "Firmas con identidad ambigua: 2" in entry["valores"]["DETALLE"]
        try:
            mark_reviewed(work, "registro-1", "stable:1")
        except ValueError as error:
            assert "identidad única" in str(error)
        else:
            raise AssertionError("No debe persistirse la revisión de una firma ambigua.")


def test_bind_promotes_only_exact_alias_and_keeps_legacy_json_entry(monkeypatch):
    old = "9" * 64 + ":1"
    timestamp = "2026-10-01T09:00:00-03:00"
    work = work_with_sources([signature("stable:1", old)], {old: timestamp})
    key, kind = intake_identity(work, work.rows[0])
    assert kind == "ingreso_real"
    data = {"version": 1, "ingresos": {key: {"alcance": kind, "firmas": {old: timestamp}}}}
    writes = []
    monkeypatch.setattr(ReviewStore, "read", lambda _self: data)
    monkeypatch.setattr(review_store, "atomic_json", lambda path, value: writes.append((path, value.copy())))

    bind(work, "not-written/revisiones_firmas.json")

    stable = work.signed_activity["registro-1"]["firmas"][0]["huella"]
    assert data["ingresos"][key]["firmas"] == {old: timestamp, stable: timestamp}
    assert len(writes) == 1
    assert writes[0][1]["ingresos"][key]["firmas"][old] == timestamp


def test_bind_does_not_promote_changed_or_ambiguous_alias(monkeypatch):
    old = "8" * 64 + ":1"
    timestamp = "2026-10-01T09:00:00-03:00"
    for signatures in ([signature("stable:1", "7" * 64 + ":1")], [signature("stable:1", old, ambiguous=True)]):
        work = work_with_sources(signatures, {old: timestamp})
        key, kind = intake_identity(work, work.rows[0])
        data = {"version": 1, "ingresos": {key: {"alcance": kind, "firmas": {old: timestamp}}}}
        writes = []
        monkeypatch.setattr(ReviewStore, "read", lambda _self, data=data: data)
        monkeypatch.setattr(review_store, "atomic_json", lambda path, value: writes.append(value))
        bind(work, "not-written/revisiones_firmas.json")
        assert data["ingresos"][key]["firmas"] == {old: timestamp}
        assert writes == []


def test_bind_reports_failed_promotion_without_losing_in_session_match(monkeypatch):
    old = "6" * 64 + ":1"
    timestamp = "2026-10-01T09:00:00-03:00"
    work = work_with_sources([signature("stable:1", old)], {old: timestamp})
    key, kind = intake_identity(work, work.rows[0])
    data = {"version": 1, "ingresos": {key: {"alcance": kind, "firmas": {old: timestamp}}}}
    monkeypatch.setattr(ReviewStore, "read", lambda _self: data)

    def fail_write(_path, _value):
        raise PermissionError("solo prueba")

    monkeypatch.setattr(review_store, "atomic_json", fail_write)
    bind(work, "not-written/revisiones_firmas.json")

    assert work.signed_activity["registro-1"]["pendientes"] == 0
    assert any("No se pudo guardar la nueva huella" in warning for warning in work.warnings)
    assert data["ingresos"][key]["firmas"][old] == timestamp
