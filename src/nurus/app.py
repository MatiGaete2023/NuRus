from __future__ import annotations

import hashlib
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from nurus.domain.models import Product, ProductKind, Template
from nurus.services.rendering import prepare
from nurus.storage.database import Database


def data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(root) / "NuRus"


class NuRusApp(ttk.Frame):
    def __init__(self, root: tk.Tk, db: Database) -> None:
        super().__init__(root, padding=16)
        self.root, self.db = root, db
        self.current: Product | None = None
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
        header = ttk.Frame(self); header.pack(fill="x")
        ttk.Label(header, text="NuRus", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Revisa y genera productos con control humano.", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 12))
        self.tabs = ttk.Notebook(self); self.tabs.pack(fill="both", expand=True)
        self.work = ttk.Frame(self.tabs, padding=12); self.templates = ttk.Frame(self.tabs, padding=12)
        self.contacts = ttk.Frame(self.tabs, padding=12); self.history = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.work, text="Trabajo")
        self.tabs.add(self.history, text="Historial")
        self.tabs.add(self.templates, text="Plantillas")
        self.tabs.add(self.contacts, text="Contactos")
        self._work_tab(); self._templates_tab(); self._contacts_tab(); self._history_tab()

    def _work_tab(self) -> None:
        ttk.Label(self.work, text="1 Cargar  ·  2 Revisar  ·  3 Generar", style="Title.TLabel").pack(anchor="w")
        row = ttk.Frame(self.work); row.pack(fill="x", pady=12)
        self.file_var = tk.StringVar(value="Sin archivo: puedes preparar una comunicación particular.")
        ttk.Label(row, textvariable=self.file_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Elegir archivo", command=self.choose_file).pack(side="right")
        form = ttk.LabelFrame(self.work, text="Producto revisable", padding=12); form.pack(fill="x")
        self.template_var = tk.StringVar(); self.recipient_var = tk.StringVar(); self.program_var = tk.StringVar(); self.court_var = tk.StringVar(value="Juzgado de Familia")
        ttk.Label(form, text="Tipo y plantilla").grid(row=0, column=0, sticky="w")
        self.template_combo = ttk.Combobox(form, textvariable=self.template_var, state="readonly", width=45); self.template_combo.grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Label(form, text="Programa / entidad").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.program_var, width=46).grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Label(form, text="Destinatario").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.recipient_var, width=46).grid(row=2, column=1, sticky="ew", padx=8)
        ttk.Label(form, text="Tribunal").grid(row=3, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.court_var, width=46).grid(row=3, column=1, sticky="ew", padx=8)
        form.columnconfigure(1, weight=1)
        ttk.Button(self.work, text="Preparar para revisión", style="Primary.TButton", command=self.prepare_product).pack(anchor="e", pady=12)
        self.preview = tk.Text(self.work, height=15, wrap="word", state="disabled"); self.preview.pack(fill="both", expand=True)
        self.refresh_templates()

    def choose_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xlsm *.xls"), ("Todos", "*.*")])
        if path:
            self.file_var.set(Path(path).name + " · " + hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12])

    def refresh_templates(self) -> None:
        self.template_items = self.db.list_templates()
        names = [f"{t.kind.value}: {t.name} (v{t.version})" for t in self.template_items if t.status == "published"]
        self.template_combo["values"] = names
        if names: self.template_combo.current(0)

    def prepare_product(self) -> None:
        index = self.template_combo.current()
        published = [t for t in self.template_items if t.status == "published"]
        if index < 0 or not published:
            return messagebox.showwarning("Falta plantilla", "Selecciona una plantilla publicada.")
        template = published[index]
        ctx = {"TRIBUNAL": self.court_var.get(), "PROGRAMA": self.program_var.get(), "FECHA_CORTE": "por completar", "OBSERVACION": "por completar", "TABLA_REGISTROS": "Sin registros cargados"}
        self.current = prepare(Product(kind=template.kind, template=template, context=ctx, recipient=self.recipient_var.get()))
        self.db.record_product(self.current, self.file_var.get())
        text = f"Estado: {self.current.status.value}\n\nAsunto\n{self.current.rendered_subject}\n\nContenido\n{self.current.rendered_body}\n\n"
        text += "Observaciones\n" + ("\n".join(f"• {x}" for x in self.current.issues) or "Sin observaciones")
        self.preview.configure(state="normal"); self.preview.delete("1.0", "end"); self.preview.insert("1.0", text); self.preview.configure(state="disabled")
        self.refresh_history()

    def _templates_tab(self) -> None:
        ttk.Label(self.templates, text="Plantillas", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.templates, text="Edita asunto y contenido; las variables permitidas se validan antes de generar.").pack(anchor="w", pady=(0, 8))
        self.template_list = tk.Listbox(self.templates, height=8); self.template_list.pack(fill="x")
        self.template_list.bind("<<ListboxSelect>>", self.load_template)
        fields = ttk.Frame(self.templates); fields.pack(fill="both", expand=True, pady=8)
        self.name_edit, self.subject_edit = tk.StringVar(), tk.StringVar()
        ttk.Entry(fields, textvariable=self.name_edit).pack(fill="x")
        ttk.Entry(fields, textvariable=self.subject_edit).pack(fill="x", pady=4)
        self.body_edit = tk.Text(fields, height=12, wrap="word"); self.body_edit.pack(fill="both", expand=True)
        ttk.Button(self.templates, text="Guardar como nueva versión", command=self.save_template).pack(anchor="e", pady=8)
        self.refresh_template_editor()

    def refresh_template_editor(self) -> None:
        self.template_list.delete(0, "end")
        for t in self.db.list_templates(): self.template_list.insert("end", f"{t.kind.value}: {t.name}")

    def load_template(self, _event=None) -> None:
        idx = self.template_list.curselection()
        if not idx: return
        self.editing_template = self.db.list_templates()[idx[0]]
        self.name_edit.set(self.editing_template.name); self.subject_edit.set(self.editing_template.subject)
        self.body_edit.delete("1.0", "end"); self.body_edit.insert("1.0", self.editing_template.body)

    def save_template(self) -> None:
        if not hasattr(self, "editing_template"): return messagebox.showwarning("Selecciona plantilla", "Elige una plantilla para editar.")
        old = self.editing_template
        self.db.save_template(Template(id=old.id, name=self.name_edit.get().strip(), kind=old.kind, subject=self.subject_edit.get(), body=self.body_edit.get("1.0", "end-1c"), allowed_variables=old.allowed_variables, status=old.status, version=old.version))
        self.refresh_template_editor(); self.refresh_templates(); messagebox.showinfo("Guardado", "Se guardó una nueva versión local.")

    def _contacts_tab(self) -> None:
        ttk.Label(self.contacts, text="Contactos", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.contacts, text="El contacto se sugiere; nunca se asigna por coincidencia aproximada.").pack(anchor="w")
        self.contacts_text = tk.Text(self.contacts, height=20, state="disabled"); self.contacts_text.pack(fill="both", expand=True, pady=10)
        ttk.Button(self.contacts, text="Actualizar lista", command=self.refresh_contacts).pack(anchor="e")
        self.refresh_contacts()

    def refresh_contacts(self) -> None:
        lines = [f"{r['display_name']}  <{r['email']}>" for r in self.db.list_contacts()] or ["Aún no hay contactos. Importa o registra los contactos durante la migración."]
        self.contacts_text.configure(state="normal"); self.contacts_text.delete("1.0", "end"); self.contacts_text.insert("1.0", "\n".join(lines)); self.contacts_text.configure(state="disabled")

    def _history_tab(self) -> None:
        ttk.Label(self.history, text="Historial", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.history, text="Productos preparados localmente. Crear un borrador Outlook exige una acción posterior y explícita.").pack(anchor="w", pady=8)
        self.history_tree = ttk.Treeview(self.history, columns=("fecha", "tipo", "estado", "destino", "asunto"), show="headings")
        for key, title, width in [("fecha", "Fecha", 150), ("tipo", "Tipo", 100), ("estado", "Estado", 100), ("destino", "Destinatario", 200), ("asunto", "Asunto", 300)]:
            self.history_tree.heading(key, text=title); self.history_tree.column(key, width=width, stretch=key == "asunto")
        self.history_tree.pack(fill="both", expand=True)
        ttk.Button(self.history, text="Actualizar historial", command=self.refresh_history).pack(anchor="e", pady=8)
        self.refresh_history()

    def refresh_history(self) -> None:
        if not hasattr(self, "history_tree"):
            return
        for row in self.history_tree.get_children(): self.history_tree.delete(row)
        for item in self.db.list_products():
            self.history_tree.insert("", "end", values=(item["created_at"], item["kind"], item["status"], item["recipient"] or "Pendiente", item["subject"]))


def main() -> None:
    root = tk.Tk()
    NuRusApp(root, Database(data_dir() / "nurus.sqlite3"))
    root.mainloop()


if __name__ == "__main__":
    main()
