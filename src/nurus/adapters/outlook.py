from __future__ import annotations

import platform

from nurus.domain.models import Product, ProductStatus


class OutlookUnavailable(RuntimeError):
    pass


def create_draft(product: Product, *, confirmed: bool = False) -> Product:
    """Guarda un borrador Outlook. NuRus nunca envía correos.

    La creación exige confirmación explícita del llamador. El destinatario puede
    quedar vacío para completarlo manualmente durante la revisión humana. Los
    errores de contenido sí bloquean la creación.
    """
    if not confirmed:
        raise ValueError("Confirma explícitamente la creación del borrador Outlook.")
    if product.status not in {ProductStatus.READY, ProductStatus.APPROVED}:
        raise ValueError("Solo se pueden crear borradores de productos completos y revisados.")
    if platform.system() != "Windows":
        raise OutlookUnavailable("Outlook Object Model solo se prueba en Windows con Outlook clásico.")
    try:
        import win32com.client  # type: ignore[import-not-found]
    except ImportError as exc:
        raise OutlookUnavailable("Instale pywin32 en el equipo Windows autorizado.") from exc

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = product.recipient
    mail.CC = product.cc
    mail.Subject = product.rendered_subject
    mail.Body = product.rendered_body
    # INVARIANTE: únicamente Save. No existe ninguna ruta de envío automático.
    mail.Save()
    product.status = ProductStatus.CREATED
    return product
