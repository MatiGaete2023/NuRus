from __future__ import annotations

import os
import json
import queue
import threading
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from nurus.domain.models import Product, ProductKind, Template
from nurus.product_ui import communications_dialog, review_product
from nurus.services.contacts import _valid_addresses, apply_contact_preview, preview_contact_import
from nurus.services.exports import ExportError, export_preserved_workbook, export_proposal_workbook
from nurus.rus import Mode
from nurus.rus.reader import list_workbook_sheets
from nurus.services.products import approve_product, persist_approved_product, prepare_from_snapshot
from nurus.services.review_import import (
    ReviewImportError,
    import_reviewed_workbook,
    preview_reviewed_workbook,
)
from nurus.services.rendering import prepare
from nurus.services.resolutions import prepare_resolution
from nurus.services.workflow import ReviewRow, WorkController
from nurus.storage.database import Database


def data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(root) / "NuRus"


class NuRusApp(ttk.Frame):
    def __init__(self, root: tk.Tk, db: Database) -> None:
        super().__init__(root, padding=12)
        self.root, self.db = root, db
        self.controller = WorkController(db)
        self.current: Product | None = None
        self.selected_path: Path | None = None
        self.current_batch_id = ""
        self.analysis_generation = 0
        self.analysis_queue: queue.Queue[tuple[int, object, Exception | None]] = queue.Queue()
        self.analysis_busy = False
        self.io_busy = False
        self.review_by_id: dict[str, ReviewRow] = {}

        root.title("NuRus · CSMP")
        root.minsize(900, 620)
        self.pack(fill="both", expand=True)
        self._style()
        self._build()

    def _style(self) -> None:
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", foreground="#536476")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _build(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="NuRus", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Analiza, propone e incorpora constancias con control humano. NuRus nunca envía correos.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        self.work = ttk.Frame(self.tabs, padding=8)
        self.templates = ttk.Frame(self.tabs, padding=12)
        self.contacts = ttk.Frame(self.tabs, padding=12)
        self.history = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.work, text="Trabajo")
        self.tabs.add(self.history, text="Historial")
        self.tabs.add(self.templates, text="Plantillas")
        self.tabs.add(self.contacts, text="Contactos")
        self._work_tab()
        self._templates_tab()
        self._contacts_tab()
        self._history_tab()
        self.counter = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.counter, text="Contador")
        ttk.Label(self.counter, text="Correos enviados", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.counter,
            text="Consulta de solo lectura por período; no abre cuerpos ni modifica Outlook.",
        ).pack(anchor="w", pady=8)
        ttk.Button(self.counter, text="Consultar período…", command=self.count_mail).pack(anchor="w")
        self.counter_status = tk.StringVar(value="Sin consulta ejecutada.")
        ttk.Label(self.counter, textvariable=self.counter_status, wraplength=800).pack(anchor="w", pady=12)

    def run_io(self, job, success) -> None:
        if self.io_busy:
            messagebox.showwarning("Operación en curso", "Espera a que termine la operación actual.")
            return
        self.io_busy = True
        output = queue.Queue()

        def worker():
            try:
                output.put((job(), None))
            except Exception as exc:
                output.put((None, exc))

        def poll():
            try:
                result, error = output.get_nowait()
            except queue.Empty:
                self.root.after(100, poll)
                return
            self.io_busy = False
            if error:
                messagebox.showerror("Operación no confirmada", str(error))
            else:
                success(result)

        threading.Thread(target=worker, daemon=True, name="NuRusSerialIO").start()
        self.root.after(100, poll)

    def count_mail(self) -> None:
        from nurus.adapters.sent_mail import count_sent_mail, export_sent_report

        start = simpledialog.askstring("Contador", "Desde (AAAA-MM-DD):", parent=self.root)
        if start is None:
            return
        end = simpledialog.askstring("Contador", "Hasta inclusive (AAAA-MM-DD):", parent=self.root)
        if end is None:
            return
        account = simpledialog.askstring(
            "Contador", "Cuenta SMTP exacta (vacío = predeterminada):", parent=self.root
        )
        if account is None:
            return
        try:
            first, last = date.fromisoformat(start), date.fromisoformat(end)
            if first > last:
                raise ValueError("Período invertido.")
        except ValueError as exc:
            messagebox.showerror("Fechas", str(exc))
            return
        self.counter_status.set("Consultando Enviados…")

        def done(report):
            self.counter_status.set(
                f"{len(report.rows)} correos · {report.skipped} omitidos · {report.errors} errores · "
                + ("consulta parcial" if report.truncated else "consulta terminada")
            )
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
            )
            if path:
                self.run_io(
                    lambda: export_sent_report(report, path),
                    lambda saved: messagebox.showinfo("Contador", f"Reporte guardado en {saved}"),
                )

        self.run_io(lambda: count_sent_mail(first, last, account_key=account or None), done)

    # ---------- Trabajo ----------
    def _work_tab(self) -> None:
        ttk.Label(
            self.work,
            text="1 Analizar  ·  2 Revisar en Excel / RUS  ·  3 Preparar productos",
            style="Title.TLabel",
        ).pack(anchor="w")
        self.work_tabs = ttk.Notebook(self.work)
        self.work_tabs.pack(fill="both", expand=True, pady=(6, 0))
        self.rus_tab = ttk.Frame(self.work_tabs, padding=8)
        self.particular_tab = ttk.Frame(self.work_tabs, padding=8)
        self.work_tabs.add(self.rus_tab, text="Análisis RUS")
        self.work_tabs.add(self.particular_tab, text="Comunicación particular")
        self._rus_work_tab()
        self._particular_work_tab()

    def _rus_work_tab(self) -> None:
        source = ttk.LabelFrame(self.rus_tab, text="Archivo de trabajo", padding=8)
        source.pack(fill="x")
        self.mode_var = tk.StringVar(value=Mode.ESPERA.value)
        self.selected_sheet = ""
        self.selected_cross_sheet = ""
        self.selected_header_row = 1
        ttk.Label(source, text="Modalidad").grid(row=0, column=0, sticky="w")
        self.mode_combo = ttk.Combobox(
            source,
            textvariable=self.mode_var,
            state="readonly",
            values=[mode.value for mode in Mode],
            width=18,
        )
        self.mode_combo.grid(row=0, column=1, sticky="w", padx=(6, 12))
        self.mode_combo.bind("<<ComboboxSelected>>", lambda _event: self._invalidate_analysis("Modalidad cambiada; analiza nuevamente."))

        self.file_var = tk.StringVar(value="Sin archivo seleccionado.")
        ttk.Label(source, textvariable=self.file_var).grid(row=0, column=2, sticky="ew")
        ttk.Button(source, text="Elegir archivo", command=self.choose_file).grid(row=0, column=3, padx=6)
        self.analyze_button = ttk.Button(source, text="Analizar archivo", style="Primary.TButton", command=self.analyze_file)
        self.analyze_button.grid(row=0, column=4)
        source.columnconfigure(2, weight=1)

        self.analysis_status = tk.StringVar(value="Selecciona un Excel. Seleccionar no equivale a analizar.")
        ttk.Label(source, textvariable=self.analysis_status, style="Subtitle.TLabel").grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(6, 0)
        )
        options = ttk.Frame(source)
        options.grid(row=2, column=0, columnspan=5, sticky="w", pady=(4, 0))
        ttk.Button(options, text="Hojas y encabezado…", command=self.choose_sheets).pack(side="left")
        ttk.Button(options, text="Retomar lote…", command=self.choose_previous_batch).pack(side="left", padx=6)

        self.review_pane = ttk.Panedwindow(self.rus_tab, orient="vertical")
        self.review_pane.pack(fill="both", expand=True, pady=(8, 0))

        table_frame = ttk.Frame(self.review_pane)
        detail_frame = ttk.LabelFrame(self.review_pane, text="Detalle de la propuesta del motor", padding=8)
        self.review_pane.add(table_frame, weight=3)
        self.review_pane.add(detail_frame, weight=2)

        columns = ("decision", "rit", "tribunal", "programa", "observacion")
        self.review_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for key, title, width in [
            ("decision", "Estado", 90),
            ("rit", "RIT", 100),
            ("tribunal", "Tribunal", 150),
            ("programa", "Programa", 180),
            ("observacion", "Observación", 420),
        ]:
            self.review_tree.heading(key, text=title)
            self.review_tree.column(key, width=width, stretch=key == "observacion")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.review_tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.review_tree.xview)
        self.review_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.review_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.review_tree.bind("<<TreeviewSelect>>", self._load_selected_review)
        self.review_tree.tag_configure("excluded", background="#FFF2CC")
        self.review_tree.tag_configure("blocked", background="#F8D7DA")
        self.review_tree.tag_configure("approved", background="#D9EAD3")
        self.review_tree.tag_configure("pending", background="#D9EAF7")

        self.review_summary = tk.StringVar(value="Sin análisis.")
        ttk.Label(detail_frame, textvariable=self.review_summary).pack(anchor="w")
        self.review_meta = tk.StringVar(value="Selecciona una fila para ver su procedencia y reglas.")
        ttk.Label(detail_frame, textvariable=self.review_meta, style="Subtitle.TLabel").pack(anchor="w", pady=(2, 4))
        self.observation_edit = tk.Text(detail_frame, height=5, wrap="word", state="disabled")
        self.observation_edit.pack(fill="both", expand=True)

        actions = ttk.Frame(detail_frame)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(
            actions, text="Congelar constancia", style="Primary.TButton",
            command=self.approve_current_batch,
        ).pack(side="right")
        ttk.Button(actions, text="Documentar excepción de cruce", command=self.document_cross_sheet_exception).pack(side="right", padx=(0, 6))
        ttk.Button(actions, text="Usar revisión guardada", command=self.use_saved_review).pack(side="right", padx=(0, 6))
        ttk.Button(actions, text="Elegir otra copia…", command=self.import_reviewed_excel).pack(side="right", padx=(0, 6))
        ttk.Button(actions, text="Exportar propuestas", command=self.export_current_workbook).pack(side="right", padx=(0, 6))
        outputs = ttk.Frame(self.rus_tab)
        outputs.pack(fill="x", pady=(4, 0))
        ttk.Button(outputs, text="Exportar constancia final…", command=self.export_final_workbook).pack(side="left")
        ttk.Button(outputs, text="Correos agrupados…", command=lambda: communications_dialog(self)).pack(side="left", padx=4)
        ttk.Button(outputs, text="Proyecto de la fila…", command=self.resolution_dialog).pack(side="left", padx=4)
        ttk.Button(outputs, text="Estadísticas…", command=self.export_statistics).pack(side="left")
        ttk.Button(outputs, text="Otro producto…", command=self.open_product_dialog).pack(side="left")

    def choose_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xlsm *.xls"), ("Todos", "*.*")])
        if not path:
            return
        self.selected_path = Path(path)
        self.selected_sheet, self.selected_cross_sheet, self.selected_header_row = "", "", 1
        self.file_var.set(f"{self.selected_path.name} · seleccionado, sin analizar")
        self._invalidate_analysis("Archivo seleccionado. Presiona «Analizar archivo».", keep_file=True)

    def choose_sheets(self) -> None:
        if self.selected_path is None:
            messagebox.showwarning("Falta archivo", "Selecciona un Excel primero.")
            return
        source = self.selected_path
        generation = self.analysis_generation

        def display(names):
            if generation != self.analysis_generation or self.selected_path != source:
                return
            dialog = tk.Toplevel(self.root)
            dialog.title("Seleccionar hojas del libro")
            dialog.transient(self.root)
            dialog.grab_set()
            primary = ttk.Combobox(dialog, state="readonly", values=("Automática", *names), width=45)
            cross = ttk.Combobox(dialog, state="readonly", values=("Automática", *names), width=45)
            header = tk.StringVar(value=str(self.selected_header_row))
            for label, field, value in (("Hoja principal", primary, self.selected_sheet),
                                         ("Cruce (solo Cumplimiento)", cross, self.selected_cross_sheet)):
                ttk.Label(dialog, text=label).pack(anchor="w", padx=12, pady=(8, 2))
                field.pack(fill="x", padx=12)
                field.set(value or "Automática")
            ttk.Label(dialog, text="Fila de encabezado principal (1 permite detección automática)").pack(padx=12, pady=(8, 2))
            ttk.Entry(dialog, textvariable=header).pack(fill="x", padx=12)

            def accept():
                try:
                    row = int(header.get())
                    if row < 1:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Encabezado", "Indica un número de fila positivo.", parent=dialog)
                    return
                self.selected_sheet = "" if primary.current() == 0 else primary.get()
                self.selected_cross_sheet = "" if cross.current() == 0 else cross.get()
                self.selected_header_row = row
                self._invalidate_analysis("Selección de hojas guardada; presiona Analizar archivo.")
                dialog.destroy()

            ttk.Button(dialog, text="Usar selección", command=accept).pack(padx=12, pady=12)

        self.run_io(lambda: list_workbook_sheets(source), display)

    def choose_previous_batch(self) -> None:
        if self.analysis_busy or self.io_busy:
            messagebox.showwarning("Operación en curso", "Espera a que termine antes de retomar otro lote.")
            return
        batches = self.db.list_batches()
        if not batches:
            messagebox.showinfo("Sin lotes", "Todavía no hay análisis guardados.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Retomar análisis guardado")
        dialog.geometry("820x380")
        listing = ttk.Treeview(dialog, columns=("fecha", "archivo", "modo", "filas"), show="headings")
        for key, title, width in (("fecha", "Fecha", 150), ("archivo", "Archivo", 360),
                                  ("modo", "Modalidad", 140), ("filas", "Registros", 80)):
            listing.heading(key, text=title)
            listing.column(key, width=width)
        listing.pack(fill="both", expand=True, padx=10, pady=10)
        for batch in batches:
            listing.insert("", "end", iid=batch["id"], values=(batch["created_at"], batch["source_name"],
                                                                batch["mode"], batch["record_count"]))

        def accept():
            chosen = listing.selection()
            if chosen and self.resume_batch(chosen[0]):
                dialog.destroy()

        ttk.Button(dialog, text="Retomar seleccionado", command=accept).pack(pady=10)

    def resume_batch(self, batch_id: str) -> bool:
        if self.analysis_busy or self.io_busy:
            messagebox.showwarning("Operación en curso", "Espera a que termine la operación actual.")
            return False
        try:
            batch = self.db.get_batch(batch_id)
            if batch is None or batch["mode"] not in {mode.value for mode in Mode}:
                raise ValueError("No existe un lote RUS recuperable.")
            self.db.get_original_workbook(batch_id)  # comprueba bytes y hash almacenados
            if batch["status"] == "approved":
                self.db.get_snapshot(batch_id)
            rows = self.controller.load_rows(batch_id)
        except (KeyError, ValueError) as exc:
            messagebox.showerror("No se pudo retomar", str(exc))
            return False
        self._invalidate_analysis("Recuperando lote guardado…")
        self.current_batch_id = batch_id
        self.selected_path = Path(batch["source_path"])
        self.selected_sheet = batch["primary_sheet"]
        self.selected_cross_sheet = batch["cross_sheet"]
        self.selected_header_row = int(batch["header_row"])
        self.mode_var.set(batch["mode"])
        self.file_var.set(f"{batch['source_name']} · lote recuperado")
        self._show_review_rows(rows)
        copy = self.db.get_working_workbook(batch_id)
        self.analysis_status.set(
            "Lote recuperado sin recalcular las reglas. "
            + (f"Copia de revisión: {copy}" if copy else "Aún no hay copia de revisión recordada.")
        )
        self.tabs.select(self.work)
        return True

    def _invalidate_analysis(self, message: str, *, keep_file: bool = True) -> None:
        self.analysis_generation += 1
        self.current_batch_id = ""
        self.review_by_id.clear()
        self.review_summary.set("Sin análisis vigente.")
        self.review_meta.set("Selecciona y analiza un archivo.")
        self._set_observation_text("")
        for item in self.review_tree.get_children():
            self.review_tree.delete(item)
        self.analysis_status.set(message)
        if not keep_file:
            self.selected_path = None

    def analyze_file(self) -> None:
        if self.analysis_busy:
            return
        if self.selected_path is None:
            messagebox.showwarning("Falta archivo", "Selecciona un archivo Excel antes de analizar.")
            return
        path = self.selected_path
        mode = self.mode_var.get()
        selected_sheet = self.selected_sheet or None
        selected_cross = self.selected_cross_sheet or None
        selected_header = self.selected_header_row
        self._invalidate_analysis("Analizando copia estable del archivo…", keep_file=True)
        generation = self.analysis_generation
        self.analysis_busy = True
        self.analyze_button.configure(state="disabled")
        self.analysis_status.set("Analizando copia estable del archivo…")

        def worker() -> None:
            try:
                result = self.controller.analyze(path, mode, sheet_name=selected_sheet,
                                                 cross_sheet_name=selected_cross, header_row=selected_header)
                self.analysis_queue.put((generation, result, None))
            except Exception as exc:
                self.analysis_queue.put((generation, None, exc))

        threading.Thread(target=worker, name="NuRusExcelAnalysis", daemon=True).start()
        self.root.after(100, self._poll_analysis)

    def _poll_analysis(self) -> None:
        try:
            generation, result, error = self.analysis_queue.get_nowait()
        except queue.Empty:
            if self.analysis_busy:
                self.root.after(100, self._poll_analysis)
            return

        if generation != self.analysis_generation:
            if self.analysis_queue.empty():
                self.analysis_busy = False
                self.analyze_button.configure(state="normal")
            return

        self.analysis_busy = False
        self.analyze_button.configure(state="normal")
        if error is not None:
            self.analysis_status.set("No se pudo completar el análisis.")
            messagebox.showerror("Error de análisis", str(error))
            return

        batch = result
        self.current_batch_id = batch.batch_id
        if self.mode_var.get() != batch.mode.value:
            self.mode_var.set(batch.mode.value)
        self.file_var.set(f"{batch.workbook_name} · analizado")
        rows = self.controller.rows_from_batch(batch)
        self._show_review_rows(rows)
        warning = f" · {len(batch.warnings)} advertencia(s)" if batch.warnings else ""
        cross_notice = ""
        detection_notice = ""
        if any(item.startswith("MODE_AND_SHEET_AUTODETECTED") for item in batch.warnings):
            detection_notice = f" · detectado como {batch.mode.value} ({batch.primary_sheet})"
        if any(item.startswith("CROSS_SHEET_NOT_SELECTED") for item in batch.warnings):
            cross_notice = " · requiere excepción documentada de hoja de cruce"
        self.analysis_status.set(
            f"Analizado: {batch.workbook_name} · SHA-256 {batch.workbook_sha256[:12]}…"
            f"{detection_notice}{warning}{cross_notice}"
        )

    def _show_review_rows(self, rows: tuple[ReviewRow, ...]) -> None:
        labels = {
            "pending": "Propuesta",
            "blocked": "Requiere atención",
            "approved": "Con constancia",
            "excluded": "Excluido",
        }
        self.review_by_id = {row.record_id: row for row in rows}
        for item in self.review_tree.get_children():
            self.review_tree.delete(item)
        for row in rows:
            observation = " ".join(row.observation.split())
            self.review_tree.insert(
                "", "end", iid=row.record_id,
                values=(labels.get(row.decision, row.decision), row.rit, row.tribunal, row.programa, observation),
                tags=(row.decision,),
            )
        counts: dict[str, int] = {}
        for row in rows:
            counts[row.decision] = counts.get(row.decision, 0) + 1
        summary = " · ".join(
            f"{labels.get(key, key)}: {value}" for key, value in sorted(counts.items())
        ) or "sin filas"
        self.review_summary.set(f"{len(rows)} fila(s) · {summary}")
        self.review_meta.set("Selecciona una fila para revisar procedencia, reglas e incidencias.")
        self._set_observation_text("")

    def _set_observation_text(self, value: str) -> None:
        self.observation_edit.configure(state="normal")
        self.observation_edit.delete("1.0", "end")
        self.observation_edit.insert("1.0", value)
        self.observation_edit.configure(state="disabled")

    def _selected_row(self) -> ReviewRow | None:
        selection = self.review_tree.selection()
        if not selection:
            messagebox.showwarning("Falta fila", "Selecciona una fila de la revisión.")
            return None
        return self.review_by_id.get(selection[0])

    def _load_selected_review(self, _event=None) -> None:
        selection = self.review_tree.selection()
        if not selection:
            return
        row = self.review_by_id.get(selection[0])
        if row is None:
            return
        issues = "; ".join(row.issues) if row.issues else "sin incidencias"
        rules = ", ".join(row.rule_ids) if row.rule_ids else "sin reglas"
        self.review_meta.set(
            f"Origen: {row.source_sheet}, fila {row.source_row} · Reglas: {rules} · {issues}"
        )
        self._set_observation_text(row.observation)

    def _refresh_review_from_db(self, selected_id: str = "") -> None:
        if not self.current_batch_id:
            return
        rows = self.controller.load_rows(self.current_batch_id)
        self._show_review_rows(rows)
        if selected_id and selected_id in self.review_by_id:
            self.review_tree.selection_set(selected_id)
            self.review_tree.see(selected_id)
            self._load_selected_review()

    def approve_current_batch(self) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta lote", "Analiza y revisa un archivo antes de aprobar.")
            return
        try:
            snapshot_hash = self.controller.approve_batch(
                self.current_batch_id, require_review_import=True
            )
        except Exception as exc:
            messagebox.showerror("Lote no aprobable", str(exc))
            return
        self.analysis_status.set(f"Lote aprobado y congelado · snapshot {snapshot_hash[:12]}…")
        messagebox.showinfo(
            "Constancia congelada",
            "La constancia del trabajo registrado en RUS quedó congelada. Ya puedes preparar productos.",
        )

    def use_saved_review(self) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta análisis", "Analiza un archivo primero.")
            return
        path = self.db.get_working_workbook(self.current_batch_id)
        if path is None or not path.is_file():
            messagebox.showwarning(
                "Copia no disponible",
                "Exporta las propuestas primero. Si moviste o renombraste el Excel, usa «Elegir otra copia…».",
            )
            return
        if not messagebox.askyesno(
            "Usar copia de trabajo",
            f"Se leerá la copia:\n{path}\n\nGuarda y cierra tus cambios en Excel antes de continuar. "
            "No necesitas volver a seleccionar el archivo. ¿Continuar?",
        ):
            return
        self.import_reviewed_excel(path=path, freeze_when_ready=True)

    def import_reviewed_excel(self, *, path=None, freeze_when_ready=False) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta análisis", "Analiza un archivo antes de cargar su constancia.")
            return
        if path is None:
            path = filedialog.askopenfilename(
                title="Seleccionar Excel revisado",
                filetypes=[("Excel", "*.xlsx *.xlsm *.xls")],
            )
        if not path:
            return
        try:
            preview = preview_reviewed_workbook(self.db, self.current_batch_id, path)
        except Exception as exc:
            messagebox.showerror("No se pudo leer la constancia", str(exc))
            return
        if not preview.valid:
            messagebox.showerror(
                "Constancia no válida",
                "\n".join(preview.errors[:12]),
            )
            return
        responsible = simpledialog.askstring(
            "Responsable de la revisión",
            "Nombre de quien confirma la revisión registrada en RUS:",
            parent=self.root,
            initialvalue=os.environ.get("USERNAME", ""),
        ) or ""
        if not responsible.strip():
            return
        confirmed = messagebox.askyesno(
            "Confirmación obligatoria",
            "¿Confirmas que las filas incluidas en esta constancia fueron revisadas una por una y que "
            "su observación oficial quedó registrada en el sistema RUS?\n\n"
            f"Incluidas revisadas: {preview.reviewed_count}\n"
            f"Excluidas: {preview.excluded_count}\n"
            f"Observaciones modificadas: {preview.changed_observations}\n"
            + ("\n".join(preview.warnings) if preview.warnings else ""),
        )
        if not confirmed:
            return
        try:
            imported = import_reviewed_workbook(
                self.db,
                self.current_batch_id,
                path,
                responsible=responsible,
                confirmed_in_rus=True,
                expected_sha256=preview.sha256,
            )
        except ReviewImportError as exc:
            messagebox.showerror("No se pudo registrar la constancia", str(exc))
            return
        self._refresh_review_from_db()
        self.db.remember_working_workbook(self.current_batch_id, path)
        pending = sum(
            row["decision"] != "excluded" and not row["rus_recorded"]
            for row in self.db.list_review_records(self.current_batch_id)
        )
        self.analysis_status.set(
            f"Constancia cargada · SHA-256 {imported.sha256[:12]}… · "
            + (f"{pending} fila(s) aún pendientes" if pending else "lista para congelar")
        )
        if freeze_when_ready and not pending:
            self.approve_current_batch()
            return
        messagebox.showinfo(
            "Constancia cargada",
            "La constancia fue validada. "
            + (
                f"Quedan {pending} fila(s) sin constancia; carga las devoluciones restantes."
                if pending
                else "Documenta la excepción de cruce si corresponde y presiona «Congelar constancia»."
            ),
        )

    def document_cross_sheet_exception(self) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta lote", "Analiza un lote de Cumplimiento antes de documentar una excepción.")
            return
        responsible = simpledialog.askstring(
            "Responsable", "Indica el nombre de quien autoriza la excepción:", parent=self.root,
            initialvalue=os.environ.get("USERNAME", ""),
        ) or ""
        if not responsible.strip():
            return
        reason = simpledialog.askstring(
            "Motivo", "Indica el motivo de aprobar sin hoja de cruce:", parent=self.root,
        ) or ""
        if not reason.strip():
            return
        try:
            self.controller.document_missing_cross_sheet_exception(
                self.current_batch_id, responsible=responsible, reason=reason
            )
        except Exception as exc:
            messagebox.showerror("No se pudo documentar", str(exc))
            return
        self.analysis_status.set(
            "Excepción de hoja de cruce documentada. Revisa el lote y apruébalo cuando corresponda."
        )
        messagebox.showinfo(
            "Excepción documentada",
            "El responsable y el motivo quedarán congelados dentro del snapshot al aprobar el lote.",
        )

    def export_current_workbook(self) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta análisis", "Analiza un archivo antes de exportar las propuestas.")
            return
        batch = self.db.get_batch(self.current_batch_id)
        if batch is None:
            messagebox.showwarning("Falta análisis", "No se encontró el análisis actual.")
            return
        suffix = Path(batch["source_name"]).suffix.lower()
        if suffix not in {".xls", ".xlsx", ".xlsm"}:
            messagebox.showerror("Formato no admitido", "El lote no proviene de un archivo Excel exportable.")
            return
        target = filedialog.asksaveasfilename(
            title="Guardar Excel de propuestas",
            defaultextension=suffix,
            initialfile=Path(batch["source_name"]).stem + " - propuestas" + suffix,
            filetypes=[("Excel", "*" + suffix)],
        )
        if not target:
            return
        batch_id = self.current_batch_id

        def done(result):
            messagebox.showinfo(
                "Excel de propuestas",
                "Se creó el insumo para revisión humana. Todavía no acredita revisión ni registro en RUS.\n"
                f"{result.row_count} fila(s) · {result.path}\n\n"
                "Revisa en RUS, guarda la constancia en este Excel y pulsa «Usar revisión guardada». "
                "NuRus recordará esta copia; no tendrás que buscarla nuevamente.",
            )
            if self.current_batch_id == batch_id:
                self.analysis_status.set(f"Copia de revisión creada: {result.path}")

        self.analysis_status.set("Exportando una copia preservada…")
        self.run_io(lambda: export_proposal_workbook(self.db, batch_id, target), done)

    def export_final_workbook(self) -> None:
        batch = self.db.get_batch(self.current_batch_id) if self.current_batch_id else None
        if batch is None or batch["status"] != "approved":
            messagebox.showwarning("Falta constancia", "Guarda tu revisión en Excel y pulsa «Usar revisión guardada» antes de exportar la constancia.")
            return
        suffix = Path(batch["source_name"]).suffix.lower()
        target = filedialog.asksaveasfilename(
            title="Guardar constancia final",
            defaultextension=suffix,
            initialfile=Path(batch["source_name"]).stem + " - constancia" + suffix,
            filetypes=[("Excel", "*" + suffix)],
        )
        if not target:
            return
        batch_id = self.current_batch_id
        self.run_io(
            lambda: export_preserved_workbook(self.db, batch_id, target),
            lambda result: messagebox.showinfo(
                "Constancia exportada", f"{result.row_count} filas · {result.path.name}"
            ),
        )

    def export_statistics(self) -> None:
        from nurus.services.statistics import build_review_statistics, export_review_statistics

        batch = self.db.get_batch(self.current_batch_id) if self.current_batch_id else None
        if batch is None or batch["status"] != "approved":
            messagebox.showwarning("Falta constancia", "Congela una constancia antes de contar gestión.")
            return
        start = simpledialog.askstring("Estadísticas", "Desde FECHA_OBS (AAAA-MM-DD):", parent=self.root)
        if start is None:
            return
        end = simpledialog.askstring("Estadísticas", "Hasta FECHA_OBS inclusive (AAAA-MM-DD):", parent=self.root)
        if end is None:
            return
        try:
            stats = build_review_statistics(
                self.db, self.current_batch_id, date.fromisoformat(start), date.fromisoformat(end)
            )
        except ValueError as exc:
            messagebox.showerror("Estadísticas", str(exc))
            return
        target = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if target:
            self.run_io(
                lambda: export_review_statistics(stats, target),
                lambda path: messagebox.showinfo(
                    "Estadísticas",
                    f"{stats.reviewed_in_period} revisiones en período. Reporte: {path}",
                ),
            )

    def open_product_dialog(self) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta lote", "Analiza y aprueba un lote antes de preparar productos.")
            return
        batch = self.db.get_batch(self.current_batch_id)
        if batch is None or batch["status"] != "approved":
            messagebox.showwarning("Falta constancia", "Guarda tu revisión en Excel y pulsa «Usar revisión guardada».")
            return

        published = [item for item in self.db.list_templates() if item.status == "published"]
        if not published:
            messagebox.showwarning("Falta plantilla", "No hay plantillas publicadas.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Preparar producto desde snapshot")
        dialog.geometry("780x620")
        dialog.minsize(680, 520)
        dialog.transient(self.root)

        frame = ttk.Frame(dialog, padding=12)
        frame.pack(fill="both", expand=True)
        template_var = tk.StringVar()
        template_names = [f"{item.kind.value}: {item.name} (v{item.version})" for item in published]
        recipient_var = tk.StringVar()
        cc_var = tk.StringVar()
        scope_var = tk.StringVar(value="all")
        status_var = tk.StringVar(value="El producto aún no ha sido preparado.")

        ttk.Label(frame, text="Plantilla").grid(row=0, column=0, sticky="w")
        combo = ttk.Combobox(frame, textvariable=template_var, state="readonly", values=template_names)
        combo.grid(row=0, column=1, columnspan=3, sticky="ew", padx=6)
        combo.current(0)
        ttk.Label(frame, text="Destinatario").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=recipient_var).grid(row=1, column=1, sticky="ew", padx=6)
        ttk.Label(frame, text="CC").grid(row=1, column=2, sticky="w")
        ttk.Entry(frame, textvariable=cc_var).grid(row=1, column=3, sticky="ew", padx=6)

        ttk.Radiobutton(frame, text="Todos los registros aprobados", variable=scope_var, value="all").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(frame, text="Solo la fila seleccionada", variable=scope_var, value="selected").grid(row=2, column=2, columnspan=2, sticky="w")

        ttk.Label(frame, text="Asunto").grid(row=3, column=0, sticky="nw", pady=(8, 2))
        subject_var = tk.StringVar()
        ttk.Entry(frame, textvariable=subject_var).grid(row=3, column=1, columnspan=3, sticky="ew", padx=6, pady=(8, 2))
        ttk.Label(frame, text="Contenido").grid(row=4, column=0, sticky="nw")
        body_text = tk.Text(frame, height=18, wrap="word")
        body_text.grid(row=4, column=1, columnspan=3, sticky="nsew", padx=6)
        ttk.Label(frame, textvariable=status_var, style="Subtitle.TLabel", wraplength=700).grid(row=5, column=0, columnspan=4, sticky="w", pady=6)

        product_holder: dict[str, Product] = {}

        def prepare_preview() -> None:
            index = combo.current()
            if index < 0:
                return
            record_ids = None
            if scope_var.get() == "selected":
                selection = self.review_tree.selection()
                if not selection:
                    messagebox.showwarning("Falta fila", "Selecciona una fila en la revisión.", parent=dialog)
                    return
                record_ids = (selection[0],)
            try:
                product = prepare_from_snapshot(
                    self.db,
                    self.current_batch_id,
                    published[index].id,
                    record_ids=record_ids,
                    recipient=recipient_var.get(),
                    cc=cc_var.get(),
                )
            except Exception as exc:
                messagebox.showerror("No se pudo preparar", str(exc), parent=dialog)
                return
            product_holder["product"] = product
            subject_var.set(product.rendered_subject)
            body_text.delete("1.0", "end")
            body_text.insert("1.0", product.rendered_body)
            messages = [*product.issues, *product.warnings]
            status_var.set(
                f"Estado: {product.status.value}" + (" · " + " · ".join(messages) if messages else "")
            )

        def approve_and_save() -> None:
            product = product_holder.get("product")
            if product is None:
                messagebox.showwarning("Falta vista previa", "Prepara primero la vista previa.", parent=dialog)
                return
            product.recipient = recipient_var.get().strip()
            product.cc = cc_var.get().strip()
            product.rendered_subject = subject_var.get().strip()
            product.rendered_body = body_text.get("1.0", "end-1c").strip()
            review_product(self, product)
            dialog.destroy()

        buttons = ttk.Frame(frame)
        buttons.grid(row=6, column=0, columnspan=4, sticky="e", pady=(4, 0))
        ttk.Button(buttons, text="Preparar vista previa", command=prepare_preview).pack(side="left", padx=4)
        ttk.Button(buttons, text="Abrir revisión final", style="Primary.TButton", command=approve_and_save).pack(side="left")

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(4, weight=1)

    def resolution_dialog(self) -> None:
        selected = self._selected_row()
        if not selected or not self.current_batch_id:
            return
        templates = [
            item for item in self.db.list_templates()
            if item.id.startswith("historica-") and item.status == "published"
        ]
        dialog = tk.Toplevel(self.root)
        dialog.title("Proyecto · revisión judicial obligatoria")
        combo = ttk.Combobox(
            dialog, state="readonly", width=60, values=[item.name for item in templates]
        )
        combo.pack(padx=12, pady=12)
        if templates:
            combo.current(0)

        def build():
            if combo.current() < 0:
                return
            if not messagebox.askyesno(
                "Revisión previa",
                "¿Verificaste la carpeta judicial, el tipo de proyecto y su procedencia?\n"
                "La antigüedad por sí sola no autoriza generar el proyecto.",
                parent=dialog,
            ):
                return
            template = templates[combo.current()]
            extra = {}
            if "NOMENCLATURA" in template.allowed_variables:
                value = simpledialog.askstring("Dato verificado", "Nomenclatura:", parent=dialog)
                if not value:
                    return
                extra["NOMENCLATURA"] = value
            try:
                product = prepare_resolution(
                    self.db, self.current_batch_id, selected.record_id, template.id,
                    confirmed_review=True, extra=extra,
                )
                review_product(self, product)
                dialog.destroy()
            except Exception as exc:
                messagebox.showerror("Proyecto", str(exc), parent=dialog)

        ttk.Button(dialog, text="Preparar desde esta fila", command=build).pack(pady=8)

    # ---------- Comunicación particular ----------
    def _particular_work_tab(self) -> None:
        form = ttk.LabelFrame(self.particular_tab, text="Producto revisable sin planilla RUS", padding=12)
        form.pack(fill="x")
        self.template_var = tk.StringVar()
        self.recipient_var = tk.StringVar()
        self.program_var = tk.StringVar()
        self.court_var = tk.StringVar(value="Juzgado de Familia")
        self.particular_detail_var = tk.StringVar()
        for row, (label, variable) in enumerate([
            ("Tipo y plantilla", self.template_var),
            ("Programa / entidad", self.program_var),
            ("Destinatario", self.recipient_var),
            ("Tribunal", self.court_var),
            ("Detalle / registros", self.particular_detail_var),
        ]):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            if row == 0:
                self.template_combo = ttk.Combobox(form, textvariable=variable, state="readonly", width=45)
                self.template_combo.grid(row=row, column=1, sticky="ew", padx=8)
            else:
                ttk.Entry(form, textvariable=variable, width=46).grid(row=row, column=1, sticky="ew", padx=8)
        form.columnconfigure(1, weight=1)
        ttk.Button(
            self.particular_tab,
            text="Preparar para revisión",
            style="Primary.TButton",
            command=self.prepare_product,
        ).pack(anchor="e", pady=8)
        self.preview = tk.Text(self.particular_tab, height=14, wrap="word", state="disabled")
        self.preview.pack(fill="both", expand=True)
        self.refresh_templates()

    def refresh_templates(self) -> None:
        self.template_items = []
        for template in self.db.list_templates():
            if template.kind is not ProductKind.EMAIL:
                continue
            try:
                if self.db.get_communication_policy(template.id)["filter"] != "manual":
                    continue
            except ValueError:
                pass
            self.template_items.append(template)
        names = [
            f"{template.kind.value}: {template.name} (v{template.version})"
            for template in self.template_items if template.status == "published"
        ]
        if hasattr(self, "template_combo"):
            self.template_combo["values"] = names
            if names:
                self.template_combo.current(0)

    def prepare_product(self) -> None:
        index = self.template_combo.current()
        published = [template for template in self.template_items if template.status == "published"]
        if index < 0 or not published:
            messagebox.showwarning("Falta plantilla", "Selecciona una plantilla publicada.")
            return
        template = published[index]
        detail = self.particular_detail_var.get().strip()
        context = {
            "TRIBUNAL": self.court_var.get().strip(),
            "PROGRAMA": self.program_var.get().strip(),
            "FECHA_CORTE": date.today().isoformat(),
            "OBSERVACION": detail,
            "TABLA_REGISTROS": detail,
        }
        for key in template.allowed_variables:
            if key not in context:
                value = simpledialog.askstring(
                    "Dato para la plantilla", key.replace("_", " "), parent=self.root
                )
                if value is None:
                    return
                context[key] = value
        try:
            attachment_required = bool(
                self.db.get_communication_policy(template.id)["required_attachment"]
            )
        except ValueError:
            attachment_required = False
        self.current = prepare(
            Product(
                kind=template.kind,
                template=template,
                context=context,
                recipient=self.recipient_var.get().strip(),
                required_attachment=attachment_required,
            )
        )
        text = (
            f"Estado: {self.current.status.value}\n\nAsunto\n{self.current.rendered_subject}\n\n"
            f"Contenido\n{self.current.rendered_body}\n\n"
        )
        if self.current.issues:
            text += "Errores\n" + "\n".join(f"• {item}" for item in self.current.issues) + "\n\n"
        if self.current.warnings:
            text += "Advertencias\n" + "\n".join(f"• {item}" for item in self.current.warnings)
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", text)
        self.preview.configure(state="disabled")
        review_product(self, self.current)

    # ---------- Plantillas ----------
    def _templates_tab(self) -> None:
        ttk.Label(self.templates, text="Plantillas", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.templates,
            text="Cada guardado crea una versión nueva; los productos antiguos conservan su versión.",
        ).pack(anchor="w", pady=(0, 8))
        self.template_list = tk.Listbox(self.templates, height=8)
        self.template_list.pack(fill="x")
        self.template_list.bind("<<ListboxSelect>>", self.load_template)
        fields = ttk.Frame(self.templates)
        fields.pack(fill="both", expand=True, pady=8)
        self.name_edit, self.subject_edit = tk.StringVar(), tk.StringVar()
        ttk.Entry(fields, textvariable=self.name_edit).pack(fill="x")
        ttk.Entry(fields, textvariable=self.subject_edit).pack(fill="x", pady=4)
        self.body_edit = tk.Text(fields, height=12, wrap="word")
        self.body_edit.pack(fill="both", expand=True)
        ttk.Button(self.templates, text="Guardar como nueva versión", command=self.save_template).pack(anchor="e", pady=8)
        ttk.Button(self.templates, text="Configurar este tipo de correo…", command=self.edit_communication_policy).pack(anchor="e")
        self.refresh_template_editor()

    def edit_communication_policy(self) -> None:
        if not hasattr(self, "editing_template"):
            messagebox.showwarning("Plantilla", "Selecciona un tipo de correo.")
            return
        try:
            policy = self.db.get_communication_policy(self.editing_template.id)
        except ValueError as exc:
            messagebox.showinfo("Política", str(exc))
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Configuración operativa · solo nuevas preparaciones")
        variables = {}
        for key, label, options in (
            ("mode", "Modalidad", ("", "ESPERA", "CUMPLIMIENTO", "INFORMES")),
            ("group", "Agrupar por", ("tribunal", "programa")),
            ("filter", "Selección propuesta", ("all", "manual", "medidas", "E-05", "I-01", "I-02")),
        ):
            ttk.Label(dialog, text=label).pack(anchor="w", padx=12)
            variable = tk.StringVar(value=policy[key])
            ttk.Combobox(
                dialog, textvariable=variable, state="readonly", values=options
            ).pack(fill="x", padx=12, pady=4)
            variables[key] = variable
        required = tk.BooleanVar(value=policy["required_attachment"])
        ttk.Checkbutton(dialog, text="Exigir adjunto", variable=required).pack(padx=12, pady=8)

        def save():
            try:
                self.db.save_communication_policy(
                    self.editing_template.id,
                    {
                        **{key: value.get() for key, value in variables.items()},
                        "required_attachment": required.get(),
                    },
                )
                self.refresh_templates()
                dialog.destroy()
            except ValueError as exc:
                messagebox.showerror("Política", str(exc), parent=dialog)

        ttk.Button(dialog, text="Guardar configuración", command=save).pack(pady=8)

    def refresh_template_editor(self) -> None:
        self.template_list.delete(0, "end")
        for template in self.db.list_templates():
            self.template_list.insert("end", f"{template.kind.value}: {template.name} · v{template.version}")

    def load_template(self, _event=None) -> None:
        index = self.template_list.curselection()
        if not index:
            return
        self.editing_template = self.db.list_templates()[index[0]]
        self.name_edit.set(self.editing_template.name)
        self.subject_edit.set(self.editing_template.subject)
        self.body_edit.delete("1.0", "end")
        self.body_edit.insert("1.0", self.editing_template.body)

    def save_template(self) -> None:
        if not hasattr(self, "editing_template"):
            messagebox.showwarning("Selecciona plantilla", "Elige una plantilla para editar.")
            return
        old = self.editing_template
        saved = self.db.save_template(
            Template(
                id=old.id,
                name=self.name_edit.get().strip(),
                kind=old.kind,
                subject=self.subject_edit.get(),
                body=self.body_edit.get("1.0", "end-1c"),
                allowed_variables=old.allowed_variables,
                status=old.status,
                version=old.version,
            )
        )
        self.editing_template = saved
        self.refresh_template_editor()
        self.refresh_templates()
        messagebox.showinfo("Guardado", f"Se guardó la versión {saved.version}.")

    # ---------- Contactos ----------
    def _contacts_tab(self) -> None:
        ttk.Label(self.contacts, text="Contactos", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.contacts, text="Los contactos se resuelven por identidad/alias explícitos, nunca por similitud automática.").pack(anchor="w")
        self.contacts_text = tk.Text(self.contacts, height=20, state="disabled")
        self.contacts_text.pack(fill="both", expand=True, pady=10)
        ttk.Button(self.contacts, text="Actualizar lista", command=self.refresh_contacts).pack(anchor="e")
        ttk.Button(self.contacts, text="Importar Excel con vista previa…", command=self.import_contacts).pack(anchor="e")
        ttk.Button(self.contacts, text="Agregar / actualizar contacto…", command=self.edit_contact).pack(anchor="e")
        self.refresh_contacts()

    def refresh_contacts(self) -> None:
        lines = [f"{row['display_name']}  <{row['email']}>" for row in self.db.list_contacts()] or [
            "Aún no hay contactos. Importa el catastro o agrega un tribunal/programa."
        ]
        self.contacts_text.configure(state="normal")
        self.contacts_text.delete("1.0", "end")
        self.contacts_text.insert("1.0", "\n".join(lines))
        self.contacts_text.configure(state="disabled")

    def edit_contact(self) -> None:
        from nurus.rus.columns import normalize

        name = simpledialog.askstring(
            "Contacto", "Nombre exacto del tribunal o programa:", parent=self.root
        )
        if not name:
            return
        email = simpledialog.askstring(
            "Contacto", "Direcciones separadas por ;", parent=self.root
        )
        if not email or not _valid_addresses(email):
            messagebox.showerror("Contacto", "Dirección inválida.")
            return
        if messagebox.askyesno("Confirmar contacto", f"¿Guardar o actualizar {name}?"):
            self.db.save_contact(normalize(name), name.strip(), email.strip())
            self.refresh_contacts()

    def import_contacts(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("Catastro Excel", "*.xlsx *.xlsm *.xls")]
        )
        if not path:
            return
        try:
            preview = preview_contact_import(self.db, path)
        except Exception as exc:
            messagebox.showerror("Importación", str(exc))
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Contactos · selecciona altas y cambios")
        dialog.geometry("900x500")
        listing = tk.Listbox(dialog, selectmode="extended")
        listing.pack(fill="both", expand=True)
        for item in preview.changes:
            listing.insert(
                "end", f"{item.action} | {item.display_name} | {item.email} | {item.issue}"
            )

        def apply():
            accepted = {preview.changes[int(index)].entity_key for index in listing.curselection()}
            try:
                count = apply_contact_preview(self.db, preview, accepted)
            except Exception as exc:
                messagebox.showerror("No se aplicaron cambios", str(exc), parent=dialog)
                return
            messagebox.showinfo(
                "Contactos", f"{count} contactos actualizados localmente. Outlook no fue modificado."
            )
            dialog.destroy()
            self.refresh_contacts()

        ttk.Button(dialog, text="Aplicar seleccionados", command=apply).pack(anchor="e")

    # ---------- Historial ----------
    def _history_tab(self) -> None:
        ttk.Label(self.history, text="Historial", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.history,
            text="Productos preparados localmente. NuRus nunca envía correos; Outlook solo puede guardar borradores confirmados.",
        ).pack(anchor="w", pady=8)
        frame = ttk.Frame(self.history)
        frame.pack(fill="both", expand=True)
        self.history_tree = ttk.Treeview(
            frame,
            columns=("fecha", "tipo", "estado", "destino", "asunto"),
            show="headings",
        )
        for key, title, width in [
            ("fecha", "Fecha", 150),
            ("tipo", "Tipo", 100),
            ("estado", "Estado", 100),
            ("destino", "Destinatario", 200),
            ("asunto", "Asunto", 300),
        ]:
            self.history_tree.heading(key, text=title)
            self.history_tree.column(key, width=width, stretch=key == "asunto")
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=self.history_tree.yview)
        xscroll = ttk.Scrollbar(frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        ttk.Button(self.history, text="Actualizar historial", command=self.refresh_history).pack(anchor="e", pady=8)
        self.refresh_history()

    def refresh_history(self) -> None:
        if not hasattr(self, "history_tree"):
            return
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for item in self.db.list_products():
            self.history_tree.insert(
                "", "end",
                values=(
                    item["created_at"], item["kind"], item["status"],
                    item["recipient"] or "Pendiente", item["subject"],
                ),
            )


def main() -> None:
    root = tk.Tk()
    NuRusApp(root, Database(data_dir() / "nurus.sqlite3"))
    root.mainloop()


if __name__ == "__main__":
    main()
