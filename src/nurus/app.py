from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from nurus.domain.models import Product, Template
from nurus.rus import Mode
from nurus.services.products import approve_product, persist_approved_product, prepare_from_snapshot
from nurus.services.rendering import prepare
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
            text="Analiza, revisa y prepara productos con control humano. NuRus nunca envía correos.",
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

    # ---------- Trabajo ----------
    def _work_tab(self) -> None:
        ttk.Label(self.work, text="1 Cargar  ·  2 Revisar  ·  3 Aprobar  ·  4 Preparar", style="Title.TLabel").pack(anchor="w")
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

        self.review_pane = ttk.Panedwindow(self.rus_tab, orient="vertical")
        self.review_pane.pack(fill="both", expand=True, pady=(8, 0))

        table_frame = ttk.Frame(self.review_pane)
        detail_frame = ttk.LabelFrame(self.review_pane, text="Detalle y revisión", padding=8)
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

        self.review_summary = tk.StringVar(value="Sin análisis.")
        ttk.Label(detail_frame, textvariable=self.review_summary).pack(anchor="w")
        self.review_meta = tk.StringVar(value="Selecciona una fila para ver su procedencia y reglas.")
        ttk.Label(detail_frame, textvariable=self.review_meta, style="Subtitle.TLabel").pack(anchor="w", pady=(2, 4))
        self.observation_edit = tk.Text(detail_frame, height=5, wrap="word")
        self.observation_edit.pack(fill="both", expand=True)

        actions = ttk.Frame(detail_frame)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(actions, text="Aprobar fila", command=self.approve_selected_row).pack(side="left")
        ttk.Button(actions, text="Excluir", command=self.exclude_selected_row).pack(side="left", padx=4)
        ttk.Button(actions, text="Restaurar propuesta", command=self.restore_selected_row).pack(side="left")
        ttk.Button(actions, text="Aprobar lote", style="Primary.TButton", command=self.approve_current_batch).pack(side="right")
        ttk.Button(actions, text="Preparar producto…", command=self.open_product_dialog).pack(side="right", padx=(0, 6))

    def choose_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xlsm *.xls"), ("Todos", "*.*")])
        if not path:
            return
        self.selected_path = Path(path)
        self.file_var.set(f"{self.selected_path.name} · seleccionado, sin analizar")
        self._invalidate_analysis("Archivo seleccionado. Presiona «Analizar archivo».", keep_file=True)

    def _invalidate_analysis(self, message: str, *, keep_file: bool = True) -> None:
        self.analysis_generation += 1
        self.current_batch_id = ""
        self.review_by_id.clear()
        self.review_summary.set("Sin análisis vigente.")
        self.review_meta.set("Selecciona y analiza un archivo.")
        self.observation_edit.delete("1.0", "end")
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
        self.analysis_generation += 1
        generation = self.analysis_generation
        self.analysis_busy = True
        self.analyze_button.configure(state="disabled")
        self.analysis_status.set("Analizando copia estable del archivo…")

        def worker() -> None:
            try:
                result = self.controller.analyze(path, mode)
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
        rows = self.controller.rows_from_batch(batch)
        self._show_review_rows(rows)
        warning = f" · {len(batch.warnings)} advertencia(s)" if batch.warnings else ""
        self.analysis_status.set(
            f"Analizado: {batch.workbook_name} · SHA-256 {batch.workbook_sha256[:12]}…{warning}"
        )

    def _show_review_rows(self, rows: tuple[ReviewRow, ...]) -> None:
        self.review_by_id = {row.record_id: row for row in rows}
        for item in self.review_tree.get_children():
            self.review_tree.delete(item)
        for row in rows:
            observation = " ".join(row.observation.split())
            self.review_tree.insert(
                "", "end", iid=row.record_id,
                values=(row.decision, row.rit, row.tribunal, row.programa, observation),
            )
        counts: dict[str, int] = {}
        for row in rows:
            counts[row.decision] = counts.get(row.decision, 0) + 1
        summary = " · ".join(f"{key}: {value}" for key, value in sorted(counts.items())) or "sin filas"
        self.review_summary.set(f"{len(rows)} fila(s) · {summary}")
        self.review_meta.set("Selecciona una fila para revisar procedencia, reglas e incidencias.")
        self.observation_edit.delete("1.0", "end")

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
        self.observation_edit.delete("1.0", "end")
        self.observation_edit.insert("1.0", row.observation)

    def _refresh_review_from_db(self, selected_id: str = "") -> None:
        if not self.current_batch_id:
            return
        rows = self.controller.load_rows(self.current_batch_id)
        self._show_review_rows(rows)
        if selected_id and selected_id in self.review_by_id:
            self.review_tree.selection_set(selected_id)
            self.review_tree.see(selected_id)
            self._load_selected_review()

    def approve_selected_row(self) -> None:
        row = self._selected_row()
        if row is None or not self.current_batch_id:
            return
        observation = self.observation_edit.get("1.0", "end-1c").strip()
        reason = ""
        if observation != row.original_observation:
            reason = simpledialog.askstring("Motivo", "Indica el motivo de la edición:", parent=self.root) or ""
            if not reason.strip():
                return
        try:
            self.controller.approve_record(
                self.current_batch_id, row.record_id, observation=observation, reason=reason
            )
        except Exception as exc:
            messagebox.showerror("No se pudo aprobar", str(exc))
            return
        self._refresh_review_from_db(row.record_id)

    def exclude_selected_row(self) -> None:
        row = self._selected_row()
        if row is None or not self.current_batch_id:
            return
        reason = simpledialog.askstring("Motivo", "Indica por qué se excluye esta fila:", parent=self.root) or ""
        if not reason.strip():
            return
        try:
            self.controller.exclude_record(self.current_batch_id, row.record_id, reason=reason)
        except Exception as exc:
            messagebox.showerror("No se pudo excluir", str(exc))
            return
        self._refresh_review_from_db(row.record_id)

    def restore_selected_row(self) -> None:
        row = self._selected_row()
        if row is None or not self.current_batch_id:
            return
        try:
            self.controller.restore_record(self.current_batch_id, row.record_id)
        except Exception as exc:
            messagebox.showerror("No se pudo restaurar", str(exc))
            return
        self._refresh_review_from_db(row.record_id)

    def approve_current_batch(self) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta lote", "Analiza y revisa un archivo antes de aprobar.")
            return
        try:
            snapshot_hash = self.controller.approve_batch(self.current_batch_id)
        except Exception as exc:
            messagebox.showerror("Lote no aprobable", str(exc))
            return
        self.analysis_status.set(f"Lote aprobado y congelado · snapshot {snapshot_hash[:12]}…")
        messagebox.showinfo(
            "Lote aprobado",
            "La revisión quedó congelada. Ya puedes preparar un producto desde ese snapshot.",
        )

    def open_product_dialog(self) -> None:
        if not self.current_batch_id:
            messagebox.showwarning("Falta lote", "Analiza y aprueba un lote antes de preparar productos.")
            return
        batch = self.db.get_batch(self.current_batch_id)
        if batch is None or batch["status"] != "approved":
            messagebox.showwarning("Lote no aprobado", "Primero aprueba y congela la revisión del lote.")
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
            try:
                approve_product(
                    product,
                    subject=subject_var.get(),
                    body=body_text.get("1.0", "end-1c"),
                )
                persist_approved_product(self.db, product)
            except Exception as exc:
                messagebox.showerror("No se pudo aprobar", str(exc), parent=dialog)
                return
            self.refresh_history()
            messagebox.showinfo(
                "Producto aprobado",
                "El texto final quedó guardado con referencia al snapshot. No se creó ni envió ningún correo.",
                parent=dialog,
            )
            dialog.destroy()

        buttons = ttk.Frame(frame)
        buttons.grid(row=6, column=0, columnspan=4, sticky="e", pady=(4, 0))
        ttk.Button(buttons, text="Preparar vista previa", command=prepare_preview).pack(side="left", padx=4)
        ttk.Button(buttons, text="Aprobar y guardar", style="Primary.TButton", command=approve_and_save).pack(side="left")

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(4, weight=1)

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
        self.template_items = self.db.list_templates()
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
        self.current = prepare(
            Product(
                kind=template.kind,
                template=template,
                context=context,
                recipient=self.recipient_var.get().strip(),
            )
        )
        self.db.record_product(self.current)
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
        self.refresh_history()

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
        self.refresh_template_editor()

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
        self.refresh_contacts()

    def refresh_contacts(self) -> None:
        lines = [f"{row['display_name']}  <{row['email']}>" for row in self.db.list_contacts()] or [
            "Aún no hay contactos. La importación con vista previa corresponde a una fase posterior."
        ]
        self.contacts_text.configure(state="normal")
        self.contacts_text.delete("1.0", "end")
        self.contacts_text.insert("1.0", "\n".join(lines))
        self.contacts_text.configure(state="disabled")

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
