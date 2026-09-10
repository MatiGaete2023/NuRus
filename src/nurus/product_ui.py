"""Revisión compacta de productos: editar, aprobar y materializar por separado."""
from hashlib import sha256
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from nurus.domain.models import ProductKind
from nurus.services.communications import attach_snapshot_table, prepare_communications
from nurus.services.contacts import _valid_addresses
from nurus.services.delivery import save_approved_draft
from nurus.services.policy import with_mandatory_cc
from nurus.services.products import approve_product, persist_approved_product
from nurus.services.resolutions import export_resolution


def review_product(app, product):
    dialog = tk.Toplevel(app.root)
    dialog.title("Revisar producto · sin envío")
    dialog.geometry("860x670")
    dialog.minsize(700, 550)
    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    recipient = tk.StringVar(value=product.recipient)
    copies = tk.StringVar(value=product.cc)
    subject = tk.StringVar(value=product.rendered_subject)
    for label, variable in (
        ("Para (puede completarse en Outlook)", recipient),
        ("CC obligatoria incluida", copies),
        ("Asunto / título", subject),
    ):
        ttk.Label(frame, text=label).pack(anchor="w")
        ttk.Entry(frame, textvariable=variable).pack(fill="x", pady=(0, 4))
    body = tk.Text(frame, wrap="word", height=18)
    body.pack(fill="both", expand=True)
    body.insert("1.0", product.rendered_body)
    status = tk.StringVar(value="; ".join(product.issues + product.warnings) or "Revisa contenido y adjuntos.")
    attachments = tk.StringVar()
    ttk.Label(frame, textvariable=attachments, wraplength=800).pack(anchor="w", pady=4)
    ttk.Label(frame, textvariable=status, wraplength=800).pack(anchor="w")
    frozen_identity = []

    def identity():
        cc = with_mandatory_cc(copies.get()) if product.kind is ProductKind.EMAIL else copies.get().strip()
        return (
            recipient.get().strip(), cc, subject.get().strip(),
            body.get("1.0", "end-1c").strip(), tuple(product.attachments),
        )

    def show_attachments():
        attachments.set("Adjuntos: " + (", ".join(Path(path).name for path, _ in product.attachments) or "ninguno"))

    def attach():
        if frozen_identity:
            messagebox.showwarning("Producto congelado", "Prepara una versión nueva para cambiar adjuntos.", parent=dialog)
            return
        for chosen in filedialog.askopenfilenames(parent=dialog, title="Adjuntar archivos revisados"):
            resolved = str(Path(chosen).resolve())
            if resolved not in {path for path, _ in product.attachments}:
                product.attachments.append((resolved, sha256(Path(resolved).read_bytes()).hexdigest()))
        show_attachments()

    def table():
        if frozen_identity:
            return
        directory = filedialog.askdirectory(parent=dialog, title="Guardar nómina limitada a este correo")
        if directory:
            try:
                attach_snapshot_table(app.db, product, directory)
                show_attachments()
            except Exception as exc:
                messagebox.showerror("Nómina", str(exc), parent=dialog)

    def approve():
        if frozen_identity:
            status.set("Producto ya aprobado. Para cambiarlo, prepara una nueva versión.")
            return
        to, cc, title, text, _ = identity()
        if product.kind is ProductKind.EMAIL and ((to and not _valid_addresses(to)) or not _valid_addresses(cc)):
            messagebox.showerror("Direcciones", "Revisa el formato de Para y CC.", parent=dialog)
            return
        try:
            if product.required_attachment and not product.attachments:
                raise ValueError("Este tipo de correo requiere un adjunto revisado.")
            for path, digest in product.attachments:
                if sha256(Path(path).read_bytes()).hexdigest() != digest:
                    raise ValueError("Un adjunto cambió desde su selección.")
            product.recipient, product.cc = to, cc
            approve_product(product, subject=title, body=text)
            persist_approved_product(app.db, product)
            frozen_identity[:] = [identity()]
            status.set("Aprobado en historial. Aún no se creó borrador ni Word.")
            app.refresh_history()
        except Exception as exc:
            messagebox.showerror("Aprobación", str(exc), parent=dialog)

    def materialize():
        if frozen_identity != [identity()]:
            messagebox.showwarning("Revisión necesaria", "Aprueba exactamente esta versión antes de guardarla.", parent=dialog)
            return
        if product.kind is ProductKind.EMAIL:
            account = simpledialog.askstring(
                "Cuenta Outlook", "Cuenta SMTP exacta (vacío = predeterminada):", parent=dialog
            )
            if account is None or not messagebox.askyesno(
                "Confirmar borrador",
                f"¿Guardar un borrador?\nPara: {product.recipient or '(vacío)'}\nCC: {product.cc}\nNo se enviará.",
                parent=dialog,
            ):
                return
            app.run_io(
                lambda: save_approved_draft(app.db, product, confirmed=True, account_key=account or None),
                lambda receipt: status.set("Borrador guardado: " + receipt.folder),
            )
        else:
            path = filedialog.asksaveasfilename(
                parent=dialog, defaultextension=".docx", filetypes=[("Word", "*.docx")]
            )
            if path:
                app.run_io(
                    lambda: export_resolution(app.db, product, path),
                    lambda target: status.set("Proyecto Word guardado: " + str(target)),
                )

    buttons = ttk.Frame(frame)
    buttons.pack(fill="x", pady=8)
    if product.kind is ProductKind.EMAIL:
        ttk.Button(buttons, text="Adjuntar archivo…", command=attach).pack(side="left")
        if product.record_ids:
            ttk.Button(buttons, text="Crear nómina limitada…", command=table).pack(side="left", padx=4)
    ttk.Button(buttons, text="Aprobar texto y adjuntos", command=approve).pack(side="left", padx=4)
    ttk.Button(
        buttons,
        text="Guardar borrador Outlook…" if product.kind is ProductKind.EMAIL else "Guardar Word…",
        command=materialize,
    ).pack(side="right")
    show_attachments()


def communications_dialog(app):
    batch = app.db.get_batch(app.current_batch_id) if app.current_batch_id else None
    if batch is None or batch["status"] != "approved":
        messagebox.showwarning("Falta constancia", "Carga y congela una constancia antes de preparar correos.")
        return
    dialog = tk.Toplevel(app.root)
    dialog.title("Correos agrupados desde la constancia")
    dialog.geometry("820x500")
    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    templates = []
    for template in app.db.list_templates():
        try:
            if template.status == "published" and app.db.get_communication_policy(template.id)["filter"] != "manual":
                templates.append(template)
        except ValueError:
            pass
    combo = ttk.Combobox(frame, state="readonly", values=[item.name for item in templates])
    combo.pack(fill="x")
    if templates:
        combo.current(0)
    ttk.Label(frame, text="Modalidades efectivamente revisadas").pack(anchor="w")
    modalities = ttk.Entry(frame)
    modalities.pack(fill="x")
    ttk.Label(frame, text="Período, si corresponde").pack(anchor="w")
    period = ttk.Entry(frame)
    period.pack(fill="x")
    ttk.Label(
        frame,
        text="La agrupación es una propuesta. Revisa la tabla y confirma cada correo antes de aprobarlo.",
    ).pack(anchor="w", pady=6)
    listing = tk.Listbox(frame)
    listing.pack(fill="both", expand=True, pady=8)
    products, signature = [], []

    def identity():
        return combo.current(), modalities.get(), period.get()

    def preview():
        try:
            if combo.current() < 0:
                return
            products[:] = prepare_communications(
                app.db, app.current_batch_id, templates[combo.current()].id,
                modalities=modalities.get(), period=period.get(),
            )
            listing.delete(0, "end")
            for product in products:
                listing.insert(
                    "end",
                    f"{product.context['TRIBUNAL']} | {product.context['PROGRAMA']} | "
                    f"{len(product.record_ids)} registros | {product.status.value}",
                )
            signature[:] = [identity()]
            if not products:
                messagebox.showinfo("Sin correos", "No hay registros para este tipo.", parent=dialog)
        except Exception as exc:
            products.clear()
            signature.clear()
            listing.delete(0, "end")
            messagebox.showerror("Preparación", str(exc), parent=dialog)

    def review():
        if signature != [identity()]:
            messagebox.showwarning("Vista previa antigua", "Prepara nuevamente la lista.", parent=dialog)
            return
        selected = listing.curselection()
        if selected:
            review_product(app, products[selected[0]])

    ttk.Button(frame, text="Preparar lista", command=preview).pack(side="left")
    ttk.Button(frame, text="Revisar seleccionado…", command=review).pack(side="right")
